# BZ98R Blender Toolkit v1.2.0

## Summary

This release adds advanced binary controls for VDF/SDF/GEO workflows, including direct preservation/editing of previously hardcoded fields.

## Added

- VDF/SDF advanced ANIM controls:
  - `null2`
  - `unknown2`
  - `reserved[5]`
  - optional location track routing to `translation2`
- VDF SCPS raw 3-int controls.
- ANIM element custom 32-int unknown GEO mask editor.
- GEO header raw int pass-through controls.
- GEO face raw metadata pass-through via per-face mesh attributes:
  - `bz_face_unknown_raw`
  - `bz_face_shade_type`
  - `bz_face_texture_type`
  - `bz_face_xluscent_type`
  - `bz_face_parent`
  - `bz_face_node`
- Reference documentation for experimental binary fields and known values.

## Fixed

- ANIM element unknown GEO mask parsing now correctly reads all 32 integers (not 31).
- ANIM mask writes are now padded/truncated safely to avoid malformed export data.
- SDF GEO transform export slice issue corrected for matrix row packing.

## Notes

- These controls are intentionally low-level and can produce invalid assets if misused.
- Always keep backups and test in game after each binary-level change.
