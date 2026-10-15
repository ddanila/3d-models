# Robotron 1715M display base ring

Plastic insert for the display's round metal base, intended to protect the
computer block from scratches. Modeled as a plain ring with a rectangular
cross-section using the supplied dimensions.

| Dimension | Value |
| --- | ---: |
| Outer diameter | 174.5 mm |
| Radial wall thickness | 3.5 mm |
| Inner diameter (derived) | 167.5 mm |
| Height | 5 mm |

Files: [OpenSCAD source](model.scad),
[STL](robotron-1715m-display-base-ring.stl), [preview](preview.png).

All dimensions are editable at the top of `model.scad`. No fit allowance has
been added to the supplied dimensions.

**Printed and verified:** on 2026-10-15, Danila confirmed that the latest
174.5 mm outer / 167.5 mm inner diameter ring was printed and fits the monitor
base perfectly. This confirms the fit from his printer and settings; printer
model, material and slicer settings were not recorded. The date is the
confirmation date; the exact print date was not specified.

Dimensions revised by Danila on 2026-10-14 for another fit trial: 174.5 mm
outer diameter, retaining the 3.5 mm radial wall and 5 mm height, giving a
167.5 mm inner diameter. Previous revisions were 175/169 mm on 2026-10-09
and 174/167 mm on 2026-10-13 (outer/inner diameters). OpenSCAD exported the model without geometry
errors; the STL was checked for the specified outer diameter, inner diameter,
and height.

Print flat with either annular face on the bed; the geometry needs no supports.
The part occupies a 174.5 × 174.5 mm footprint before any brim or skirt. Remove
any rough edges from the contact face before installing it.

From the repository root:

```sh
./scripts/open.sh robotron-1715m/display-base-ring
```
