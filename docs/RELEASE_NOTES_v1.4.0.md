# BZ98R Blender Toolkit v1.4.0

## Summary

This release focuses on UI and workflow improvements for legacy Battlezone export, Redux auto-port setup, and ZFS archive browsing.

## Added

- Legacy export validation panel with grouped results, counts, and export blocking for hard errors.
- Actionable validation results:
  - select the referenced object directly
  - one-click legacy name repair for invalid export names
  - stale-result warning when the scene changes after validation
- Legacy export dialog layouts for `.geo`, `.vdf`, and `.sdf`.
- Named `GEOType` selector with role hints instead of raw integer-only editing.
- Material helpers:
  - export preview for resolved legacy texture names
  - derive texture names from the Blender material name
  - derive texture names from linked image textures
- Animation editor workflow tools:
  - duplicate selected element
  - move selected element up/down
  - preset slot groups for common starting layouts
- ZFS browser improvements:
  - selectable archive file list with text/type filtering
  - persistent per-archive cache folders
  - open root cache folder
  - open active archive cache folder
  - clear active archive cache
  - show resolved cache path and last extracted file
- Export presets for `.geo`, `.vdf`, and `.sdf`:
  - built-in workflow presets
  - save/delete custom presets

## Changed

- Reorganized Scene, Object, Material, Animation, and ZFS panels into workflow-oriented groupings.
- Grouped Battlezone import/export entries under dedicated File menu submenus.
- GEO export texture fallback now prefers linked image names before material-name fallback.

## Fixed

- Legacy export validation now catches more silent-failure cases before export.
- ZFS imports now keep extracted dependencies in predictable cache paths instead of anonymous temp directories.
- Export dialogs now expose common options more clearly and reduce flat property dumps.

## Notes

- Custom export presets are stored inside the addon folder under `_presets/geo`, `_presets/vdf`, and `_presets/sdf`.
- ZFS cache data is stored under the addon `_cache/zfs` folder unless the user changes the cache root in the Scene panel.
