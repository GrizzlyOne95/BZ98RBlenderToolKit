from typing import Any

# Battlezone 98R Blender ToolKit
# Copyright (C) 2024–2025 “GrizzlyOne95” and contributors
#
# This file is part of BZ98R Blender ToolKit, which is distributed
# under the terms of the GNU General Public License v3.0.
# See the LICENSE file or <https://www.gnu.org/licenses/>.

import bpy
import importlib
import os

from . import geo_classes

# Reload it just in case something changed!
importlib.reload(geo_classes)


def _prepare_export_object(context, obj):
    view_layer = getattr(context, "view_layer", None)
    if view_layer is None:
        view_layer = bpy.context.view_layer

    previous_active = getattr(view_layer.objects, "active", None)
    if obj is not None and previous_active is not obj:
        view_layer.objects.active = obj

    if obj is not None and getattr(obj, "mode", "OBJECT") != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")

    return view_layer, previous_active


def _derive_legacy_texture_name(name):
    base_name = os.path.splitext((name or "").strip())[0]
    base_name = base_name.replace(" ", "_").lower()
    return base_name[:8]


def _geo_coord(co):
    return (float(co.x), float(co.z), float(co.y))


def _vector_sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _vector_cross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def _vector_dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _normalize(vec):
    length_sq = _vector_dot(vec, vec)
    if length_sq <= 0.0:
        return (0.0, 0.0, 1.0)
    length = length_sq**0.5
    return (vec[0] / length, vec[1] / length, vec[2] / length)


def _compute_face_plane(mesh, face):
    if len(face.vertices) < 3:
        center = _geo_coord(face.center)
        return (0.0, 0.0, 1.0, center[2])

    points = [_geo_coord(mesh.vertices[index].co) for index in face.vertices[:3]]
    edge_a = _vector_sub(points[1], points[0])
    edge_b = _vector_sub(points[2], points[0])
    normal = _normalize(_vector_cross(edge_a, edge_b))
    distance = _vector_dot(normal, points[0])
    return (normal[0], normal[1], normal[2], distance)


def _get_image_derived_texture_name(material):
    node_tree = getattr(material, "node_tree", None)
    if node_tree is None:
        return ""

    image_nodes = [
        node
        for node in getattr(node_tree, "nodes", [])
        if getattr(node, "type", "") == "TEX_IMAGE"
        and getattr(node, "image", None) is not None
    ]
    if not image_nodes:
        return ""

    active_node = next(
        (node for node in image_nodes if getattr(node, "select", False)), None
    )
    if active_node is None:
        active_node = image_nodes[0]

    image = active_node.image
    return _derive_legacy_texture_name(
        getattr(image, "name", "") or getattr(image, "filepath", "")
    )


def geoexport(context, filepath, obj, *, face_plane_mode="CURRENT"):
    Vertices = []
    Normals = []
    Faces = []

    if obj is None:
        raise ValueError("No object provided for GEO export.")

    view_layer, previous_active = _prepare_export_object(context, obj)
    mesh = obj.data

    try:

        def _get_face_attr_int(attr_name, face_index, default_value=0):
            attrs = getattr(mesh, "attributes", None)
            if attrs is None:
                return int(default_value)
            attr = attrs.get(attr_name)
            if attr is None or attr.domain != "FACE":
                return int(default_value)
            try:
                return int(attr.data[face_index].value)
            except Exception:
                return int(default_value)

        def _get_face_attr_float(attr_name, face_index, default_value=0.0):
            attrs = getattr(mesh, "attributes", None)
            if attrs is None:
                return float(default_value)
            attr = attrs.get(attr_name)
            if attr is None or attr.domain != "FACE":
                return float(default_value)
            try:
                return float(attr.data[face_index].value)
            except Exception:
                return float(default_value)

        def _has_face_plane_attrs(face_index):
            attrs = getattr(mesh, "attributes", None)
            if attrs is None:
                return False
            for attr_name in (
                "bz_face_plane_x",
                "bz_face_plane_y",
                "bz_face_plane_z",
                "bz_face_plane_d",
            ):
                attr = attrs.get(attr_name)
                if attr is None or attr.domain != "FACE":
                    return False
                if face_index >= len(attr.data):
                    return False
            return True

        # ------------------------------------------------------------------
        # Failsafe: fix any invalid material indices on polygons
        # (Sometimes Blender can end up with garbage indices like 24264.)
        # ------------------------------------------------------------------
        mat_count = len(mesh.materials)
        if mat_count > 0:
            for poly in mesh.polygons:
                # Blender usually guarantees material_index is an int, but guard anyway
                idx = getattr(poly, "material_index", 0)
                if idx is None or idx < 0 or idx >= mat_count:
                    print(
                        "[BZ GEO Export] Warning: Invalid material index %s on polygon %s; resetting to 0."
                        % (idx, poly.index)
                    )
                    poly.material_index = 0

        # Collect vertices and normals
        for vertex in mesh.vertices:
            Vertices.append(
                geo_classes.GEOVertex([vertex.co.x, vertex.co.z, vertex.co.y])
            )
            Normals.append(
                geo_classes.GEONormal(
                    [-vertex.normal.x, -vertex.normal.z, -vertex.normal.y]
                )
            )

        face_plane_mode = (face_plane_mode or "CURRENT").upper()

        # Collect faces
        for face in mesh.polygons:
            # Get the basic data about the faces.
            facematerial = ""
            facecolor = [1, 1, 1]

            if (
                obj.data.materials is not None
                and len(obj.data.materials) > 0
                and face.material_index is not None
            ):
                mat = obj.data.materials[face.material_index]

                # ------------------------------------------------------------------
                # Default BZ texture name (MapTexture) from Blender material name
                # if the Battlezone Texture Name field is blank.
                # ------------------------------------------------------------------
                tex_name = ""
                if hasattr(mat, "MaterialPropertyGroup"):
                    # Current value in the Battlezone Texture Name box
                    raw = mat.MaterialPropertyGroup.MapTexture
                    tex_name = (raw or "").strip()

                    if not tex_name:
                        tex_name = _get_image_derived_texture_name(mat)
                    if not tex_name:
                        tex_name = _derive_legacy_texture_name(mat.name)

                    if tex_name:
                        # Write back so the UI box auto-fills after export
                        mat.MaterialPropertyGroup.MapTexture = tex_name

                facematerial = tex_name
                facecolor = getattr(mat, "diffuse_color", facecolor)

            # Convert Blender's 0–1 color into 0–255 RGB
            r = int(facecolor[0] * 255)
            g = int(facecolor[1] * 255)
            b = int(facecolor[2] * 255)

            # Create a new face object to be added in the GEO we are exporting.
            geo_pg = getattr(obj, "GEOPropertyGroup", None)
            default_unknown = (
                getattr(geo_pg, "GEOFaceUnknownDefault", 0) if geo_pg else 0
            )
            default_parent = getattr(geo_pg, "GEOFaceParentDefault", 0) if geo_pg else 0
            default_node = getattr(geo_pg, "GEOFaceNodeDefault", 0) if geo_pg else 0
            default_shade = (
                getattr(geo_pg, "GEOFaceShadeTypeDefault", 4) if geo_pg else 4
            )
            default_texture = (
                getattr(geo_pg, "GEOFaceTextureTypeDefault", 0) if geo_pg else 0
            )
            default_xluscent = (
                getattr(geo_pg, "GEOFaceXluscentTypeDefault", 0) if geo_pg else 0
            )

            face_unknown = _get_face_attr_int(
                "bz_face_unknown_raw", face.index, default_unknown
            )
            face_parent = _get_face_attr_int(
                "bz_face_parent", face.index, default_parent
            )
            face_node = _get_face_attr_int("bz_face_node", face.index, default_node)
            shade_type = (
                _get_face_attr_int("bz_face_shade_type", face.index, default_shade)
                & 0xFF
            )
            texture_type = (
                _get_face_attr_int("bz_face_texture_type", face.index, default_texture)
                & 0xFF
            )
            xluscent_type = (
                _get_face_attr_int(
                    "bz_face_xluscent_type", face.index, default_xluscent
                )
                & 0xFF
            )
            string_header_bytes = bytes([shade_type, texture_type, xluscent_type])

            if face_plane_mode == "PRESERVE" and _has_face_plane_attrs(face.index):
                plane_x = _get_face_attr_float(
                    "bz_face_plane_x", face.index, face.center.x
                )
                plane_y = _get_face_attr_float(
                    "bz_face_plane_y", face.index, face.center.y
                )
                plane_z = _get_face_attr_float(
                    "bz_face_plane_z", face.index, face.center.z
                )
                plane_d = _get_face_attr_float("bz_face_plane_d", face.index, 1.0)
            elif face_plane_mode in {"RECOMPUTE", "DX_FIX"}:
                plane_x, plane_y, plane_z, plane_d = _compute_face_plane(mesh, face)
            else:
                plane_x = face.center.x
                plane_y = face.center.y
                plane_z = face.center.z
                plane_d = 1.0

            NewFace = geo_classes.GEOFace(
                [
                    face.index,  # Index
                    len(face.vertices),  # Vertices
                    r,
                    g,
                    b,  # Color
                    plane_x,  # x
                    plane_y,  # y
                    plane_z,  # z
                    plane_d,  # d
                    face_unknown,  # unknown/raw int
                    string_header_bytes,  # StringHeader (shade/texture/xluscent bytes)
                    facematerial,  # MapName (texture name)
                    face_parent,  # Parent
                    face_node,  # Node
                    "",  # Extra entry (ignored by GEOFace)
                ]
            )

            # Ensure we have a UV layer
            if mesh.uv_layers.active is None:
                mesh.uv_layers.new()

            # Gather UVs for our face vertices.
            uv_layer = mesh.uv_layers.active.data
            curvert = 0
            for loop_index in range(face.loop_start, face.loop_start + face.loop_total):
                vert_index = face.vertices[curvert]
                u = uv_layer[loop_index].uv[0]
                v = 1.0 - uv_layer[loop_index].uv[1]

                NewFace.VertList.append(
                    geo_classes.PolygonVert(
                        [
                            vert_index,  # vertID
                            vert_index,  # vertID2 (often same as vertID)
                            u,
                            v,
                        ]
                    )
                )
                curvert += 1

            Faces.append(NewFace)

        import os
        import struct

        with open(filepath, mode="wb") as file:  # b is important -> binary
            geo_pg = getattr(obj, "GEOPropertyGroup", None)
            header_unknown = (
                int(getattr(geo_pg, "GEOHeaderUnknown", 69)) if geo_pg else 69
            )
            header_unknown2 = (
                int(getattr(geo_pg, "GEOHeaderUnknown2", 0)) if geo_pg else 0
            )
            NewHeader = geo_classes.GEOHeader(
                [
                    "OEG.",
                    header_unknown,
                    obj.name,
                    len(Vertices),
                    len(Faces),
                    header_unknown2,
                ]
            )
            buffer = bytearray(36)
            struct.pack_into("=4si16siii", buffer, 0, *NewHeader.Read())
            file.write(buffer)

            for vertex in Vertices:
                buffer = bytearray(12)
                struct.pack_into("=fff", buffer, 0, *vertex.Read())
                file.write(buffer)

            for normal in Normals:
                buffer = bytearray(12)
                struct.pack_into("=fff", buffer, 0, *normal.Read())
                file.write(buffer)

            for face in Faces:
                buffer = bytearray(55)
                struct.pack_into("=iiBBBffffi3s13sii", buffer, 0, *face.Read())
                file.write(buffer)
                for vert in face.VertList:
                    buffer = bytearray(16)
                    struct.pack_into("=iiff", buffer, 0, *vert.Read())
                    file.write(buffer)
    finally:
        if (
            view_layer is not None
            and previous_active is not None
            and previous_active is not obj
        ):
            view_layer.objects.active = previous_active

    return {"FINISHED"}


def export(context, *, filepath, face_plane_mode="CURRENT"):
    view_layer = getattr(context, "view_layer", None)
    active_obj = getattr(getattr(view_layer, "objects", None), "active", None)
    if active_obj is None:
        active_obj = bpy.context.view_layer.objects.active
    geoexport(context, filepath, active_obj, face_plane_mode=face_plane_mode)
    return {"FINISHED"}
