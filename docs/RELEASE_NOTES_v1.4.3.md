# BZ98R Blender Toolkit v1.4.3

## Summary

This release adds the Organic Redux Skin helper for turning legacy VDF/SDF/GEO control hierarchies into Redux-ready weighted armatures. It is intended for organic-looking Redux meshes that should flex between engine-driven control pieces while preserving the normal rigid GEO workflow for legacy VDF/SDF export.

## Added

- **Create Organic Redux Skin From VDF Hierarchy** in the 3D View Battlezone sidebar.
- Generates an armature from selected valid GEO control pivots or an active GEO hierarchy.
- Creates bones with matching GEO names and deterministic `OGREID` values.
- Binds a selected continuous mesh through an Armature modifier.
- Creates starter vertex groups with nearest-control weighting and optional parent/child blend zones.
- Supports up to three influences per vertex to match the native Redux export path.
- Added `docs/ORGANIC_REDUX_SKIN_WALKTHROUGH.md` with setup, export, troubleshooting, and `fvsentry` test guidance.

## Clarified

- Organic Redux skins for ships such as `fvsentry` do not require exported skeleton actions.
- The generated static skeleton should be driven by Redux runtime control motion through matching GEO-named bones.
- Blender actions are only useful as temporary local previews while checking or painting weights.

## Verified

- Created an `fvsentry` example from the real `fvsentry.vdf`, `fse*.geo`, `fvsentry.mesh`, and `fvsentry.skeleton` files.
- Joined the imported Redux submeshes into one visible mesh.
- Generated an 11-bone GEO-control armature from LOD1 `fse11*` controls.
- Confirmed all 2289 vertices were weighted, with no bad weight sums and no more than three influences per vertex.
- Exported `.mesh`, `.skeleton`, and `.material` successfully with `Export Animations` disabled.

## Installation

1. Download `bz98tools.zip` from this release.
2. In Blender, go to **Edit > Preferences > Add-ons**.
3. Click **Install...** and select the downloaded `.zip` file.
4. Ensure **Battlezone GEO/VDF/SDF Formats** is enabled.
