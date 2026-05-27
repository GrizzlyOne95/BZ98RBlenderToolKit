import os

INNER_COLLISION_NAMES = {
    "inner_col",
    "innercol",
    "inner_collision",
    "innercollision",
}

OUTER_COLLISION_NAMES = {
    "outer_col",
    "outercol",
    "outer_collision",
    "outercollision",
}

HARDPOINT_SUFFIX_RULES = {
    70: ("Weapon hardpoint", "g"),
    71: ("Cannon hardpoint", "gc"),
    72: ("Rocket hardpoint", "gr"),
    73: ("Mortar hardpoint", "gm"),
    74: ("Special hardpoint", "gs"),
}

SEVERITY_ORDER = {
    "ERROR": 0,
    "WARNING": 1,
    "INFO": 2,
}

LEGACY_ORIENTATION_MESSAGE = (
    "Legacy VDF/SDF/GEO vehicle export expects the nose/front toward Blender +Y. "
    "Direct Redux .mesh export expects Blender -Y; Legacy + Redux auto-port converts the legacy setup."
)


def fixgeoname(name, lod):
    geofilename = list(name)
    if len(geofilename) > 8:
        geofilename = geofilename[0:8]
    if lod in (1, 2, 3):
        geofilename[3] = str(lod)
    else:
        geofilename[3] = "3"
    geofilename[4] = "1"
    return "".join(geofilename)


def parse_legacy_geo_name(name):
    lower_name = (name or "").strip().lower()
    if len(lower_name) < 5:
        return {"valid": False, "reason": "too_short", "lod": None}
    if len(lower_name) > 8:
        return {"valid": False, "reason": "too_long", "lod": None}

    lod_char = lower_name[3]
    if lod_char not in {"1", "2", "3"}:
        return {"valid": False, "reason": "invalid_lod", "lod": None}

    return {"valid": True, "reason": None, "lod": int(lod_char)}


def is_collision_helper_name(name):
    lower_name = (name or "").strip().lower()
    return lower_name in INNER_COLLISION_NAMES or lower_name in OUTER_COLLISION_NAMES


def normalized_export_name(name, lod):
    return fixgeoname(name, lod).lower()


def legacy_geo_suffix(name):
    return ((name or "").strip().lower())[5:]


def legacy_geo_base_prefix(name):
    lower_name = (name or "").strip().lower()
    if len(lower_name) < 5:
        return lower_name
    return lower_name[:3] + lower_name[4]


def _is_numbered_suffix(suffix, prefix, min_index=1, max_index=5):
    if len(suffix) != 3 or not suffix.startswith(prefix):
        return False
    slot = suffix[2:]
    return slot.isdigit() and min_index <= int(slot) <= max_index


def issue_applies(issue, export_mode):
    export_modes = issue.get("export_modes", {"ALL"})
    return "ALL" in export_modes or export_mode in export_modes


def sort_issues(issues):
    return sorted(
        issues,
        key=lambda issue: (
            SEVERITY_ORDER.get(issue["severity"], 99),
            issue.get("target", "").lower(),
            issue.get("message", "").lower(),
        ),
    )


def collect_legacy_validation_issues(context, export_mode="ALL"):
    if export_mode == "GEO":
        issues = _collect_geo_export_issues(context)
        issues.append(_orientation_reference_issue({"GEO"}))
        return sort_issues(issues)
    return sort_issues(_collect_scene_export_issues(context))


def _make_issue(
    severity,
    scope,
    target,
    message,
    export_modes=None,
    object_name="",
    action="",
):
    return {
        "severity": severity,
        "scope": scope,
        "target": target or "",
        "message": message,
        "export_modes": set(export_modes or {"ALL"}),
        "object_name": object_name or "",
        "action": action or "",
    }


def _orientation_reference_issue(export_modes):
    modes = set(export_modes)
    modes.add("ALL")
    return _make_issue(
        "INFO",
        "Orientation",
        "vehicle front",
        LEGACY_ORIENTATION_MESSAGE,
        modes,
    )


def _derive_legacy_texture_name(name):
    base_name = os.path.splitext((name or "").strip())[0]
    base_name = base_name.replace(" ", "_").lower()
    return base_name[:8]


def _get_image_derived_texture_name(material):
    node_tree = getattr(material, "node_tree", None)
    if node_tree is None:
        return ""

    image_nodes = [
        node for node in getattr(node_tree, "nodes", [])
        if getattr(node, "type", "") == 'TEX_IMAGE' and getattr(node, "image", None) is not None
    ]
    if not image_nodes:
        return ""

    active_node = next((node for node in image_nodes if getattr(node, "select", False)), None)
    if active_node is None:
        active_node = image_nodes[0]

    image = active_node.image
    image_name = getattr(image, "name", "") or getattr(image, "filepath", "")
    return _derive_legacy_texture_name(image_name)


def _collect_geo_export_issues(context):
    issues = []
    view_layer = getattr(context, "view_layer", None)
    active_obj = getattr(getattr(view_layer, "objects", None), "active", None)

    if active_obj is None:
        issues.append(
                _make_issue(
                    "ERROR",
                    "Scene",
                    "",
                    "No active object selected. GEO export requires an active mesh object.",
                    {"GEO"},
                    action="select_object",
                )
            )
        return issues

    if getattr(active_obj, "type", None) != "MESH" or getattr(active_obj, "data", None) is None:
        issues.append(
                _make_issue(
                    "ERROR",
                    "Object",
                    active_obj.name,
                    "Active object is not a mesh. GEO export only supports mesh objects.",
                    {"GEO"},
                    object_name=active_obj.name,
                    action="select_object",
                )
            )
        return issues

    if len(getattr(active_obj.data, "vertices", [])) == 0:
        issues.append(
                _make_issue(
                    "ERROR",
                    "Object",
                    active_obj.name,
                    "Active mesh has no vertices and cannot be exported as GEO.",
                    {"GEO"},
                    object_name=active_obj.name,
                    action="select_object",
                )
            )

    issues.extend(_collect_material_issues(active_obj, {"GEO"}))
    return issues


def _collect_scene_export_issues(context):
    scene = getattr(context, "scene", None)
    if scene is None:
        return [
            _make_issue(
                "ERROR",
                "Scene",
                "",
                "No active scene available for validation.",
                {"VDF", "SDF"},
            )
        ]

    issues = [_orientation_reference_issue({"VDF", "SDF"})]
    named_candidates = []
    normalized_names = {}
    inner_helpers = []
    outer_helpers = []

    issues.extend(_collect_scene_armature_issues(scene.objects))

    for obj in scene.objects:
        lower_name = obj.name.lower()
        if lower_name in INNER_COLLISION_NAMES:
            inner_helpers.append(obj)
        if lower_name in OUTER_COLLISION_NAMES:
            outer_helpers.append(obj)

        name_info = parse_legacy_geo_name(obj.name)
        geo_props = getattr(obj, "GEOPropertyGroup", None)
        is_spinner_helper = bool(getattr(geo_props, "IsSpinnerHelper", False))
        spinner_like = is_spinner_helper or (int(getattr(geo_props, "GEOType", 0)) == 15)

        if not name_info["valid"]:
            if _looks_like_export_candidate(obj, spinner_like):
                issues.append(
                    _make_issue(
                        "WARNING",
                        "Object",
                        obj.name,
                        _invalid_name_message(name_info["reason"]),
                        {"VDF", "SDF"},
                        object_name=obj.name,
                        action="fix_name",
                    )
                )
            continue

        lod = name_info["lod"]
        normalized_name = normalized_export_name(obj.name, lod)
        named_candidates.append(
            {
                "object": obj,
                "lod": lod,
                "normalized_name": normalized_name,
                "spinner_like": spinner_like,
            }
        )
        normalized_names.setdefault(normalized_name, []).append(obj)

        if getattr(obj, "type", None) != "MESH":
            if spinner_like:
                issues.append(
                    _make_issue(
                        "ERROR",
                        "Object",
                        obj.name,
                        "Spinner/helper empties are VDF-only helpers and will break SDF export if left in a structure scene.",
                        {"SDF"},
                        object_name=obj.name,
                        action="select_object",
                    )
                )
            else:
                issues.append(
                    _make_issue(
                        "ERROR",
                        "Object",
                        obj.name,
                        "Object has a valid legacy export name but is not a mesh. Legacy VDF/SDF export expects mesh GEO data.",
                        {"VDF", "SDF"},
                        object_name=obj.name,
                        action="select_object",
                    )
                )
            continue

        if len(getattr(obj.data, "vertices", [])) == 0:
            issues.append(
                _make_issue(
                    "ERROR",
                    "Object",
                    obj.name,
                    "Mesh has a valid legacy export name but contains no vertices.",
                    {"VDF", "SDF"},
                    object_name=obj.name,
                    action="select_object",
                )
            )
            continue

        issues.extend(_collect_legacy_animation_limit_issues(obj))
        issues.extend(_collect_geotype_suffix_issues(obj))
        issues.extend(_collect_material_issues(obj, {"VDF", "SDF"}))

    for normalized_name, objects in normalized_names.items():
        if len(objects) < 2:
            continue
        object_names = ", ".join(sorted(obj.name for obj in objects))
        issues.append(
            _make_issue(
                "ERROR",
                "Scene",
                normalized_name,
                f"Multiple objects normalize to the same export name: {object_names}.",
                {"VDF", "SDF"},
            )
        )

    candidate_name_set = set(normalized_names.keys())
    for entry in named_candidates:
        obj = entry["object"]
        parent = getattr(obj, "parent", None)
        if parent is None:
            continue

        parent_info = parse_legacy_geo_name(parent.name)
        if not parent_info["valid"]:
            issues.append(
                _make_issue(
                    "WARNING",
                    "Object",
                    obj.name,
                    f"Parent '{parent.name}' is not legacy-exportable. This object will export with parent WORLD.",
                    {"VDF", "SDF"},
                    object_name=obj.name,
                    action="select_object",
                )
            )
            continue

        parent_name = normalized_export_name(parent.name, entry["lod"])
        if parent_name not in candidate_name_set:
            issues.append(
                _make_issue(
                    "WARNING",
                    "Object",
                    obj.name,
                    f"Parent '{parent.name}' does not resolve to an exportable object in the same LOD set. This object will likely export with parent WORLD.",
                    {"VDF", "SDF"},
                    object_name=obj.name,
                    action="select_object",
                )
            )

    issues.extend(_collect_collision_helper_issues(inner_helpers, "inner"))
    issues.extend(_collect_collision_helper_issues(outer_helpers, "outer"))
    issues.extend(_collect_turret_cockpit_issues(named_candidates))
    return issues


def _iter_action_fcurves(action):
    fcurves = getattr(action, "fcurves", None)
    if fcurves is not None:
        yield from fcurves
        return

    for layer in getattr(action, "layers", []):
        for strip in getattr(layer, "strips", []):
            for channelbag in getattr(strip, "channelbags", []):
                yield from getattr(channelbag, "fcurves", [])


def _has_action_fcurves(animation_data):
    action = getattr(animation_data, "action", None) if animation_data is not None else None
    if action is None:
        return False
    return any(True for _curve in _iter_action_fcurves(action))


def _has_armature_modifier(obj):
    for modifier in getattr(obj, "modifiers", []):
        if getattr(modifier, "type", None) == "ARMATURE":
            return True
    return False


def _has_weighted_vertex_groups(obj):
    vertex_groups = getattr(obj, "vertex_groups", None)
    if not vertex_groups:
        return False

    mesh = getattr(obj, "data", None)
    for vertex in getattr(mesh, "vertices", []):
        for group in getattr(vertex, "groups", []):
            try:
                if float(group.weight) != 0.0:
                    return True
            except Exception:
                continue
    return False


def _collect_scene_armature_issues(objects):
    issues = []
    for obj in objects:
        if getattr(obj, "type", None) != "ARMATURE":
            continue

        message = (
            "Armature objects are ignored by legacy VDF/SDF animation export. "
            "Only separate GEO object rotation and location keys are written; use Redux mesh/skeleton export for skeletal deformation."
        )
        if _has_action_fcurves(getattr(obj, "animation_data", None)):
            message = (
                "Armature animation will not export to legacy VDF/SDF. "
                "Legacy ANIM only writes separate GEO object rotation and location keys; use Redux mesh/skeleton export for bone animation."
            )

        issues.append(
            _make_issue(
                "WARNING",
                "Armature",
                obj.name,
                message,
                {"VDF", "SDF"},
                object_name=obj.name,
                action="select_object",
            )
        )
    return issues


def _collect_legacy_animation_limit_issues(obj):
    issues = []
    has_armature_modifier = _has_armature_modifier(obj)
    parent = getattr(obj, "parent", None)
    parent_is_armature = getattr(parent, "type", None) == "ARMATURE"
    has_weighted_groups = _has_weighted_vertex_groups(obj)

    if has_armature_modifier or parent_is_armature or (has_weighted_groups and has_armature_modifier):
        issues.append(
            _make_issue(
                "WARNING",
                "Animation",
                obj.name,
                (
                    "Skinned mesh deformation will not export to legacy VDF/SDF. "
                    "Each moving section must be a separate GEO object with its own rotation/location keys; use Redux mesh/skeleton export for weighted bones."
                ),
                {"VDF", "SDF"},
                object_name=obj.name,
                action="select_object",
            )
        )

    mesh = getattr(obj, "data", None)
    shape_keys = getattr(mesh, "shape_keys", None)
    key_blocks = getattr(shape_keys, "key_blocks", None)
    if shape_keys is not None and key_blocks is not None and len(key_blocks) > 1:
        issues.append(
            _make_issue(
                "WARNING",
                "Animation",
                obj.name,
                (
                    "Shape keys are not exported by legacy VDF/SDF. "
                    "Legacy ANIM only supports object rotation and location keys."
                ),
                {"VDF", "SDF"},
                object_name=obj.name,
                action="select_object",
            )
        )

    if _has_action_fcurves(getattr(shape_keys, "animation_data", None)):
        issues.append(
            _make_issue(
                "WARNING",
                "Animation",
                obj.name,
                (
                    "Shape key animation will be ignored by legacy VDF/SDF export. "
                    "Use separate rigid GEO pieces or Redux skeletal/mesh animation instead."
                ),
                {"VDF", "SDF"},
                object_name=obj.name,
                action="select_object",
            )
        )

    unsupported_paths = []
    anim = getattr(obj, "animation_data", None)
    action = getattr(anim, "action", None) if anim is not None else None
    supported_paths = {"location", "rotation_euler", "rotation_quaternion"}
    if action is not None:
        for curve in _iter_action_fcurves(action):
            data_path = getattr(curve, "data_path", "")
            if data_path and data_path not in supported_paths:
                unsupported_paths.append(data_path)

    if unsupported_paths:
        unique_paths = sorted(set(unsupported_paths))
        shown_paths = ", ".join(unique_paths[:4])
        if len(unique_paths) > 4:
            shown_paths += ", ..."
        issues.append(
            _make_issue(
                "WARNING",
                "Animation",
                obj.name,
                (
                    f"Unsupported animation channels will be ignored by legacy VDF/SDF export: {shown_paths}. "
                    "Only object location, Euler rotation, and quaternion rotation curves are written."
                ),
                {"VDF", "SDF"},
                object_name=obj.name,
                action="select_object",
            )
        )

    constraints = getattr(obj, "constraints", None)
    if constraints is not None and len(constraints) > 0:
        issues.append(
            _make_issue(
                "INFO",
                "Animation",
                obj.name,
                (
                    "Object constraints are not baked automatically for legacy VDF/SDF export. "
                    "Bake the final object rotation/location keys before exporting if constraints drive motion."
                ),
                {"VDF", "SDF"},
                object_name=obj.name,
                action="select_object",
            )
        )

    return issues


def _collect_geotype_suffix_issues(obj):
    issues = []
    geo_props = getattr(obj, "GEOPropertyGroup", None)
    if geo_props is None:
        return issues

    try:
        geo_type = int(getattr(geo_props, "GEOType", 0))
    except Exception:
        return issues

    suffix = legacy_geo_suffix(obj.name)
    if geo_type == 65:
        pitch_ok = _is_numbered_suffix(suffix, "tx", max_index=9)
        yaw_ok = _is_numbered_suffix(suffix, "ty", max_index=9)
        if not pitch_ok and not yaw_ok:
            issues.append(
                _make_issue(
                    "WARNING",
                    "GEO Type",
                    obj.name,
                    (
                        "Type 65 turret rotators should use a tx# pitch suffix or ty# yaw suffix "
                        "(for example tx1 or ty1). Battlezone may not apply turret rotation to this GEO."
                    ),
                    {"VDF"},
                    object_name=obj.name,
                    action="select_object",
                )
            )
        return issues

    hardpoint_rule = HARDPOINT_SUFFIX_RULES.get(geo_type)
    if hardpoint_rule is None:
        return issues

    role, prefix = hardpoint_rule
    if not _is_numbered_suffix(suffix, prefix, max_index=5):
        issues.append(
            _make_issue(
                "WARNING",
                "GEO Type",
                obj.name,
                (
                    f"Type {geo_type} {role.lower()} GEOs should use suffix {prefix}1-{prefix}5. "
                    "Battlezone uses that suffix to bind the hardpoint slot."
                ),
                {"VDF"},
                object_name=obj.name,
                action="select_object",
            )
        )

    return issues


def _geo_type(obj):
    geo_props = getattr(obj, "GEOPropertyGroup", None)
    if geo_props is None:
        return 0
    try:
        return int(getattr(geo_props, "GEOType", 0))
    except Exception:
        return 0


def _is_turret_yaw_name(name):
    return _is_numbered_suffix(legacy_geo_suffix(name), "ty", max_index=9)


def _is_turret_pitch_name(name):
    return _is_numbered_suffix(legacy_geo_suffix(name), "tx", max_index=9)


def _iter_ancestors(obj):
    seen = set()
    parent = getattr(obj, "parent", None)
    while parent is not None and id(parent) not in seen:
        seen.add(id(parent))
        yield parent
        parent = getattr(parent, "parent", None)


def _has_ancestor_matching(obj, predicate):
    return any(predicate(parent) for parent in _iter_ancestors(obj))


def _collect_turret_cockpit_issues(named_candidates):
    issues = []
    candidates = [entry["object"] for entry in named_candidates]
    if not candidates:
        return issues

    has_turret_rotator = any(_geo_type(obj) == 65 for obj in candidates)
    if not has_turret_rotator:
        return issues

    has_cockpit_lod = any(entry.get("lod") == 2 for entry in named_candidates)
    has_pov = any(_geo_type(obj) == 40 for obj in candidates)

    if has_cockpit_lod and has_pov:
        issues.append(
            _make_issue(
                "INFO",
                "Scene",
                "Turret cockpit",
                (
                    "Turret cockpit detected. Redux output should use separate cockpit files so cockpit-only "
                    "geometry can follow duplicate ty#/tx# cockpit bones instead of the camera bone."
                ),
                {"VDF"},
            )
        )

    for obj in candidates:
        geo_type = _geo_type(obj)
        if geo_type == 40:
            pitch_parent = next(
                (
                    parent for parent in _iter_ancestors(obj)
                    if _geo_type(parent) == 65 and _is_turret_pitch_name(parent.name)
                ),
                None,
            )
            if pitch_parent is not None:
                issues.append(
                    _make_issue(
                        "WARNING",
                        "Object",
                        obj.name,
                        (
                            f"POV is parented under pitch rotator '{pitch_parent.name}'. Redux turret cockpits "
                            "are more reliable when POV follows yaw only; keep guns/hardpoints under tx#."
                        ),
                        {"VDF"},
                        object_name=obj.name,
                        action="select_object",
                    )
                )

            yaw_parent = _has_ancestor_matching(
                obj,
                lambda parent: _geo_type(parent) == 65 and _is_turret_yaw_name(parent.name),
            )
            if not yaw_parent:
                issues.append(
                    _make_issue(
                        "WARNING",
                        "Object",
                        obj.name,
                        "Turret POV should usually be parented under a ty# yaw rotator so the cockpit view follows left/right aiming.",
                        {"VDF"},
                        object_name=obj.name,
                        action="select_object",
                    )
                )

        if geo_type in HARDPOINT_SUFFIX_RULES:
            pitch_parent = _has_ancestor_matching(
                obj,
                lambda parent: _geo_type(parent) == 65 and _is_turret_pitch_name(parent.name),
            )
            if not pitch_parent:
                issues.append(
                    _make_issue(
                        "WARNING",
                        "Object",
                        obj.name,
                        (
                            "Turret weapon/hardpoint GEOs should normally be parented under a tx# pitch rotator. "
                            "Otherwise guns may not follow up/down aiming in Redux."
                        ),
                        {"VDF"},
                        object_name=obj.name,
                        action="select_object",
                    )
                )

    cockpit_rotators = [
        obj for entry in named_candidates
        for obj in [entry["object"]]
        if entry.get("lod") == 2 and _geo_type(obj) == 65
    ]
    primary_rotator_prefixes = {
        legacy_geo_base_prefix(obj.name) + legacy_geo_suffix(obj.name)
        for entry in named_candidates
        for obj in [entry["object"]]
        if entry.get("lod") == 1 and _geo_type(obj) == 65
    }
    for obj in cockpit_rotators:
        counterpart_key = legacy_geo_base_prefix(obj.name) + legacy_geo_suffix(obj.name)
        if counterpart_key not in primary_rotator_prefixes:
            issues.append(
                _make_issue(
                    "WARNING",
                    "Object",
                    obj.name,
                    (
                        "Cockpit turret rotator has no matching primary ty#/tx# rotator. Separate Redux cockpit "
                        "files work best when cockpit LOD rotators mirror the primary turret rotators."
                    ),
                    {"VDF"},
                    object_name=obj.name,
                    action="select_object",
                )
            )

    return issues


def _collect_collision_helper_issues(helpers, label):
    issues = []
    if not helpers:
        return issues

    if len(helpers) > 1:
        helper_names = ", ".join(sorted(obj.name for obj in helpers))
        issues.append(
            _make_issue(
                "WARNING",
                "Scene",
                label,
                f"Multiple {label} collision helpers are present ({helper_names}). VDF export will use whichever object is encountered last.",
                {"VDF"},
            )
        )

    for helper in helpers:
        if getattr(helper, "type", None) != "MESH" or getattr(helper, "data", None) is None:
            issues.append(
                _make_issue(
                    "ERROR",
                    "Object",
                    helper.name,
                    "Collision helper is not a mesh object. VDF collision helpers must be meshes.",
                    {"VDF"},
                    object_name=helper.name,
                    action="select_object",
                )
            )
            continue

        if len(getattr(helper.data, "vertices", [])) == 0:
            issues.append(
                _make_issue(
                    "ERROR",
                    "Object",
                    helper.name,
                    "Collision helper mesh contains no vertices.",
                    {"VDF"},
                    object_name=helper.name,
                    action="select_object",
                )
            )

    return issues


def _collect_material_issues(obj, export_modes):
    issues = []
    mesh = getattr(obj, "data", None)
    materials = getattr(mesh, "materials", None)
    if materials is None:
        return issues

    for index, material in enumerate(materials):
        slot_label = f"{obj.name}:slot{index}"
        if material is None:
            issues.append(
                _make_issue(
                    "WARNING",
                    "Material",
                    slot_label,
                    "Material slot is empty. Export will fall back to blank texture naming for faces using this slot.",
                    export_modes,
                )
            )
            continue

        material_props = getattr(material, "MaterialPropertyGroup", None)
        raw_texture = ""
        if material_props is not None:
            raw_texture = (getattr(material_props, "MapTexture", "") or "").strip()
        image_texture = _get_image_derived_texture_name(material)

        if raw_texture and len(raw_texture) > 8:
            issues.append(
                _make_issue(
                    "WARNING",
                    "Material",
                    material.name,
                    f"Legacy texture name '{raw_texture}' exceeds 8 characters and may not round-trip cleanly.",
                    export_modes,
                    object_name=obj.name,
                    action="select_object",
                )
            )
            continue

        if raw_texture:
            continue

        if image_texture:
            issues.append(
                _make_issue(
                    "INFO",
                    "Material",
                    material.name,
                    f"Texture name is blank. Export will derive '{image_texture}' from the linked image texture.",
                    export_modes,
                    object_name=obj.name,
                    action="select_object",
                )
            )
            continue

        derived_name = _derive_legacy_texture_name(material.name)
        if not derived_name:
            issues.append(
                _make_issue(
                    "WARNING",
                    "Material",
                    slot_label,
                    "Material has no Battlezone texture name and no usable Blender material name to derive one from.",
                    export_modes,
                    object_name=obj.name,
                    action="select_object",
                )
            )
        elif len((material.name or "").strip().replace(" ", "_")) > 8:
            issues.append(
                _make_issue(
                    "INFO",
                    "Material",
                    material.name,
                    f"Texture name is blank. Export will auto-derive and truncate this material name to '{derived_name}'.",
                    export_modes,
                    object_name=obj.name,
                    action="select_object",
                )
            )

    return issues


def _looks_like_export_candidate(obj, spinner_like):
    if is_collision_helper_name(obj.name):
        return False
    if getattr(obj, "type", None) in {"MESH", "EMPTY"}:
        return True
    if spinner_like:
        return True
    return getattr(obj, "parent", None) is not None


def _invalid_name_message(reason):
    if reason == "too_short":
        return "Object name is shorter than 5 characters and will be skipped by legacy VDF/SDF export."
    if reason == "too_long":
        return "Object name exceeds 8 characters and will be skipped by legacy VDF/SDF export."
    if reason == "invalid_lod":
        return "Object name does not have a valid LOD marker at character 4 and will be skipped by legacy VDF/SDF export."
    return "Object name is not valid for legacy VDF/SDF export."
