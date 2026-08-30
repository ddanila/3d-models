include <dimensions.scad>

module rounded_xy_box(size, radius, fn = 48) {
    hull()
        for (x = [radius, size[0] - radius])
            for (y = [radius, size[1] - radius])
                translate([x, y, 0])
                    cylinder(h = size[2], r = radius, $fn = fn);
}

module centered_cavity(width, height, y, length) {
    translate([
        (case_width - width) / 2,
        y,
        (case_height - height) / 2
    ])
        cube([width, length, height]);
}

module hollow_case() {
    difference() {
        rounded_xy_box(
            [case_width, case_length, case_height],
            corner_radius
        );

        // Full flange recess, open at the connector face.
        centered_cavity(
            flange_pocket_width,
            flange_pocket_height,
            -epsilon,
            flange_pocket_depth + epsilon
        );

        // Close-fitting throat around the connector body and terminals.
        centered_cavity(
            body_cavity_width,
            body_cavity_height,
            flange_pocket_depth - epsilon,
            body_cavity_end - flange_pocket_depth + 2 * epsilon
        );

        // Larger chamber for the folded loopback wiring.
        centered_cavity(
            wire_cavity_width,
            wire_cavity_height,
            body_cavity_end - epsilon,
            case_length - back_wall - body_cavity_end + 2 * epsilon
        );
    }
}

module mounting_bosses() {
    union() {
        for (x = mounting_x_positions)
            translate([x, mounting_boss_start, mounting_axis_z])
                rotate([-90, 0, 0])
                    cylinder(
                        h = mounting_boss_end - mounting_boss_start,
                        d = mounting_boss_diameter,
                        $fn = 48
                    );

        // Solid buttresses project both horizontal bosses to the printed
        // floor. Their inner edges stop at the connector-body cavity.
        translate([0, mounting_boss_start, wall])
            cube([
                (case_width - body_cavity_width) / 2,
                mounting_boss_end - mounting_boss_start,
                mounting_axis_z - wall
            ]);

        translate([
            (case_width + body_cavity_width) / 2,
            mounting_boss_start,
            wall
        ])
            cube([
                (case_width - body_cavity_width) / 2,
                mounting_boss_end - mounting_boss_start,
                mounting_axis_z - wall
            ]);
    }
}

module mounting_screw_bores() {
    for (x = mounting_x_positions)
        translate([x, -epsilon, mounting_axis_z])
            rotate([-90, 0, 0])
                cylinder(
                    h = mounting_boss_end + 2 * epsilon,
                    d = mounting_screw_clearance_diameter,
                    $fn = 36
                );
}

module mounting_nut_traps() {
    for (x = mounting_x_positions) {
        // Hexagonal pocket with its axis parallel to the mounting bolt.
        translate([
            x,
            mounting_nut_center_y - mounting_nut_pocket_length / 2,
            mounting_axis_z
        ])
            rotate([-90, 0, 0])
                cylinder(
                    h = mounting_nut_pocket_length,
                    d = mounting_nut_across_corners,
                    $fn = 6
                );

        // Loading slot opens into the lower half before the lid is fitted.
        translate([
            x - mounting_nut_across_corners / 2,
            mounting_nut_center_y - mounting_nut_pocket_length / 2,
            mounting_axis_z
        ])
            cube([
                mounting_nut_across_corners,
                mounting_nut_pocket_length,
                split_height - mounting_axis_z + epsilon
            ]);
    }
}

module mounted_case_shell() {
    difference() {
        union() {
            hollow_case();
            mounting_bosses();
        }

        mounting_screw_bores();
        mounting_nut_traps();
    }
}

module lower_half_volume() {
    translate([-epsilon, -epsilon, -epsilon])
        cube([
            case_width + 2 * epsilon,
            case_length + 2 * epsilon,
            split_height + epsilon
        ]);
}

module upper_half_volume() {
    translate([-epsilon, -epsilon, split_height])
        cube([
            case_width + 2 * epsilon,
            case_length + 2 * epsilon,
            case_height - split_height + epsilon
        ]);
}

module pin_bosses(z, height) {
    for (x = pin_x_positions)
        for (y = pin_y_positions)
            translate([x, y, z])
                cylinder(h = height, d = boss_diameter, $fn = 36);
}

module alignment_pins() {
    for (x = pin_x_positions)
        for (y = pin_y_positions)
            translate([x, y, split_height - epsilon])
                cylinder(
                    h = pin_height + epsilon,
                    d = pin_diameter,
                    $fn = 36
                );
}

module alignment_holes() {
    for (x = pin_x_positions)
        for (y = pin_y_positions)
            translate([x, y, split_height - epsilon])
                cylinder(
                    h = pin_hole_depth + epsilon,
                    d = pin_hole_diameter,
                    $fn = 36
                );
}

module case_base() {
    union() {
        intersection() {
            mounted_case_shell();
            lower_half_volume();
        }

        // The lower boss joins the floor and side wall to support each pin.
        intersection() {
            pin_bosses(wall, split_height - wall);
            lower_half_volume();
        }

        alignment_pins();
    }
}

module case_lid() {
    difference() {
        union() {
            intersection() {
                mounted_case_shell();
                upper_half_volume();
            }

            pin_bosses(
                split_height,
                case_height - wall - split_height
            );
        }

        alignment_holes();
    }
}

module printable_lid() {
    // Put the outer top face on the bed so the cavity prints upward.
    translate([0, case_length, case_height])
        rotate([180, 0, 0])
            case_lid();
}
