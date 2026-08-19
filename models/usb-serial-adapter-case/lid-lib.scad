module rounded_db9_face(
    wide_width,
    narrow_width,
    height,
    radius,
    fn = 48
) {
    hull() {
        for (point = [
            [-narrow_width / 2 + radius, -height / 2 + radius],
            [ narrow_width / 2 - radius, -height / 2 + radius],
            [-wide_width / 2 + radius, height / 2 - radius],
            [ wide_width / 2 - radius, height / 2 - radius]
        ])
            translate(point)
                circle(r = radius, $fn = fn);
    }
}

module db9_pattern(
    center,
    face_wide_width,
    face_narrow_width,
    face_height,
    face_radius,
    screw_spacing,
    screw_diameter,
    clearance,
    extrusion_height,
    fn = 48
) {
    translate([center[0], center[1], 0]) {
        linear_extrude(height = extrusion_height)
            rounded_db9_face(
                face_wide_width + 2 * clearance,
                face_narrow_width + 2 * clearance,
                face_height + 2 * clearance,
                face_radius + clearance,
                fn
            );

        for (x = [-screw_spacing / 2, screw_spacing / 2])
            translate([x, 0, 0])
                cylinder(
                    h = extrusion_height,
                    d = screw_diameter + 2 * clearance,
                    $fn = fn
                );
    }
}

module lid(
    size,
    thickness,
    db9_center,
    face_wide_width,
    face_narrow_width,
    face_height,
    face_radius,
    screw_spacing,
    screw_diameter,
    clearance,
    epsilon = 0.01
) {
    difference() {
        cube([size[0], size[1], thickness]);
        translate([0, 0, -epsilon])
            db9_pattern(
                db9_center,
                face_wide_width,
                face_narrow_width,
                face_height,
                face_radius,
                screw_spacing,
                screw_diameter,
                clearance,
                thickness + 2 * epsilon
            );
    }
}
