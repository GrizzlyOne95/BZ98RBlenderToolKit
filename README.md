# Changelog
All notable changes to this project are documented in this file.

## [0.9.4] – 2025-11-07
### Blender 4.5.1 compatibility & major robustness pass

#### Added
- **Blender 4.5.1 support**
  - Updated `bl_info` to target Blender 4.5.1 and version 0.9.4 of the addon. :contentReference[oaicite:0]{index=0}
- **Full SDF export pipeline**
  - New `ExportSDF` operator with options for exporting animations and SDF-only (skip GEO writes). :contentReference[oaicite:1]{index=1}  
  - New `export_sdf.py` implementing structure GEO export, LOD packing, and ANIM block generation. :contentReference[oaicite:2]{index=2}
- **Extended GEO class IDs & UI descriptions**
  - Added a unified `geotypes` list covering CLASS_IDs 0–81, including modern roles like `VEHICLE_GEOMETRY`, `TURRET_GEOMETRY`, `WEAPON_HARDPOINT`, emitters, and PARKING_LOT. :contentReference[oaicite:3]{index=3}
- **GEO flags UI**
  - New `GEOFlags` `IntProperty` (32-bit bitfield) exposed in the GEO panel to toggle engine behaviors per-geo. :contentReference[oaicite:4]{index=4}
- **Battlezone material properties**
  - `MaterialPropertyGroup.MapTexture` string field and a “Battlezone Material Properties” panel to keep .MAP texture names on materials. :contentReference[oaicite:5]{index=5}

#### Changed
- **More robust string handling for all file classes**
  - Introduced `safe_decode_ascii` helper and wired it through GEO, VDF and SDF headers, names, and section tags to ignore stray non-ASCII bytes instead of crashing. :contentReference[oaicite:6]{index=6} :contentReference[oaicite:7]{index=7} :contentReference[oaicite:8]{index=8}
- **Import/Export panels streamlined**
  - GEO/VDF/SDF properties organized into clearer sections (VDF Settings, SDF Settings, LOD Settings, GEO Collision Settings, SDF Specific GEO Settings, etc.). :contentReference[oaicite:9]{index=9}

---

### GEO pipeline

#### Added / Changed
- **Automatic map name population on GEO export**
  - If a material’s “Battlezone Texture” name is blank, it now auto-derives a `.map` name from the Blender material name (trims to 8 chars, replaces spaces, forces lowercase) and writes it back to the custom property so the UI auto-fills next time. :contentReference[oaicite:10]{index=10}
- **UV safety & creation**
  - GEO export guarantees there is an active UV layer and writes UVs for each face loop, generating one if none exists. :contentReference[oaicite:11]{index=11}
- **StringHeader / MapName normalization**
  - GEO faces now normalize `StringHeader` and `MapName` through `safe_decode_ascii`, avoiding garbage strings from bad data. :contentReference[oaicite:12]{index=12}

#### Fixed
- **Invalid material indices on export**
  - GEO export now scans polygons for invalid `material_index` values (negative or ≥ material count) and resets them to 0, preventing crashes and malformed GEOs. :contentReference[oaicite:13]{index=13}
- **GEO import face/material mismatch**
  - GEO import now:
    - Skips duplicate/invalid faces with a `try: bm.faces.new(...)` guard.
    - Tracks a `used_faces` list so that face indices always align with `mesh.polygons`.
    - Falls back to `(0.0, 0.0)` UVs if any vertex lacks UV data. :contentReference[oaicite:14]{index=14}  
  - This fixes earlier `IndexError` issues when assigning materials after import.

---

### VDF pipeline

#### Added / Changed
- **Safer GEO + ANIM + COLP parsing**
  - VDF importer now:
    - Reads all 28 LOD bands × `geocount`, including NULLs. :contentReference[oaicite:15]{index=15}
    - Treats ANIM, EXIT and COLP as optional; if sections are missing or truncated, it falls back to a default empty collision box instead of crashing. :contentReference[oaicite:16]{index=16}  
    - COLP reading is hardened with length checks and returns default data when fewer than 56 bytes remain. :contentReference[oaicite:17]{index=17}
- **Inner/outer collision reconstruction**
  - VDF import reconstructs inner and outer collision boxes as actual Blender meshes (`inner_col`, `outer_col`) from COLP values, making collision volumes visible and editable in Blender. :contentReference[oaicite:18]{index=18}
- **Transform import now preserves baked scale**
  - On import, GEO 3×3 matrices are decomposed into scale and pure rotation: column lengths become object scale, normalized columns become the rotation, and translation is remapped to Blender axes. This is done for both root objects and children. :contentReference[oaicite:19]{index=19}
- **Quaternion animation import**
  - VDF importer reconstructs rotations from stored quaternions, converts them to Euler, and inserts keyframes for both rotation and location, setting scene frame range automatically. :contentReference[oaicite:20]{index=20}
- **Animation header layout cleanup**
  - VDF `ANIMHeader`, `ANIMElement`, and `ANIM*` blocks have been corrected and centralized, with `safe_decode_ascii` on names and consistent packing for write. :contentReference[oaicite:21]{index=21}

#### Fixed
- **Invalid material indices on VDF export**
  - VDF export now performs the same polygon material index sanity check as GEO export before writing GEOs, preventing invalid indices from propagating into exported files. :contentReference[oaicite:22]{index=22}
- **Scale not round-tripping**
  - GEO matrix writing now explicitly bakes object scale into the matrix: rotation matrix × diagonal scale matrix, instead of relying on deprecated `resize_3x3()`. This fixes cases where scaled GEOs re-imported with scale 1.0. :contentReference[oaicite:23]{index=23}
- **Quaternion vs Euler animation mismatch on export**
  - Exporter now:
    - Detects if an object is in `QUATERNION` rotation mode and prefers quaternion F-curves, converting them to Euler.
    - Falls back to Euler curves if no usable quaternions exist.
    - Stores resulting Eulers into `rotanim` and converts them back to quaternions in Battlezone’s YZX convention when writing ANIM. :contentReference[oaicite:24]{index=24}

---

### SDF pipeline

#### Added / Changed
- **SDF header & struct correctness**
  - `SDFHeader`, `SDFCHeader`, `SGEOHeader`, and SDF `GEOData` structs updated to match the real layout, including:
    - 32-bit `geoflags` field.
    - Extra DDR/X/Y/Z/Time fields for structure GEO behavior. :contentReference[oaicite:25]{index=25}
- **SDF GEO metadata wiring**
  - SDF import populates `GEOPropertyGroup` with type, flags, collision box, DDR, XYZ, and Time values so they can be edited and re-exported. :contentReference[oaicite:26]{index=26}
- **SDF transform handling**
  - Like VDF, SDF import reconstructs rotation and position from GEO matrices and applies them with the same YZX axis remap. :contentReference[oaicite:27]{index=27}
- **Quaternion-aware SDF export**
  - SDF export reads either Euler or quaternion animation curves:
    - If object is in QUATERNION mode, it collects `rotation_quaternion` F-curves and converts them to Euler before packing ANIM.
    - Else, it uses the original Euler-only behavior. :contentReference[oaicite:28]{index=28}

#### Fixed
- **SGEO / GEOData layout mismatches**
  - Corrected SDF `GEOData` packing and unpacking so that type, flags, DDR, and timing fields align with the actual file format, preventing corrupted SDF GEO blocks. :contentReference[oaicite:29]{index=29}
- **Animation header inconsistencies**
  - Reimplemented `ANIMHeader.Write` for SDF with proper counts, reserved fields, and a sane default configuration so SDF ANIM sections are valid even for minimal animations. :contentReference[oaicite:30]{index=30}

---

### UI, registration & misc

#### Fixed
- **GEOFlags registration overflow**
  - Replaced the problematic `IntProperty` definition that caused an overflow on registration with explicit 32-bit range (`min=-2147483648`, `max=2147483647`), resolving the “Python int too large to convert to C long” error when enabling the addon. :contentReference[oaicite:31]{index=31}
- **Centralized registration**
  - PropertyGroups, panels, operators, and import/export classes are now registered from lists (`Properties`, `GUIClasses`, `ImportExportClasses`), simplifying future additions and ensuring all pieces unregister cleanly. :contentReference[oaicite:32]{index=32}

---

## [Unreleased]
- Further documentation and tooltips for GEO class IDs and GEOFlags bit meanings.
- Potential Ogre mesh/skeleton export integration after VDF/SDF/GEO export.
