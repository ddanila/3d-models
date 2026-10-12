// Owner photographs, 2026-10-12. Original MIT geometry, clean condition.
// Feature dimensions/positions are estimates, not an electrical reconstruction.
// Component pitch is nominal 2.54 mm; board envelope inferred from DIP-40.
module keyboard_controller_pose() {
    translate([-65,keyboard_y+74,8]) children();
}
// x,y,pins,row spacing; positions follow 123622947, not a generic chip grid.
controller_dips=[[62,8,40,15.24],[20,-12,14,7.62],[20,12,14,7.62],
 [57,-12,20,7.62],[89,-12,16,7.62],[114,-12,14,7.62],[-48,-12,16,7.62],[-48,12,14,7.62]];
module owner_dip_body(p) {
 translate([p[0],p[1],2.6]) difference(){
  slab((p[2]/2-1)*2.54+3,p[3]-1.7,3.5,.6);
  translate([-(p[2]/2-1)*1.27-1.5,0,2.3])cylinder(d=3,h=2,$fn=20);
 }
}
module owner_dip_pins(p) {
 for(i=[0:p[2]/2-1],s=[-1,1])translate([p[0]+(i-(p[2]/2-1)/2)*2.54,p[1]+s*p[3]/2,0]){
  translate([-.25,-.25,-.7])cube([.5,.5,3.8]);
  translate([-.4,min(0,-s*1.4),2.7])cube([.8,1.4,.35]);
 }
}
module keyboard_controller_board(){keyboard_controller_pose()difference(){
 translate([-135,-23,0])cube([270,46,1.6]);
 for(x=[-130,130],y=[-18,18])translate([x,y,-1])cylinder(d=3.2,h=4);
}}
module keyboard_controller_chips(){keyboard_controller_pose(){
 for(p=controller_dips)owner_dip_body(p);
 // Socket below the photographed UB880D and socket below replacement EPROM.
 for(p=[[62,8,54,19],[114,8,34,19]])translate([p[0],p[1],1.6])difference(){slab(p[2],p[3],1.2,.6);slab(p[2]-4,p[3]-4,2,.4);}
 for(x=[-113,-104,-95,-86],y=[-12,5])translate([x,y,3])rotate([0,0,25])cube([4,3,5]);
}}
module keyboard_controller_ceramic(){keyboard_controller_pose(){
 translate([114,8,2.8])slab(32,13.5,3.5,.7);
 for(x=[-80,-74,-68,-62,-56,-50,-44,-38])translate([x,-2,3])rotate([90,0,0])cylinder(d=2.5,h=6,$fn=16);
}}
module keyboard_controller_rom_cover(){keyboard_controller_pose()translate([112,8,6.35])slab(18,13,.15,.2);}
module keyboard_controller_connectors(){keyboard_controller_pose(){
 translate([-10,3,1.6])difference(){slab(43,10,6,.6);translate([0,0,1])slab(36,5,7,.3);}
 for(x=[-33,13])translate([x,3,1.6])cube([3,15,4],center=true);
}}
module keyboard_controller_caps(){keyboard_controller_pose(){
 for(p=[[-124,10],[-118,-13],[-106,16],[-92,-15],[130,-10]])translate([p[0],p[1],1.6])cylinder(d=5,h=9,$fn=24);
}}
module keyboard_controller_metal(){keyboard_controller_pose(){
 for(p=controller_dips)owner_dip_pins(p);
 owner_dip_pins([114,8,24,15.24]);
 for(i=[0:12],s=[-1,1])translate([-25+i*2.54,3+s*2.54,2])cylinder(d=.65,h=4,$fn=8);
 for(p=[[-124,10],[-118,-13],[-106,16],[-92,-15],[130,-10]])translate([p[0],p[1],10.65])cylinder(d=4.5,h=.2,$fn=24);
 // Cable shield clamp, folded over the incoming lead.
 translate([-125,0,1.6])difference(){cube([8,22,5],center=true);rotate([0,90,0])cylinder(d=5.8,h=10,center=true,$fn=24);}
 for(x=[-130,130],y=[-18,18])translate([x,y,1.6])screw(5,1);
}}
module keyboard_controller_ink(){keyboard_controller_pose(){
 translate([62,8,6.15])linear_extrude(.08)text("UB880D",size=3,halign="center",valign="center",font="Liberation Sans");
 translate([128,8,6.35])slab(4,12,.12,.1);
}}
module keyboard_insulators(){
 translate([0,keyboard_y,11.2])rotate([keyboard_slope,0,0])for(y=[-64,54])translate([0,y,0])slab(472,10,1.5,.5);
}
module keyboard_matrix_artwork(){
 translate([0,keyboard_y,12.8])rotate([keyboard_slope,0,0]){
 // Simplified visible row buses only; deliberately no invented netlist.
 for(i=[0:7])translate([0,-55+i*14,0])cube([435,1,.15],center=true);
 for(k=keys)translate([k[0],k[1],-.1])difference(){cylinder(d=2.6,h=.25,$fn=12);cylinder(d=1,h=.4,$fn=8);}
 }
}
module system_foot_metal(){for(x=[-225,225],y=[-170,170])translate([x,y,-6]){
 slab(25,8,1,.4);for(s=[-1,1])translate([0,s*3.5,0])cube([25,1,2],center=true);
 translate([0,0,-1.5])rotate([180,0,0])screw(4.5,1.5);
}}
module monitor_under_controls(){
 for(x=[-112,112])translate([x,monitor_y-115,monitor_z-1])rotate([180,0,0]){
  cylinder(d1=38,d2=35,h=3,$fn=72);
  for(a=[0:6:354])rotate([0,0,a])translate([14,0,2])cube([7,.65,1.5],center=true);
  translate([0,0,3])cylinder(d=15,h=.8,$fn=48);
 }
 // Cable outlet boot, leaving a real recess in the lower shell.
 translate([72,monitor_y+30,monitor_z-2])difference(){slab(30,22,5,2);translate([0,0,-1])slab(21,12,7,1);}
}
module monitor_stand_metal(){
 translate([0,monitor_y,monitor_z-4])for(y=[-58,58])translate([0,y,0]){
  difference(){translate([-40,-6,-2])cube([80,12,2]);for(x=[-33,33])translate([x,0,-3])cylinder(d=3.5,h=5);}
  translate([-40,y<0?4:-6,-15])cube([80,2,15]);
  translate([0,0,-14])cylinder(d=5,h=14,$fn=24);
  translate([0,0,-10])cylinder(d=9,h=4,$fn=6);
 }
}
// Rear sockets in a local plane: X horizontal, Z vertical, Y toward viewer.
module rear_pose(x,z){translate([x,case_d/2-3,z])rotate([-90,0,0])children();}
rear_sockets=[[20,62,50,5,2],[20,20,72,12,2],[-78,20,72,12,2],[-179,20,65,13,3]];
module rear_enclosure_openings(){
 for(p=[[-85,43,300,80],[172,43,138,80]])rear_pose(p[0],p[1])translate([0,0,-5])slab(p[2],p[3],14,4);
}
module rear_panel(){difference(){
 for(p=[[-85,43,300,80],[172,43,138,80]])rear_pose(p[0],p[1])slab(p[2],p[3],1,4);
 rear_cutouts();
}}
module rear_cutouts(){
 for(p=rear_sockets)rear_pose(p[0],p[1])translate([0,0,-5])slab(p[2]+8,20,12,1);
 rear_pose(130,37)translate([0,0,-5])slab(29,23,12,2);
 rear_pose(205,51)translate([0,0,-5])slab(22,39,12,1);
}
module rear_socket_bodies(){
 for(p=rear_sockets)rear_pose(p[0],p[1])difference(){slab(p[2],15,5,.8);translate([0,0,1])slab(p[2]-12,10,7,.4);}
 rear_pose(205,51)difference(){slab(20,37,5,1);translate([0,0,1])for(v=[[-3,-9],[3,0],[-3,9]])translate([v[0],v[1],0])cylinder(d=5,h=6,$fn=24);}
}
module rear_socket_contacts(){
 for(p=rear_sockets)rear_pose(p[0],p[1])for(i=[0:p[3]-1],y=p[4]==3?[-3.5,0,3.5]:[-2.5,2.5])translate([(i-(p[3]-1)/2)*2.54,y,1])cube([.65,.65,3]);
 rear_pose(205,51)for(v=[[-3,-9],[3,0],[-3,9]])translate([v[0],v[1],1])difference(){cylinder(d=5,h=3,$fn=24);cylinder(d=3.8,h=4,$fn=24);}
 rear_pose(130,37)for(p=[[-7,-3],[7,-3],[0,5]])translate([p[0],p[1],1])cube([3,.7,3],center=true);
}
module rear_power_black(){
 rear_pose(130,37)difference(){slab(32,26,3,2);translate([0,0,1])slab(24,18,5,2);}
 for(z=[34,70])rear_pose(170,z){cylinder(d=16,h=3,$fn=48);translate([0,0,3])difference(){cylinder(d=12,h=3,$fn=32);translate([-5,-.7,2])cube([10,1.4,2]);}}
}
module rear_blanking_plates(){for(p=[[-78,73],[-179,73],[-78,52]])rear_pose(p[0],p[1])translate([0,0,1.2])slab(84,19,1.2,2);}
module rear_legends(){
 for(p=[[20,77,"DISPLAY"],[20,35,"V24"],[-78,35,"PRINTER"],[-179,35,"FLOPPY-DISK"],[170,82,"F1"],[170,47,"F2"],[-78,64,"GRAF.-DISPLAY"]])
 translate([p[0],case_d/2-1.8,p[1]])rotate([90,0,180])linear_extrude(.12)text(p[2],size=3,halign="center",font="Liberation Sans");
}
module specimen_shape(p){
 if(p=="keyboard-controller-board")keyboard_controller_board();
 if(p=="keyboard-controller-chips")keyboard_controller_chips();
 if(p=="keyboard-controller-ceramic")keyboard_controller_ceramic();
 if(p=="keyboard-controller-rom-cover")keyboard_controller_rom_cover();
 if(p=="keyboard-controller-connectors")keyboard_controller_connectors();
 if(p=="keyboard-controller-caps")keyboard_controller_caps();
 if(p=="keyboard-controller-metal")keyboard_controller_metal();
 if(p=="keyboard-controller-ink")keyboard_controller_ink();
 if(p=="keyboard-insulators")keyboard_insulators();
 if(p=="keyboard-matrix-artwork")keyboard_matrix_artwork();
 if(p=="system-foot-metal")system_foot_metal();
 if(p=="monitor-under-controls")monitor_under_controls();
 if(p=="monitor-stand-metal")monitor_stand_metal();
 if(p=="rear-panel")rear_panel();
 if(p=="rear-socket-bodies")rear_socket_bodies();
 if(p=="rear-socket-contacts")rear_socket_contacts();
 if(p=="rear-power-black")rear_power_black();
 if(p=="rear-blanking-plates")rear_blanking_plates();
 if(p=="rear-legends")rear_legends();
}
