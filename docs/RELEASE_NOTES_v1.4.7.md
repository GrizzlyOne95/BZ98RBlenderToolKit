# BZ98R Blender Toolkit v1.4.7

## Summary

This hotfix makes the Legacy Object Animation mirror/copy tool open its settings dialog from the Animation Tools panel.

## Fixed

- Fixed **Animation Tools > Mirror Legacy Keys** so it opens the operator dialog containing the explicit **Mirror From** and **Mirror To** object selectors.
- Added compact text in the Animation Tools panel noting that the button can be used for explicit source/target pairing.

## Verified

- Python compile check passed for `bz98tools/__init__.py`.
- Git diff whitespace check passed for `bz98tools/__init__.py`.
- Synced the Blender 4.5 AppData addon folder from the repo copy.

## Installation

1. Download `bz98tools.zip` from this release.
2. In Blender, go to **Edit > Preferences > Add-ons**.
3. Click **Install...** and select the downloaded `.zip` file.
4. Ensure **Battlezone GEO/VDF/SDF Formats** is enabled.
