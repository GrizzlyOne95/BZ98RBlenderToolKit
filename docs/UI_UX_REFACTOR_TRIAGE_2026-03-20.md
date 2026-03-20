# BZ98R Blender Toolkit UI/UX Refactor Triage

Date: 2026-03-20

## Goal

Implement the requested Blender addon usability overhaul without mixing risky behavior changes and panel cleanup into one uncontrolled pass.

This plan covers:

- export validation and clearer warnings
- better grouping for legacy import/export dialogs
- scene/object/material panel cleanup
- a named `GEOType` selector instead of raw numeric entry
- animation editor improvements
- ZFS explorer cleanup
- File menu grouping improvements

## Guiding Constraints

- Preserve existing file I/O behavior unless a phase explicitly targets behavior changes.
- Keep changes incremental enough to validate inside Blender after each phase.
- Avoid a large early module split of `bz98tools/__init__.py`; start with helpers and small internal extraction points first.
- Treat raw binary controls as advanced features, not first-run workflow controls.

## Triage Summary

### Track A: Validation and Export Safety

Priority: Highest

Why first:

- This removes the worst current usability failure mode: silent export skipping.
- It gives immediate value even before UI polish lands.
- It provides shared data for later panels and export dialogs.

Primary work:

- Add a reusable scene validation pass for legacy exports.
- Detect:
  - invalid GEO naming and missing LOD markers
  - names that collide after `fixgeoname()`
  - invalid parent naming / parent references that collapse to `WORLD`
  - invalid or missing collision helper objects
  - empty or non-mesh export candidates
  - suspicious material texture names for legacy GEO export
- Add a validator operator and a scene-side results panel.
- Add export-time warning reporting for VDF/SDF/GEO exports.

Acceptance target:

- A user can run a validation pass before export and see exactly what will be skipped or normalized.
- Legacy exports no longer fail silently on common naming mistakes.

### Track B: Legacy Export Dialog Layout

Priority: High

Why second:

- The operator surfaces are currently flat and crowded.
- This is a low-risk UI improvement once validation helpers exist.

Primary work:

- Add custom `draw()` implementations for:
  - `ExportGEO`
  - `ExportVDF`
  - `ExportSDF`
- Group fields into:
  - `Core Export`
  - `Animations`
  - `Legacy Output`
  - `Create Redux/BZR Files`
  - `Advanced`
- Only show Ogre auto-port options when `auto_port_ogre` is enabled.
- Add short inline warnings for destructive or unusual options.

Acceptance target:

- Legacy export dialogs match the clarity level of the current Redux mesh dialogs.

### Track C: Scene/Object Panel Reorganization

Priority: High

Why third:

- This is where most users spend time after import.
- The current panels mix routine work with engine-internals editing.

Primary work:

- Reorganize scene panel content into task-based sections:
  - `Asset Properties`
  - `Animations`
  - `Collision Helpers`
  - `Advanced`
- Reorganize object panel content into:
  - `Role`
  - `Collision`
  - `SDF Extras`
  - `VDF Extras`
  - `Experimental`
- Move raw ANIM, SCPS, raw VDF matrix, and GEO face defaults under collapsed advanced sections.
- Improve labels for `DeathExplosion`, `DeathSound`, and similar low-context fields.

Acceptance target:

- A new user can follow roughly the same flow taught in Commando950's manual without being exposed to raw binary fields by default.

### Track D: GEO Type UX

Priority: High

Why fourth:

- `GEOType` is one of the most important fields in the addon.
- The addon already has the data needed for a better selector.

Primary work:

- Convert `GEOType` from an `IntProperty` entry workflow to an enum-driven workflow.
- Keep numeric IDs visible in labels.
- Preserve import/export compatibility with existing `.blend` files if possible.
- Retain the reference popover as a secondary info surface, not the primary selector.
- Add contextual help text for sensitive types:
  - type 15 spinner
  - headlight/pov/hardpoint classes
  - known unsafe or crash-prone IDs

Acceptance target:

- Users pick named GEO roles directly instead of memorizing integer IDs.

### Track E: Animation Editor UX

Priority: Medium

Why after core panel cleanup:

- This benefits from clearer scene panel organization.
- It is somewhat self-contained but needs careful iteration.

Primary work:

- Replace list abbreviations with readable labels.
- Improve selected-element editor layout.
- Add inline index-role hints instead of a popup-only reference flow.
- Add starter presets/templates for common unit classes if the implementation stays low-risk.
- Keep raw custom GEO mask editing available, but hide it until enabled.

Acceptance target:

- Animation elements are understandable without opening a large reference popup every time.

### Track F: Material Panel Improvements

Priority: Medium

Primary work:

- Expand material panel beyond `MapTexture` plus diffuse color.
- Add:
  - resolved legacy texture name preview
  - 8-character validation
  - optional derive/fill helper from material name or image
  - clearer distinction between legacy texture naming and Redux material flow

Acceptance target:

- Material setup communicates what legacy GEO export will actually write.

### Track G: ZFS Explorer and Menu Cleanup

Priority: Medium

Primary work:

- Replace the ad hoc ZFS panel listing with a `UIList`.
- Add type filters and clearer import affordances.
- Plan a managed extraction cache instead of indefinite temp retention.
- Group File > Import / Export entries under Battlezone-specific submenus.

Acceptance target:

- Archive browsing is usable on large ZFS files.
- Blender's global import/export menus are less cluttered.

## Recommended Execution Order

1. Track A: validation and export safety
2. Track B: legacy export dialog layout
3. Track C: scene/object panel reorganization
4. Track D: GEO type enum workflow
5. Track E: animation editor UX
6. Track F: material panel improvements
7. Track G: ZFS explorer and menu cleanup

## Suggested Commit Slices

1. Add validation data model and scene validator operator/panel.
2. Wire validation warnings into legacy export operators.
3. Add grouped `draw()` methods for `ExportGEO` / `ExportVDF` / `ExportSDF`.
4. Reorganize scene/object panels and move advanced fields behind collapsed sections.
5. Convert `GEOType` to enum-based UI.
6. Refresh animation panel layout and hints.
7. Refresh material panel.
8. Rework ZFS explorer and File menu grouping.

## Immediate Next Slice

Start with a small but high-value implementation batch:

1. Add a shared validation helper for legacy export candidates.
2. Add a `Validate Battlezone Scene` operator and results panel in Scene properties.
3. Add grouped `draw()` methods to the three legacy export operators.

This gives users immediate feedback and improves the most crowded operator UIs without changing file formats yet.

## Risks To Watch

- `GEOType` property migration may affect existing saved `.blend` files if not handled carefully.
- Export validation must warn clearly without becoming noisy for intentional advanced workflows.
- ZFS cache management must not break texture references after import.
- Over-aggressive panel hiding can frustrate advanced users; advanced sections should be collapsed, not removed.
- `bz98tools/__init__.py` is already large, so helper extraction should be incremental and mechanical.

## Manual Validation Matrix

Run these after each major phase inside Blender:

- Import a representative `.geo`, `.vdf`, and `.sdf`.
- Export a clean legacy scene with valid names.
- Export a broken legacy scene and confirm validation catches it.
- Export a VDF with `inner_col` and `outer_col`.
- Export an SDF using auto-generated GEO collisions.
- Verify spinner helper creation and export ordering still work.
- Verify raw VDF matrix override still exports when enabled.
- Verify Ogre auto-port options still function after dialog regrouping.
- Import from a ZFS archive with dependencies and textures.

## Out of Scope For The First Pass

- Large codebase modularization of the whole addon.
- Automated Blender GUI tests.
- Deep redesign of Ogre backend behavior.
- New asset pipeline features unrelated to the requested UI/UX overhaul.
