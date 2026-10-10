// Hand-winding trial mandrel for the photographed Robotron 1715 spring.
// Millimetres. Print grip-down. See README before choosing a diameter.
// 6.4 mm is an unvalidated high-index extrapolation for 0.35 mm music wire,
// NOT a guaranteed tool diameter for a finished 13 mm OD spring.

mandrel_diameter = 6.4; // Change after a short trial using the actual wire.
winding_length = 35;   // Straight cylindrical working length, before tip bevel.
tip_bevel = 0.6;
grip_diameter = 28;     // Hexagon across corners.
grip_height = 6;
anchor_hole_diameter = 1.2; // Vertical through-hole for a wire tail.
anchor_radius = 9;
label_size = 2.5;
label_height = 0.5;

$fn = 192;
epsilon = 0.02;
grip_inradius = grip_diameter * cos(30) / 2;
assert(mandrel_diameter > 2 * tip_bevel && tip_bevel > 0);
assert(winding_length > 0 && grip_height > 0);
assert(anchor_hole_diameter > 0);
assert(anchor_radius - anchor_hole_diameter / 2 > mandrel_diameter / 2 + 1);
assert(anchor_radius + anchor_hole_diameter / 2 < grip_inradius - 1);
assert(mandrel_diameter / 2 < anchor_radius - label_size);

union() {
    difference() {
        cylinder(d = grip_diameter, h = grip_height, $fn = 6);
        translate([anchor_radius, 0, -epsilon])
            cylinder(d = anchor_hole_diameter, h = grip_height + 2 * epsilon);
    }
    // The base overlap ensures one connected printable solid.
    translate([0, 0, grip_height - epsilon])
        cylinder(d = mandrel_diameter, h = winding_length + epsilon);
    translate([0, 0, grip_height + winding_length])
        cylinder(d1 = mandrel_diameter,
                 d2 = mandrel_diameter - 2 * tip_bevel,
                 h = tip_bevel);
    translate([0, -anchor_radius, grip_height - epsilon])
        linear_extrude(height = label_height + epsilon)
            text(str(mandrel_diameter), size = label_size,
                 halign = "center", valign = "center");
}
