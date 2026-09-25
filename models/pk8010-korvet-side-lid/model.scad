// ПК8010 Корвет small right-side lid. All dimensions are in millimetres.
// Print with the broad base on the bed.

base_length = 154;
base_width = 26;
base_thickness = 1;
upper_length = 150;
upper_width = 22;
upper_height = 3;
button_hole_diameter = 10;
button_hole_from_right = 23;
button_hole_from_bottom = 10;
groove_from_bottom = 10;
groove_width = 2;
groove_depth = 1;
right_groove_length = 7;
left_groove_length = 113;
finger_recess_width = 25;
finger_recess_height = 17;
finger_recess_depth = 1;

upper_left = (base_length - upper_length) / 2;
upper_right = (base_length + upper_length) / 2;
epsilon = 0.01;
$fn = 128;

assert(base_length >= upper_length && base_width >= upper_width);
assert(upper_length > 0 && upper_width > 0);
assert(base_thickness > 0 && upper_height > 0);
assert(groove_depth > 0 && groove_depth < upper_height);
assert(finger_recess_width > button_hole_diameter
       && finger_recess_height > button_hole_diameter);
assert(finger_recess_depth > 0 && finger_recess_depth < upper_height);

difference() {
    union() {
        cube([base_length, base_width, base_thickness]);
        translate([
            (base_length - upper_length) / 2,
            (base_width - upper_width) / 2,
            base_thickness
        ])
            cube([upper_length, upper_width, upper_height]);
    }
    // Offsets are measured from the outer base edges in top view.
    translate([base_length - button_hole_from_right,
               button_hole_from_bottom, -epsilon])
        cylinder(d = button_hole_diameter,
                 h = base_thickness + upper_height + 2 * epsilon);

    // Gradual circular-to-oval recess, deepest at the through-hole rim.
    translate([base_length - button_hole_from_right,
               button_hole_from_bottom,
               base_thickness + upper_height - finger_recess_depth]) {
        linear_extrude(height = finger_recess_depth,
                       scale = [finger_recess_width / button_hole_diameter,
                                finger_recess_height / button_hole_diameter])
            circle(d = button_hole_diameter);
        translate([0, 0, finger_recess_depth])
            linear_extrude(height = epsilon)
                scale([finger_recess_width / button_hole_diameter,
                       finger_recess_height / button_hole_diameter])
                    circle(d = button_hole_diameter);
    }

    // Short groove opens at the raised section's right edge.
    translate([upper_right - right_groove_length,
               groove_from_bottom - groove_width / 2,
               base_thickness + upper_height - groove_depth])
        cube([right_groove_length + epsilon, groove_width,
              groove_depth + epsilon]);

    // Long groove opens at the raised section's left edge.
    translate([upper_left - epsilon,
               groove_from_bottom - groove_width / 2,
               base_thickness + upper_height - groove_depth])
        cube([left_groove_length + epsilon,
              groove_width, groove_depth + epsilon]);
}
