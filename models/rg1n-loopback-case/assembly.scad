// Closed case with a simplified RG1N-1-4 reference connector.
// The reference geometry is preview-only and is not exported to either STL.

include <dimensions.scad>
use <case-lib.scad>

module reference_contact(x, z) {
    color([0.72, 0.72, 0.72])
        translate([x - 0.3, flange_pocket_depth, z - 0.25])
            cube([0.6, connector_rear_projection - flange_pocket_depth, 0.5]);
}

module reference_connector() {
    // Brown carbolite flange and rear body.
    color([0.34, 0.13, 0.06])
        difference() {
            union() {
                translate([
                    (case_width - connector_flange_width) / 2,
                    0,
                    (case_height - connector_flange_height) / 2
                ])
                    cube([
                        connector_flange_width,
                        connector_flange_thickness,
                        connector_flange_height
                    ]);

                translate([
                    (case_width - connector_body_width) / 2,
                    connector_flange_thickness,
                    (case_height - connector_body_height) / 2
                ])
                    cube([
                        connector_body_width,
                        connector_rear_projection - connector_flange_thickness,
                        connector_body_height
                    ]);
            }

            for (x = mounting_x_positions)
                translate([x, -epsilon, mounting_axis_z])
                    rotate([-90, 0, 0])
                        cylinder(
                            h = connector_flange_thickness + 2 * epsilon,
                            d = mounting_screw_clearance_diameter,
                            $fn = 36
                        );
        }

    // Two rows of six solder contacts on the published 2.8 mm pitch.
    for (column = [0 : 5])
        for (row = [-1, 1])
            reference_contact(
                case_width / 2 + (column - 2.5) * 2.8,
                case_height / 2 + row * 1.4
            );
}

module reference_mounting_bolts() {
    for (x = mounting_x_positions)
        color([0.68, 0.68, 0.7]) {
            translate([x, -1.2, mounting_axis_z])
                rotate([-90, 0, 0])
                    cylinder(h = 10.5, d = mounting_thread, $fn = 36);

            translate([x, -1.2, mounting_axis_z])
                rotate([90, 0, 0])
                    cylinder(h = 1.2, d = 3.8, $fn = 36);
        }
}

color([0.82, 0.86, 0.91])
    case_base();

color([0.68, 0.75, 0.84, 0.82])
    case_lid();

reference_connector();
reference_mounting_bolts();
