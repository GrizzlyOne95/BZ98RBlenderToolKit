# Experimental Binary Fields Reference

This note documents raw values currently exposed in the toolkit for advanced import/export workflows.

Sources used:
- Commando950 addon docs
- Nielk1 `bz1-geo-editor` (`BZ1GeoEditor/Geo.cs`)

## VDF / SDF ANIM

- `ANIM null2` and `ANIM unknown2` are preserved as raw 32-bit ints.
- `ANIM reserved[5]` is preserved as raw ints.
- `ANIM element unknowngeoflag[32]` is preserved per element.
- `UseTranslation2Track` routes location keys to `ANIMTranslation2` instead of `ANIMPosition`.

## VDF SCPS

- `SCPS data[3]` is preserved as raw 32-bit ints.
- Many files leave these as zero; treat non-zero values as experimental.

## GEO Header (`=4si16siii`)

Toolkit fields:
- `GEOHeaderUnknown` = second int in header
- `GEOHeaderUnknown2` = trailing int in header

From `bz1-geo-editor`, the trailing int is treated as object `Flags` with these common bits:
- `0x001` Gouraud shaded
- `0x002` Tiled bitmap
- `0x004` Texture map
- `0x008` Parallel
- `0x010` True perspective
- `0x020` Wireframe
- `0x040` Transparent pixels
- `0x080` One-third translucent pixels
- `0x100` Project polygon only

## GEO Face (`=iiBBBffffi3s13sii`)

Toolkit per-face attrs (import/export):
- `bz_face_unknown_raw` (int)
- `bz_face_shade_type` (byte stored in int attr)
- `bz_face_texture_type` (byte stored in int attr)
- `bz_face_xluscent_type` (byte stored in int attr)
- `bz_face_parent` (int)
- `bz_face_node` (int)

Face enum values from `bz1-geo-editor`:

Shade type (`bz_face_shade_type`):
- `1` wireframe
- `2` solid wireframe
- `3` constant shaded
- `4` flat shaded
- `5` gouraud shaded

Texture type bits (`bz_face_texture_type`):
- `0x01` true perspective
- `0x02` tiled texturemap
- `0x04` transparent textmap

Xluscent type (`bz_face_xluscent_type`):
- `0` none
- `1` one-third
- `2` two-third

Node/tree branch (`bz_face_node`):
- commonly treated as `0` back, `1` front.

## Safety

- Always keep backups.
- Change one field at a time and test in-game.
- Some values are engine- or asset-specific and may be ignored.
