// Shared dimensions for the four-chip DIP-28 tray.
// All dimensions are in millimetres.

// Worst-case storage envelope. This covers the larger ceramic, windowed
// 2764-style FDIP package as well as the smaller plastic AT28C64B PDIP.
chip_length = 38.10;
chip_lead_span = 18.32;
chip_height = 5.71;

// A little room prevents the leads from catching on the pocket walls.
horizontal_clearance = 0.60; // per side
vertical_clearance = 2.80;

columns = 4;
rows = 1;

// Four extrusion lines for the perimeter and three for the nonstructural
// dividers with a 0.4 mm nozzle.
outer_wall = 1.60;
divider = 1.20;
bottom_thickness = 2.00;

// The package body rests here while the two rows of leads remain suspended.
body_support_width = 11.00;
body_support_length = 28.00;
body_support_height = 0.80;
ejector_hole_diameter = 10.00;

// Four external corner pads keep the locators clear of the chip pockets.
// Conical sockets close progressively and therefore print without supports.
locator_pad_size = 7.20;
locator_pad_radius = locator_pad_size / 2;
locator_diagonal_offset = locator_pad_radius / sqrt(2);
locator_peg_height = 3.00;
locator_peg_diameter = 4.00;
stack_fit_clearance = 0.25;
locator_socket_height = locator_peg_height + stack_fit_clearance;
locator_socket_diameter = locator_peg_diameter
    + 2 * stack_fit_clearance;

epsilon = 0.01;

pocket_length = chip_length + 2 * horizontal_clearance;
pocket_width = chip_lead_span + 2 * horizontal_clearance;
pocket_depth = body_support_height + chip_height + vertical_clearance;

// Chips are parallel, with their narrow sides forming one compact row.
outer_length = 2 * outer_wall
    + columns * pocket_width
    + (columns - 1) * divider;
outer_width = 2 * outer_wall
    + rows * pocket_length
    + (rows - 1) * divider;
locator_overhang = locator_pad_radius
    + locator_diagonal_offset
    - outer_wall;
overall_length = outer_length + 2 * locator_overhang;
overall_width = outer_width + 2 * locator_overhang;
tray_body_height = bottom_thickness + pocket_depth;
tray_total_height = tray_body_height + locator_peg_height;

function pocket_x(column) = outer_wall
    + column * (pocket_width + divider);
function pocket_y(row) = outer_wall
    + row * (pocket_length + divider);
function pocket_center(column, row) = [
    pocket_x(column) + pocket_width / 2,
    pocket_y(row) + pocket_length / 2
];
