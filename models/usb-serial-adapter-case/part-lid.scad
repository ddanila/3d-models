// Flat DB9-end lid, oriented face-down for printing.

include <dimensions.scad>
use <lid-lib.scad>

lid(
    [outer_width, outer_depth],
    lid_thickness,
    [db9_center_x, db9_center_y],
    db9_face_pcb_width,
    db9_face_outer_width,
    db9_face_height,
    db9_face_corner_radius,
    db9_screw_spacing,
    db9_screw_boss_diameter,
    db9_fit_clearance,
    epsilon
);
