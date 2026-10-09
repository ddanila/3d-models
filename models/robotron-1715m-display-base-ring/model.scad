// Robotron 1715M display base protective insert. Dimensions in millimetres.
// Print flat, with either annular face on the bed.
outer_diameter = 175;
wall_thickness = 3; // Radial thickness; inner diameter = 169 mm.
height = 5;

inner_diameter = outer_diameter - 2 * wall_thickness;
epsilon = 0.01;
$fn = 512;

assert(outer_diameter > 0 && wall_thickness > 0 && height > 0);
assert(inner_diameter > 0);

difference() {
    cylinder(d = outer_diameter, h = height);
    translate([0, 0, -epsilon])
        cylinder(d = inner_diameter, h = height + 2 * epsilon);
}
