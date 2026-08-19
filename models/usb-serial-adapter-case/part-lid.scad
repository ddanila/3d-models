// Flat DB9-end lid, oriented face-down for printing.

include <dimensions.scad>
use <lid-lib.scad>

lid(
    [outer_width, outer_depth],
    lid_thickness,
    [db9_opening_x, db9_opening_y],
    [db9_opening_width, db9_opening_depth],
    epsilon
);
