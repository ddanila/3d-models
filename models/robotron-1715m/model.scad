// Danila's Robotron 1715 M with a provisional reference interior.
// See README for measured vs inferred dimensions and unseen surfaces.
include <dimensions.scad>
include <keyboard-layout.scad>
include <monitor-profile.scad>
include <interior.scad>
include <monitor-interior.scad>
part = "assembly";
key_index = 0;

module rounded(size,r=3) {
    hull() for(x=[r,size[0]-r],y=[r,size[1]-r],z=[r,size[2]-r])
        translate([x,y,z]) sphere(r=r,$fn=32);
}
module slab(w,h,t,r=2) {
    linear_extrude(t) offset(r=r) square([w-2*r,h-2*r],center=true);
}
module front_slot(x,z,w,h) {
    translate([x,-case_d/2-12,z]) rotate([90,0,0]) slab(w,h,30,min(w/2-0.1,3));
}
module side_slot(y,z,h=30) {
    translate([-case_w/2-10,y,z]) rotate([90,0,90]) slab(5,h,22,2.4);
}
module case_base() {
    difference() {
        translate([-case_w/2,-case_d/2,0]) rounded([case_w,case_d,seam_z],4);
        translate([-case_w/2+wall,-case_d/2+wall,wall]) cube([case_w-2*wall,case_d-2*wall,seam_z]);
        for(y=[-95:10:15]) side_slot(y,22,20);
        for(y=[90:10:190]) side_slot(y,22,20);
        translate([-case_w/2-2,-164,15]) cube([10,38,14]);
    }
}
module case_lid() {
    difference() {
        translate([-case_w/2,-case_d/2,seam_z+1]) rounded([case_w,case_d,case_h-seam_z-1],5);
        translate([-case_w/2+wall,-case_d/2+wall,seam_z-2]) cube([case_w-2*wall,case_d-2*wall,case_h-seam_z-wall+2]);
        translate([-case_w/2-1,-case_d/2-1,seam_z]) cube([case_w+2,wall+3,case_h]);
        for(y=[-165:10:-35]) side_slot(y,72,42);
        for(y=[50:10:180]) side_slot(y,72,42);
    }
}
module fascia() {
    difference() {
        translate([0,-case_d/2-1,(case_h+seam_z)/2]) rotate([90,0,0]) slab(case_w-2,case_h-seam_z,8,5);
        for(x=[-158,-4]) translate([x,-case_d/2+8,81]) rotate([90,0,0]) slab(148,44,30,3);
        for(i=[0:13]) translate([93+i*10.2,-case_d/2+8,82]) rotate([90,0,0]) slab(5.8,65,30,2.8);
    }
}
// Recessed moulded drive fronts. No full-face photograph or baked shadow.
module drives() {
    for(x=[-158,-4]) translate([x,-case_d/2-6,81]) rotate([90,0,0]) difference() {
        slab(146,42,2.5,2);
        translate([0,8,-1]) slab(140,3.5,5,1);
        translate([4,-2,-1]) slab(41,25,5,1.5);
        translate([-60,15,-1]) slab(11,4,5,.7);
    }
}
module drive_insets() {
    for(x=[-158,-4]) translate([x,-case_d/2-3,81]) rotate([90,0,0]) {
        slab(144,40,1,1);
        // Recessed central finger well, with the insertion slot above it.
        translate([4,-3,1]) slab(39,20,1,1);
    }
}
module drive_latches() {
    for(x=[-158,-4]) translate([x+45,-case_d/2-9,92]) rotate([90,0,0]) {
        cylinder(d=12,h=3,$fn=40);
        hull(){cylinder(d=8,h=5,$fn=32);translate([23,1,0])cylinder(d=7,h=5,$fn=32);}
        translate([11,1,5])slab(20,3,.5,1);
    }
}
module drive_led(i) {
    translate([-218+i*154,-case_d/2-8.6,96]) rotate([90,0,0]) slab(10,3.5,.7,.5);
}
module switch_part(x,w,h) {
    translate([x,-case_d/2-4,17]) rotate([90,0,0]) {
        difference(){slab(w,h,4,2);translate([0,0,1])slab(w-4,h-4,5,1);}
        translate([0,0,4]) rotate([0,x>0?8:0,0]) slab(w-5,h-5,3,1);
        if(x>0)for(i=[-7:7])translate([i*2,0,7.2])cube([.35,h-7,.4],center=true);
    }
}
module pedestal() {
    translate([0,monitor_y,case_h+ring_h]) cylinder(d=171,h=31);
    translate([0,monitor_y,case_h+ring_h+31]) cylinder(d1=145,d2=105,h=14);
}
module ring() {
    translate([0,monitor_y,case_h]) difference(){cylinder(d=ring_od,h=ring_h);translate([0,0,-1])cylinder(d=ring_id,h=ring_h+2);}
}
module monitor_shell() {
    translate([0,monitor_y,monitor_z]) difference() {
        hull() {
            translate([-monitor_w/2,-monitor_d/2,0]) rounded([monitor_w,30,monitor_h],14);
            translate([-135,monitor_d/2-28,20]) rounded([270,28,240],12);
        }
        hull(){translate([-monitor_w/2+wall,-monitor_d/2+wall,wall])rounded([monitor_w-2*wall,22,monitor_h-2*wall],7);translate([-132,monitor_d/2-31,23])rounded([264,28,234],7);}
        translate([-139,-monitor_d/2-3,21]) rounded([278,60,238],8);
        // Side/rear shell joint visible in the owner photograph.
        translate([-monitor_w/2-1,-monitor_d/2-1,monitor_h*monitor_seam_fraction-.6]) cube([monitor_w+2,monitor_d+2,1.2]);
        for(i=[-12:12]) translate([i*10,70,monitor_h-24]) cube([4,60,40],center=true);
    }
}
module bezel() {
    translate([0,monitor_y-monitor_d/2-3,monitor_z+monitor_h/2]) rotate([90,0,0]) difference() {
        hull(){slab(303,264,1,19);translate([0,0,8])slab(296,257,1,22);}
        translate([0,4,-1]) linear_extrude(12) crt_outline(268,221);
    }
}
// A bowed, superelliptical tube face rather than a rounded flat rectangle.
function signed_pow(v,p)=sign(v)*pow(abs(v),p);
module crt_outline(w,h) {
    polygon([for(t=[0:2:358]) [w/2*signed_pow(cos(t),2/crt_power),h/2*signed_pow(sin(t),2/crt_power)]]);
}
module crt_dome(w,h) {
    intersection() {
        translate([0,0,-crt_back])linear_extrude(crt_depth+crt_back)crt_outline(w,h);
        translate([0,0,crt_depth-crt_radii[2]])scale(crt_radii)sphere(r=1,$fn=384);
    }
}
module crt_rim() {
    translate(crt_position)rotate([90,0,0])difference(){
        crt_dome(269,222);
        translate([0,0,-crt_back-1])linear_extrude(crt_depth+crt_back+2)crt_outline(crt_size[0]-.4,crt_size[1]-.4);
    }
}
module crt_glass() {
    translate(crt_position)rotate([90,0,0])crt_dome(crt_size[0],crt_size[1]);
}
module keyboard_shell() {
    translate([0,keyboard_y,0]) difference() {
        hull(){translate([-keyboard_w/2+3,-keyboard_d/2,0])rounded([keyboard_w-6,12,16],4);translate([-keyboard_w/2+3,keyboard_d/2-12,0])rounded([keyboard_w-6,12,40],4);}
        // Hollow sheet-metal shell, closed by a separate removable bottom plate.
        hull(){translate([-keyboard_w/2+6,-keyboard_d/2+3,-3])rounded([keyboard_w-12,10,16],3);translate([-keyboard_w/2+6,keyboard_d/2-13,-3])rounded([keyboard_w-12,10,40],3);}
        translate([0,0,25]) rotate([keyboard_slope,0,0]) slab(keyboard_w-12,keyboard_d-30,30,4);
    }
}
module keyboard_bottom() {
    translate([0,keyboard_y,0]) difference() {
        union(){slab(keyboard_w-12,keyboard_d-7,1.6,5);
            for(x=[-200,200],y=[-65,65])translate([x,y,-1.2])slab(33,15,2,5);}
        translate([80,55,-3])slab(36,25,8,2);
        for(x=[-218,0,218],y=[-87,87])translate([x,y,-2])cylinder(d=3.5,h=6);
    }
}
module keyboard_feet() {
    for(x=[-200,200],y=[-65,65]) translate([x,keyboard_y+y,-5]) difference() {
        slab(28,11,4,1.3);
        translate([0,0,-1])slab(23,6,3.5,.7);
    }
}
module screw(d=5,h=1.7) {
    difference(){cylinder(d=d,h=h,$fn=32);translate([-d/2,-.45,-.1])cube([d,.9,.7]);}
}
module keyboard_metal() {
    for(x=[-200,200],y=[-65,65])translate([x,keyboard_y+y,0]){
        translate([0,0,-3.2])slab(22,5,1,.4);
        translate([0,0,-4])screw(3,1.2);
    }
    for(x=[-218,0,218],y=[-87,87])translate([x,keyboard_y+y,0]){
        translate([0,0,-.7])cylinder(d=7,h=.8,$fn=32);
        translate([0,0,-2.1])difference(){cylinder(d=5.5,h=1.5,$fn=6);translate([-3,-.45,-.1])cube([6,.9,.8]);}
    }
}
module keyboard_grommet() {
    translate([80,keyboard_y+55,-2]) {
        difference(){slab(37,26,3,2);translate([0,0,-1])slab(29,18,5,2);}
        for(y=[-15,15])translate([0,y,-.5])rotate([y<0?-18:18,0,0])slab(41,7,2,1);
    }
}
module keyboard_deck() {
    translate([0,keyboard_y,26]) rotate([keyboard_slope,0,0]) difference() {
        slab(keyboard_w-8,keyboard_d-34,4,5);
        for(k=keys) translate([k[0],k[1],-1]) slab(k[2]*keyboard_pitch-1,k[3]*keyboard_pitch-1,7,2);
    }
    translate([0,keyboard_y+87,37]) rotate([0,90,0]) cylinder(r=3,h=keyboard_w-24,center=true,$fn=40);
}
module keyboard_fillers() {
    translate([0,keyboard_y,28]) rotate([keyboard_slope,0,0]) {
        // Blank spacers and indicator carriers visible between the key groups.
        for(p=[[-242,-5,8,19],[83,35,18,19],[28,-45,8,18]])
            translate([p[0],p[1],0])slab(p[2],p[3],3,2);
    }
}
module cap(w,h,style) {
    // Square skirt, tapered shoulder and dished top: all highlights are 3D.
    union(){slab(w,h,1.4,2);
        difference(){hull(){translate([0,0,1.4])slab(w-.4,h-.4,1,2);
            translate([0,0,7])
                if(style==1)slab(w-2,h-3,1,3);
                else slab(w-2,h-3,1,min(w-2,h-3)/2-.1);
        }translate([0,0,36])scale([max(1,(w-4)/16),max(1,(h-4)/16),1])sphere(r=29,$fn=96);}
    }
}
module keycaps(style) {
    translate([0,keyboard_y,28]) rotate([keyboard_slope,0,0])
        for(k=keys) if(k[4]==style) translate([k[0],k[1],0])cap(k[2]*keyboard_pitch-1.2,k[3]*keyboard_pitch-1.2,style);
}
function bezier(p,t)=pow(1-t,3)*p[0]+3*pow(1-t,2)*t*p[1]+3*(1-t)*t*t*p[2]+t*t*t*p[3];
module cable() {
    // One continuous lead: underside grommet -> around the left -> plug.
    // Control points describe an estimated resting route, not a second lead.
    curves=[[[80,keyboard_y+55,4],[80,keyboard_y+57,-7],[80,keyboard_y+70,-7],[75,-250,-5]],
        [[75,-250,-5],[55,-215,-5],[-175,-244,-5],[-258,-230,1]],
        [[-258,-230,1],[-300,-223,4],[-309,-156,20],[-275,-145,22]]];
    for(p=curves,i=[0:19])hull(){translate(bezier(p,i/20))sphere(r=2.6,$fn=16);translate(bezier(p,(i+1)/20))sphere(r=2.6,$fn=16);}
}
// Owner connector close-ups, 2026-10-10. Envelope estimated; no scale in photos.
// Local X points into the socket, Y spans the two release levers.
module plug_pose() { translate([-278,-145,22]) children(); }
module cable_plug() { plug_pose() {
    difference() {
        translate([0,0,-6])linear_extrude(12)
            polygon([[0,-8],[9,-18],[27,-18],[27,18],[9,18],[0,8]]);
        translate([-1,-20,-.3])cube([29,40,.6]);
        for(p=[[10,-14],[10,14],[3,0]]) {
            translate([p[0],p[1],4.5])cylinder(d=5.2,h=2,$fn=32);
            translate([p[0],p[1],-6.1])cylinder(d=5.2,h=1.6,$fn=6);
        }
        translate([4,-10,5])rotate([0,0,-42])cube([2,18,2]);
    }
    // Two hooked, recessed release levers, with the spring clearance below.
    for(side=[-1,1])scale([1,side,1]) {
        translate([0,0,-3])linear_extrude(6)
            polygon([[4,19],[8,20],[13,19],[32,19],[32,16],[35,16],[35,22],[12,22],[7,23],[3,22]]);
        translate([12,17,-2])cube([3,3,4]);
    }
    translate([-3,0,0])rotate([0,90,0])cylinder(d=8,h=6,$fn=32);
} }
module plug_insert() { plug_pose() difference() {
    union() {
        translate([26,-11,-4.5])cube([7,22,9]);
        for(y=[-17,13])translate([26,y,-4])cube([6,4,8]);
    }
    // Recessed two-row face; contacts remain concealed when plugged in.
    for(y=[-8:4:8],z=[-2,2])translate([30,y-1.3,z-.9])cube([4,2.6,1.8]);
} }
module plug_screws() { plug_pose() {
    for(p=[[10,-14],[10,14],[3,0]]) {
        translate([p[0],p[1],5.6])rotate([180,0,0])screw(4.5,1);
        translate([p[0],p[1],-5.7])difference(){cylinder(d=4.6,h=1,$fn=6);translate([0,0,-.1])cylinder(d=2,h=1.2,$fn=16);}
    }
} }
module monitor_tape() {
    translate([0,monitor_y-120,monitor_z+monitor_h-2.1])rotate([-3.9,0,-3])slab(52,9,.3,.5);
}
module hardware() {
    // PSU shield behind the front vents is modeled in interior.scad.
    // Base-unit feet remain provisional without an underside photograph.
    for(x=[-225,225],y=[-170,170])translate([x,y,-9])cylinder(d=25,h=10,$fn=40);
}
module shape(p) {
    interior_shape(p);
    monitor_interior_shape(p);
    if(p=="drive-insets")drive_insets();
    if(p=="drive-latches")drive_latches();
    if(p=="drive-led-0")drive_led(0);
    if(p=="drive-led-1")drive_led(1);
    if(p=="keyboard-bottom")keyboard_bottom();
    if(p=="keyboard-feet")keyboard_feet();
    if(p=="keyboard-metal")keyboard_metal();
    if(p=="keyboard-grommet")keyboard_grommet();
    if(p=="keyboard-fillers")keyboard_fillers();
    if(p=="cable-plug")cable_plug();
    if(p=="plug-screws")plug_screws();
    if(p=="plug-insert")plug_insert();
    if(p=="monitor-tape")monitor_tape();
    if(p=="case-base")case_base();
    if(p=="case-lid")case_lid();
    if(p=="fascia")fascia();
    if(p=="drives")drives();
    if(p=="power")switch_part(207,43,18);
    if(p=="reset")switch_part(-208,21,19);
    if(p=="pedestal")pedestal();
    if(p=="ring")ring();
    if(p=="monitor-shell")monitor_shell();
    if(p=="bezel")bezel();
    if(p=="crt-rim")crt_rim();
    if(p=="crt-glass")crt_glass();
    if(p=="keyboard-shell")keyboard_shell();
    if(p=="keyboard-deck")keyboard_deck();
    if(p=="keys-black")keycaps(0);
    if(p=="keys-light")keycaps(1);
    if(p=="keys-red")keycaps(2);
    if(p=="hardware")hardware();
    if(p=="cable")cable();
    if(p=="keycap")let(k=keys[key_index])cap(k[2]*keyboard_pitch-1.2,k[3]*keyboard_pitch-1.2,k[4]);
}
parts=["case-base", "case-lid", "fascia", "drives", "power", "reset", "pedestal", "ring", "monitor-shell-lower", "bezel", "crt-rim", "crt-glass", "keyboard-shell", "keyboard-deck", "keys-black", "keys-light", "keys-red", "hardware", "cable", "drive-insets", "drive-latches", "drive-led-0", "drive-led-1", "keyboard-bottom", "keyboard-feet", "keyboard-metal", "keyboard-grommet", "keyboard-fillers", "cable-plug", "plug-screws", "monitor-tape", "drive-frames", "drive-mechanisms", "drive-motors", "drive-boards", "drive-contacts", "drive-coils", "drive-bracket", "logic-boards", "logic-chips", "logic-pins", "logic-connectors", "logic-capacitors", "psu-chassis", "psu-cover", "fan-frame", "fan-rotor", "ribbon-cables", "ribbon-stripes", "power-wires-red", "power-wires-black", "power-wires-yellow", "keyboard-pcb", "keyboard-switches", "monitor-shell-upper", "tube-funnel", "tube-neck", "monitor-yoke", "monitor-coils", "monitor-chassis", "monitor-boards", "monitor-components", "monitor-capacitors", "monitor-shield", "monitor-wires", "plug-insert", "drive-power-sockets", "drive-traces", "drive-label-plates", "drive-spindle-0", "drive-spindle-1", "drive-head-0", "drive-head-1"];
colors=["Wheat", "Wheat", "#8d887a", "#242627", "#333839", "#333839", "Wheat", "#333333", "Wheat", "#8c857a", "#141919", "#0b1712", "#9daeb1", "#242929", "#202526", "#bac1b8", "#c6343b", "#242725", "#b7b3a0", "#101312", "#242827", "#590b0b", "#590b0b", "#9daeb1", "#252928", "#96988f", "#30312e", "#242929", "#c3b995", "#96988f", "#487eac", "#a2a4a0", "#bec2bd", "#282c2b", "#28675a", "#b3a775", "#9e793b", "#afb4ae", "#386349", "#25292b", "#b3b8b4", "#b1b5a1", "#b2a15c", "#a2a6a3", "#b5b9b2", "#818984", "#282d2a", "#a0a59b", "#975b50", "#9e3930", "#252a28", "#b6a05b", "#346750", "#30352f", "Wheat", "#363d3a", "#78765f", "#38372e", "#ae7545", "#a3a79c", "#486551", "#343835", "#438c9b", "#979e92", "#b2a374", "#969782", "#d0c6a4", "#78a58d", "#c2bba4", "#a8aaa4", "#a8aaa4", "#30322f", "#30322f"];
if(part=="assembly") for(i=[0:len(parts)-1]) color(colors[i]) shape(parts[i]);
else if(part=="interior") { for(i=[31:len(parts)-1]) if(parts[i]!="monitor-shell-upper") color(colors[i]) shape(parts[i]); }
else shape(part);
