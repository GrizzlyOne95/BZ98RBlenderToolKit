# Changelog
All notable changes to this project are documented in this file.

# Quick Updates Recap
- Blender 4.5.1 Support
- GeoFlags are read and written properly
- The Red Odyssey VDF's import without crashing
- If Battlezone Material Name is blank, it auto generates a safe file name on export based on Blender material name
- Any matching detected .MAP files are decoded into .PNG and loaded into Blender as a material node for previewing
- Invalid material indices are automatically fixed on export
- Exporter no longer ignogres Quaternion animation keyframes and auto converts
- GEO Scaling is no longer ignored and will be written/ignored as they can change behavior in game
- Option on exports to auto port the result to Ogre mesh/skeleton/material (Redux format)
- Import/Export Redux format meshes/skeletons


## [0.9.4] – 2025-11-07
### Blender 4.5.1 compatibility & major robustness pass

#### Added
- **Blender 4.5.1 support**
  - Updated `bl_info` to target Blender 4.5.1 and version 0.9.4 of the addon.
- **Extended GEO class IDs & UI descriptions**
  - Added a unified `geotypes` list covering CLASS_IDs 0–81
- **GEO flags UI**
  - New `GEOFlags` `IntProperty` (32-bit bitfield) exposed in the GEO panel to toggle engine behaviors per-geo. This data is written and read correctly now.

#### Changed
- **More robust string handling for all file classes**
  - Introduced `safe_decode_ascii` helper and wired it through GEO, VDF and SDF headers, names, and section tags to ignore stray non-ASCII bytes instead of crashing. This fixes the issue with importing TRO VDF's. 
- **Import/Export panels streamlined**
  - GEO/VDF/SDF properties organized into clearer sections (VDF Settings, SDF Settings, LOD Settings, GEO Collision Settings, SDF Specific GEO Settings, etc.)

---

### GEO pipeline

#### Added / Changed
- **Automatic map name population on GEO export**
  - If a material’s “Battlezone Texture” name is blank, it now auto-derives a `.map` name from the Blender material name (trims to 8 chars, replaces spaces, forces lowercase) and writes it back to the custom property so the UI auto-fills next time.
- **UV safety & creation**
  - GEO export guarantees there is an active UV layer and writes UVs for each face loop, generating one if none exists.
- **StringHeader / MapName normalization**
  - GEO faces now normalize `StringHeader` and `MapName` through `safe_decode_ascii`, avoiding garbage strings from bad data.
- **Automatic .MAP texture conversion**
  - .map textures found (referenced by the GEOs) are converted to .PNG in the same directory and loaded into Blender materials for preview.

#### Fixed
- **Invalid material indices on export**
  - GEO export now scans polygons for invalid `material_index` values (negative or ≥ material count) and resets them to 0, preventing crashes and malformed GEOs.
- **GEO import face/material mismatch**
  - GEO import now:
    - Skips duplicate/invalid faces with a `try: bm.faces.new(...)` guard.
    - Tracks a `used_faces` list so that face indices always align with `mesh.polygons`.
    - Falls back to `(0.0, 0.0)` UVs if any vertex lacks UV data.
  - This fixes earlier `IndexError` issues when assigning materials after import.

---

### VDF pipeline

#### Added / Changed
- **Safer GEO + ANIM + COLP parsing**
  - VDF importer now:
    - Reads all 28 LOD bands × `geocount`, including NULLs.
    - Treats ANIM, EXIT and COLP as optional; if sections are missing or truncated, it falls back to a default empty collision box instead of crashing.
    - COLP reading is hardened with length checks and returns default data when fewer than 56 bytes remain.
- **Inner/outer collision reconstruction**
  - VDF import reconstructs inner and outer collision boxes as actual Blender meshes (`inner_col`, `outer_col`) from COLP values, making collision volumes visible and editable in Blender.
- **Transform import now preserves baked scale**
  - On import, GEO 3×3 matrices are decomposed into scale and pure rotation: column lengths become object scale, normalized columns become the rotation, and translation is remapped to Blender axes. This is done for both root objects and children. 
- **Quaternion animation import**
  - VDF importer reconstructs rotations from stored quaternions, converts them to Euler, and inserts keyframes for both rotation and location, setting scene frame range automatically.
- **Animation header layout cleanup**
  - VDF `ANIMHeader`, `ANIMElement`, and `ANIM*` blocks have been corrected and centralized, with `safe_decode_ascii` on names and consistent packing for write.

#### Fixed
- **Invalid material indices on VDF export**
  - VDF export now performs the same polygon material index sanity check as GEO export before writing GEOs, preventing invalid indices from propagating into exported files.
- **Scale not round-tripping**
  - GEO matrix writing now explicitly bakes object scale into the matrix: rotation matrix × diagonal scale matrix, instead of relying on deprecated `resize_3x3()`. This fixes cases where scaled GEOs re-imported with scale 1.0 and didn't export properly with scales.
- **Quaternion vs Euler animation mismatch on export**
  - Exporter now:
    - Detects if an object is in `QUATERNION` rotation mode and prefers quaternion F-curves, converting them to Euler.
    - Falls back to Euler curves if no usable quaternions exist.
    - Stores resulting Eulers into `rotanim` and converts them back to quaternions in Battlezone’s YZX convention when writing ANIM.

---

### SDF pipeline

#### Added / Changed
- **SDF header & struct correctness**
  - `SDFHeader`, `SDFCHeader`, `SGEOHeader`, and SDF `GEOData` structs updated to match the real layout, including:
    - 32-bit `geoflags` field.
    - Extra DDR/X/Y/Z/Time fields for structure GEO behavior.
- **SDF GEO metadata wiring**
  - SDF import populates `GEOPropertyGroup` with type, flags, collision box, DDR, XYZ, and Time values so they can be edited and re-exported.
- **SDF transform handling**
  - Like VDF, SDF import reconstructs rotation and position from GEO matrices and applies them with the same YZX axis remap.
- **Quaternion-aware SDF export**
  - SDF export reads either Euler or quaternion animation curves:
    - If object is in QUATERNION mode, it collects `rotation_quaternion` F-curves and converts them to Euler before packing ANIM.
    - Else, it uses the original Euler-only behavior.

#### Fixed
- **SGEO / GEOData layout mismatches**
  - Corrected SDF `GEOData` packing and unpacking so that type, flags, DDR, and timing fields align with the actual file format, preventing corrupted SDF GEO blocks.
- **Animation header inconsistencies**
  - Reimplemented `ANIMHeader.Write` for SDF with proper counts, reserved fields, and a sane default configuration so SDF ANIM sections are valid even for minimal animations.

---

### UI, registration & misc

#### Fixed
- **GEOFlags registration overflow**
  - Replaced the problematic `IntProperty` definition that caused an overflow on registration with explicit 32-bit range (`min=-2147483648`, `max=2147483647`), resolving the “Python int too large to convert to C long” error when enabling the addon. 
- **Centralized registration**
  - PropertyGroups, panels, operators, and import/export classes are now registered from lists (`Properties`, `GUIClasses`, `ImportExportClasses`), simplifying future additions and ensuring all pieces unregister cleanly.

### CREDITS
- DivisionByZero for bzmap.py, bzmap_serializer.py, and bzact_serializer.py
- Commando950 for original SDF/VDF/Geo Blender Editor Plugin
- Kindrad for Ogre Import/Export code
