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
        [db9_opening_x, db9_opening_y],
        [db9_opening_width, db9_opening_depth],
        epsilon
    );

color([0.08, 0.25, 0.08])
    translate([pcb_x, pcb_y, usb_projection])
        cube([pcb_width, pcb_thickness, pcb_length]);

color([0.65, 0.65, 0.68])
    translate([
        (outer_width - db9_body_width) / 2,
        pcb_top_y - db9_opening_below_pcb_top,
        usb_projection + pcb_length
    ])
        cube([db9_body_width, db9_body_depth, 6]);
