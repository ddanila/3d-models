// Drives follow owner photographs; other internals still use comparative references.
// Board populations, mounting and wiring are provisional, not verified 1715M/W.
include <components/teac-fd55fv.scad>
include <pcb-packages.scad>
module drive_pair() { for(x=[-158,-4])translate([x-73,-203,60])children(); }
module drive_bracket() {
    translate([-235,-199,55])difference(){cube([310,197,2]);
        for(x=[10,164])translate([x,15,-1])cube([132,168,4]);}
    for(x=[-235,71])translate([x,-199,22])cube([3,197,35]);
    for(y=[-196,-12])translate([-235,y,52])cube([310,3,7]);
}
module logic_boards() {
    translate([-231,-178,12])cube([250,355,1.6]);
    // Controller board above the rear section; mounting is estimated.
    translate([-222,10,41])cube([220,165,1.6]);
}
module dip(w=8,l=20,h=4) { cube([w,l,h]); }
module logic_chips() {
    for(p=pcb_packages)translate([p[0],p[1],p[2]])cube([p[3],p[4],p[5]]);
}
module logic_pins() {
    // Leads along the two long edges of each photo-aligned package.
    for(p=pcb_packages)translate([p[0],p[1],p[2]])
        if(p[3]>p[4])for(x=[1:2.54:p[3]-1],y=[-.5,p[4]])translate([x,y,0])cube([.6,.5,1.8]);
        else for(y=[1:2.54:p[4]-1],x=[-.5,p[3]])translate([x,y,0])cube([.5,.6,1.8]);
}
module logic_connectors() {
    translate([-68,14,43])difference(){cube([44,10,8]);translate([2,2,2])cube([40,7,8]);}
}
module logic_caps() {
    // Tall cans match the controller photo rather than an invented grid.
    for(p=[[-86,55],[-84,45],[-86,34],[-82,20]])translate([p[0],p[1],43])cylinder(d=7,h=8,$fn=16);
}
module psu_chassis() {
    // Folded shield, right hand compartment, photo-scaled within 500x400 case.
    translate([94,-183,9])difference(){cube([144,369,104]);translate([2,2,2])cube([140,365,105]);
        translate([-1,292,52])rotate([0,90,0])cylinder(d=79,h=4,$fn=48);}
}
module psu_cover() {
    translate([94,-183,113])difference(){cube([144,369,1.4]);
        for(y=[-85,25])translate([70,y+183,-1])cylinder(d=11,h=4,$fn=24);}
    for(x=[101,230],y=[-175,0,177])translate([x,y,114.4])screw(5,1.2);
}
module fan_frame() {
    translate([68,67,25])difference(){cube([25,84,84]);translate([-1,42,42])rotate([0,90,0])cylinder(d=77,h=27,$fn=48);
        for(y=[5,79],z=[5,79])translate([-1,y,z])rotate([0,90,0])cylinder(d=3.5,h=27,$fn=12);}
}
module fan_rotor() {
    translate([80,109,67])rotate([0,90,0]){
        cylinder(d=27,h=11,center=true,$fn=32);
        for(a=[0:60:300])rotate([0,0,a])translate([11,-7,-3])rotate([25,0,0])linear_extrude(2)polygon([[0,0],[23,3],[23,15],[3,12]]);
    }
}
// Smooth ribbon runs with a real rectangular cross-section, not a photo plane.
module ribbon_run(points,w=42,t=.8) {
    for(i=[0:len(points)-2])hull(){translate(points[i])cube([w,1,t],center=true);translate(points[i+1])cube([w,1,t],center=true);}
}
module ribbons() {
    for(x=[-158,-4])ribbon_run([[x,3,67],[x,18,83],[x,39,74],[x,60,53]],42);
}
module ribbon_stripes() {
    for(x=[-158,-4])ribbon_run([[x-20,3,67.5],[x-20,18,83.5],[x-20,39,74.5],[x-20,60,53.5]],1.2,.2);
}
module wire_run(points,r=1) {
    for(i=[0:len(points)-2])hull(){translate(points[i])sphere(r=r,$fn=10);translate(points[i+1])sphere(r=r,$fn=10);}
}
module power_wires(offset=0) {
    for(x=[-207,-53])wire_run([[x,-1,71+offset],[x,17,75+offset],[64,28,82+offset],[87,42,71+offset],[96,46,59+offset]],.9);
    wire_run([[96,55,22+offset],[70,50,20+offset],[48,28,20+offset],[38,25,24+offset]],1);
}
module keyboard_pcb() {
    translate([0,keyboard_y,13])rotate([keyboard_slope,0,0])translate([-235,-74,0])cube([470,146,1.6]);
}
module keyboard_switches() {
    translate([0,keyboard_y,15])rotate([keyboard_slope,0,0])for(k=keys)translate([k[0]-5,k[1]-5,0])cube([10,10,10]);
}
module interior_shape(p) {
    if(p=="drive-frames")drive_pair()teac_frame();
    if(p=="drive-mechanisms")drive_pair()teac_mechanism();
    if(p=="drive-motors")drive_pair()teac_black();
    if(p=="drive-boards")for(i=[0:1])translate([[-231,-77][i],-203,60])teac_boards(i==1);
    if(p=="drive-traces")for(i=[0:1])translate([[-231,-77][i],-203,60])teac_traces(i==1);
    if(p=="drive-power-sockets")drive_pair()teac_power_socket();
    if(p=="drive-label-plates"){
        translate([-225,-.05,77])cube([108,.25,21.6]);
        translate([-34,-.05,70])cube([92,.25,28]);
    }
    if(p=="drive-contacts")drive_pair()teac_contacts();
    if(p=="drive-coils")drive_pair()teac_coils();
    if(p=="drive-bracket")drive_bracket();
    if(p=="logic-boards")logic_boards();
    if(p=="logic-chips")logic_chips();
    if(p=="logic-pins")logic_pins();
    if(p=="logic-connectors")logic_connectors();
    if(p=="logic-capacitors")logic_caps();
    if(p=="psu-chassis")psu_chassis();
    if(p=="psu-cover")psu_cover();
    if(p=="fan-frame")fan_frame();
    if(p=="fan-rotor")fan_rotor();
    if(p=="ribbon-cables")ribbons();
    if(p=="ribbon-stripes")ribbon_stripes();
    if(p=="power-wires-red")power_wires(0);
    if(p=="power-wires-black")power_wires(2.2);
    if(p=="power-wires-yellow")power_wires(4.4);
    if(p=="keyboard-pcb")keyboard_pcb();
    if(p=="keyboard-switches")keyboard_switches();
}
