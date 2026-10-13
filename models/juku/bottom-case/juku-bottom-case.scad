// Juku bottom case
// Units: millimeters

include <leg-interface.scad>

outside_width = 340;
outside_depth = 290;
outside_height = 18;
case_thickness = 3;
bottom_chamfer = 8;
top_edge_chamfer = 3;
rear_pcb_opening_width = 300;
rear_pcb_opening_height = 12;
pcb_support_hole_diameter = 3.5;
pcb_support_boss_diameter = 12;
pcb_support_boss_height = 3;
pcb_support_nut_across_flats = 6;
pcb_support_nut_depth = 3;
pcb_support_segments = 128;
pcb_support_outer_x = [25, outside_width - 25];
pcb_support_rear_x = [25, 129, 233, outside_width - 25];
pcb_support_front_x = [25, 120, 215, outside_width - 25];
pcb_support_rear_y = outside_depth - 18;
pcb_support_middle_y = pcb_support_rear_y - 120;
pcb_support_front_y = pcb_support_middle_y - 120;
lid_mount_edge_offset = 7;
lid_mount_end_offset = 25;
lid_mount_hole_diameter = 3;
lid_mount_boss_diameter = 13;
lid_mount_boss_height = 7;
lid_mount_recess_diameter = 8;
lid_mount_recess_depth = 6.5;
lid_mount_segments = 128;
logo_plaque_width = 30;
logo_plaque_depth = 10;
logo_plaque_front_offset = 50;
logo_plaque_depth_into_case = 0.6;
logo_height = 0.6;
logo_margin = 1.2;
logo_dxf_min_x = -0.4367642811194372;
logo_dxf_min_y = -2;
logo_dxf_width = 29.39264521818426 - logo_dxf_min_x;
logo_dxf_depth = 6 - logo_dxf_min_y;
logo_scale = min(
    (logo_plaque_width - 2 * logo_margin) / logo_dxf_width,
    (logo_plaque_depth - 2 * logo_margin) / logo_dxf_depth
);
logo_width = logo_dxf_width * logo_scale;
logo_depth = logo_dxf_depth * logo_scale;
logo_plaque_x = (outside_width - logo_plaque_width) / 2;
logo_plaque_y = logo_plaque_front_offset;
logo_x = logo_plaque_x + (logo_plaque_width - logo_width) / 2;
logo_y = logo_plaque_y + (logo_plaque_depth - logo_depth) / 2;
serial_plate_recess_width = 30;
serial_plate_recess_depth = 20;
serial_plate_recess_gap = 20;
serial_plate_recess_depth_into_case = logo_plaque_depth_into_case;
serial_plate_recess_x =
    (outside_width - serial_plate_recess_width) / 2;
serial_plate_recess_y =
    logo_plaque_y + logo_plaque_depth + serial_plate_recess_gap;
rear_outer_rail_depth = 4;
rear_rail_gap = 2;
rear_inner_rail_depth = 3;
rear_inner_rail_length = rear_pcb_opening_width + 2 * case_thickness;
rear_outer_rail_length = rear_inner_rail_length + 2 * case_thickness;
rear_rail_base_z = case_thickness;
rear_rail_height = outside_height - rear_rail_base_z;
rear_rail_end_length = (rear_outer_rail_length - rear_inner_rail_length) / 2;
rear_guide_y_offset = case_thickness;

cut_overlap = 0.01;
inner_chamfer_offset = case_thickness * sqrt(2);
inner_chamfer_end_z = bottom_chamfer + inner_chamfer_offset;
rear_pcb_opening_x = (outside_width - rear_pcb_opening_width) / 2;
rear_pcb_opening_z = outside_height - rear_pcb_opening_height;
rear_inner_rail_x = (outside_width - rear_inner_rail_length) / 2;
rear_outer_rail_x = (outside_width - rear_outer_rail_length) / 2;
rear_outer_rail_y =
    outside_depth - case_thickness - rear_outer_rail_depth
    + rear_guide_y_offset;
rear_inner_rail_y =
    rear_outer_rail_y - rear_rail_gap - rear_inner_rail_depth;

assert(case_thickness > 0);
assert(2 * case_thickness < outside_width);
assert(2 * case_thickness < outside_depth);
assert(case_thickness < outside_height);
assert(bottom_chamfer > 0);
assert(inner_chamfer_end_z < outside_height);
assert(top_edge_chamfer > 0);
assert(top_edge_chamfer <= case_thickness);
assert(bottom_chamfer < outside_height - top_edge_chamfer);
assert(rear_pcb_opening_width > 0);
assert(rear_pcb_opening_width < outside_width);
assert(rear_pcb_opening_height > 0);
assert(rear_pcb_opening_height < outside_height);
assert(leg_hole_edge_offset > bottom_chamfer);
assert(leg_hole_diameter > 0);
assert(leg_counterbore_diameter > leg_hole_diameter);
assert(leg_counterbore_depth > 0);
assert(leg_counterbore_depth < case_thickness);
assert(leg_boss_diameter >= leg_hole_diameter);
assert(leg_boss_height > 0);
assert(leg_through_hole_depth == case_thickness + leg_boss_height);
assert(leg_hole_segments >= 3);
assert(pcb_support_hole_diameter > 0);
assert(pcb_support_boss_diameter > pcb_support_hole_diameter);
assert(pcb_support_boss_height > 0);
assert(pcb_support_nut_across_flats > pcb_support_hole_diameter);
assert(pcb_support_nut_depth > 0);
assert(pcb_support_nut_depth <= case_thickness);
assert(pcb_support_segments >= 3);
assert(pcb_support_front_y > 0);
assert(lid_mount_edge_offset > 0);
assert(lid_mount_edge_offset < bottom_chamfer);
assert(lid_mount_end_offset > 0);
assert(lid_mount_hole_diameter > 0);
assert(lid_mount_boss_diameter > lid_mount_hole_diameter);
assert(lid_mount_boss_height > 0);
assert(lid_mount_recess_diameter > lid_mount_hole_diameter);
assert(lid_mount_recess_depth > case_thickness);
assert(lid_mount_segments >= 3);
assert(logo_plaque_width > 0);
assert(logo_plaque_depth > 0);
assert(logo_plaque_front_offset > bottom_chamfer);
assert(logo_plaque_depth_into_case > 0);
assert(logo_height > 0);
assert(logo_height <= logo_plaque_depth_into_case);
assert(logo_margin >= 0);
assert(2 * logo_margin < logo_plaque_width);
assert(2 * logo_margin < logo_plaque_depth);
assert(serial_plate_recess_width > 0);
assert(serial_plate_recess_depth > 0);
assert(serial_plate_recess_gap >= 0);
assert(serial_plate_recess_depth_into_case > 0);
assert(
    serial_plate_recess_y + serial_plate_recess_depth
    < outside_depth - bottom_chamfer
);
assert(rear_outer_rail_depth > 0);
assert(rear_rail_gap > 0);
assert(rear_inner_rail_depth > 0);
assert(rear_inner_rail_length < outside_width);
assert(rear_outer_rail_length < outside_width);
assert(rear_rail_base_z + rear_rail_height <= outside_height);
assert(rear_rail_base_z < rear_pcb_opening_z);
assert(rear_rail_end_length > 0);

module section(width, depth, x, y, z) {
    translate([x, y, z])
        cube([width, depth, cut_overlap]);
}

module outside_shape() {
    hull() {
        section(
            outside_width - 2 * bottom_chamfer,
            outside_depth - bottom_chamfer,
            bottom_chamfer,
            bottom_chamfer,
            0
        );

        section(outside_width, outside_depth, 0, 0, bottom_chamfer);
        section(
            outside_width,
            outside_depth,
            0,
            0,
            outside_height - top_edge_chamfer
        );
        section(
            outside_width - 2 * top_edge_chamfer,
            outside_depth - 2 * top_edge_chamfer,
            top_edge_chamfer,
            top_edge_chamfer,
            outside_height
        );
    }
}

module inside_cutout() {
    lower_inset = bottom_chamfer + inner_chamfer_offset - case_thickness;

    hull() {
        section(
            outside_width - 2 * lower_inset,
            outside_depth - lower_inset - case_thickness,
            lower_inset,
            lower_inset,
            case_thickness
        );

        section(
            outside_width - 2 * case_thickness,
            outside_depth - 2 * case_thickness,
            case_thickness,
            case_thickness,
            inner_chamfer_end_z
        );

        section(
            outside_width - 2 * case_thickness,
            outside_depth - 2 * case_thickness,
            case_thickness,
            case_thickness,
            outside_height + cut_overlap
        );
    }
}

module rear_pcb_opening() {
    translate([
        rear_pcb_opening_x,
        rear_inner_rail_y - cut_overlap,
        rear_pcb_opening_z
    ])
        // Over-cut past the top rim (+cut_overlap) so the opening clears the
        // top-edge chamfer instead of leaving a thin remnant on its edge.
        cube([
            rear_pcb_opening_width,
            outside_depth - rear_inner_rail_y + 2 * cut_overlap,
            rear_pcb_opening_height + cut_overlap
        ]);
}

module rear_pcb_guide_rails() {
    translate([
        rear_outer_rail_x,
        rear_outer_rail_y,
        rear_rail_base_z
    ])
        cube([
            rear_outer_rail_length,
            rear_outer_rail_depth,
            rear_rail_height
        ]);

    translate([
        rear_inner_rail_x,
        rear_inner_rail_y,
        rear_rail_base_z
    ])
        cube([
            rear_inner_rail_length,
            rear_inner_rail_depth,
            rear_rail_height
        ]);

    for (x = [rear_outer_rail_x, rear_inner_rail_x + rear_inner_rail_length]) {
        translate([
            x,
            rear_inner_rail_y,
            rear_rail_base_z
        ])
            cube([
                rear_rail_end_length,
                rear_outer_rail_y + rear_outer_rail_depth - rear_inner_rail_y,
                rear_rail_height
            ]);
    }
}

module rear_top_edge_chamfer_cut() {
    translate([-cut_overlap, 0, 0])
        multmatrix([
            [0, 0, 1, 0],
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 1]
        ])
            linear_extrude(height = outside_width + 2 * cut_overlap)
                polygon([
                    [
                        outside_depth - top_edge_chamfer,
                        outside_height
                    ],
                    [
                        outside_depth,
                        outside_height - top_edge_chamfer
                    ],
                    [
                        outside_depth,
                        outside_height
                    ]
                ]);
}

module leg_hole_bosses() {
    leg_mount_positions(outside_width, outside_depth)
        translate([0, 0, case_thickness])
            cylinder(
                h = leg_boss_height,
                d = leg_boss_diameter,
                $fn = leg_hole_segments
            );
}

module leg_hole_cuts() {
    leg_mount_positions(outside_width, outside_depth) {
        translate([0, 0, -cut_overlap])
            cylinder(
                h = case_thickness + leg_boss_height + 2 * cut_overlap,
                d = leg_hole_diameter,
                $fn = leg_hole_segments
            );

        translate([0, 0, -cut_overlap])
            cylinder(
                h = leg_counterbore_depth + cut_overlap,
                d = leg_counterbore_diameter,
                $fn = leg_hole_segments
            );
    }
}

module pcb_support_positions() {
    for (x = pcb_support_rear_x)
        translate([x, pcb_support_rear_y, 0])
            children();

    for (x = pcb_support_outer_x)
        translate([x, pcb_support_middle_y, 0])
            children();

    for (x = pcb_support_front_x)
        translate([x, pcb_support_front_y, 0])
            children();
}

module pcb_support_bosses() {
    pcb_support_positions()
        translate([0, 0, case_thickness])
            cylinder(
                h = pcb_support_boss_height,
                d = pcb_support_boss_diameter,
                $fn = pcb_support_segments
            );
}

module pcb_support_cuts() {
    nut_radius = pcb_support_nut_across_flats / sqrt(3);

    pcb_support_positions() {
        translate([0, 0, -cut_overlap])
            cylinder(
                h =
                    case_thickness
                    + pcb_support_boss_height
                    + 2 * cut_overlap,
                d = pcb_support_hole_diameter,
                $fn = pcb_support_segments
            );

        translate([0, 0, -cut_overlap])
            rotate([0, 0, 30])
                cylinder(
                    h = pcb_support_nut_depth + cut_overlap,
                    r = nut_radius,
                    $fn = 6
                );
    }
}

module lid_mount_positions() {
    for (
        x = [
            lid_mount_edge_offset,
            outside_width - lid_mount_edge_offset
        ],
        y = [
            lid_mount_end_offset,
            outside_depth - lid_mount_end_offset
        ]
    ) {
        translate([x, y, 0])
            children();
    }

    translate([outside_width / 2, lid_mount_edge_offset, 0])
        children();
}

module lid_mount_recess_2d(direction) {
    projection_length = lid_mount_edge_offset + cut_overlap;

    union() {
        circle(d = lid_mount_recess_diameter, $fn = lid_mount_segments);

        if (direction[0] < 0)
            translate([-projection_length / 2, 0])
                square(
                    [projection_length, lid_mount_recess_diameter],
                    center = true
                );
        else if (direction[0] > 0)
            translate([projection_length / 2, 0])
                square(
                    [projection_length, lid_mount_recess_diameter],
                    center = true
                );
        else
            translate([0, -projection_length / 2])
                square(
                    [lid_mount_recess_diameter, projection_length],
                    center = true
                );
    }
}

module lid_mount_boss_2d(direction) {
    projection_length = lid_mount_edge_offset + cut_overlap;

    union() {
        circle(d = lid_mount_boss_diameter, $fn = lid_mount_segments);

        if (direction[0] < 0)
            translate([-projection_length / 2, 0])
                square(
                    [projection_length, lid_mount_boss_diameter],
                    center = true
                );
        else if (direction[0] > 0)
            translate([projection_length / 2, 0])
                square(
                    [projection_length, lid_mount_boss_diameter],
                    center = true
                );
        else
            translate([0, -projection_length / 2])
                square(
                    [lid_mount_boss_diameter, projection_length],
                    center = true
                );
    }
}

module lid_mount_bosses() {
    intersection() {
        outside_shape();

        union() {
            for (
                x = [
                    lid_mount_edge_offset,
                    outside_width - lid_mount_edge_offset
                ],
                y = [
                    lid_mount_end_offset,
                    outside_depth - lid_mount_end_offset
                ]
            ) {
                direction = x < outside_width / 2 ? [-1, 0] : [1, 0];

                translate([x, y, case_thickness])
                    linear_extrude(height = lid_mount_boss_height)
                        lid_mount_boss_2d(direction);
            }

            translate([
                outside_width / 2,
                lid_mount_edge_offset,
                case_thickness
            ])
                linear_extrude(height = lid_mount_boss_height)
                    lid_mount_boss_2d([0, -1]);
        }
    }
}

module lid_mount_cuts() {
    for (
        x = [
            lid_mount_edge_offset,
            outside_width - lid_mount_edge_offset
        ],
        y = [
            lid_mount_end_offset,
            outside_depth - lid_mount_end_offset
        ]
    ) {
        direction = x < outside_width / 2 ? [-1, 0] : [1, 0];

        translate([0, 0, -cut_overlap])
            translate([x, y, 0])
                cylinder(
                    h =
                        case_thickness
                        + lid_mount_boss_height
                        + 2 * cut_overlap,
                    d = lid_mount_hole_diameter,
                    $fn = lid_mount_segments
                );

        translate([x, y, -cut_overlap])
            linear_extrude(height = lid_mount_recess_depth + cut_overlap)
                lid_mount_recess_2d(direction);
    }

    translate([outside_width / 2, lid_mount_edge_offset, -cut_overlap]) {
        cylinder(
            h =
                case_thickness
                + lid_mount_boss_height
                + 2 * cut_overlap,
            d = lid_mount_hole_diameter,
            $fn = lid_mount_segments
        );

        linear_extrude(height = lid_mount_recess_depth + cut_overlap)
            lid_mount_recess_2d([0, -1]);
    }
}

module underside_logo_recess_cut() {
    translate([
        logo_plaque_x,
        logo_plaque_y,
        -cut_overlap
    ])
        linear_extrude(
            height = logo_plaque_depth_into_case + cut_overlap
        )
            difference() {
                square([logo_plaque_width, logo_plaque_depth]);

                translate([
                    logo_x - logo_plaque_x,
                    logo_y - logo_plaque_y + logo_depth
                ])
                    mirror([0, 1, 0])
                        scale([logo_scale, logo_scale])
                            translate([-logo_dxf_min_x, -logo_dxf_min_y])
                            import("estron-logo.dxf");
            }
}

module underside_serial_plate_recess_cut() {
    translate([
        serial_plate_recess_x,
        serial_plate_recess_y,
        -cut_overlap
    ])
        cube([
            serial_plate_recess_width,
            serial_plate_recess_depth,
            serial_plate_recess_depth_into_case + cut_overlap
        ]);
}

module bottom_case() {
    difference() {
        union() {
            difference() {
                outside_shape();
                inside_cutout();
            }

            rear_pcb_guide_rails();
            leg_hole_bosses();
            pcb_support_bosses();
            lid_mount_bosses();
        }

        rear_pcb_opening();
        rear_top_edge_chamfer_cut();
        leg_hole_cuts();
        pcb_support_cuts();
        lid_mount_cuts();
        underside_logo_recess_cut();
        underside_serial_plate_recess_cut();
    }
}

bottom_case();
