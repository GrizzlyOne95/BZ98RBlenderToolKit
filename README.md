# BZ98RBlenderToolKit
Supports legacy and Ogre files all in one

All credit to Commando950 for the initial Blender plugin code for VDF/SDF/Geo support.
All credit to Kindrad for Blender plugin code for Ogre Mesh code.

- Fixed GEO Normal Exports for BZR
- Fixed VDF/SDF/Geo imports for non-ASCII characters in files (e.g. TRO VDF's)
- Fixed bad material indices 
- Safe handling if a VDF has a corrupted/missing COL
- Geo Material Name autofills with a safe format from Blender Material Name if it is blank
