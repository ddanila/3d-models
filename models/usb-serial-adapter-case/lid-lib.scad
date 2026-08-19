module lid(
    size,
    thickness,
    opening_position,
    opening_size,
    epsilon = 0.01
) {
    difference() {
        cube([size[0], size[1], thickness]);
        translate([
            opening_position[0],
            opening_position[1],
            -epsilon
        ])
            cube([
                opening_size[0],
                opening_size[1],
                thickness + 2 * epsilon
            ]);
    }
}
