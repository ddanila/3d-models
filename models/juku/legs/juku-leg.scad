// Juku bottom-case rubber leg
// Units: millimeters

include <../bottom-case/leg-interface.scad>

leg_outer_diameter = 10;
leg_outer_height = 3;
leg_counterbore_plug_diameter = 5;
leg_counterbore_plug_height = 1.5;
leg_stem_diameter = 3.5;
leg_stem_height = 3;
leg_inner_retainer_diameter = 6;
leg_inner_retainer_height = 2;
leg_segments = 128;

module juku_leg_fit_check() {
    assert(leg_outer_diameter > leg_counterbore_plug_diameter);
    assert(leg_outer_height > 0);
    assert(leg_counterbore_plug_diameter <= leg_counterbore_diameter);
    assert(leg_counterbore_plug_height <= leg_counterbore_depth);
    assert(leg_stem_diameter <= leg_hole_diameter);
    assert(leg_stem_height > 0);
    assert(
        leg_counterbore_plug_height + leg_stem_height
        == leg_through_hole_depth
    );
    assert(leg_inner_retainer_diameter > leg_stem_diameter);
    assert(leg_inner_retainer_diameter <= leg_boss_diameter);
    assert(leg_inner_retainer_height > 0);
    assert(leg_segments >= 3);
}

module juku_leg() {
    juku_leg_fit_check();

    color([0.16, 0.16, 0.16])
        union() {
            translate([0, 0, -leg_outer_height])
                cylinder(
                    h = leg_outer_height,
                    d = leg_outer_diameter,
                    $fn = leg_segments
                );

            cylinder(
                h = leg_counterbore_plug_height,
                d = leg_counterbore_plug_diameter,
                $fn = leg_segments
            );

            translate([0, 0, leg_counterbore_plug_height])
                cylinder(
                    h = leg_stem_height,
                    d = leg_stem_diameter,
                    $fn = leg_segments
                );

            translate([
                0,
                0,
                leg_counterbore_plug_height + leg_stem_height
            ])
                cylinder(
                    h = leg_inner_retainer_height,
                    d = leg_inner_retainer_diameter,
                    $fn = leg_segments
                );
        }
}

juku_leg();
