// Корвет ПК8010 ↑/8 keycap, first review prototype. Units: mm.
// +Y points toward the arrow tip; Z=0 is the bottom skirt edge.
// Only the 5.5 x 3.5 socket opening is measured; other values are estimates.
base_width = 17.8;
base_depth = 17.8;
top_width = 12.8;
top_depth = 14.0;
height = 12.0;
// Align the +Y (arrow-tip side) edges: this face is parallel to XZ.
top_offset_y = (base_depth - top_depth) / 2;
top_tilt = 0; // User observation: top is parallel to base in side view.
corner_radius = 0.9;
wall = 1.1;
roof = 1.4;
dish_depth = 0.6;
socket_long = 5.5;
socket_short = 3.5;
socket_clearance = 0; // Total additional opening size, not per side.
socket_rotation = 0; // Long side along X; orientation is provisional.
socket_wall = 1.0;
socket_bottom = 1.0;
socket_depth = 8.0;
rib_thickness = 1.0;
rib_bottom = 7.5;
engrave_legend = true;
legend_depth = 0.35;
$fn = 96;
eps = 0.02;
dish_radius = (top_width * top_width / 4 + dish_depth * dish_depth)
              / (2 * dish_depth);

assert(wall > 0 && roof > legend_depth && dish_depth > 0);
assert(socket_long > 0 && socket_short > 0 && socket_depth > 0);
assert(socket_bottom + socket_depth < height - dish_depth - roof);
assert(top_width > socket_long + 2 * socket_wall + 2 * wall);

module rounded_rectangle(w, d, r) {
    offset(r = r) square([w - 2*r, d - 2*r], center = true);
}

module taper(inset = 0) {
    hull() {
        translate([0, 0, -eps]) linear_extrude(eps)
            rounded_rectangle(base_width - 2*inset,
                              base_depth - 2*inset, corner_radius);
        // Extend the blank above the dish to avoid tangent slivers at its rim.
        translate([0, top_offset_y, height + 0.3]) rotate([top_tilt, 0, 0])
            linear_extrude(eps)
                rounded_rectangle(top_width - 2*inset,
                                  top_depth - 2*inset, corner_radius);
    }
}

// Cylinder scoops a shallow dish across X. Tilt controls front/rear height.
module dish(lower = 0) {
    translate([0, top_offset_y, height - lower])
        rotate([top_tilt, 0, 0])
            translate([0, 0, dish_radius - dish_depth])
                rotate([90, 0, 0])
                    cylinder(r = dish_radius, h = base_depth * 3,
                             center = true, $fn = 512);
}

module exterior() {
    difference() { taper(); dish(); }
}

module cavity() {
    difference() { taper(wall); dish(roof); }
}

module legend() {
    translate([0, top_offset_y, 0]) linear_extrude(height * 2) {
        translate([0, 1.8]) polygon([[-3.8, -2.8], [3.8, -2.8], [0, 3.8]]);
        translate([0, -4.2])
            text("8", size = 2.8, font = "Liberation Sans:style=Bold",
                 halign = "center", valign = "center");
    }
}

difference() {
    union() {
        difference() { exterior(); cavity(); }
        // Clip the tube and upper reinforcing webs to the dished exterior.
        intersection() {
            exterior();
            rotate([0, 0, socket_rotation]) union() {
                translate([0, 0, socket_bottom]) linear_extrude(height)
                    square([socket_long + socket_clearance + 2*socket_wall,
                            socket_short + socket_clearance + 2*socket_wall],
                           center = true);
                translate([0, 0, rib_bottom]) linear_extrude(height) {
                    square([base_width, rib_thickness], center = true);
                    square([rib_thickness, base_depth], center = true);
                }
            }
        }
    }
    rotate([0, 0, socket_rotation])
        translate([0, 0, socket_bottom - eps])
            linear_extrude(socket_depth + eps)
                square([socket_long + socket_clearance,
                        socket_short + socket_clearance], center = true);
    if (engrave_legend) intersection() { legend(); dish(legend_depth); }
    // Make the skirt bottom exactly Z=0.
    translate([-base_width, -base_depth, -1])
        cube([base_width*2, base_depth*2, 1]);
}
