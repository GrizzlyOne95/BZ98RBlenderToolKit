# Battlezone Blender Toolkit  
### Full Import/Export Suite for Battlezone 1998 Redux / The Red Odyssey  

---

## Overview
The **Battlezone Blender Toolkit** is a modern, unified Blender add-on for working with classic Battlezone model formats (`.VDF`, `.SDF`, `.GEO`, `.MAP`), Battlezone Redux model formats (`.MESH`, `.SKELETON`, `.MATERIAL`), and Battlezone map terrain workflows (`.HG2`).
It combines multiple tools into one streamlined workflow — no external scripts or converters required.

This plugin targets the **Blender 4.5 LTS** and **Blender 5.1** lines, with **quaternion animation**, **auto Ogre export**, integrated map tooling, and major stability fixes for the Red Odyssey VDFs.

---

## Installation
-- Download the newest .zip from Releases
-- In Blender, go to Edit > Preferences > Addons > Install From Disk
-- Ensure addon is enabled

## Quick Feature Summary

- ✅ **Import models directly from ZFS archives** (Auto-extracts dependencies)
- ✅ Full **Blender 4.5 LTS** and **Blender 5.1** compatibility
- ✅ **Auto Ogre Mesh/Skeleton/Material export** (Redux-ready)  
- ✅ **Optional native Ogre mesh/skeleton fast path** on Windows Blender 4.5.x; Blender 5.1 falls back to XML conversion until a Python 3.13 native backend is available
- ✅ **Integrated BZMapIO map tools** for `.HG2` terrain import/export, texture tools, and game playback data
- ✅ **Quaternion animation** import/export  
- ✅ **Automatic `.MAP` → `.PNG` conversion** for textures on import
- ✅ **Automatic `.PNG` or `.MAP` → `.DDS` conversion** for textures on export
- ✅ **Clear export modes** for Legacy Only, Legacy + Redux, and Redux Only workflows
- ✅ **Hardpoint/turret GEO suffix validation** for common `gc`, `gr`, `gm`, `gs`, `tx`, and `ty` naming conventions
- ✅ **Safe material name auto-generation**  
- ✅ **Auto UV unwrap** when missing  
- ✅ **Accurate GEO scaling and GEOFlags**  
- ✅ **TRO/Red Odyssey VDF support**  
- ✅ **COLP collision import safety checks**  
- ✅ **No external dependencies required**
- ✅ **Automatic VDF COL box generation**
- ✅ **Includes all known documented GEO types and Animation Indexes as Info Boxes**
- ✅ **Experimental binary controls for advanced VDF/SDF/GEO fields** (see `docs/EXPERIMENTAL_BINARY_FIELDS.md`)

---

## Workflow Comparison

### Previously
Before this toolkit, modders relied on several separate tools:

- **Kenshi Ogre Add-on** – handled Redux `.mesh` I/O  
- **Ogre CLI Tools** – required upgrading exported meshes  
- **DivisionByZero’s Python script** – converted `.VDF`/`.SDF`/`.GEO` files  
- **Commando950’s VDF/SDF Add-on** – Blender editor for legacy formats  
- **Manual normal-fix scripts** – for correcting mesh lighting

- **OR paid software such as UU3D because there aren't any official free tools that support BZR meshes**

This process required multiple exports, conversions, CLI tools, next to zero documentation and no centralized source for all of the tools.

### Now
Everything is handled inside Blender:

- **Import models directly from `.ZFS` archives** (Explorer in Scene tab)
- Open the bundled BZMapIO template and import/export `.HG2` terrain from the Battlezone panel
- Import or export `.GEO`, `.VDF`, and `.SDF` directly  
- Auto-convert `.MAP` textures to `.PNG`  
- Export or Import Redux `.mesh`, `.skeleton`, and `.material` automatically, complete with animations
- Correct scaling, collisions, and flags preserved  
- No CLI tools or Python installs needed  

---

## Changelog
**Blender 5.1 Compatibility, Map Tooling, Export UX, and Validation Updates**

#### Added
- **Integrated BZMapIO**
  - Added Battlezone map panels in the 3D View sidebar.
  - Bundled the BZMapIO `.blend` template for one-click setup.
  - Added `.HG2` terrain import/export, map texture tools, and game playback log tooling.
- **Blender 5.1 support**
  - Verified registration, model import/export, Redux mesh export, ZFS browsing, and HG2 map import under Blender 5.1.2.
  - Added compatibility for Blender 5.1 layered Action f-curves in VDF/SDF animation export.
  - Added compatibility wrappers for map operators changed or removed in modern Blender.
- **Export workflow clarity**
  - Legacy exporters are labeled as **Legacy Geometry (.geo)**, **Legacy Vehicle (.vdf)**, and **Legacy Structure (.sdf)**.
  - Redux direct export is labeled as **Redux Mesh Only (.mesh)**.
  - Legacy exporters now describe whether the output mode is **Legacy only** or **Legacy + Redux**.
  - The Redux checkbox is labeled **Also Create Redux Files** to make it clear that Redux files are generated after the legacy export.
- **Modder validation**
  - Added validation warnings for documented hardpoint and turret suffix conventions such as `gc1`, `gr1`, `gm1`, `gs1`, `tx1`, and `ty1`.

#### Changed
- Shortened Redux option labels so Blender dialogs do not truncate important setting names.
- Moved command-line flag names into tooltips where they are still available without crowding the UI.
- Filtered the GEO Type Reference down to confirmed/handled type entries.
- Tracked bundled `.blend` assets through Git LFS to keep the repository lightweight.

#### Notes
- Blender 5.1 uses Python 3.13. The bundled native Ogre backend currently includes a Python 3.11 Windows module, so Blender 5.1 uses the legacy XML converter fallback. Export still works; native Blender 5.1 Ogre support requires a future `cp313-win_amd64` native backend build.

---

**Import from ZFS, Blender 4.5 LTS Compatibility, Ogre Auto-Port Integration, and Major Pipeline Updates**

#### Added
- **Import from ZFS**
  - New **ZFS Explorer** panel in the Scene properties tab.
  - Browse `.ZFS` archives and import models directly.
  - **Recursive Dependency Extraction**: Automatically finds and extracts all required `.GEO` and texture files from the archive upon import.
  - Bundled Lzo decompression library for full Redux archive support.
- **Blender 4.5 LTS support**
  - Updated `bl_info`, registration, and UI functions for new API.
- **Automatic Ogre export integration**
  - Option to automatically run the Ogre exporter after saving a `.VDF`, `.SDF`, or `.GEO`.
  - Outputs `.mesh`, `.skeleton`, and `.material` directly.
- **Optional native Ogre backend**
  - Added a bundled `kenshi_blender_tool` fast path for `.mesh` import/export on Windows Blender 4.5.x.
  - Falls back to the legacy Ogre XML converter path automatically when the native runtime is unavailable.
- **Unified serializer framework**
  - Standardized binary read/write across `baseserializer.py`, `bz_baseserializer.py`, and `ogre_baseserializer.py`.
  - Added `AbruptEOFError` for safer handling of truncated files.
- **Expanded GEO class IDs**
  - Full set of 82 types (0-81) with descriptive labels shown in the UI.
- **ObjectFlags / GEO flags**
  - 32-bit VDF/SDF `ObjectFlags` field implemented across all formats; editable in Blender properties.
- **Material and texture handling**
  - Generates a safe `.map` name if blank.
  - Converts `.map` to `.png` automatically and links it in materials.
- **Automatic UV layer creation**
  - GEO export ensures at least one UV set exists.
- **Automatic VDF COL box generation under Scene Settings**

#### Changed
- **Quaternion animation support**
  - Automatically detects and converts quaternion F-curves to Euler, and back to quaternions on export.
- **Scale handling**
  - GEO export multiplies rotation × scale to preserve proper transforms.
- **Encoding safety**
  - All string reads use `safe_decode_ascii()` to prevent crashes.
- **SDF GEO structures**
  - Corrected `GEOData`, `SGEO`, and `ANIMHeader` packing.

#### Fixed
- **TRO/Red Odyssey imports**
  - Handles non-ASCII bytes safely without crashing.
- **Invalid material indices**
  - Invalid or missing material slots reset to index 0 on export.
- **GEO scaling**
  - Fixed round-trip scale loss on re-imported objects.
- **Parent/child hierarchy**
  - Preserved during import of nested GEOs and LODs.
- **Overflow on ObjectFlags**
  - Explicit 32-bit min/max range prevents Blender registration errors.

#### User Interface
- Fixed property registration and UI refresh issues  

#### Internal
- Integrated `bzportmodels.py` and `ogre_autoport.py` for automatic Ogre conversion  
- Added future-ready `.map` → `.dds` conversion stub  
- Hardened `import_vdf.py`/`export_vdf.py` for incomplete ANIM/COLP blocks  

---

## Summary of Improvements Since 0.9.3 (Commando950's original Blender plugin)

| Category | Update |
|-----------|---------|
| **ZFS** | **Directly browse and import from .ZFS archives** |
| Compatibility | Full Blender 4.5 LTS and Blender 5.1 compliance |
| File I/O | Safe ASCII decoding, EOF handling |
| Maps | Integrated BZMapIO `.HG2` terrain, texture, and playback tools |
| Materials | `.MAP → .PNG` conversion and name auto-fill |
| Geometry | Scale, collision, and UV safety |
| Animation | Quaternion/Euler auto-conversion |
| VDF | Robust ANIM/COLP parsing, visible collision boxes |
| SDF | Correct ObjectFlags/DDR/Target/Time fields, fixed struct layouts |
| Export | Explicit Legacy Only, Legacy + Redux, and Redux Only workflows |
| UI | Organized panels, confirmed GEO type reference, clearer Redux labels |
| Stability | Major crash and data-corruption fixes |

---

## Credits

| Contributor | Role |
|--------------|------|
| **DivisionByZero** | Original Python Ogre mesh port script |
| **Commando950** | Original SDF/VDF/GEO Blender plugin |
| **Kindrad** | Ogre import/export base code (Kenshi add-on) |
| **Business Lawyer** | Original Battlezone Map IO tool |
| **GrizzlyOne95** | Blender 4.5 LTS update, Ogre integration, quaternion/scaling/UI modernization, multiple bug fixes |

---

## Repository

Source code and issue tracking:  
[https://github.com/GrizzlyOne95/bz98tools](https://github.com/GrizzlyOne95/bz98tools)

Advanced binary field notes:  
[`docs/EXPERIMENTAL_BINARY_FIELDS.md`](docs/EXPERIMENTAL_BINARY_FIELDS.md)

## License

This project is licensed under the **GNU General Public License v3.0** (GPL-3.0).

Portions of the importer/exporter system are derived from  
[Kenshi_IO_Continued](https://codeberg.org/Kindrad/Kenshi_IO_Continued),  
which is also licensed under GPL-3.0. All such portions retain their original
copyright notices.

See the [LICENSE](LICENSE) file for full terms.

Other portions of code were derived from sources by Commando950's plugin here: https://commando950.neocities.org/downloads/
And DivisionByZeoro's porting code, never put on any site or repo.

### Third-Party Components

**OGRE (Object-Oriented Graphics Rendering Engine)**  
© 2000–2023 Torus Knot Software Ltd and other contributors  
Licensed under the MIT License. See `OGRE_LICENSE.txt`.  
Used for conversion utilities such as `OgreXMLConverter.exe`.


