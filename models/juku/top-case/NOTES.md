# Top Case Notes

All dimensions are in millimeters.

The top case is an open-bottom shell. The main front/back/top body is built
from a single extruded side profile so OpenSCAD preview does not show stray
internal vectors from overlapping wall and top pieces. The left and right
side walls are separate 3 mm profiles added to close the sides while keeping
the underside open for the computer internals.

The keyboard opening is modeled as six row cutouts. Row parameters are kept
near the top of `juku-top-case.scad` so the measured offsets and row widths
can be adjusted without changing the construction modules.

The front top edge roundover is a subtractive cutter applied after the shell
and side walls are unioned. Keeping it out of the base profiles preserves the
separate side-wall chamfers while letting the roundover continue across the
full front edge.
