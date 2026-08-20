include <dimensions.scad>

function locator_centers() = [
    [
        outer_wall - locator_diagonal_offset,
        outer_wall - locator_diagonal_offset
    ],
    [
        outer_length - outer_wall + locator_diagonal_offset,
        outer_wall - locator_diagonal_offset
    ],
    [
        outer_wall - locator_diagonal_offset,
        outer_width - outer_wall + locator_diagonal_offset
    ],
    [
        outer_length - outer_wall + locator_diagonal_offset,
        outer_width - outer_wall + locator_diagonal_offset
    ]
];

module locator_pads() {
    for (center = locator_centers())
        translate([center[0], center[1], 0])
            cylinder(
                h = tray_body_height,
                d = locator_pad_size,
                $fn = 64
            );
}

module locator_pegs() {
    for (center = locator_centers())
        translate([center[0], center[1], tray_body_height])
            cylinder(
                h = locator_peg_height,
                d1 = locator_peg_diameter,
                d2 = 0,
                $fn = 64
            );
}

module locator_sockets() {
    for (center = locator_centers())
        translate([center[0], center[1], -epsilon])
            cylinder(
                h = locator_socket_height + epsilon,
                d1 = locator_socket_diameter,
                d2 = 0,
                $fn = 64
            );
}

module body_support(center) {
    translate([
        center[0] - body_support_width / 2,
        center[1] - body_support_length / 2,
        bottom_thickness
    ])
        cube([
            body_support_width,
            body_support_length,
            body_support_height
        ]);
}

module tray() {
    difference() {
        union() {
            difference() {
                union() {
                    cube([outer_length, outer_width, tray_body_height]);
                    locator_pads();
                }

                for (column = [0 : columns - 1])
                    for (row = [0 : rows - 1])
                        translate([
                            pocket_x(column),
                            pocket_y(row),
                            bottom_thickness
                        ])
                            cube([
                                pocket_width,
                                pocket_length,
                                pocket_depth + epsilon
                            ]);
            }

            for (column = [0 : columns - 1])
                for (row = [0 : rows - 1])
                    body_support(pocket_center(column, row));

            locator_pegs();
        }

        // A fingertip or blunt tool can push each package out from below.
        for (column = [0 : columns - 1])
            for (row = [0 : rows - 1])
                translate([
                    pocket_center(column, row)[0],
                    pocket_center(column, row)[1],
                    -epsilon
                ])
                    cylinder(
                        h = bottom_thickness
                            + body_support_height
                            + 2 * epsilon,
                        d = ejector_hole_diameter,
                        $fn = 64
                    );

        // Matching tapered sockets for the four pegs below. Their conical
        // ceilings stay within a support-free printing angle.
        locator_sockets();
    }
}
