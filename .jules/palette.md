## 2025-05-15 - [Blender Addon List UI Pattern]
**Learning:** For list-based UI in Blender addons, the standard pattern is to place control buttons (add, remove, move) in a column to the right of the list box. Using icons only for these buttons saves space and follows the native look.
**Action:** Always use the `row = box.row(); col = row.column(); col.template_list(...); col = row.column(align=True);` pattern for list UIs in Blender.

## 2025-05-15 - [Iconography for Scannability]
**Learning:** Adding icons to operator buttons in sidebars and property panels significantly improves scannability for power users who recognize icons faster than reading labels.
**Action:** Proactively suggest or add icons to major "Quick Tool" buttons in specialized addons.
