// Five Oral-B toothbrush supports on a flat shelf-mounted base.
// Millimetres. Print with the base flat on the bed.

brush_count = 5;
brush_spacing = 40;
base_thickness = 3.2;
base_width = 36;
end_margin = 27;
corner_radius = 4;
screw_hole_diameter = 4;
screw_end_offset = 7;

base_length = (brush_count - 1) * brush_spacing + 2 * end_margin;
$fn = 96;
epsilon = 0.02;

// Source STL coordinates: pool floor and central support only.
source_center = [0.00103569, 0.02866364];
source_floor_z = -4.337996006;
support_crop_radius = 15;
source_top_z = 13.398708344;
support_height = source_top_z - source_floor_z;

assert(brush_count >= 1 && brush_count == floor(brush_count));
assert(base_thickness > 0 && screw_hole_diameter > 0);
assert(brush_spacing > 2 * support_crop_radius);
assert(base_width > 2 * support_crop_radius);
assert(end_margin - screw_end_offset
       > support_crop_radius + screw_hole_diameter / 2);
assert(screw_end_offset > screw_hole_diameter / 2);

module brush_support() {
    // Retain the original peg shape, taper, rounded tip, and raised foot.
    // Cut away the surrounding pool; embed 0.02 mm into the new base.
    intersection() {
        translate([-source_center[0], -source_center[1], -source_floor_z])
            import("reference/oralb_longer3.stl", convexity = 10);
        translate([0, 0, -epsilon])
            cylinder(r = support_crop_radius,
                     h = support_height + 2 * epsilon);
    }
}

difference() {
    union() {
        linear_extrude(height = base_thickness)
            hull()
                for (x = [corner_radius, base_length - corner_radius])
                    for (y = [corner_radius, base_width - corner_radius])
                        translate([x, y]) circle(r = corner_radius);
        for (i = [0 : brush_count - 1])
            translate([end_margin + i * brush_spacing,
                       base_width / 2, base_thickness])
                brush_support();
    }
    for (x = [screw_end_offset, base_length - screw_end_offset])
        translate([x, base_width / 2, -epsilon])
            cylinder(d = screw_hole_diameter,
                     h = base_thickness + 2 * epsilon);
}
