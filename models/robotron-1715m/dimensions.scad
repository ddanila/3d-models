// Millimetres. Overall envelopes: Robotron manual p.35 (see README).
// Owner confirms painted bent 1 mm sheet for all three enclosures.
// Local feature positions and bend radii remain photo estimates.
case_w = 500; case_d = 400; case_h = 130; seam_z = 36; wall = 1;
// Display envelope includes its pedestal and front bezel.
monitor_w = 320; monitor_d = 334; monitor_h = 280;
monitor_y = 25; monitor_z = case_h + 50;
keyboard_w = 500; keyboard_d = 200; keyboard_y = -355;
keyboard_pitch = 19.0; // Photo-fit within the ruler estimate of 20 +/- 1 mm.
// Owner side-profile measurements, relative to the bottom plate datum.
keyboard_front_height = 15;
keyboard_rear_height = 29;
keyboard_slope_end = 59; // Rear edge of the black panel, photo-fit Y position.
keyboard_slope = atan((keyboard_rear_height-keyboard_front_height)/(keyboard_slope_end+keyboard_d/2));
// Black skirt bottom is local -4, base top -5: preserve their 1 mm gap.
keyboard_deck_z = keyboard_front_height + keyboard_d/2*tan(keyboard_slope) + 5/cos(keyboard_slope);
keyboard_z_shift = keyboard_deck_z-26;
ring_od = 174; ring_id = 167; ring_h = 5; // Danila's measured insert.
$fn = 24;

// Owner underside photos 123319025 / 123907435. Rear stays +Y in both
// views; underside images reverse X. Positions are photo estimates.
keyboard_cable_x = -80; keyboard_cable_y = 55;
keyboard_support_x = keyboard_cable_x+21;
keyboard_controller_x = 95; keyboard_controller_y = 46.6;
keyboard_controller_z = 5.5;
keyboard_cable_z = keyboard_controller_z+4.5;
