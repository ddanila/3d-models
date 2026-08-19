// Shared dimensions for the case, lid, and assembly preview.

// PCB dimensions.
pcb_length = 65; // USB edge to DB9 edge; confirmed
pcb_width = 35;  // confirmed
pcb_thickness = 1.6;
width_clearance = 0.8;

// Cross-section viewed from the USB end.
underboard_clearance = 2;
component_height = 13; // estimated PCB top to tallest component
component_clearance = 0.5;

// Case dimensions. A 1.6 mm wall is four lines with a 0.4 mm nozzle.
wall = 1.6;
bottom_thickness = 1.6;
top_clearance = 0.5;

// Distance the USB-B shell extends beyond the PCB edge.
usb_projection = 6.5;

// USB-B opening in the closed bottom, viewed from the connector end.
usb_opening_width = 13.5;
usb_opening_depth = 12.5;
usb_opening_below_pcb_top = 0.5;

// Side ribs overlap only this much of each PCB edge.
guide_contact_width = 0.8;

// Flat DB9-end lid. Measurements are derived from the straight-on product
// photo and the connector's 25 mm screw spacing; verify after a fit test.
lid_thickness = 1.6;
db9_face_wide_width = 18.6;
db9_face_narrow_width = 16.2;
db9_face_height = 9.5;
db9_face_corner_radius = 1;
db9_screw_spacing = 25;
db9_screw_boss_diameter = 4.8;
db9_fit_clearance = 0.25;
db9_center_above_pcb_top = 6.5;

epsilon = 0.01;

inner_width = pcb_width + 2 * width_clearance;
inner_depth = underboard_clearance
    + pcb_thickness
    + component_height
    + component_clearance;
outer_width = inner_width + 2 * wall;
outer_depth = inner_depth + 2 * wall;
case_height = usb_projection + pcb_length + top_clearance;

pcb_x = wall + width_clearance;
pcb_y = wall + underboard_clearance;
pcb_top_y = pcb_y + pcb_thickness;

db9_center_x = outer_width / 2;
db9_center_y = pcb_top_y + db9_center_above_pcb_top;
