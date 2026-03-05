# Battlezone 98R Blender ToolKit
# Copyright (C) 2024–2025 “GrizzlyOne95” and contributors
# 
# This file is part of BZ98R Blender ToolKit, which is distributed
# under the terms of the GNU General Public License v3.0.
# See the LICENSE file or <https://www.gnu.org/licenses/>.

import bpy
import importlib

from . import geo_classes
# Reload it just in case something changed!
importlib.reload(geo_classes)


def geoexport(context, filepath, obj):
    Vertices = []
    Normals = []
    Faces = []

    bpy.ops.object.mode_set(mode='OBJECT')
    mesh = obj.data

    def _get_face_attr_int(attr_name, face_index, default_value=0):
        attrs = getattr(mesh, "attributes", None)
        if attrs is None:
            return int(default_value)
        attr = attrs.get(attr_name)
        if attr is None or attr.domain != 'FACE':
            return int(default_value)
        try:
            return int(attr.data[face_index].value)
        except Exception:
            return int(default_value)

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

    # Collect faces
    for face in mesh.polygons:
        # Get the basic data about the faces.
        facematerial = ''
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
                    # Derive from material name, clamp to 8 chars
                    # (Battlezone .map name limit)
                    derived = (mat.name or "").strip()
                    # Replace spaces just to avoid weird names; feel free to tweak
                    derived = derived.replace(" ", "_")
                    tex_name = derived[:8]
                    # Optional: Battlezone usually uses lowercase map names
                    tex_name = tex_name.lower()

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
        default_unknown = getattr(geo_pg, "GEOFaceUnknownDefault", 0) if geo_pg else 0
        default_parent = getattr(geo_pg, "GEOFaceParentDefault", 0) if geo_pg else 0
        default_node = getattr(geo_pg, "GEOFaceNodeDefault", 0) if geo_pg else 0
        default_shade = getattr(geo_pg, "GEOFaceShadeTypeDefault", 4) if geo_pg else 4
        default_texture = getattr(geo_pg, "GEOFaceTextureTypeDefault", 0) if geo_pg else 0
        default_xluscent = getattr(geo_pg, "GEOFaceXluscentTypeDefault", 0) if geo_pg else 0

        face_unknown = _get_face_attr_int("bz_face_unknown_raw", face.index, default_unknown)
        face_parent = _get_face_attr_int("bz_face_parent", face.index, default_parent)
        face_node = _get_face_attr_int("bz_face_node", face.index, default_node)
        shade_type = _get_face_attr_int("bz_face_shade_type", face.index, default_shade) & 0xFF
        texture_type = _get_face_attr_int("bz_face_texture_type", face.index, default_texture) & 0xFF
        xluscent_type = _get_face_attr_int("bz_face_xluscent_type", face.index, default_xluscent) & 0xFF
        string_header_bytes = bytes([shade_type, texture_type, xluscent_type])

        NewFace = geo_classes.GEOFace(
            [
                face.index,              # Index
                len(face.vertices),      # Vertices
                r, g, b,                 # Color
                face.center.x,           # x
                face.center.y,           # y
                face.center.z,           # z
                1.0,                     # d
                face_unknown,            # unknown/raw int
                string_header_bytes,     # StringHeader (shade/texture/xluscent bytes)
                facematerial,            # MapName (texture name)
                face_parent,             # Parent
                face_node,               # Node
                '',                      # Extra entry (ignored by GEOFace)
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

    with open(filepath, mode='wb') as file:  # b is important -> binary
        geo_pg = getattr(obj, "GEOPropertyGroup", None)
        header_unknown = int(getattr(geo_pg, "GEOHeaderUnknown", 69)) if geo_pg else 69
        header_unknown2 = int(getattr(geo_pg, "GEOHeaderUnknown2", 0)) if geo_pg else 0
        NewHeader = geo_classes.GEOHeader(
            ['OEG.', header_unknown, obj.name, len(Vertices), len(Faces), header_unknown2]
        )
        buffer = bytearray(36)
        struct.pack_into('=4si16siii', buffer, 0, *NewHeader.Read())
        file.write(buffer)

        for vertex in Vertices:
            buffer = bytearray(12)
            struct.pack_into('=fff', buffer, 0, *vertex.Read())
            file.write(buffer)

        for normal in Normals:
            buffer = bytearray(12)
            struct.pack_into('=fff', buffer, 0, *normal.Read())
            file.write(buffer)

        for face in Faces:
            buffer = bytearray(55)
            struct.pack_into('=iiBBBffffi3s13sii', buffer, 0, *face.Read())
            file.write(buffer)
            for vert in face.VertList:
                buffer = bytearray(16)
                struct.pack_into('=iiff', buffer, 0, *vert.Read())
                file.write(buffer)

    return {'FINISHED'}


def export(context, *, filepath):
    geoexport(context, filepath, bpy.context.view_layer.objects.active)
    return {'FINISHED'}
