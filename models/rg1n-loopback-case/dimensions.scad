// Shared dimensions for the RG1N-1-4 loopback case.
// All dimensions are in millimetres.

// Requested finished envelope. The socket face is flush with the front.
case_length = 40;

// Published RG1N-1-4 socket dimensions.
connector_flange_width = 29.4;
connector_flange_height = 12;
connector_flange_thickness = 2.5; // maximum
connector_rear_projection = 12.5; // maximum, behind the mounting face

// Published mounting geometry. The original latch hardware uses these holes.
mounting_hole_spacing = 24.5;
mounting_thread = 2;

// The rear body is not separately dimensioned in the available drawing.
// These conservative defaults are estimated from that drawing and photos.
connector_body_width = 20.5;
connector_body_height = 11;

// Four extrusion lines with a 0.4 mm nozzle.
wall = 1.6;
back_wall = 1.6;

// FDM fit allowances, applied on each side unless noted otherwise.
flange_clearance = 0.2;
body_clearance = 0.3;

flange_pocket_width = connector_flange_width + 2 * flange_clearance;
flange_pocket_height = connector_flange_height + 2 * flange_clearance;
flange_pocket_depth = connector_flange_thickness + 0.3;

body_cavity_width = connector_body_width + 2 * body_clearance;
body_cavity_height = connector_body_height + 2 * body_clearance;
body_cavity_end = connector_rear_projection + 1.0;

// The wire chamber opens up behind the solder terminals.
wire_cavity_width = flange_pocket_width;
wire_cavity_height = 14;

case_width = wire_cavity_width + 2 * wall;
case_height = wire_cavity_height + 2 * wall;
// A deeper lower half keeps the longitudinal screw and nut features out of
// the seam while still leaving the connector easy to place from above.
split_height = case_height - 5.6;
corner_radius = 2.4;

// M2 bolts through the connector engage captive standard M2 hex nuts.
mounting_boss_diameter = 6;
mounting_boss_start = flange_pocket_depth;
mounting_boss_end = 11.5;
mounting_screw_clearance_diameter = 2.4;
mounting_nut_across_corners = 4.9;
mounting_nut_pocket_length = 2;
mounting_nut_center_y = 8.4;
mounting_axis_z = case_height / 2;
mounting_x_positions = [
    case_width / 2 - mounting_hole_spacing / 2,
    case_width / 2 + mounting_hole_spacing / 2
];

// Four vertical pins align and lightly retain the lid.
boss_diameter = 4;
pin_diameter = 2.4;
pin_height = 2.4;
pin_hole_diameter = 2.8;
pin_hole_depth = 2.8;
pin_x_positions = [wall + boss_diameter / 2 - 0.4,
                   case_width - wall - boss_diameter / 2 + 0.4];
pin_y_positions = [19, 34.5];

epsilon = 0.01;
