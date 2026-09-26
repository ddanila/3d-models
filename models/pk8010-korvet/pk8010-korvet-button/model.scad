// ПК8010 Корвет right-side button. All dimensions are in millimetres.
// Print standing on the closed end, with the bore facing upward.

outer_diameter = 7.6;
wall_thickness = 2;
length = 19;
bore_depth = 14;

bore_diameter = outer_diameter - 2 * wall_thickness;
end_thickness = length - bore_depth;
epsilon = 0.01;
$fn = 128;

assert(bore_diameter > 0 && wall_thickness > 0);
assert(bore_depth > 0 && end_thickness > 0);

difference() {
    cylinder(d = outer_diameter, h = length);
    translate([0, 0, end_thickness])
        cylinder(d = bore_diameter, h = bore_depth + epsilon);
}
