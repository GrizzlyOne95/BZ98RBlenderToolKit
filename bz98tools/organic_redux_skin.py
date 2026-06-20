from typing import Any

# Battlezone 98R Blender ToolKit
# Copyright (C) 2024-2026 "GrizzlyOne95" and contributors
#
# This file is part of BZ98R Blender ToolKit, which is distributed
# under the terms of the GNU General Public License v3.0.
# See the LICENSE file or <https://www.gnu.org/licenses/>.

from collections import defaultdict, deque

import bpy
from mathutils import Vector

from . import validation as bz_validation

WEIGHT_MODE_NEAREST = "NEAREST"
WEIGHT_MODE_BLENDS = "BLENDS"

ORGANIC_ARMATURE_MODIFIER_NAME = "Organic Redux Skin"


def is_valid_geo_control(obj):
    if obj is None:
        return False
    if bz_validation.is_collision_helper_name(getattr(obj, "name", "")):
        return False
    if getattr(obj, "GEOPropertyGroup", None) is None:
        return False
    return bool(
        bz_validation.parse_legacy_geo_name(getattr(obj, "name", "")).get("valid")
    )


def collect_selected_geo_controls(context, target_obj):
    return sort_controls_for_bones(
        [
            obj
            for obj in getattr(context, "selected_objects", [])
            if obj != target_obj and is_valid_geo_control(obj)
        ]
    )


def collect_active_geo_hierarchy(target_obj):
    seed = target_obj if is_valid_geo_control(target_obj) else None
    parent = getattr(target_obj, "parent", None)
    while seed is None and parent is not None:
        if is_valid_geo_control(parent):
            seed = parent
            break
        parent = getattr(parent, "parent", None)

    if seed is None:
        return []

    root = seed
    while getattr(root, "parent", None) is not None and is_valid_geo_control(
        root.parent
    ):
        root = root.parent

    controls = []
    queue = deque([root])
    seen = set()
    while queue:
        obj = queue.popleft()
        if obj.name in seen:
            continue
        seen.add(obj.name)
        if not is_valid_geo_control(obj):
            continue
        controls.append(obj)
        queue.extend(getattr(obj, "children", []))

    return sort_controls_for_bones(controls)


def sort_controls_for_bones(controls):
    control_set = set(controls)
    children_by_parent = defaultdict(list)
    roots = []

    for control in controls:
        parent = getattr(control, "parent", None)
        if parent in control_set:
            children_by_parent[parent].append(control)
        else:
            roots.append(control)

    for key in list(children_by_parent.keys()):
        children_by_parent[key].sort(key=lambda obj: obj.name.lower())
    roots.sort(key=lambda obj: obj.name.lower())

    ordered = []
    visited = set()

    def visit(obj):
        if obj.name in visited:
            return
        visited.add(obj.name)
        ordered.append(obj)
        for child in children_by_parent.get(obj, []):
            visit(child)

    for root in roots:
        visit(root)

    for control in sorted(controls, key=lambda obj: obj.name.lower()):
        visit(control)

    return ordered


def ensure_unique_control_names(controls):
    seen = set()
    duplicates = []
    for obj in controls:
        key = obj.name.lower()
        if key in seen:
            duplicates.append(obj.name)
        seen.add(key)
    if duplicates:
        duplicate_list = ", ".join(sorted(set(duplicates)))
        raise ValueError(
            f"Control names must be unique before creating bones: {duplicate_list}"
        )


def create_armature_from_controls(context, controls, name=None):
    ensure_unique_control_names(controls)

    collection = getattr(context, "collection", None) or context.scene.collection
    arm_data = bpy.data.armatures.new(name or "OrganicReduxSkin")
    arm_obj = bpy.data.objects.new(arm_data.name, arm_data)
    collection.objects.link(arm_obj)

    previous_active = context.view_layer.objects.active
    previous_selected = list(context.selected_objects)
    for obj in previous_selected:
        obj.select_set(False)
    arm_obj.select_set(True)
    context.view_layer.objects.active = arm_obj

    try:
        bpy.ops.object.mode_set(mode="EDIT")
        control_set = set(controls)
        children_by_parent = defaultdict(list)
        for control in controls:
            parent = getattr(control, "parent", None)
            if parent in control_set:
                children_by_parent[parent].append(control)
        for child_list in children_by_parent.values():
            child_list.sort(key=lambda obj: obj.name.lower())

        heads = {
            control: control.matrix_world.translation.copy() for control in controls
        }

        for index, control in enumerate(controls):
            bone = arm_data.edit_bones.new(control.name)
            head = heads[control]
            tail = _tail_for_control(control, heads, children_by_parent)
            bone.head = head
            bone.tail = tail
        for control in controls:
            parent = getattr(control, "parent", None)
            if parent in control_set:
                arm_data.edit_bones[control.name].parent = arm_data.edit_bones[
                    parent.name
                ]

        bpy.ops.object.mode_set(mode="OBJECT")

        for index, control in enumerate(controls):
            data_bone = arm_data.bones.get(control.name)
            if data_bone is not None:
                data_bone["OGREID"] = index

    finally:
        try:
            if context.mode != "OBJECT":
                bpy.ops.object.mode_set(mode="OBJECT")
        except Exception:
            pass
        for obj in list(context.selected_objects):
            obj.select_set(False)
        for obj in previous_selected:
            if obj.name in bpy.data.objects:
                obj.select_set(True)
        if previous_active and previous_active.name in bpy.data.objects:
            context.view_layer.objects.active = previous_active

    return arm_obj


def _tail_for_control(control, heads, children_by_parent):
    head = heads[control]
    children = children_by_parent.get(control, [])
    if children:
        tail = heads[children[0]]
        if (tail - head).length > 1e-5:
            return tail

    parent = getattr(control, "parent", None)
    if parent in heads:
        direction = head - heads[parent]
        if direction.length > 1e-5:
            return head + direction.normalized() * max(0.1, direction.length * 0.25)

    return head + Vector((0.0, 0.25, 0.0))


def bind_mesh_to_armature(
    target_obj,
    armature_obj,
    controls,
    weight_mode=WEIGHT_MODE_BLENDS,
    blend_radius=0.35,
    max_influences=3,
    replace_existing=True,
):
    if getattr(target_obj, "type", None) != "MESH":
        raise ValueError("Target object must be a mesh.")

    control_names = [control.name for control in controls]
    if replace_existing:
        _clear_existing_rig_data(target_obj, control_names)

    groups = {}
    for name in control_names:
        group = target_obj.vertex_groups.get(name)
        if group is None:
            group = target_obj.vertex_groups.new(name=name)
        groups[name] = group

    _write_vertex_weights(
        target_obj,
        controls,
        groups,
        weight_mode=weight_mode,
        blend_radius=max(0.0, float(blend_radius)),
        max_influences=max(1, min(3, int(max_influences))),
    )

    modifier = target_obj.modifiers.get(ORGANIC_ARMATURE_MODIFIER_NAME)
    if modifier is None:
        modifier = target_obj.modifiers.new(ORGANIC_ARMATURE_MODIFIER_NAME, "ARMATURE")
    modifier.object = armature_obj
    modifier.use_bone_envelopes = False
    modifier.use_vertex_groups = True


def _clear_existing_rig_data(target_obj, control_names):
    for modifier in list(target_obj.modifiers):
        if (
            modifier.type == "ARMATURE"
            and modifier.name == ORGANIC_ARMATURE_MODIFIER_NAME
        ):
            target_obj.modifiers.remove(modifier)

    for name in control_names:
        group = target_obj.vertex_groups.get(name)
        if group is not None:
            target_obj.vertex_groups.remove(group)


def _write_vertex_weights(
    target_obj, controls, groups, weight_mode, blend_radius, max_influences
):
    pivots = {
        control.name: control.matrix_world.translation.copy() for control in controls
    }
    hierarchy_edges = _hierarchy_edges(controls)
    for vertex in target_obj.data.vertices:
        vertex_world = target_obj.matrix_world @ vertex.co
        weights = _weights_for_vertex(
            vertex_world,
            controls,
            pivots,
            hierarchy_edges,
            weight_mode=weight_mode,
            blend_radius=blend_radius,
            max_influences=max_influences,
        )

        for name, weight in weights:
            groups[name].add([vertex.index], weight, "REPLACE")

    target_obj.data.update()


def _hierarchy_edges(controls):
    control_set = set(controls)
    edges = []
    for control in controls:
        parent = getattr(control, "parent", None)
        if parent in control_set:
            edges.append((parent.name, control.name))
    return edges


def _weights_for_vertex(
    vertex_world,
    controls,
    pivots,
    hierarchy_edges,
    weight_mode,
    blend_radius,
    max_influences,
):
    by_distance = sorted(
        (
            (control.name, max((vertex_world - pivots[control.name]).length, 1e-6))
            for control in controls
        ),
        key=lambda item: (item[1], item[0].lower()),
    )

    if not by_distance:
        return []

    if weight_mode == WEIGHT_MODE_NEAREST or max_influences == 1:
        return [(by_distance[0][0], 1.0)]

    candidates = {
        name: 1.0 / (distance * distance)
        for name, distance in by_distance[:max_influences]
    }

    if blend_radius > 0.0:
        for parent_name, child_name in hierarchy_edges:
            parent_pos = pivots[parent_name]
            child_pos = pivots[child_name]
            distance, factor = _distance_and_factor_on_segment(
                vertex_world, parent_pos, child_pos
            )
            if distance <= blend_radius:
                strength = max(0.0, 1.0 - (distance / blend_radius))
                candidates[parent_name] = max(
                    candidates.get(parent_name, 0.0), (1.0 - factor) * strength
                )
                candidates[child_name] = max(
                    candidates.get(child_name, 0.0), factor * strength
                )

    ranked = sorted(
        candidates.items(), key=lambda item: (item[1], item[0].lower()), reverse=True
    )[:max_influences]
    total = sum(weight for _name, weight in ranked)
    if total <= 0.0:
        return [(by_distance[0][0], 1.0)]
    return [(name, weight / total) for name, weight in ranked if weight > 0.0]


def _distance_and_factor_on_segment(point, start, end):
    segment = end - start
    length_sq = segment.length_squared
    if length_sq <= 1e-10:
        return (point - start).length, 0.0

    factor = (point - start).dot(segment) / length_sq
    factor = max(0.0, min(1.0, factor))
    nearest = start + segment * factor
    return (point - nearest).length, factor


def create_organic_redux_skin(
    context,
    target_obj,
    control_source="SELECTED",
    keep_controls_visible=False,
    weight_mode=WEIGHT_MODE_BLENDS,
    blend_radius=0.35,
    max_influences=3,
    replace_existing=True,
):
    if control_source == "HIERARCHY":
        controls = collect_active_geo_hierarchy(target_obj)
    else:
        controls = collect_selected_geo_controls(context, target_obj)
        if not controls:
            controls = collect_active_geo_hierarchy(target_obj)

    if len(controls) < 1:
        raise ValueError(
            "Select a target mesh plus at least one valid GEO control, or parent the mesh under a GEO hierarchy."
        )

    armature_name = f"{target_obj.name}_organic_rig"
    armature_obj = create_armature_from_controls(context, controls, name=armature_name)
    bind_mesh_to_armature(
        target_obj,
        armature_obj,
        controls,
        weight_mode=weight_mode,
        blend_radius=blend_radius,
        max_influences=max_influences,
        replace_existing=replace_existing,
    )

    if not keep_controls_visible:
        for control in controls:
            control.hide_viewport = True
            control.hide_render = True

    return armature_obj, controls
