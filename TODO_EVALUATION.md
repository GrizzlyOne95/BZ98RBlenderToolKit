# Evaluation of TODOs in Battlezone Blender Toolkit

A total of 58 TODO markers were found in the codebase (excluding third-party vendor code). They can be categorized as follows:

## 1. Exception Handling (High Frequency)
*   **Issues**: Many places in `bzportmodels.py` have comments like `# TODO: Name this exception`. This indicates that generic `Exception` is being caught or raised, making debugging difficult.
*   **Impact**: Moderate. It doesn't break functionality but makes the code less robust and harder to maintain.

## 2. Reverse Engineering & Logic Gaps (Critical)
*   **Issues**:
    *   `bzrmodelporter/ogremesh_serializer.py:398`: `edge_data = None # TODO` - Missing edge data implementation for Redux meshes.
    *   `bzrmodelporter/bzportmodels.py:779`: `TODO: When there are multiple POV bones, which one is used?` - Ambiguity in vehicle POV handling.
    *   `bzrmodelporter/bzportmodels.py:2142`: `TODO: Detect when normals point in the wrong direction and flip them!` - Potential visual bugs in exported models.
    *   `sdf_classes.py:390`: `# TODO: Figure out what this even does...` - Indicates unknown binary fields in the SDF format.
*   **Impact**: High. These represent incomplete features or potential bugs in the core import/export logic.

## 3. Performance & Optimization (Medium)
*   **Issues**:
    *   `bzrmodelporter/bzportmodels.py:14`: `import numpy as np # TODO: Make better use of numpy`.
    *   Several TODOs about checking buffer sizes and calculating LOD levels.
*   **Impact**: Low. The tool works but could be faster for large models.

## 4. Refactoring & Cleanliness (Medium)
*   **Issues**:
    *   `bz98tools/ogretools/OgreImport.py:176`: `# TODO: this is not needed for Blender 2.62 and above` - Legacy code from very old Blender versions.
    *   `bzrmodelporter/bzportmodels.py:323`: `TODO: Take anim slices out of InterObject` - Architectural technical debt.
*   **Impact**: Moderate. Contributes to the "God Object" problem and general code rot.

## 5. Feature Requests (Low)
*   **Issues**:
    *   `bzrmodelporter/port_models.py:158`: `TODO: Pull from a config file`.
    *   `bzrmodelporter/port_models.py:739`: `TODO: Track which BWD2s have already been ported`.
*   **Impact**: Low. These are enhancements rather than fixes.

---
**Conclusion**: The majority of TODOs are in the `bzrmodelporter` sub-package, which handles the conversion to Redux formats. The most concerning are those related to incomplete binary format implementation and generic exception handling.
