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
    for(b=pcb_boards)board_blank(b[1],b[2],b[0]);
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
    for(p=pcb_footprints)if(pcb_selected(p[3]))translate([p[0],p[1],p[2]])scale([1,1,p[4]])pcb_pad();
}
module logic_solder() {
    for(p=pcb_footprints)if(pcb_selected(p[3]))translate([p[0],p[1],p[2]])scale([1,1,p[4]])pcb_solder();
}
module logic_chips() {
    for(p=pcb_component_instances)if(pcb_selected(p[3]))translate(p[1])rotate([0,0,p[2]])rotate([p[4]==-1?180:0,0,0])import(pcb_component_models[p[0]][0]);
}
module logic_pins() {
    for(p=pcb_component_instances)if(pcb_selected(p[3]))translate(p[1])rotate([0,0,p[2]])rotate([p[4]==-1?180:0,0,0])import(pcb_component_models[p[0]][1]);
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
module connector_pose(){for(c=pcb_connectors)if(pcb_selected(c[3]))translate(c[0])rotate([0,0,c[2]])rotate([c[4]==-1?180:0,0,0])let($pins=c[1])children();}
module logic_connectors(){connector_pose()translate([0,0,3.7])board_socket($pins);}
module logic_connector_contacts(){connector_pose()translate([0,0,3.7])board_socket_contacts($pins);}
function display_xy(p)=[-222+(p[0]-40)/1630*220,10+(1-(p[1]-180)/1170)*165];
module logic_artwork(){
 if(pcb_selected("display-controller")){
  // Clean raised route geometry from the owner's solder-side photograph.
  for(path=pcb_display_routes,i=[0:len(path)-2])hull()for(j=[i,i+1])translate(concat(display_xy(path[j]),[42.62]))cylinder(d=.42,h=.08,$fn=8);
  // Local endpoint fan-outs are deliberately not connected into a claimed netlist.
  for(p=pcb_footprints)if(p[3]=="display-controller")translate([p[0]-.9,p[1],42.62])cube([1.8,.3,.08]);
 }
}
module psu_chassis() {
    // Folded shield, right hand compartment, photo-scaled within 500x400 case.
    translate([94,-183,9])difference(){cube([144,369,104]);translate([2,2,2])cube([140,365,105]);
        translate([-1,292,52])rotate([0,90,0])cylinder(d=79,h=4,$fn=48);}
}
module psu_cover() {
    translate([94,-183,113])difference(){cube([144,369,1.4]);
        for(y=[-125,-5])translate([130,y+183,-1])cylinder(d=11,h=4,$fn=24);}
    for(x=[101,230],y=[-175,0,177])translate([x,y,114.4])screw(5,1.2);
}
module fan_frame() {
    translate([68,67,25])difference(){cube([25,84,84]);translate([-1,42,42])rotate([0,90,0])cylinder(d=77,h=27,$fn=48);
        for(y=[5,79],z=[5,79])translate([-1,y,z])rotate([0,90,0])cylinder(d=3.5,h=27,$fn=12);}
}
// October 13 owner photos; dimensions estimated within existing fan envelope.
module fan_retainers(){
    for(a=[-45,45])translate([66,109,67])rotate([a,0,0])cube([1.2,107,5.5],center=true);
    for(y=[72,146],z=[30,104])translate([65.2,y,z])rotate([0,90,0])screw(5,1.2);
}
module fan_cushions(){for(y=[65,147])translate([68,y,27])cube([25,4,80]);}
module psu_grommets(){for(y=[-125,-5])translate([224,y,114.4])difference(){cylinder(d=14,h=1.5,$fn=32);translate([0,0,-1])cylinder(d=7,h=4,$fn=24);}}
// Brown 05-330-0024 adapter, photo 150520316. Nominal 2.54mm connector pitch;
// routing is visual, not an electrical netlist. Both drive interfaces are seen in 150535694.
// Installed adapter: vertical board, white ribbon connector on its rear face;
// black drive-edge socket below. Clean geometry excludes stains/solder oxidation.
adapter_w=58;adapter_h=38;adapter_pitch=2.54;
module drive_adapter_pose(){for(x=[-158,-4])translate([x-29,2,57])rotate([90,0,0])children();}
module drive_adapter_boards(){drive_adapter_pose()difference(){cube([adapter_w,adapter_h,1.6]);for(x=[3,55],y=[3,35])translate([x,y,-1])cylinder(d=3,h=4,$fn=20);}}
module drive_adapter_traces(){drive_adapter_pose(){
 // 34 drive contacts to the narrower 26-way ribbon interface. Paths reproduce
 // visible staggered bends; they are not offered as an electrical pinout.
 for(i=[0:16],row=[0:1]){
  x=8+i*adapter_pitch;y=5+row*adapter_pitch;
  translate([x,y,1.6])cylinder(d=1.6,h=.25,$fn=12);
  if(i<13){
   xx=13+i*adapter_pitch;yy=29+row*adapter_pitch;
   translate([xx,yy,1.6])cylinder(d=1.6,h=.25,$fn=12);
   points=[[x,y],[x,11+row],[xx,21+row],[xx,yy]];
   for(k=[0:2])hull()for(j=[k,k+1])translate([points[j][0],points[j][1],1.6])cylinder(d=.3,h=.12,$fn=8);
  }
 }
}}
module drive_adapter_sockets(){drive_adapter_pose(){
 translate([8,25,-10])difference(){cube([43,11,10]);translate([4,3,-1])cube([35,5,9]);}
 for(x=[8,49])translate([x,24,-18])difference(){cube([2,14,20]);translate([-.1,3,3])cube([3,8,12]);}
}}
module drive_adapter_edge(){drive_adapter_pose()translate([5,1,-9])difference(){cube([48,10,9]);translate([3,3,-1])cube([42,4,8]);}}
module drive_adapter_contacts(){drive_adapter_pose(){
 for(i=[0:12],row=[0:1])translate([13+i*2.54,29+row*2.54,-8])cube([.55,.55,9.8]);
 for(i=[0:16],row=[0:1])translate([8+i*2.54,5+row*2.54,-7])cube([.5,.5,8.8]);
 // Metal latch bar runs across the white connector, visible in side photo.
 translate([8,24,-16])cube([43,1,2]);
}}
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
function drive_ribbon_path(unit,dx=0,lift=0)=unit==0?
 [[-158+dx,-13,89+lift],[-158+dx,24,109+lift],[-181+dx,39,120+lift],[-207+dx,37,88+lift],[-219+dx,35,24+lift]]:
 [[-4+dx,-13,89+lift],[-4+dx,27,113+lift],[-48+dx,41,123+lift],[-91+dx,39,95+lift],[-130+dx,28,73+lift],[-196+dx,22,50+lift],[-219+dx,35,24+lift]];
module ribbons(){for(u=[0:1])ribbon_run(drive_ribbon_path(u),33);}
module ribbon_ridges(){for(u=[0:1],i=[0:25])ribbon_run(drive_ribbon_path(u,(i-12.5)*1.27,.45),.35,.12);}
module ribbon_stripes(){for(u=[0:1])ribbon_run(drive_ribbon_path(u,-15.9,.55),.7,.12);}
module wire_run(points,r=1) {
    for(i=[0:len(points)-2])hull(){translate(points[i])sphere(r=r,$fn=10);translate(points[i+1])sphere(r=r,$fn=10);}
}
module power_wires(offset=0) {
    for(x=[-207,-53])wire_run([[x-6+offset*2.04545,5,67.5],[x,17,75+offset],[64,28,82+offset],[87,42,71+offset],[96,46,59+offset]],.9);
    if(offset==2.2)for(x=[-207,-53])wire_run([[x-10.5,5,67.5],[x-4.5,17,77.2],[59.5,28,84.2],[82.5,42,73.2],[96,46,61.2]],.9);
    wire_run([[96,55,22+offset],[70,50,20+offset],[48,28,20+offset],[38,25,24+offset]],1);
}
module keyboard_pcb() {
    translate([0,keyboard_y,28+keyboard_z_shift])rotate([keyboard_slope,0,0])translate([0,0,-14.918])difference(){
        translate([-240,-71,0])cube([480,110,1.6]);
        for(x=[-220,0,220],y=[-65,33])translate([x,y,-1])cylinder(d=3.2,h=4,$fn=16);
    }
}
module keyboard_switches() {
    translate([0,keyboard_y,15+keyboard_z_shift])rotate([keyboard_slope,0,0])for(k=keys)translate([k[0],k[1],0])switch_housing();
}
module interior_shape(p) {
    if(p=="fan-retainers")fan_retainers();
    if(p=="fan-cushions")fan_cushions();
    if(p=="psu-grommets")psu_grommets();
    if(p=="drive-adapter-boards")drive_adapter_boards();
    if(p=="drive-adapter-traces")drive_adapter_traces();
    if(p=="drive-adapter-sockets")drive_adapter_sockets();
    if(p=="drive-adapter-edge")drive_adapter_edge();
    if(p=="drive-adapter-contacts")drive_adapter_contacts();
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
    if(p=="logic-artwork")logic_artwork();
    if(p=="logic-chips")logic_chips();
    if(p=="logic-pins")logic_pins();
    if(p=="logic-connectors")logic_connectors();
    if(p=="psu-chassis")psu_chassis();
    if(p=="psu-cover")psu_cover();
    if(p=="fan-frame")fan_frame();
    if(p=="fan-rotor")fan_rotor();
    if(p=="ribbon-cables")ribbons();
    if(p=="ribbon-ridges")ribbon_ridges();
    if(p=="drive-cable-plugs"){
      drive_pair()teac_cable_plug(adapter=true);
      // Removable ribbon plug seats in the pale adapter socket, not at the
      // drive edge connector already occupied by the adapter itself.
      for(x=[-158,-4])translate([x-16.5,-13,84])cube([33,5,7]);
    }
    if(p=="ribbon-stripes")ribbon_stripes();
    if(p=="power-wires-red")power_wires(0);
    if(p=="power-wires-black")power_wires(2.2);
    if(p=="power-wires-yellow")power_wires(4.4);
    if(p=="keyboard-pcb")keyboard_pcb();
    if(p=="keyboard-switches")keyboard_switches();
}
