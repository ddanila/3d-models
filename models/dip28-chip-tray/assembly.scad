// Two loaded trays in their actual stacked positions.
// Reference chip envelopes are preview-only and are not exported.

include <dimensions.scad>
use <tray-lib.scad>

module reference_chip(center, z) {
    // Lead envelope.
    color([0.72, 0.72, 0.72])
        translate([
            center[0] - chip_lead_span / 2,
            center[1] - chip_length / 2,
            z
        ])
            cube([chip_lead_span, chip_length, 0.7]);

    // Conservative package body, including a ceramic UV-window outline.
    color([0.12, 0.12, 0.12])
        translate([
            center[0] - 15.8 / 2,
            center[1] - chip_length / 2,
            z
        ])
            cube([15.8, chip_length, chip_height]);
}

tray();

for (column = [0 : columns - 1])
    for (row = [0 : rows - 1])
        reference_chip(
            pocket_center(column, row),
            bottom_thickness + body_support_height
        );

translate([0, 0, tray_body_height])
    tray();

for (column = [0 : columns - 1])
    for (row = [0 : rows - 1])
        reference_chip(
            pocket_center(column, row),
            tray_body_height
                + bottom_thickness
                + body_support_height
        );
