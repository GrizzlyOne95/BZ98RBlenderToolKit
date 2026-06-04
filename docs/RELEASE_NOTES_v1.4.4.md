# BZ98R Blender Toolkit v1.4.4

## Summary

This release adds experimental legacy GEO face-plane preservation/recompute controls, a best-effort `DX Normal Distance Fix` mode based on reverse engineering older Battlezone tools, and an experimental Redux walker cockpit stabilizer for first-person cockpit jitter.

## Added

- Added `Face Plane Export` to GEO, VDF, and SDF export dialogs.
- Added imported GEO face-plane preservation through per-face attributes:
  - `bz_face_plane_x`
  - `bz_face_plane_y`
  - `bz_face_plane_z`
  - `bz_face_plane_d`
- Added `Preserve Imported`, `Recompute From Faces`, and `DX Normal Distance Fix` face-plane export modes.
- Added selected-face display for preserved face-plane floats.
- Added an experimental VDF auto-port option, `Experimental Walker Cockpit Stabilizer`, for separate Redux cockpit output on walker units.
- Added validation warning for GEO faces with more than 10 vertices, matching the fixed per-face capacity found in the unpacked legacy GEO viewer.

## Reverse Engineering Notes

- Unpacked the legacy VDF, SDF, and GEO viewers with a run-and-memory-dump pass after confirming all three were Petite-packed.
- Confirmed the old GEO viewer reads the standard `OEG.` GEO header and stores each face in a 216-byte in-memory record: 56 bytes of fixed face data plus ten 16-byte polygon vertex records.
- Confirmed the old VDF viewer writes `VGEO` as `geocount * 28 * 100`.
- Confirmed the old SDF viewer writes `SGEO` as `geocount * 6 * 0x78`.
- Confirmed VDF/SDF `ANIM`, `COLP`, and `SPCS` chunk sizes align with the toolkit serializer and existing experimental binary-field documentation.
- Confirmed the old Max `GEOExport.dle` exposes a `DX normal distance fix` intended to work around disappearing triangles; the toolkit's current mode recomputes the face plane normal/distance as a best-effort version pending byte-for-byte formula confirmation.

## Fixed

- Direct GEO import no longer discards the four face-plane floats.
- VDF/SDF exports can now apply the same face-plane mode to referenced GEO files they write.
- Separate Redux cockpit output can now optionally root cockpit/POV bones in model space to reduce walker body-animation jitter in first person.

## Verified

- Python compile checks passed for all touched addon modules.
- Tested the walker cockpit stabilizer against the Mauler conversion path and confirmed cockpit/POV bones are rooted when enabled.
- Confirmed the unpacked legacy viewers and Max plugins agree with the toolkit's VDF/SDF object record and animation record sizes.

## Installation

1. Download `bz98tools.zip` from this release.
2. In Blender, go to **Edit > Preferences > Add-ons**.
3. Click **Install...** and select the downloaded `.zip` file.
4. Ensure **Battlezone GEO/VDF/SDF Formats** is enabled.
