# Experimental Binary Fields Reference

This note documents raw values currently exposed in the toolkit for advanced import/export workflows.

Sources used:
- Commando950 addon docs
- Nielk1 `bz1-geo-editor` (`BZ1GeoEditor/Geo.cs`)
- Battlezone 98 Redux PDB reference in `Battlezone98Redux_Shim`
- Stock Redux assets in `Documents/Battlezone 98 Redux/Edit/stock` (1615 GEO, 98 VDF, 115 SDF scanned)

## VDF / SDF ANIM

The PDB names the 64-byte ANIM payload as `tagANIMOBJ_HEADER`:

- `ANIM null2` maps to `animPtr`.
- `ANIM unknown2` maps to `meshPtr`.
- `ANIM reserved[0]` maps to `rotKeyPtr`.
- `ANIM reserved[1]` maps to `sclKeyPtr`.
- `ANIM reserved[2]` maps to `posKeyPtr`.
- `ANIM reserved[3]` maps to `obj`.
- `ANIM reserved[4]` maps to `entity`.

On disk, stock exported assets store these pointer-placeholder fields as zero. The toolkit preserves them for round-trip safety, but modders normally should not edit them.

The PDB names `ANIMElement.unknowngeoflag[32]` as `meshIndex[32]`. Stock files use it as a 0/1 per-mesh-slot mask: `1` means the animation element affects that indexed GEO/mesh slot, `0` means it does not.

The PDB names `ANIMOrientation.unknown` as `tagANIMOBJ_MESH.flags`. Stock files scanned so far store `0`.

`UseTranslation2Track` writes keys to the legacy `SCLKEY` slot (`tagANIMOBJ_SCLKEY`). The toolkit still uses the historical internal class name `ANIMTranslation2`, but engine symbols identify this as the scale-key track. A few stock assets use it for special motion.

## VDF SPCS / SCPS

Redux symbols contain an `SPCS` chunk tag and a `VDF_VEHICLE_SHELL_INFO` structure for shell UI slots, while older addon code called the preserved raw block `SCPS`. No stock VDF in the current scan contained this optional block. Treat the toolkit's `SPCS/SCPS Data` fields as compatibility preservation only until a real sample is found.

## VDF / SDF Object Records

The PDB names the VDF object record as `ObjectType` and the SDF object record as `StructObjectType`.

Confirmed names:

- `GEOFlags` is `ObjectFlags`.
- `SDFDDR` is `ddr`.
- `SDFX`, `SDFY`, `SDFZ` are the `Target` vector.
- `SDFTime` is `Time`.

Stock scan notes:

- VDF `ObjectFlags` was `0` in all 1243 valid stock VDF object records.
- SDF `ObjectFlags` was `0` in all normal valid structure records seen in the scan.
- Stock SDF `ddr` is commonly `500000`; mine/powerup-like SDFs can use smaller values such as `200`.
- Stock type-15 structure spinner helpers commonly use `Target.y` as a small spin-speed value such as `0.1` or `0.2`.

## GEO Header (`=4si16siii`)

Toolkit fields:
- `GEOHeaderUnknown` = second int in header. This is still unconfirmed; stock values vary widely and do not match vertex or face counts.
- `GEOHeaderUnknown2` = trailing int in header.

Stock scan notes:

- `GEOHeaderUnknown2` was `0` in all 1615 stock Redux GEO files scanned.

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
- `bz_face_unknown_raw` (reserved int; stock scan found `0` on all faces)
- `bz_face_shade_type` (byte stored in int attr)
- `bz_face_texture_type` (byte stored in int attr)
- `bz_face_xluscent_type` (byte stored in int attr)
- `bz_face_parent` (int)
- `bz_face_node` (int)

The PDB `FACE` structure confirms the three string-header bytes as:

- `ShadeType`
- `TextureType`
- `XluscentType`

The same structure has an in-memory `front_facet` pointer and `Test_Point`; the on-disk parent/node integers appear to be loader inputs for that face tree rather than arbitrary user data.

Stock scan notes:

- Most faces use bytes `04 01 00` (flat shaded, true perspective, not translucent).
- Gouraud faces use `05 01 00`.
- A small number use `04 03 00` (flat shaded plus true perspective and tiled texture bits).

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
