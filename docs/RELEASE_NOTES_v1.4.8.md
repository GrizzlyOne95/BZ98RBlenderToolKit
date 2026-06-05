# BZ98R Blender Toolkit v1.4.8

## Summary

This release adds import-time texture source options so stock or stock-derived GEO/VDF/SDF imports can resolve referenced `.map` textures from an extra folder or a stock ZFS archive.

## Added

- Added `.MAP Texture Folder` to GEO, VDF, and SDF import options.
- Added `.MAP Texture ZFS` to GEO, VDF, and SDF import options.
- Missing `.map` textures can now be extracted from a selected ZFS archive into the addon cache during import.
- Added wiki documentation for importing models with stock `.map` texture sources.

## Changed

- Texture lookup now checks the imported model folder first, then the optional texture folder, then the optional ZFS archive.
- Import texture source fields are plain pasteable paths to avoid Blender's nested file-selector limitation inside the import dialog.

## Fixed

- ZFS extraction now creates needed output subfolders when archive entries include paths.
- `zfs_reader.py` now imports `struct` explicitly.

## Verified

- Python compile checks passed for `bz98tools/__init__.py`, `bz98tools/import_geo.py`, `bz98tools/import_vdf.py`, `bz98tools/import_sdf.py`, and `bz98tools/zfs_reader.py`.
- Git diff whitespace checks passed for touched addon modules.
- The Blender 4.5 AppData addon folder was synced during local testing.

## Installation

1. Download `bz98tools.zip` from this release.
2. In Blender, go to **Edit > Preferences > Add-ons**.
3. Click **Install...** and select the downloaded `.zip` file.
4. Ensure **Battlezone GEO/VDF/SDF Formats** is enabled.
