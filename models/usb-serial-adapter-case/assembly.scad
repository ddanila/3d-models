// Case and DB9 lid in their assembled positions, with a translucent PCB and
// connector envelope for context. Reference geometry is not exported.

include <dimensions.scad>
use <model.scad>
use <lid-lib.scad>

case();

translate([0, 0, case_height])
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

color([0.08, 0.25, 0.08])
    translate([pcb_x, pcb_y, usb_projection])
        cube([pcb_width, pcb_thickness, pcb_length]);

color([0.65, 0.65, 0.68])
    translate([0, 0, usb_projection + pcb_length])
        db9_pattern(
            [db9_center_x, db9_center_y],
            db9_face_pcb_width,
            db9_face_outer_width,
            db9_face_height,
            db9_face_corner_radius,
            db9_screw_spacing,
            db9_screw_boss_diameter,
            0,
            6
        );
