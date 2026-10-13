// Shared bottom-case leg mounting interface
// Units: millimeters

leg_hole_edge_offset = 15;
leg_hole_diameter = 3.5;
leg_counterbore_diameter = 5;
leg_counterbore_depth = 1.5;
leg_boss_diameter = 7;
leg_boss_height = 1.5;
leg_through_hole_depth = 4.5;
leg_hole_segments = 128;

module leg_mount_positions(
    outside_width,
    outside_depth
) {
    for (
        x = [
            leg_hole_edge_offset,
            outside_width - leg_hole_edge_offset
        ],
        y = [
            leg_hole_edge_offset,
            outside_depth - leg_hole_edge_offset
        ]
    ) {
        translate([x, y, 0])
            children();
    }
}
