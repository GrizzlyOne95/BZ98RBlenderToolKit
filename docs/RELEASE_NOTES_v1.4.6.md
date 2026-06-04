# BZ98R Blender Toolkit v1.4.6

## Summary

This hotfix corrects popup info buttons that could execute without opening their dialog from Blender panels.

## Fixed

- Fixed **What Gets Checked** so it opens the validation coverage report from the selected GEO validation panel.
- Fixed related info popup buttons for Redux model system notes, pivot/dummyroot notes, and advanced VDF notes by invoking their dialogs explicitly from UI panels.

## Verified

- Python compile check passed for `bz98tools/__init__.py`.
- Git diff whitespace check passed for `bz98tools/__init__.py`.

## Installation

1. Download `bz98tools.zip` from this release.
2. In Blender, go to **Edit > Preferences > Add-ons**.
3. Click **Install...** and select the downloaded `.zip` file.
4. Ensure **Battlezone GEO/VDF/SDF Formats** is enabled.
