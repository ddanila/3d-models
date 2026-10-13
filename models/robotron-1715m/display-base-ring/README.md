# Robotron 1715M display base ring

Plastic insert for the display's round metal base, intended to protect the
computer block from scratches. Modeled as a plain ring with a rectangular
cross-section using the supplied dimensions.

| Dimension | Value |
| --- | ---: |
| Outer diameter | 174 mm |
| Radial wall thickness | 3.5 mm |
| Inner diameter (derived) | 167 mm |
| Height | 5 mm |

Files: [OpenSCAD source](model.scad),
[STL](robotron-1715m-display-base-ring.stl), [preview](preview.png).

All dimensions are editable at the top of `model.scad`. No fit allowance has
been added to the supplied dimensions. Fit in the metal base is untested.

Dimensions revised by Danila on 2026-10-13: 174 mm outer diameter,
3.5 mm radial wall and 167 mm inner diameter. This revision supersedes the
175/169 mm version visually approved on 2026-10-09. Printer and
physical-fit checks are pending. OpenSCAD exported the model without geometry
errors; the STL was checked for the specified outer diameter, inner diameter,
and height.

Print flat with either annular face on the bed; the geometry needs no supports.
The part occupies a 175 × 174 mm footprint before any brim or skirt. Remove
any rough edges from the contact face before installing it.

From the repository root:

```sh
./scripts/open.sh robotron-1715m/display-base-ring
```
