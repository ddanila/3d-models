// Keyboard-only review entry point. All physical shapes come from the museum model.
include <../model.scad>
include <legends.scad>

/* [Review] */
view = "assembled"; // [assembled, exploded, boards]
// Millimetres of separation; zero restores the actual assembled positions.
separation = 35; // [0:5:80]
show_legends = true;
legend_font = "Arial Unicode MS";
show_springs = false;
// Coarse spring tessellation for interactive review; canonical exports are unchanged.
draft = true;

/* [Indicators] */
// Static preview states; emulator-driven illumination remains in the museum.
caps_led_on = false;
siso_led_on = false;
led_off_color = "#89621d";
led_on_color = "#ff9c16";

/* [Colors] */
shell_color = "#9daeb1";
deck_color = "#242929";
black_key_color = "#202526";
core_color = "#dedecf";
clear_key_color = "#ffffff";
clear_key_alpha = 0.28; // [0:0.01:1]
inlay_color = "#a3a7a8";
red_key_color = "#b82e35";
pcb_color = "#91ae94";
rubber_color = "#30322d";

/* [Hidden] */
// Suppress the full-machine top-level output in the included source.
part = "keyboard-review";
lift = view=="exploded" ? separation : 0;
board_parts = ["keyboard-pcb", "keyboard-contact-pads", "keyboard-matrix-artwork", "keyboard-pcb-metal", "keyboard-insulators", "keyboard-pcb-supports", "keyboard-pcb-fasteners", "keyboard-contact-routes", "keyboard-matrix-socket", "keyboard-matrix-contacts"];
base_parts = ["keyboard-bottom", "keyboard-feet", "keyboard-metal", "keyboard-grommet", "keyboard-cable-support", "keyboard-internal-cable", "keyboard-entry-wires", "keyboard-entry-black", "keyboard-entry-pink", "keyboard-entry-blue"];
plate_parts = ["keyboard-plate", "keyboard-switches", "keyboard-guides"];
case_parts = ["keyboard-shell", "keyboard-deck", "keyboard-fillers"];
function has(list,name) = len([for(item=list)if(item==name)1])>0;
function tint(name,index) = name=="keyboard-shell" || name=="keyboard-bottom" ? shell_color :
    name=="keyboard-deck" || name=="keyboard-fillers" ? deck_color :
    name=="keyboard-pcb" ? pcb_color : colors[index];
function controller(name) = len(name)>=20 && [for(i=[0:19])name[i]]==[for(i=[0:19])"keyboard-controller-"[i]];
function layer(name) = controller(name) ? 4 : has(case_parts,name) ? 3 : has(plate_parts,name) ? 2 : has(board_parts,name) ? 1 : 0;

module review_key(i) {
    k=keys[i]; w=k[2]*keyboard_pitch-1.2; h=k[3]*keyboard_pitch-1.2;
    tw=k[5]>0 ? k[5] : w-4;
    color(k[4]==0 ? black_key_color : k[4]==1 ? clear_key_color : red_key_color,
        k[4]==1 ? clear_key_alpha : 1) render(convexity=10)cap(w,h,k[4],k[5]);
    if(k[4]==0 && view=="exploded")color(core_color)render(convexity=10)keycap_white_core(w,h,tw,h-4);
    if(k[4]==1)color(inlay_color)render(convexity=10)cap_insert(w,h);
    // Flat, shallow preview ink. Curved browser legends remain the museum's job.
    // Preview only: these labels never become raised lettering in an STL export.
    if(show_legends && $preview)color(k[4]==1 ? "#111311" : "#e7e6cd")
        for(j=[0:len(key_legends[i])-1])
            translate([0,(len(key_legends[i])-1-2*j)*2.4,k[4]==0 ? 11.5 : 9.6])
                linear_extrude(.025)text(key_legends[i][j],size=len(key_legends[i])>1 ? 3.3 : len(key_legends[i][j])>2 ? 3 : 4,
                    halign="center",valign="center",font=legend_font);
}

// Center the keyboard at the origin so orbit/zoom stays local to this assembly.
translate([0,-keyboard_y,0]) {
    for(i=[0:len(parts)-1])let(p=parts[i])
        if((view!="boards" && (has(base_parts,p) || has(case_parts,p) || has(plate_parts,p))) || has(board_parts,p) || controller(p))
            translate([0,controller(p) ? lift*1.3 : 0,lift*layer(p)])
                color(tint(p,i))render(convexity=10)shape(p);
    if(view!="boards") {
        // Lenses stay with their fixed carriers when the deck is exploded.
        translate([0,0,lift*3])for(i=[0:1])
            color((i==0 ? caps_led_on : siso_led_on) ? led_on_color : led_off_color)
                render(convexity=4)keyboard_indicator(i);
        translate([0,keyboard_y,28+keyboard_z_shift+lift*4])rotate([keyboard_slope,0,0])
            for(i=[0:len(keys)-1])translate([keys[i][0],keys[i][1],0])review_key(i);
        if(view=="exploded" || show_springs)
            translate([0,keyboard_y,28+keyboard_z_shift+lift*2])rotate([keyboard_slope,0,0])for(k=keys)translate([k[0],k[1],0]){
                if(show_springs)color("Silver")translate([0,0,-10.4])render(convexity=12)contact_spring(spring_installed,draft ? 16 : 48,draft ? 6 : 12);
                translate([0,0,lift*.55]){
                    color(core_color)render(convexity=8)contact_carrier();
                    color(rubber_color)render(convexity=8)contact_rubber();
                }
            }
    }
}
