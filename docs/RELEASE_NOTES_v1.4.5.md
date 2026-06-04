# BZ98R Blender Toolkit v1.4.5

## Summary

This release adds custom world atlas terrain painting support, removes the unsupported Game Playback tooling, and expands legacy Battlezone modeling validation based on the classic unit modeling guide.

## Added

- Added **Import Custom World** in the map texture painting tools.
- Custom worlds can load their terrain material/atlas data from a world folder, using `.trn` and atlas CSV data when available.
- Stock terrain painting worlds remain available and unchanged.
- Added compact validation reports with a `What Gets Checked` popup.
- Added LOD2 cockpit validation for matching LOD1 counterparts, direct parent linkage, and matching pivot/origin/orientation.
- Added LOD3 validation for missing LOD1 counterparts, high-detail meshes, and material/texture usage.
- Added validation warnings for multiple exportable model roots in one scene.
- Added legacy animation validation for looping first/last pose mismatches, high animated-GEO counts, and legacy 10-20 frame range guidance.
- Added a `Pivot / Dummyroot Info` popup explaining Blender object origins, Battlezone pivots, local axes, hover/sink offsets, and dummyroot-equivalent authoring.
- Added Redux export warning when headlights are enabled but no Type 38 headlight GEO exists.
- Added UI notes for LOD2 cockpit GEOs, LOD3 legacy fallback GEOs, multiplayer-only path point respawning, SDF-only automatic collision generation, and Redux dual-component model structure.
- Added advanced VDF helper notes for spinner helpers and raw transform scaling.

## Changed

- The validation button now reports checked items and compact findings instead of only showing counts.
- GEO data, selected GEO info, object GEO info, and animation element display text now wraps more compactly in Blender side panels.
- VDF collision-helper validation is less broad for structure/producer-style exports while keeping vehicle checks available.
- Mirror Legacy Animation Keys now supports explicit `Mirror From` and `Mirror To` object selectors with warning-only mesh similarity verification.
- Map texture painting now uses a loaded custom atlas when active and falls back to stock worlds otherwise.
- The BZMapIO addon metadata now describes terrain, texture, object, and path data without Game Playback.

## Removed

- Removed the unsupported Game Playback feature from active UI and registration.

## Verified

- Python compile checks passed for `bz98tools/__init__.py`, `bz98tools/map_io.py`, and `bz98tools/validation.py`.
- Git diff whitespace checks passed for touched addon modules.
- Custom atlas parsing was tested against the Polar Mars world example, including `.trn` material discovery and atlas tile code mapping.

## Installation

1. Download `bz98tools.zip` from this release.
2. In Blender, go to **Edit > Preferences > Add-ons**.
3. Click **Install...** and select the downloaded `.zip` file.
4. Ensure **Battlezone GEO/VDF/SDF Formats** is enabled.
