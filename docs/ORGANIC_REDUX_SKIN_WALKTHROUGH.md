# Organic Redux Skin Walkthrough

This walkthrough covers the **Create Organic Redux Skin From VDF Hierarchy** helper in the Battlezone Blender Toolkit.

The helper lets you keep a normal legacy VDF/SDF/GEO control hierarchy, then create a Redux `.mesh/.skeleton` rig that bends a continuous mesh between those controls. The legacy VDF/SDF version still exports as rigid GEO pieces. The organic deformation is for direct Redux mesh/skeleton export.

## Mental Model

Legacy VDF/SDF GEOs are control pieces:

- body/root
- wing base
- wing mid
- wing tip or nacelle
- fins, rotators, hardpoints, and type-specific control GEOs

The helper turns those GEO object pivots into Redux bones with matching names. A continuous visible mesh can then be weighted across those bones so nearby vertices stretch or bend instead of pivoting as hard chunks.

## Before You Start

You need:

- A valid legacy GEO hierarchy already in the Blender scene.
- GEO control objects with valid legacy names and `GEOPropertyGroup` data.
- A separate continuous mesh object that will become the visible Redux mesh.
- Blender in Object Mode.

The continuous mesh should be the object you want to export as Redux `.mesh`. It does not need to be split like the legacy GEO chunks.

## Recommended Scene Layout

For an organic wing and nacelle setup, use a legacy hierarchy like this:

```text
body/root GEO
  wing_base GEO
    wing_mid GEO
      nacelle or wing_tip GEO
```

Then create or import one larger mesh for the visible wing surface. Keep hard mechanical parts separate if they should remain rigid.

## Basic Workflow

1. Select the continuous visible mesh.
2. Select the GEO control objects that should become bones.
3. Make the continuous mesh the active object.
4. Open the 3D View sidebar.
5. Go to `Battlezone > Organic Redux Skin`.
6. Click `Create Organic Redux Skin`.
7. Keep `Control Source` set to `Selected GEO Controls`.
8. Use the default `Nearest Controls With Joint Blends` weight mode.
9. Click OK.

The tool creates an armature named after the mesh, creates bones at the GEO pivots, assigns `OGREID` values, adds vertex groups to the mesh, and binds the mesh with an Armature modifier.

## Hierarchy Fallback Workflow

Use `Control Source: Active GEO Hierarchy` when the continuous mesh is parented somewhere under the GEO control hierarchy.

1. Parent the continuous mesh under one of the GEO controls.
2. Select only the continuous mesh.
3. Make it active.
4. Run `Create Organic Redux Skin`.
5. Set `Control Source` to `Active GEO Hierarchy`.

The tool finds the nearest valid GEO ancestor, walks up to the GEO root, then collects valid GEO descendants as controls.

## Tool Options

| Option | Default | Use |
| --- | --- | --- |
| Control Source | Selected GEO Controls | Chooses whether controls come from selection or the active mesh hierarchy. |
| Keep GEO Controls Visible | Off | Leave this on if you want the original GEO chunks visible after rig creation. |
| Weight Mode | Nearest Controls With Joint Blends | Creates starter blended weights near parent/child control joints. |
| Blend Radius | 0.35 | Larger values make wider transition zones between controls. |
| Max Influences | 3 | Matches the native Redux exporter limit used by the toolkit. |
| Replace Existing Rig Data | On | Clears matching generated vertex groups and the generated armature modifier before rebinding. |

## Weighting Behavior

`Nearest Controls With Joint Blends` creates starter weights from the nearest GEO/bone pivots and adds blend influence near parent/child joints. This is intended as a first pass, not final art weighting.

Use Blender's normal weight paint tools after generation to refine:

- vertices near the body mostly to `body` or `wing_base`
- mid-wing vertices blended between `wing_base` and `wing_mid`
- tip or nacelle-adjacent vertices blended between `wing_mid` and `nacelle`
- hard mechanical bits weighted 100 percent to one bone

Use `Nearest Single Control` when you want rigid starter weights and plan to paint blends manually.

## Animating The Result

Animate the generated armature bones using the same motion rules the GEO controls would use: rotation and location on the control part. The visible Redux mesh deforms between weighted bones, while the original GEO hierarchy remains available for legacy rigid export.

For direct Redux export:

1. Select the weighted continuous mesh.
2. Use `File > Export > Redux Mesh Only (.mesh)`.
3. Enable `Export Skeleton`.
4. Enable `Export Animations` if the generated armature has animation actions.
5. Export the `.mesh` and `.skeleton`.

The exporter maps vertex groups by bone name, and the generated bones already have `OGREID` values.

## Legacy Export Limitation

Legacy VDF/SDF export does not support skinned deformation. If you export the same scene as VDF/SDF, Battlezone will still use rigid GEO pieces and object transform animation. Use the generated Redux rig only for `.mesh/.skeleton` output.

## Troubleshooting

### The operator is disabled

Make sure the active object is a mesh. The continuous visible Redux mesh must be active when you run the helper.

### No controls were found

For `Selected GEO Controls`, select at least one valid GEO control object in addition to the active mesh.

For `Active GEO Hierarchy`, parent the active mesh under a valid GEO control hierarchy.

### Export reports invalid vertex groups

Confirm that the mesh's vertex group names match generated bone names. If you renamed bones or vertex groups manually, keep the names aligned before exporting.

### The mesh bends too much or too little

Run the helper again with a different `Blend Radius`, or use Weight Paint mode to refine the generated vertex groups.

### The original GEO chunks disappeared

They were hidden, not deleted. Enable `Keep GEO Controls Visible` next time, or unhide the GEO control objects in the Outliner.
