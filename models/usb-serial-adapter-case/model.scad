// Vertical, open-ended case for the DIYMORE FT232BM/BL USB serial adapter.
// The USB end is the print bed; the DB9 end is the open top.
// All dimensions are in millimetres.

include <dimensions.scad>

module guide_ribs() {
    for (x = [wall, pcb_x + pcb_width - guide_contact_width])
        translate([x, wall, bottom_thickness])
            cube([
                width_clearance + guide_contact_width,
                underboard_clearance,
                case_height - bottom_thickness
            ]);
}

module case() {
    difference() {
        union() {
            difference() {
                cube([outer_width, outer_depth, case_height]);

                // The cavity continues through the DB9 end, making that end
                // the completely open mouth of the well.
                translate([wall, wall, bottom_thickness])
                    cube([inner_width, inner_depth, case_height]);
            }
            guide_ribs();
        }

        // USB-B opening through the closed bottom face.
        translate([
            pcb_x + (pcb_width - usb_opening_width) / 2,
            pcb_top_y - usb_opening_below_pcb_top,
            -epsilon
        ])
            cube([
                usb_opening_width,
                usb_opening_depth,
                bottom_thickness + 2 * epsilon
            ]);
    }
}

case();
