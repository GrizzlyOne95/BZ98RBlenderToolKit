"""
patch_ui.py  -  Apply all BZ98R UI rename changes described in the design doc.
Run once from the repo root:  python patch_ui.py
"""
import re, sys, textwrap

PATH = r"bz98tools\__init__.py"

with open(PATH, "r", encoding="utf-8") as fh:
    src = fh.read()

original = src  # keep for diff summary

# ─────────────────────────────────────────────────────────────────────────────
# 1.  Export menu labels
# ─────────────────────────────────────────────────────────────────────────────

src = src.replace(
    'layout.operator(ExportGEO.bl_idname, text="Geometry (.geo)")',
    'layout.operator(ExportGEO.bl_idname, text="Legacy Geometry (.geo)")',
)
src = src.replace(
    'layout.operator(ExportVDF.bl_idname, text="Vehicle Definition (.vdf)")',
    'layout.operator(ExportVDF.bl_idname, text="Legacy Vehicle (.vdf)")',
)
src = src.replace(
    'layout.operator(ExportSDF.bl_idname, text="Structure Definition (.sdf)")',
    'layout.operator(ExportSDF.bl_idname, text="Legacy Structure (.sdf)")',
)
src = src.replace(
    'layout.operator(BZ98TOOLS_OT_export_bzr_mesh.bl_idname, text="Redux Mesh (.mesh)")',
    'layout.operator(BZ98TOOLS_OT_export_bzr_mesh.bl_idname, text="Redux Mesh Only (.mesh)")',
)

# ─────────────────────────────────────────────────────────────────────────────
# 2.  ExportGEO – rename auto_port_ogre property label + description
# ─────────────────────────────────────────────────────────────────────────────

src = src.replace(
    '''    # Ogre auto-port toggle
    auto_port_ogre: BoolProperty(
        name="Create Redux Files",
        description=(
            "After writing the GEO, run the Battlezone model porter to create "
            "OGRE .mesh/.skeleton/.material/.dds in the same directory"
        ),
        default=False,
    )''',
    '''    # Ogre auto-port toggle
    auto_port_ogre: BoolProperty(
        name="Also Create Redux Files",
        description=(
            "After exporting the legacy GEO, also generate Redux "
            ".mesh / .skeleton / .material / .dds files"
        ),
        default=False,
    )''',
)

# ─────────────────────────────────────────────────────────────────────────────
# 3.  ExportVDF – rename auto_port_ogre + ExportVDFOnly labels
# ─────────────────────────────────────────────────────────────────────────────

# 3a. auto_port_ogre on VDF
src = src.replace(
    '''    # NEW: Ogre auto-port checkbox
    auto_port_ogre: BoolProperty(
        name="Create BZR Files",
        description=(
            "After writing the VDF, run the Battlezone model porter to create "
            "OGRE .mesh/.skeleton/.material/.dds in the same directory"
        ),
        default=False,
    )''',
    '''    # NEW: Ogre auto-port checkbox
    auto_port_ogre: BoolProperty(
        name="Also Create Redux Files",
        description=(
            "After exporting legacy files, also generate Redux "
            ".mesh / .skeleton / .material / .dds files"
        ),
        default=False,
    )''',
)

# 3b. ExportVDFOnly on VDF
src = src.replace(
    '''    ExportVDFOnly: BoolProperty(
        name="Export Only VDF (Don't Export GEOs)",
        description="Export only the VDF file to preserve old GEO files",
        default=False,
    )''',
    '''    ExportVDFOnly: BoolProperty(
        name="Skip GEO File Export",
        description=(
            "Only write the VDF container and keep existing referenced GEO files; "
            "does not create or overwrite any .geo files"
        ),
        default=False,
    )''',
)

# ─────────────────────────────────────────────────────────────────────────────
# 4.  ExportSDF – rename auto_port_ogre + ExportSDFOnly labels
# ─────────────────────────────────────────────────────────────────────────────

# 4a. auto_port_ogre on SDF
src = src.replace(
    '''    # NEW: Ogre auto-port toggle
    auto_port_ogre: BoolProperty(
        name="Create BZR Files",
        description=(
            "After writing the SDF, run the Battlezone model porter to create "
            "OGRE .mesh/.skeleton/.material/.dds in the same directory"
        ),
        default=False,
    )''',
    '''    # NEW: Ogre auto-port toggle
    auto_port_ogre: BoolProperty(
        name="Also Create Redux Files",
        description=(
            "After exporting legacy files, also generate Redux "
            ".mesh / .skeleton / .material / .dds files"
        ),
        default=False,
    )''',
)

# 4b. ExportSDFOnly on SDF
src = src.replace(
    '''    ExportSDFOnly: BoolProperty(
        name="Export SDF Only",
        description="Skip exporting referenced GEO files; export only the SDF container",
        default=False,
    )''',
    '''    ExportSDFOnly: BoolProperty(
        name="Skip GEO File Export",
        description=(
            "Only write the SDF container and keep existing referenced GEO files; "
            "does not create or overwrite any .geo files"
        ),
        default=False,
    )''',
)

# ─────────────────────────────────────────────────────────────────────────────
# 5.  ExportGEO.draw()  –  add Output Mode summary and rename section header
# ─────────────────────────────────────────────────────────────────────────────

OLD_GEO_DRAW_PORT = '''\
        port = layout.box()
        port.label(text="Create Redux Files")
        port.prop(self, "auto_port_ogre")
        if self.auto_port_ogre:
            _draw_shared_autoport_options(port, self)'''

NEW_GEO_DRAW_PORT = '''\
        # Output Mode summary
        mode_box = layout.box()
        if self.auto_port_ogre:
            mode_box.label(text="Output Mode: Legacy + Redux", icon='INFO')
            mode_box.label(text="Writes .geo, then generates .mesh / .skeleton / .material / .dds")
        else:
            mode_box.label(text="Output Mode: Legacy only", icon='INFO')
            mode_box.label(text="Writes .geo file only.  Enable \\"Also Create Redux Files\\" below to also port.")

        port = layout.box()
        port.label(text="Redux Output")
        port.prop(self, "auto_port_ogre")
        if self.auto_port_ogre:
            _draw_shared_autoport_options(port, self)'''

src = src.replace(OLD_GEO_DRAW_PORT, NEW_GEO_DRAW_PORT)

# ─────────────────────────────────────────────────────────────────────────────
# 6.  ExportVDF.draw()  –  add Output Mode summary and fix section labels
# ─────────────────────────────────────────────────────────────────────────────

OLD_VDF_LEGACY = '''\
        legacy = layout.box()
        legacy.label(text="Legacy Output")
        legacy.prop(self, "ExportVDFOnly")
        if not self.ExportVDFOnly:
            legacy.label(text="Referenced GEO files in the export folder may be overwritten.", icon='ERROR')

        _draw_validation_summary_box(layout, scene, export_mode="VDF")

        port = layout.box()
        port.label(text="Create BZR Files")
        port.prop(self, "auto_port_ogre")
        if self.auto_port_ogre:
            _draw_shared_autoport_options(port, self)
            _draw_vdf_autoport_options(port, self)'''

NEW_VDF_LEGACY = '''\
        legacy = layout.box()
        legacy.label(text="Legacy Output")
        legacy.prop(self, "ExportVDFOnly")
        if not self.ExportVDFOnly:
            legacy.label(text="Referenced GEO files in the export folder may be overwritten.", icon='ERROR')

        _draw_validation_summary_box(layout, scene, export_mode="VDF")

        # Output Mode summary
        mode_box = layout.box()
        if self.auto_port_ogre:
            mode_box.label(text="Output Mode: Legacy + Redux", icon='INFO')
            mode_box.label(text="Writes .vdf + .geo files, then generates .mesh / .skeleton / .material / .dds")
        else:
            mode_box.label(text="Output Mode: Legacy only", icon='INFO')
            mode_box.label(text="Writes .vdf + .geo files only.  Enable \\"Also Create Redux Files\\" below to also port.")

        port = layout.box()
        port.label(text="Redux Output")
        port.prop(self, "auto_port_ogre")
        if self.auto_port_ogre:
            _draw_shared_autoport_options(port, self)
            _draw_vdf_autoport_options(port, self)'''

src = src.replace(OLD_VDF_LEGACY, NEW_VDF_LEGACY)

# ─────────────────────────────────────────────────────────────────────────────
# 7.  ExportSDF.draw()  –  add Output Mode summary and fix section labels
# ─────────────────────────────────────────────────────────────────────────────

OLD_SDF_LEGACY = '''\
        legacy = layout.box()
        legacy.label(text="Legacy Output")
        legacy.prop(self, "ExportSDFOnly")
        if not self.ExportSDFOnly:
            legacy.label(text="Referenced GEO files in the export folder may be overwritten.", icon='ERROR')

        _draw_validation_summary_box(layout, scene, export_mode="SDF")

        port = layout.box()
        port.label(text="Create BZR Files")
        port.prop(self, "auto_port_ogre")
        if self.auto_port_ogre:
            _draw_shared_autoport_options(port, self)'''

NEW_SDF_LEGACY = '''\
        legacy = layout.box()
        legacy.label(text="Legacy Output")
        legacy.prop(self, "ExportSDFOnly")
        if not self.ExportSDFOnly:
            legacy.label(text="Referenced GEO files in the export folder may be overwritten.", icon='ERROR')

        _draw_validation_summary_box(layout, scene, export_mode="SDF")

        # Output Mode summary
        mode_box = layout.box()
        if self.auto_port_ogre:
            mode_box.label(text="Output Mode: Legacy + Redux", icon='INFO')
            mode_box.label(text="Writes .sdf + .geo files, then generates .mesh / .skeleton / .material / .dds")
        else:
            mode_box.label(text="Output Mode: Legacy only", icon='INFO')
            mode_box.label(text="Writes .sdf + .geo files only.  Enable \\"Also Create Redux Files\\" below to also port.")

        port = layout.box()
        port.label(text="Redux Output")
        port.prop(self, "auto_port_ogre")
        if self.auto_port_ogre:
            _draw_shared_autoport_options(port, self)'''

src = src.replace(OLD_SDF_LEGACY, NEW_SDF_LEGACY)

# ─────────────────────────────────────────────────────────────────────────────
# 8.  BZ98TOOLS_OT_export_bzr_mesh.draw()  –  add "Redux only" mode badge
# ─────────────────────────────────────────────────────────────────────────────

OLD_BZR_DRAW = '''\
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "xml_converter")
        layout.prop(self, "keep_xml")
        layout.separator()
        col = layout.column()
        col.label(text="Geometry:")'''

NEW_BZR_DRAW = '''\
    def draw(self, context):
        layout = self.layout

        # Output Mode summary
        mode_box = layout.box()
        mode_box.label(text="Output Mode: Redux only", icon='INFO')
        mode_box.label(text="Writes .mesh / .skeleton / .material directly.  No .geo / .vdf / .sdf files are created.")

        layout.prop(self, "xml_converter")
        layout.prop(self, "keep_xml")
        layout.separator()
        col = layout.column()
        col.label(text="Geometry:")'''

src = src.replace(OLD_BZR_DRAW, NEW_BZR_DRAW)

# ─────────────────────────────────────────────────────────────────────────────
# Write back only if something changed
# ─────────────────────────────────────────────────────────────────────────────

if src == original:
    print("WARNING: no substitutions were made – check that old strings still match.")
    sys.exit(1)

# Count changes
changes = 0
for old, new in [
    ('text="Geometry (.geo)"',       'text="Legacy Geometry (.geo)"'),
    ('text="Vehicle Definition',      'text="Legacy Vehicle'),
    ('text="Structure Definition',    'text="Legacy Structure'),
    ('text="Redux Mesh (.mesh)"',     'text="Redux Mesh Only (.mesh)"'),
    ('name="Also Create Redux Files"', 'name="Also Create Redux Files"'),
    ('name="Skip GEO File Export"',   'name="Skip GEO File Export"'),
    ('Output Mode: Legacy only',      'Output Mode: Legacy only'),
    ('Output Mode: Legacy + Redux',   'Output Mode: Legacy + Redux'),
    ('Output Mode: Redux only',       'Output Mode: Redux only'),
]:
    count = src.count(new)
    if count:
        changes += count
        print(f"  OK [{count}x] {new[:60]}")
    else:
        print(f"  MISSING: {new[:60]}")

with open(PATH, "w", encoding="utf-8") as fh:
    fh.write(src)

print(f"\nDone.  {changes} pattern occurrences verified in patched file.")
