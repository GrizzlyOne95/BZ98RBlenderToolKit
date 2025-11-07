Battlezone 1998 / Redux Blender Toolkit [WIP]
Supports legacy and Ogre files all in one

All credit to Commando950 for the initial Blender plugin code for VDF/SDF/Geo support.
All credit to Kindrad for Blender plugin code for Ogre Mesh code.
All credit to DivisionByZero for code for porting legacy files to Ogre format.

- Fixed GEO Normal Exports for BZR
- Fixed VDF/SDF/Geo imports for non-ASCII characters in files (e.g. TRO VDF's)
- Fixed bad material indices 
- Safe handling if a VDF has a corrupted/missing COL
- Geo Material Name autofills with a safe format from Blender Material Name if it is blank
- Added support for Geo scaling on both import/export. Writes geo scale transforms as they have unique effects inside BZ. (currently VDF only)
- Added Quaternion support in Blender, so it will not ignore quat animation on export. (currently VDF only)
