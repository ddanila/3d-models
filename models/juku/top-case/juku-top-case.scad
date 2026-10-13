// Juku top case
// Units: millimeters

outside_width = 352;
outside_depth = 295;
rear_height = 50;
front_height = 9;
wall_thickness = 3;
slope_starts_from_back = 143;
keyboard_row_front_offset = 27;
keyboard_row_left_offset = 50;
keyboard_row_width = 252;
keyboard_row_depth = 18;
keyboard_row_side_step = 9;
keyboard_row_4_left_shift = 4;
keyboard_row_6_right_shift = 18;
keyboard_row_6_width = 144;
side_wall_chamfer_height = 3;
side_wall_chamfer_width = 2;
side_wall_chamfer_z_overlap = 1;
vent_cut_count = 4;
vent_cut_width = 2;
vent_cut_gap = 3;
side_vent_count = 8;
side_vent_y_gap_from_rear_vents = 22;
side_vent_top_length = 10;
side_vent_side_depth_z = 30;
vent_reinforcement_width = 3;
vent_reinforcement_top_height = 4;
vent_reinforcement_side_depth_x = 7;
vent_reinforcement_z_overlap = 1;
vent_cross_reinforcement_count = 5;
vent_cross_reinforcement_spacing = 60;
vent_cross_reinforcement_width = 2;
rear_side_reinforcement_y_gap = 83;
front_side_reinforcement_y_gap = 95;
front_edge_round_radius = 1;
front_edge_round_segments = 12;
logo_bevel_width = 79;
logo_bevel_depth_y = 15;
logo_bevel_depth_z = 1;
logo_bevel_x_gap_from_top_row = 10;
logo_bevel_y_gap_from_row_5 = 2;
led_hole_x_offset_from_logo = 70;
led_hole_y_offset_from_logo = 11.5;
led_hole_diameter = 6;
led_hole_segments = 96;
led_hole_extra_depth = 6;
switch_access_x_offset_from_logo = 22;
switch_access_width = 44;
switch_access_depth_y = 12;
switch_access_corner_radius = 6;
switch_access_extra_depth = 12;
switch_access_segments = 96;
keyboard_support_outer_diameter = 12;
keyboard_support_hole_diameter = 5;
keyboard_support_height = 9;
// M3 threaded insert pilot depth; tune after selecting the actual insert.
keyboard_support_hole_depth = 7;
keyboard_support_overlap = 1;
keyboard_support_segments = 96;
keyboard_support_top_row_spacing = [100, 95, 100];
keyboard_support_bottom_row_spacing = [80, 135, 80];
keyboard_support_row_spacing_y = 125;
keyboard_support_top_row_gap_from_keyboard = 10;
keyboard_support_x_offset = -1.5;

slope_start_y = outside_depth - slope_starts_from_back;
cut_overlap = 0.01;

assert(wall_thickness > 0);
assert(2 * wall_thickness < outside_width);
assert(2 * wall_thickness < outside_depth);
assert(wall_thickness < front_height);
assert(front_height < rear_height);
assert(slope_starts_from_back > 0);
assert(slope_starts_from_back < outside_depth);
assert(keyboard_row_front_offset > 0);
assert(keyboard_row_left_offset > wall_thickness);
assert(keyboard_row_width > 0);
assert(keyboard_row_depth > 0);
assert(keyboard_row_side_step > 0);
assert(keyboard_row_6_width > 0);
assert(side_wall_chamfer_height > 0);
assert(side_wall_chamfer_width > 0);
assert(side_wall_chamfer_height < front_height);
assert(side_wall_chamfer_width < wall_thickness);
assert(side_wall_chamfer_z_overlap >= 0);
assert(vent_cut_count > 0);
assert(vent_cut_width > 0);
assert(vent_cut_gap > 0);
assert(side_vent_count > 0);
assert(side_vent_y_gap_from_rear_vents > 0);
assert(side_vent_top_length > wall_thickness);
assert(side_vent_side_depth_z > wall_thickness);
assert(side_vent_side_depth_z < rear_height);
assert(vent_reinforcement_width > 0);
assert(vent_reinforcement_top_height > 0);
assert(vent_reinforcement_side_depth_x > wall_thickness);
assert(vent_reinforcement_z_overlap >= 0);
assert(vent_cross_reinforcement_count == 5);
assert(vent_cross_reinforcement_spacing > 0);
assert(vent_cross_reinforcement_width > 0);
assert(rear_side_reinforcement_y_gap > 0);
assert(front_side_reinforcement_y_gap > 0);
assert(front_edge_round_radius > 0);
assert(front_edge_round_radius < front_height);
assert(front_edge_round_segments >= 3);
assert(logo_bevel_width > 0);
assert(logo_bevel_depth_y > 0);
assert(logo_bevel_depth_z > 0);
assert(logo_bevel_depth_z < wall_thickness);
assert(logo_bevel_x_gap_from_top_row >= 0);
assert(logo_bevel_y_gap_from_row_5 >= 0);
assert(led_hole_x_offset_from_logo > 0);
assert(led_hole_y_offset_from_logo > 0);
assert(led_hole_diameter > 0);
assert(led_hole_segments >= 3);
assert(led_hole_extra_depth >= 0);
assert(led_hole_x_offset_from_logo < logo_bevel_width);
assert(led_hole_y_offset_from_logo < logo_bevel_depth_y);
assert(switch_access_x_offset_from_logo >= 0);
assert(switch_access_width > 0);
assert(switch_access_depth_y > 0);
assert(switch_access_corner_radius > 0);
assert(2 * switch_access_corner_radius <= switch_access_depth_y);
assert(switch_access_width >= 2 * switch_access_corner_radius);
assert(switch_access_extra_depth >= 0);
assert(switch_access_segments >= 3);
assert(keyboard_support_outer_diameter > 0);
assert(keyboard_support_hole_diameter > 0);
assert(keyboard_support_hole_diameter < keyboard_support_outer_diameter);
assert(keyboard_support_height > 0);
assert(keyboard_support_hole_depth > 0);
assert(keyboard_support_hole_depth < keyboard_support_height);
assert(keyboard_support_overlap >= 0);
assert(keyboard_support_segments >= 3);
assert(len(keyboard_support_top_row_spacing) == 3);
assert(len(keyboard_support_bottom_row_spacing) == 3);
assert(keyboard_support_row_spacing_y > 0);
assert(keyboard_support_top_row_gap_from_keyboard > 0);
assert(
    switch_access_x_offset_from_logo + switch_access_width
    <= logo_bevel_width
);
assert(switch_access_depth_y <= logo_bevel_depth_y);
assert(
    slope_start_y
    + vent_cut_count * vent_cut_width
    + (vent_cut_count - 1) * vent_cut_gap
    < outside_depth - wall_thickness
);
assert(rear_vent_front_reinforcement_y() > wall_thickness);
assert(front_side_reinforcement_y() > wall_thickness);
assert(
    rear_vent_rear_reinforcement_y() + vent_reinforcement_width
    < outside_depth - wall_thickness
);
assert(
    rear_side_reinforcement_y() + vent_reinforcement_width
    < outside_depth - wall_thickness
);
assert(
    outside_width / 2 - 2 * vent_cross_reinforcement_spacing
    - vent_cross_reinforcement_width / 2
    > wall_thickness
);
assert(
    outside_width / 2 + 2 * vent_cross_reinforcement_spacing
    + vent_cross_reinforcement_width / 2
    < outside_width - wall_thickness
);
assert(
    slope_start_y
    + vent_cut_count * vent_cut_width
    + (vent_cut_count - 1) * vent_cut_gap
    + side_vent_y_gap_from_rear_vents
    + side_vent_count * vent_cut_width
    + (side_vent_count - 1) * vent_cut_gap
    < outside_depth - wall_thickness
);

function top_height_at(y) =
    y < slope_start_y
        ? front_height
            + (rear_height - front_height) * y / slope_start_y
        : rear_height;

function inner_top_height_at(y) = top_height_at(y) - wall_thickness;
function rear_vent_group_depth_y() =
    vent_cut_count * vent_cut_width
    + (vent_cut_count - 1) * vent_cut_gap;
function rear_vent_front_reinforcement_y() =
    slope_start_y - vent_reinforcement_width;
function rear_vent_rear_reinforcement_y() =
    slope_start_y + rear_vent_group_depth_y();
function rear_side_reinforcement_y() =
    rear_vent_rear_reinforcement_y() + rear_side_reinforcement_y_gap;
function front_side_reinforcement_y() =
    rear_vent_front_reinforcement_y() - front_side_reinforcement_y_gap;
function rear_vent_reinforcement_bottom_z() =
    inner_top_height_at(rear_vent_rear_reinforcement_y())
    - vent_reinforcement_top_height;
function row_width(spacing) = spacing[0] + spacing[1] + spacing[2];
function support_row_x_positions(spacing) =
    let(
        x0 = (outside_width - row_width(spacing)) / 2
            + keyboard_support_x_offset
    )
        [
            x0,
            x0 + spacing[0],
            x0 + spacing[0] + spacing[1],
            x0 + spacing[0] + spacing[1] + spacing[2]
        ];
function keyboard_support_top_row_y() =
    keyboard_row_6_y()
    + keyboard_row_depth
    + keyboard_support_top_row_gap_from_keyboard;
function keyboard_support_bottom_row_y() =
    keyboard_support_top_row_y() - keyboard_support_row_spacing_y;
function keyboard_support_slope() =
    (rear_height - front_height) / slope_start_y;
function front_edge_slope() = (rear_height - front_height) / slope_start_y;
function front_edge_round_center_y() = front_edge_round_radius;
function front_edge_round_center_z() =
    let(
        m = front_edge_slope(),
        r = front_edge_round_radius
    )
        front_height + m * r - r * sqrt(m * m + 1);
function front_edge_round_top_y() =
    let(
        m = front_edge_slope(),
        r = front_edge_round_radius,
        cz = front_edge_round_center_z(),
        n = m * r - cz + front_height
    )
        r - m * n / (m * m + 1);
function front_edge_round_top_z() =
    let(
        m = front_edge_slope(),
        r = front_edge_round_radius,
        cz = front_edge_round_center_z(),
        n = m * r - cz + front_height
    )
        cz + n / (m * m + 1);
function front_edge_round_top_angle() =
    atan2(
        front_edge_round_top_z() - front_edge_round_center_z(),
        front_edge_round_top_y() - front_edge_round_center_y()
    );
function front_edge_round_points() = [
    for (i = [0 : front_edge_round_segments])
        let(
            a =
                front_edge_round_top_angle()
                + (180 - front_edge_round_top_angle())
                    * i / front_edge_round_segments
        )
            [
                front_edge_round_center_y()
                    + front_edge_round_radius * cos(a),
                front_edge_round_center_z()
                    + front_edge_round_radius * sin(a)
            ]
];

function keyboard_row_1_x() = keyboard_row_left_offset;
function keyboard_row_2_x() = keyboard_row_1_x() - keyboard_row_side_step;
function keyboard_row_3_x() = keyboard_row_2_x() - keyboard_row_side_step;
function keyboard_row_4_x() = keyboard_row_3_x() - keyboard_row_4_left_shift;
function keyboard_row_5_x() = keyboard_row_4_x() + keyboard_row_side_step;
function keyboard_row_6_x() = keyboard_row_5_x() + keyboard_row_6_right_shift;

function keyboard_row_1_y() = keyboard_row_front_offset;
function keyboard_row_2_y() = keyboard_row_1_y() + keyboard_row_depth;
function keyboard_row_3_y() = keyboard_row_2_y() + keyboard_row_depth;
function keyboard_row_4_y() = keyboard_row_3_y() + keyboard_row_depth;
function keyboard_row_5_y() = keyboard_row_4_y() + keyboard_row_depth;
function keyboard_row_6_y() = keyboard_row_5_y() + keyboard_row_depth;

function logo_bevel_x() =
    keyboard_row_6_x()
    + keyboard_row_6_width
    + logo_bevel_x_gap_from_top_row;
function logo_bevel_y() =
    keyboard_row_5_y()
    + keyboard_row_depth
    + logo_bevel_y_gap_from_row_5;

module shell_profile_2d() {
    polygon([
        [0, 0],
        [wall_thickness, 0],
        [wall_thickness, inner_top_height_at(wall_thickness)],
        [slope_start_y, inner_top_height_at(slope_start_y)],
        [
            outside_depth - wall_thickness,
            inner_top_height_at(outside_depth - wall_thickness)
        ],
        [outside_depth - wall_thickness, 0],
        [outside_depth, 0],
        [outside_depth, rear_height],
        [slope_start_y, rear_height],
        [0, front_height]
    ]);
}

module shell(width) {
    multmatrix([
        [0, 0, 1, 0],
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 0, 1]
    ])
        linear_extrude(height = width)
            shell_profile_2d();
}

module side_wall_profile_2d() {
    polygon([
        [0, 0],
        [outside_depth, 0],
        [outside_depth, inner_top_height_at(outside_depth)],
        [slope_start_y, inner_top_height_at(slope_start_y)],
        [0, inner_top_height_at(0)]
    ]);
}

module side_wall(x) {
    translate([x, 0, 0])
        multmatrix([
            [0, 0, 1, 0],
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 1]
        ])
            linear_extrude(height = wall_thickness)
                side_wall_profile_2d();
}

module side_top_chamfer_fill_segment(x_outer, x_inner, y0, y1) {
    z0 = top_height_at(y0);
    z1 = top_height_at(y1);

    polyhedron(
        points = [
            [x_outer, y0, z0 - side_wall_chamfer_height],
            [x_inner, y0, z0 - side_wall_chamfer_height],
            [x_inner, y0, z0],

            [x_outer, y1, z1 - side_wall_chamfer_height],
            [x_inner, y1, z1 - side_wall_chamfer_height],
            [x_inner, y1, z1]
        ],
        faces = [
            [0, 2, 1],
            [3, 4, 5],
            [0, 3, 5, 2],
            [0, 1, 4, 3],
            [1, 2, 5, 4]
        ]
    );
}

module front_side_chamfer_cut(x_outer, x_inner) {
    translate([0, 0, -cut_overlap])
        linear_extrude(
            height =
                front_height
                + side_wall_chamfer_z_overlap
                + 2 * cut_overlap
        )
            polygon([
                [x_outer, -cut_overlap],
                [x_inner, -cut_overlap],
                [x_outer, side_wall_chamfer_height]
            ]);
}

module left_side_top_chamfers() {
    side_top_chamfer_fill_segment(
        0,
        side_wall_chamfer_width,
        0,
        slope_start_y
    );
    side_top_chamfer_fill_segment(
        0,
        side_wall_chamfer_width,
        slope_start_y,
        outside_depth
    );
}

module right_side_top_chamfers() {
    translate([outside_width, 0, 0])
        mirror([1, 0, 0])
            left_side_top_chamfers();
}

module side_top_chamfers() {
    left_side_top_chamfers();
    right_side_top_chamfers();
}

module side_wall_chamfer_cuts() {
    front_side_chamfer_cut(
        -cut_overlap,
        side_wall_chamfer_width
    );
    front_side_chamfer_cut(
        outside_width + cut_overlap,
        outside_width - side_wall_chamfer_width
    );
}

module front_edge_round_cut() {
    translate([-cut_overlap, 0, 0])
        multmatrix([
            [0, 0, 1, 0],
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 1]
        ])
            linear_extrude(height = outside_width + 2 * cut_overlap)
                polygon(
                    concat(
                        [
                            [
                                -cut_overlap,
                                front_edge_round_center_z()
                                    - cut_overlap
                            ],
                            [
                                -cut_overlap,
                                front_height + cut_overlap
                            ],
                            [
                                front_edge_round_top_y() + cut_overlap,
                                top_height_at(front_edge_round_top_y())
                                    + cut_overlap
                            ]
                        ],
                        [
                            for (
                                i = [
                                    0 : len(front_edge_round_points()) - 1
                                ]
                            )
                                front_edge_round_points()[i]
                        ],
                        [
                            [
                                -cut_overlap,
                                front_edge_round_center_z()
                                    - cut_overlap
                            ]
                        ]
                    )
                );
}

module keyboard_row_cut(x, y, width) {
    translate([x, y, -cut_overlap])
        cube([
            width,
            keyboard_row_depth,
            rear_height + 2 * cut_overlap
        ]);
}

module keyboard_cutout() {
    row_1_x = keyboard_row_1_x();
    row_1_y = keyboard_row_1_y();
    row_1_width = keyboard_row_width;

    row_2_x = row_1_x - keyboard_row_side_step;
    row_2_y = row_1_y + keyboard_row_depth;
    row_2_width = row_1_width + 2 * keyboard_row_side_step;

    row_3_x = row_2_x - keyboard_row_side_step;
    row_3_y = row_2_y + keyboard_row_depth;
    row_3_width = row_2_width + 2 * keyboard_row_side_step;

    row_4_x = row_3_x - keyboard_row_4_left_shift;
    row_4_y = row_3_y + keyboard_row_depth;
    row_4_width = row_3_width;

    row_5_x = row_4_x + keyboard_row_side_step;
    row_5_y = row_4_y + keyboard_row_depth;
    row_5_width = row_4_width - 2 * keyboard_row_side_step;

    row_6_x = row_5_x + keyboard_row_6_right_shift;
    row_6_y = row_5_y + keyboard_row_depth;

    keyboard_row_cut(row_1_x, row_1_y, row_1_width);
    keyboard_row_cut(row_2_x, row_2_y, row_2_width);
    keyboard_row_cut(row_3_x, row_3_y, row_3_width);
    keyboard_row_cut(row_4_x, row_4_y, row_4_width);
    keyboard_row_cut(row_5_x, row_5_y, row_5_width);
    keyboard_row_cut(row_6_x, row_6_y, keyboard_row_6_width);
}

module sloped_rect_recess_cut(x, y, width, depth_y, depth_z) {
    x0 = x;
    x1 = x + width;
    y0 = y;
    y1 = y + depth_y;
    z0 = top_height_at(y0);
    z1 = top_height_at(y1);

    polyhedron(
        points = [
            [x0, y0, z0 - depth_z],
            [x1, y0, z0 - depth_z],
            [x1, y1, z1 - depth_z],
            [x0, y1, z1 - depth_z],

            [x0, y0, z0 + cut_overlap],
            [x1, y0, z0 + cut_overlap],
            [x1, y1, z1 + cut_overlap],
            [x0, y1, z1 + cut_overlap]
        ],
        faces = [
            [0, 1, 2, 3],
            [4, 7, 6, 5],
            [0, 4, 5, 1],
            [1, 5, 6, 2],
            [2, 6, 7, 3],
            [3, 7, 4, 0]
        ]
    );
}

module logo_bevel_cut() {
    sloped_rect_recess_cut(
        logo_bevel_x(),
        logo_bevel_y(),
        logo_bevel_width,
        logo_bevel_depth_y,
        logo_bevel_depth_z
    );
}

module led_hole_cut() {
    led_x = logo_bevel_x() + led_hole_x_offset_from_logo;
    led_y = logo_bevel_y() + led_hole_y_offset_from_logo;

    translate([
        led_x,
        led_y,
        inner_top_height_at(led_y) - led_hole_extra_depth - cut_overlap
    ])
        cylinder(
            h =
                wall_thickness
                + led_hole_extra_depth
                + 2 * cut_overlap,
            d = led_hole_diameter,
            $fn = led_hole_segments
        );
}

module switch_access_2d() {
    hull() {
        translate([
            switch_access_corner_radius,
            switch_access_depth_y / 2
        ])
            circle(
                r = switch_access_corner_radius,
                $fn = switch_access_segments
            );

        translate([
            switch_access_width - switch_access_corner_radius,
            switch_access_depth_y / 2
        ])
            circle(
                r = switch_access_corner_radius,
                $fn = switch_access_segments
            );
    }
}

module switch_access_cut() {
    switch_x = logo_bevel_x() + switch_access_x_offset_from_logo;
    switch_y =
        logo_bevel_y()
        + (logo_bevel_depth_y - switch_access_depth_y) / 2;
    switch_cut_bottom =
        inner_top_height_at(switch_y) - switch_access_extra_depth
        - cut_overlap;
    switch_cut_top =
        top_height_at(switch_y + switch_access_depth_y) + cut_overlap;

    translate([
        switch_x,
        switch_y,
        switch_cut_bottom
    ])
        linear_extrude(
            height = switch_cut_top - switch_cut_bottom
        )
            switch_access_2d();
}

module vent_cut(y) {
    translate([
        -cut_overlap,
        y,
        inner_top_height_at(y) - cut_overlap
    ])
        cube([
            outside_width + 2 * cut_overlap,
            vent_cut_width,
            wall_thickness + 2 * cut_overlap
        ]);
}

module ventilation_cutouts() {
    for (i = [0 : vent_cut_count - 1])
        vent_cut(
            slope_start_y + i * (vent_cut_width + vent_cut_gap)
        );
}

module left_side_vent_cut(y) {
    top_z = top_height_at(y);

    translate([
        -cut_overlap,
        y,
        top_z - side_vent_side_depth_z
    ])
        cube([
            wall_thickness + 2 * cut_overlap,
            vent_cut_width,
            side_vent_side_depth_z + cut_overlap
        ]);

    translate([
        -cut_overlap,
        y,
        inner_top_height_at(y) - cut_overlap
    ])
        cube([
            side_vent_top_length + cut_overlap,
            vent_cut_width,
            wall_thickness + 2 * cut_overlap
        ]);
}

module right_side_vent_cut(y) {
    translate([outside_width, 0, 0])
        mirror([1, 0, 0])
            left_side_vent_cut(y);
}

module side_ventilation_cutouts() {
    for (i = [0 : side_vent_count - 1]) {
        y =
            slope_start_y
            + vent_cut_count * vent_cut_width
            + (vent_cut_count - 1) * vent_cut_gap
            + side_vent_y_gap_from_rear_vents
            + i * (vent_cut_width + vent_cut_gap);

        left_side_vent_cut(y);
        right_side_vent_cut(y);
    }
}

module rear_vent_reinforcement(y) {
    top_z = inner_top_height_at(y);
    bottom_z = rear_vent_reinforcement_bottom_z();

    translate([
        wall_thickness,
        y,
        bottom_z
    ])
        cube([
            outside_width - 2 * wall_thickness,
            vent_reinforcement_width,
            top_z - bottom_z + vent_reinforcement_z_overlap
        ]);

    translate([
        wall_thickness,
        y,
        0
    ])
        cube([
            vent_reinforcement_side_depth_x,
            vent_reinforcement_width,
            top_z
        ]);

    translate([
        outside_width - wall_thickness - vent_reinforcement_side_depth_x,
        y,
        0
    ])
        cube([
            vent_reinforcement_side_depth_x,
            vent_reinforcement_width,
            top_z
        ]);
}

module rear_vent_reinforcements() {
    rear_vent_reinforcement(rear_vent_front_reinforcement_y());
    rear_vent_reinforcement(rear_vent_rear_reinforcement_y());
}

module side_wall_reinforcement_pair(y) {
    top_z = inner_top_height_at(y);
    rear_top_z = inner_top_height_at(y + vent_reinforcement_width);

    translate([
        wall_thickness,
        y,
        0
    ])
        cube([
            vent_reinforcement_side_depth_x,
            vent_reinforcement_width,
            max(top_z, rear_top_z) + vent_reinforcement_z_overlap
        ]);

    translate([
        outside_width - wall_thickness - vent_reinforcement_side_depth_x,
        y,
        0
    ])
        cube([
            vent_reinforcement_side_depth_x,
            vent_reinforcement_width,
            max(top_z, rear_top_z) + vent_reinforcement_z_overlap
        ]);
}

module rear_side_reinforcements() {
    side_wall_reinforcement_pair(rear_side_reinforcement_y());
}

module front_side_reinforcements() {
    side_wall_reinforcement_pair(front_side_reinforcement_y());
}

module rear_vent_cross_reinforcement(x) {
    y = rear_vent_front_reinforcement_y();
    depth_y =
        rear_vent_rear_reinforcement_y()
        + vent_reinforcement_width
        - rear_vent_front_reinforcement_y();
    bottom_z = rear_vent_reinforcement_bottom_z();
    top_z = inner_top_height_at(rear_vent_rear_reinforcement_y());

    translate([
        x - vent_cross_reinforcement_width / 2,
        y,
        bottom_z
    ])
        cube([
            vent_cross_reinforcement_width,
            depth_y,
            top_z - bottom_z + vent_reinforcement_z_overlap
        ]);
}

module rear_vent_cross_reinforcements() {
    for (i = [-2 : 2])
        rear_vent_cross_reinforcement(
            outside_width / 2 + i * vent_cross_reinforcement_spacing
        );
}

module keyboard_support(x, y) {
    slope = keyboard_support_slope();
    support_top_center_z = inner_top_height_at(y);
    support_bottom_center_z = support_top_center_z - keyboard_support_height;
    support_radius = keyboard_support_outer_diameter / 2;
    support_start_z =
        support_bottom_center_z - slope * support_radius - cut_overlap;
    support_end_z =
        support_top_center_z + slope * support_radius
        + keyboard_support_overlap;

    difference() {
        intersection() {
            translate([x, y, support_start_z])
                cylinder(
                    h = support_end_z - support_start_z,
                    d = keyboard_support_outer_diameter,
                    $fn = keyboard_support_segments
                );

            polyhedron(
                points = [
                    [
                        x - support_radius - cut_overlap,
                        y - support_radius - cut_overlap,
                        support_bottom_center_z
                            - slope * support_radius
                            - cut_overlap
                    ],
                    [
                        x + support_radius + cut_overlap,
                        y - support_radius - cut_overlap,
                        support_bottom_center_z
                            - slope * support_radius
                            - cut_overlap
                    ],
                    [
                        x + support_radius + cut_overlap,
                        y + support_radius + cut_overlap,
                        support_bottom_center_z
                            + slope * support_radius
                            - cut_overlap
                    ],
                    [
                        x - support_radius - cut_overlap,
                        y + support_radius + cut_overlap,
                        support_bottom_center_z
                            + slope * support_radius
                            - cut_overlap
                    ],

                    [
                        x - support_radius - cut_overlap,
                        y - support_radius - cut_overlap,
                        support_top_center_z
                            - slope * support_radius
                            + keyboard_support_overlap
                    ],
                    [
                        x + support_radius + cut_overlap,
                        y - support_radius - cut_overlap,
                        support_top_center_z
                            - slope * support_radius
                            + keyboard_support_overlap
                    ],
                    [
                        x + support_radius + cut_overlap,
                        y + support_radius + cut_overlap,
                        support_top_center_z
                            + slope * support_radius
                            + keyboard_support_overlap
                    ],
                    [
                        x - support_radius - cut_overlap,
                        y + support_radius + cut_overlap,
                        support_top_center_z
                            + slope * support_radius
                            + keyboard_support_overlap
                    ]
                ],
                faces = [
                    [0, 1, 2, 3],
                    [4, 7, 6, 5],
                    [0, 4, 5, 1],
                    [1, 5, 6, 2],
                    [2, 6, 7, 3],
                    [3, 7, 4, 0]
                ]
            );
        }

        translate([x, y, support_start_z - cut_overlap])
            cylinder(
                h =
                    keyboard_support_hole_depth
                    + 2 * slope * support_radius
                    + 2 * cut_overlap,
                d = keyboard_support_hole_diameter,
                $fn = keyboard_support_segments
            );
    }
}

module keyboard_supports() {
    for (x = support_row_x_positions(keyboard_support_top_row_spacing))
        keyboard_support(x, keyboard_support_top_row_y());

    for (x = support_row_x_positions(keyboard_support_bottom_row_spacing))
        keyboard_support(x, keyboard_support_bottom_row_y());
}

module top_case() {
    difference() {
        union() {
            translate([side_wall_chamfer_width, 0, 0])
                shell(outside_width - 2 * side_wall_chamfer_width);
            side_wall(0);
            side_wall(outside_width - wall_thickness);
            side_top_chamfers();
            rear_vent_reinforcements();
            front_side_reinforcements();
            rear_side_reinforcements();
            rear_vent_cross_reinforcements();
            keyboard_supports();
        }

        front_edge_round_cut();
        side_wall_chamfer_cuts();
        keyboard_cutout();
        logo_bevel_cut();
        led_hole_cut();
        switch_access_cut();
        ventilation_cutouts();
        side_ventilation_cutouts();
    }
}

top_case();
