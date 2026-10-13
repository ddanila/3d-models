// Juku bottom case with rubber legs installed
// Units: millimeters

include <../bottom-case/leg-interface.scad>

use <../bottom-case/juku-bottom-case.scad>
use <../legs/juku-leg.scad>

outside_width = 340;
outside_depth = 290;

bottom_case();

leg_mount_positions(outside_width, outside_depth)
    juku_leg();
