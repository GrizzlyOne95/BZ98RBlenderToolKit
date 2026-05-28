# BZ98R Blender Toolkit v1.4.2

## Summary

This patch tightens several legacy Battlezone binary fields based on reverse-engineering against Redux symbols and stock assets, and fixes the collision panel so automatic collision generation hides manual fields that are ignored on export.

## Changed

- Legacy `SCLKEY` / `ANIMTranslation2` now imports and exports Blender scale animation instead of location animation.
- POSKEY location animation remains independent when scale keys are enabled.
- SDF `Defensive` is now exposed as the raw integer `SDFC DDR` field.
- VDF vehicle size/type and SDF structure type descriptions now document observed stock values and preserve imported values.
- GEO face byte tooltips now document flat/Gouraud shading, texture flag bytes, and translucency values.
- GEO header second int is now labeled as a preserved checksum/signature-like field rather than a general authoring control.

## Fixed

- The GEO Collision panel now hides manual center, projectile box, sphere radius, and manual generation controls when **Automatically Generate Collisions** is checked.
- Legacy export validation now treats scale f-curves as supported for VDF/SDF animation export.

## Notes

- The internal class name `ANIMTranslation2` remains for compatibility with existing toolkit code, but the file slot is the legacy `SCLKEY` scale-key track.
- The `SDFC DDR` field is preserved as an integer. Stock structures commonly use `500000`; mine/powerup-like structures may use smaller values.

## Installation

1. Download `bz98tools.zip` from this release.
2. In Blender, go to **Edit > Preferences > Add-ons**.
3. Click **Install...** and select the downloaded `.zip` file.
4. Ensure **Battlezone GEO/VDF/SDF Formats** is enabled.
