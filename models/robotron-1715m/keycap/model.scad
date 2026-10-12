// Standalone loose 1-unit black keycap; clean reconstruction, MIT.
include <geometry.scad>
part = "keycap"; // keycap, shell, core, preview
width=17.8; depth=17.8; top_diameter=13.8; height=11.4; skirt_height=4;
$fn=96;
if(part=="keycap")keycap_volume(width,depth,top_diameter,top_diameter,height,skirt_height);
if(part=="shell" || part=="preview")color("#20211f")keycap_black_shell(width,depth,top_diameter,top_diameter,height,skirt_height);
if(part=="core" || part=="preview")color("#deded1")keycap_white_core(width,depth,top_diameter,top_diameter,height,skirt_height);
