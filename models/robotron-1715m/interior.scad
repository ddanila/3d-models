// Drives follow owner photographs; other internals still use comparative references.
// Board populations, mounting and wiring are provisional, not verified 1715M/W.
include <components/teac-fd55fv.scad>
include <pcb-components.scad>
include <components/pcb-discretes.scad>
module drive_pair() { for(x=[-158,-4])translate([x-73,-203,60])children(); }
module drive_bracket() {
    translate([-235,-199,55])difference(){cube([310,197,2]);
        for(x=[10,164])translate([x,15,-1])cube([132,168,4]);}
    for(x=[-235,71])translate([x,-199,22])cube([3,197,35]);
    for(y=[-196,-12])translate([-235,y,52])cube([310,3,7]);
}
// Selection is shared by standalone OpenSCAD and the per-board browser exports.
pcb_board = "";
function pcb_selected(board) = pcb_board=="" || pcb_board==board;
module board_blank(origin,size,board) {
    if(pcb_selected(board))translate(origin)linear_extrude(1.6)difference(){
        square(size);
        for(p=pcb_mounts)if(p[4]==board)translate([p[0]-origin[0],p[1]-origin[1]])circle(d=3.4,$fn=20);
        for(p=pcb_footprints)if(p[3]==board)translate([p[0]-origin[0],p[1]-origin[1]])circle(d=.95,$fn=12);
    }
}
module logic_boards() {
    board_blank([-231,-178,12],[250,355],"motherboard");
    board_blank([-222,10,41],[220,165],"floppy-controller");
}
module pcb_pad() {
    translate([0,0,-1.64])difference(){
        cylinder(d=1.8,h=1.72,$fn=12);
        translate([0,0,-.1])cylinder(d=.95,h=2,$fn=12);
    }
}
module pcb_solder() {
    translate([0,0,-2])difference(){
        cylinder(d1=.85,d2=1.7,h=.36,$fn=12);
        translate([0,0,-.1])cylinder(d=.72,h=.6,$fn=12);
    }
}
module logic_pads() {
    for(p=pcb_footprints)if(pcb_selected(p[3]))translate([p[0],p[1],p[2]])pcb_pad();
}
module logic_solder() {
    for(p=pcb_footprints)if(pcb_selected(p[3]))translate([p[0],p[1],p[2]])pcb_solder();
}
module logic_chips() {
    for(p=pcb_component_instances)if(pcb_selected(p[3]))translate(p[1])rotate([0,0,p[2]])import(pcb_component_models[p[0]][0]);
}
module logic_pins() {
    for(p=pcb_component_instances)if(pcb_selected(p[3]))translate(p[1])rotate([0,0,p[2]])import(pcb_component_models[p[0]][1]);
}
// Photo-estimated two-row connector, with individual metal contacts.
// No electrical pinout is asserted. Long axis follows local Y.
module board_socket(n=32) {
    difference(){cube([9,(n-1)*2.54+6,7],center=true);
        translate([0,0,1.5])cube([5,(n-1)*2.54+2,6],center=true);
        translate([4,0,2])cube([4,5,5],center=true);}
    for(y=[-(n-1)*1.27:2.54:(n-1)*1.27])translate([0,y,0])cube([5,.5,3],center=true);
}
module board_socket_contacts(n=32) {
    for(x=[-1.27,1.27],i=[0:n-1])translate([x,(i-(n-1)/2)*2.54,-2])cube([.55,.55,8],center=true);
}
module connector_pose() {
    if(pcb_selected("motherboard"))translate([-13.02,99.60,17.3])children();
    if(pcb_selected("floppy-controller"))translate([-10.68,91.71,46.3])children();
}
module logic_connectors(){
    connector_pose()board_socket();
    if(pcb_selected("floppy-controller"))translate([-46,19,46.3])rotate([0,0,90]){
        board_socket(17);
        // Illustrative ribbon plug and strain-relief bar at the existing cable end.
        translate([0,0,4.2])cube([8,44,1.8],center=true);
    }
}
module logic_connector_contacts(){
    connector_pose()board_socket_contacts();
    if(pcb_selected("floppy-controller"))translate([-46,19,46.3])rotate([0,0,90])board_socket_contacts(17);
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
    for(x=[-158,-4])ribbon_run([[x-4,2,66.5],[x-4,20,79],[x-4,45,69],[-46,45,58],[-46,19,51]],42);
}
module ribbon_ridges() {
    for(x=[-158,-4],i=[0:32])let(dx=(i-16)*1.27)
        ribbon_run([[x-4+dx,2,66.95],[x-4+dx,20,79.45],[x-4+dx,45,69.45],[-46+dx,45,58.45],[-46+dx,19,51.45]],.4,.15);
}
module ribbon_stripes() {
    for(x=[-158,-4])ribbon_run([[x-24,2,67],[x-24,20,79.5],[x-24,45,69.5],[-66,45,58.5],[-66,19,51.5]],1.2,.2);
}
module wire_run(points,r=1) {
    for(i=[0:len(points)-2])hull(){translate(points[i])sphere(r=r,$fn=10);translate(points[i+1])sphere(r=r,$fn=10);}
}
module power_wires(offset=0) {
    for(x=[-207,-53])wire_run([[x-6+offset*2.04545,5,67.5],[x,17,75+offset],[64,28,82+offset],[87,42,71+offset],[96,46,59+offset]],.9);
    if(offset==2.2)for(x=[-207,-53])wire_run([[x-10.5,5,67.5],[x-4.5,17,77.2],[59.5,28,84.2],[82.5,42,73.2],[96,46,61.2]],.9);
    wire_run([[96,55,22+offset],[70,50,20+offset],[48,28,20+offset],[38,25,24+offset]],1);
}
module keyboard_pcb() {
    translate([0,keyboard_y,13])rotate([keyboard_slope,0,0])difference(){
        translate([-240,-71,0])cube([480,110,1.6]);
        for(x=[-220,0,220],y=[-65,33])translate([x,y,-1])cylinder(d=3.2,h=4,$fn=16);
    }
}
module keyboard_switches() {
    translate([0,keyboard_y,15])rotate([keyboard_slope,0,0])for(k=keys)translate([k[0],k[1],0])switch_housing();
}
module interior_shape(p) {
    for(i=[0:1]) {
      if(p==str("drive-spindle-",i))translate([[-231,-77][i],-203,60])teac_spindle();
      if(p==str("drive-head-",i))translate([[-231,-77][i],-203,60])teac_head();
    }
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
    logic_discretes(p);
    if(p=="prototype-pcb-pad")pcb_pad();
    if(p=="prototype-pcb-solder")pcb_solder();
    if(p=="logic-pads")logic_pads();
    if(p=="logic-solder")logic_solder();
    if(p=="logic-connector-contacts")logic_connector_contacts();
    if(p=="logic-boards")logic_boards();
    if(p=="logic-chips")logic_chips();
    if(p=="logic-pins")logic_pins();
    if(p=="logic-connectors")logic_connectors();
    if(p=="psu-chassis")psu_chassis();
    if(p=="psu-cover")psu_cover();
    if(p=="fan-frame")fan_frame();
    if(p=="fan-rotor")fan_rotor();
    if(p=="ribbon-cables")ribbons();
    if(p=="ribbon-ridges")ribbon_ridges();
    if(p=="drive-cable-plugs")drive_pair()teac_cable_plug();
    if(p=="ribbon-stripes")ribbon_stripes();
    if(p=="power-wires-red")power_wires(0);
    if(p=="power-wires-black")power_wires(2.2);
    if(p=="power-wires-yellow")power_wires(4.4);
    if(p=="keyboard-pcb")keyboard_pcb();
    if(p=="keyboard-switches")keyboard_switches();
}
