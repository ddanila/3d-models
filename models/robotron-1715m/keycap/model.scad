// Standalone loose 1-unit black keycap; clean reconstruction, MIT.
include <geometry.scad>
part = "keycap"; // [keycap, shell, core, preview, section]
width=17.8; depth=17.8; top_diameter=15; height=11.4; skirt_height=height/2;
body_taper=.6; // provisional diameter reduction from lower round body to top
// Owner measurements, 2026-10-13; bore excludes the projecting latch and key.
spring_recess_diameter=15;
support_outer_diameter=11;
support_inner_diameter=9;
underside_diameters=[spring_recess_diameter,support_outer_diameter,support_inner_diameter];
// Owner: 5 mm spring seat; base and raised round portion have equal heights.
spring_recess_depth=5;
// Provisional latch profile, mm. Projection is radial, not diametral.
// Set projection to zero for the previous straight cup wall.
latch_projection=.45;
latch_start=.8;       // depth from underside to start of entry bevel
latch_lead=1.0;       // axial length of entry bevel
latch_land=.25;       // axial length of narrowest opening
latch_shoulder=.2;    // axial return to the full cup bore
// Small axial orientation rib inside the cup, aligned with a skirt corner.
// Provisional dimensions; angle is measured from +X toward +Y, viewed from +Z.
key_projection=.6;    // radial intrusion; zero disables the rib
key_width=1.2;        // tangential width
key_start=.5;        // recessed from underside; entry bevel is 0.5 mm long
key_angle=135;       // toward the -X/+Y corner
orientation_key=[key_projection,key_width,key_start,key_angle];
$fn=96;
module volume() {
    keycap_volume(width,depth,top_diameter,top_diameter,height,skirt_height,
        latch_projection,latch_start,latch_lead,latch_land,latch_shoulder,orientation_key,underside_diameters,spring_recess_depth,body_taper);
}
if(part=="keycap") volume();
if(part=="shell" || part=="preview")color("#20211f")
    keycap_black_shell(width,depth,top_diameter,top_diameter,height,skirt_height,
        latch_projection,latch_start,latch_lead,latch_land,latch_shoulder,orientation_key,underside_diameters,spring_recess_depth,body_taper);
if(part=="core" || part=="preview")color("#deded1")
    keycap_white_core(width,depth,top_diameter,top_diameter,height,skirt_height,
        latch_projection,latch_start,latch_lead,latch_land,latch_shoulder,orientation_key,underside_diameters,spring_recess_depth,body_taper);
// Remove the front half to expose the latch ring's axial profile for review.
if(part=="section") difference() {
    volume();
    translate([-width,-depth,-1])cube([2*width,depth,height+2]);
}
