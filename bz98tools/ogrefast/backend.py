from . import probe_native_backend


def _fallback(operator, reason, legacy_handler, *args, **kwargs):
    if reason:
        print(f"Native Ogre backend unavailable, falling back to legacy XML path: {reason}")
    return legacy_handler(*args, **kwargs)


def _map_tangent_format(export_tangents, export_binormals, zero_tangents_binormals, tangent_parity):
    if zero_tangents_binormals:
        return "ZERO"
    if not export_tangents:
        return "TANGENT_0"
    if export_binormals:
        return "ALL" if tangent_parity else "TANGENT_3"
    return "TANGENT_4"


def import_mesh(
        operator,
        context,
        filepath,
        legacy_handler,
        xml_converter=None,
        keep_xml=False,
        import_normals=True,
        normal_mode="custom",
        import_shapekeys=True,
        import_animations=False,
        round_frames=True,
        use_selected_skeleton=False,
        import_materials=True):
    available, reason = probe_native_backend()
    if not available:
        return _fallback(
            operator,
            reason,
            legacy_handler,
            operator,
            context,
            filepath,
            xml_converter=xml_converter,
            keep_xml=keep_xml,
            import_normals=import_normals,
            normal_mode=normal_mode,
            import_shapekeys=import_shapekeys,
            import_animations=import_animations,
            round_frames=round_frames,
            use_selected_skeleton=use_selected_skeleton,
            import_materials=import_materials,
        )

    from . import ogre_importer

    try:
        print("Using native Ogre backend for mesh import.")
        return ogre_importer.load(
            operator,
            context,
            filepath,
            import_normals=import_normals,
            import_shapekeys=import_shapekeys,
            import_animations=import_animations,
            round_frames=round_frames,
            use_selected_skeleton=use_selected_skeleton,
            create_materials=import_materials,
        )
    except Exception as exc:
        return _fallback(
            operator,
            f"native import failed: {exc}",
            legacy_handler,
            operator,
            context,
            filepath,
            xml_converter=xml_converter,
            keep_xml=keep_xml,
            import_normals=import_normals,
            normal_mode=normal_mode,
            import_shapekeys=import_shapekeys,
            import_animations=import_animations,
            round_frames=round_frames,
            use_selected_skeleton=use_selected_skeleton,
            import_materials=import_materials,
        )


def export_mesh(
        operator,
        context,
        filepath,
        legacy_handler,
        xml_converter=None,
        keep_xml=False,
        export_tangents=True,
        export_binormals=True,
        zero_tangents_binormals=False,
        export_colour=True,
        tangent_parity=True,
        apply_transform=True,
        apply_modifiers=True,
        export_materials=True,
        overwrite_material=False,
        copy_textures=False,
        export_skeleton=True,
        export_poses=True,
        export_animation=False,
        renormalize_weights=True,
        batch_export=False):
    if batch_export:
        return _fallback(
            operator,
            "native batch mesh export is not wired yet",
            legacy_handler,
            operator,
            context,
            filepath,
            xml_converter=xml_converter,
            keep_xml=keep_xml,
            export_tangents=export_tangents,
            export_binormals=export_binormals,
            zero_tangents_binormals=zero_tangents_binormals,
            export_colour=export_colour,
            tangent_parity=tangent_parity,
            apply_transform=apply_transform,
            apply_modifiers=apply_modifiers,
            export_materials=export_materials,
            overwrite_material=overwrite_material,
            copy_textures=copy_textures,
            export_skeleton=export_skeleton,
            export_poses=export_poses,
            export_animation=export_animation,
            renormalize_weights=renormalize_weights,
            batch_export=batch_export,
        )

    available, reason = probe_native_backend()
    if not available:
        return _fallback(
            operator,
            reason,
            legacy_handler,
            operator,
            context,
            filepath,
            xml_converter=xml_converter,
            keep_xml=keep_xml,
            export_tangents=export_tangents,
            export_binormals=export_binormals,
            zero_tangents_binormals=zero_tangents_binormals,
            export_colour=export_colour,
            tangent_parity=tangent_parity,
            apply_transform=apply_transform,
            apply_modifiers=apply_modifiers,
            export_materials=export_materials,
            overwrite_material=overwrite_material,
            copy_textures=copy_textures,
            export_skeleton=export_skeleton,
            export_poses=export_poses,
            export_animation=export_animation,
            renormalize_weights=renormalize_weights,
            batch_export=batch_export,
        )

    selected_objects = [
        obj for obj in context.view_layer.objects
        if obj.select_get() and obj.type != 'ARMATURE'
    ]

    from . import ogre_exporter

    try:
        print("Using native Ogre backend for mesh export.")
        result = ogre_exporter.save(
            operator,
            context,
            filepath,
            tangent_format=_map_tangent_format(
                export_tangents,
                export_binormals,
                zero_tangents_binormals,
                tangent_parity,
            ),
            export_colour=export_colour,
            apply_transform=apply_transform,
            apply_modifiers=apply_modifiers,
            export_skeleton=export_skeleton,
            export_poses=export_poses,
            export_animation=export_animation,
            export_all_bones=False,
            mesh_optimize=True,
            export_version='V_1_10',
            is_visual_keying=False,
            use_scale_keyframe=False,
            num_fake_pose=0,
            renormalize_weights=renormalize_weights,
        )

        if result == {'FINISHED'} and export_materials:
            from ..ogretools import OgreExport as legacy_export

            material_data = {}
            legacy_export.bCollectMaterialData(material_data, selected_objects)
            legacy_export.xSaveMaterialData(
                filepath if filepath.lower().endswith(".mesh") else filepath + ".mesh",
                material_data,
                overwrite_material,
                copy_textures,
            )

        return result
    except Exception as exc:
        return _fallback(
            operator,
            f"native export failed: {exc}",
            legacy_handler,
            operator,
            context,
            filepath,
            xml_converter=xml_converter,
            keep_xml=keep_xml,
            export_tangents=export_tangents,
            export_binormals=export_binormals,
            zero_tangents_binormals=zero_tangents_binormals,
            export_colour=export_colour,
            tangent_parity=tangent_parity,
            apply_transform=apply_transform,
            apply_modifiers=apply_modifiers,
            export_materials=export_materials,
            overwrite_material=overwrite_material,
            copy_textures=copy_textures,
            export_skeleton=export_skeleton,
            export_poses=export_poses,
            export_animation=export_animation,
            renormalize_weights=renormalize_weights,
            batch_export=batch_export,
        )
