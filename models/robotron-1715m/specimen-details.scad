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
 translate([0,keyboard_y,11.2])rotate([keyboard_slope,0,0])for(y=[-75,43])translate([0,y,0])slab(482,10,1.5,.5);
}
// Visible underside buses from 123907435. This is artwork, not a netlist.
function matrix_bus(i) = let(y=-62+i*13)
 [[-231+i%3*9,y],[25+i*4,y],[32+i*4,y+7],[85+i*2,y+7],
  [92+i*2,y],[223-i%3*13,y]];
module board_trace(path,width=.75,height=.12){
 for(i=[0:len(path)-2])hull()for(j=[i,i+1])translate([path[j][0],path[j][1],0])cylinder(d=width,h=height,$fn=12);
}
module keyboard_matrix_artwork(){
 translate([0,keyboard_y,12.8])rotate([keyboard_slope,0,0]){
  for(i=[0:7])board_trace(matrix_bus(i),1.5);
  for(i=[0:7],j=[0,5])translate(matrix_bus(i)[j])cylinder(d=3,h=.12,$fn=20);
  // Narrow parallel bundle joining the controller side of the broad board.
  for(i=[0:5])board_trace([[-65+i*1.6,12],[-35+i*1.6,12],[-24+i*1.6,24],[56,24+i*1.3],[69,38+i*1.3],[180,38+i*1.3]],.6);
 }
}
module keyboard_pcb_metal(){
 translate([0,keyboard_y,12.55])rotate([keyboard_slope,0,0]){
  for(i=[0:7],j=[0,5])translate(matrix_bus(i)[j])difference(){cylinder(d=1.6,h=.23,$fn=20);translate([0,0,-.1])cylinder(d=.65,h=.5,$fn=12);}
  // Clean screw heads and through-board solder points visible in the photos.
  for(x=[-214,-152,-82,-12,58,128,198],y=[-51,1,32])translate([x,y,0])rotate([180,0,0])screw(3.5,.6);
 }
}
module keyboard_controller_traces(){keyboard_controller_pose(){
 // Parallel edge routing and local lead fan-outs, photo-estimated. Component
 // identities/lead pitch are retained; these visual routes are not electrical.
 for(i=[0:4])translate([0,0,1.65])board_trace([[-125,-21+i],[-62-i*2,-21+i],[-55-i*2,-14+i],[-8,-14+i],[-2,-20+i],[127,-20+i]],.45);
 for(p=controller_dips,i=[0:p[2]/2-1],side=[-1,1])
  let(x=p[0]+(i-(p[2]/2-1)/2)*2.54,y=p[1]+side*p[3]/2)
  translate([0,0,1.65]){
   translate([x,y,0])difference(){cylinder(d=1.5,h=.12,$fn=12);cylinder(d=.7,h=.2,$fn=12);}
   board_trace([[x,y],[x,y+side*2],[x+1,y+side*3]],.45);
  }
 // Solder side remains inspectable when orbiting below the controller.
 for(i=[0:11])translate([0,0,-.12])board_trace([[-115,-18+i*2.4],[-32-i,-18+i*2.4],[-24-i,-10+i*2.4],[100-i,-10+i*2.4]],.4);
}}
module system_foot_metal(){
 for(x=[-225,225],y=[-170,170])translate([x,y,-3])specimen_foot_insert();
}
module monitor_under_controls(){
 for(x=[-112,112])translate([x,monitor_y-115,monitor_z-1])rotate([180,0,0]){
  cylinder(d1=38,d2=35,h=3,$fn=72);
  for(a=[0:6:354])rotate([0,0,a])translate([14,0,2])cube([7,.65,1.5],center=true);
  translate([0,0,3])cylinder(d=15,h=.8,$fn=48);
 }
 // Cable outlet boot, leaving a real recess in the lower shell.
 translate([108,monitor_y+25,monitor_z-2])difference(){slab(34,63,4,1);translate([0,0,-1])slab(23,49,6,.5);}
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
// Owner October 12 close-ups; local connector sizes are photo estimates.
// Local +Z faces out of the back, local +Y points down in the rear view.
module rear_pose(x,z){translate([x,case_d/2-3,z])rotate([-90,0,0])children();}
// [X, height, cutout width, columns, rows, body width, body height]
rear_sockets=[[10,43,64,5,2,24,14],[20,14,88,13,2,41,14],[-78,14,88,13,2,41,14],[-179,20,78,13,3,41,20]];
module rear_enclosure_openings(){
 for(p=[[-85,43,300,80],[172,43,138,80]])rear_pose(p[0],p[1])translate([0,0,-5])slab(p[2],p[3],14,4);
}
module rear_cutouts(){
 for(p=rear_sockets)rear_pose(p[0],p[1])translate([0,0,-5])slab(p[2],p[6]+6,12,.5);
 rear_pose(130,40)translate([0,0,-5])slab(26,37,12,4);
 rear_pose(205,41)translate([0,0,-5])slab(22,44,12,.6);
 rear_pose(-198,51)translate([0,0,-5])cylinder(d=4,h=12,$fn=24);
 for(x=[43,-25])rear_pose(x,43)translate([0,0,-5])slab(1,5,12,.1);
}
module rear_panel(){difference(){
 for(p=[[-85,43,300,80],[172,43,138,80]])rear_pose(p[0],p[1])slab(p[2],p[3],1,4);
 rear_cutouts();
}}
module rear_recesses(){
 // Dark recessed trays leave space around the connectors, rather than filling
 // each large panel opening with an oversized connector face.
 for(p=rear_sockets)rear_pose(p[0],p[1])translate([0,0,-8])difference(){
  slab(p[2]+1,p[6]+7,7,.7);translate([0,0,1])slab(p[2]-1,p[6]+5,8,.4);
 }
 rear_pose(205,41)translate([0,0,-6])slab(22,44,1,.5);
 rear_pose(-198,51)translate([0,0,-3])cylinder(d=4,h=.5,$fn=24);
}
module rear_socket_bodies(){
 // Separate stepped retaining blocks at both ends of each insert.
 for(p=rear_sockets)rear_pose(p[0],p[1])for(side=[-1,1]){
  translate([side*(p[5]/2+4),0,-4])slab(8,p[6]-1,5,.5);
  translate([side*(p[5]/2+4),0,1])slab(7,p[6]-4,1.5,.3);
  translate([side*(p[5]/2+4),0,2.5])slab(7,.45,.3,.1);
 }
 // Retaining bridge around the monitor power connector.
 rear_pose(205,41)for(y=[-18,18])translate([0,y,-1])difference(){
  slab(20,7,4,.5);translate([-4,0,-1])cylinder(d=4,h=6,$fn=20);
 }
}
module rear_socket_inserts(){
 for(p=rear_sockets)rear_pose(p[0],p[1])difference(){
  translate([0,0,-4])slab(p[5],p[6],7,.5);
  translate([0,0,-2])slab(p[5]-2.8,p[6]-2.8,7,.25);
  // The keyed reliefs in the lower/side lips are visible in the owner photos.
  translate([p[5]*.18,p[6]/2,1])cube([2,4,5],center=true);
  translate([-p[5]/2,2,1])cube([3,3,5],center=true);
  for(i=[0:p[3]-1],j=[0:p[4]-1])
   translate([(i-(p[3]-1)/2)*(p[3]==5?3.5:2.54),(j-(p[4]-1)/2)*3.5,-5])cube([.9,.9,4],center=true);
 }
 // Three contact sleeves and two unplated alignment holes, not five contacts.
 rear_pose(205,41)translate([0,0,-3])difference(){
  slab(18,30,4,.5);
  for(v=[[3,-9],[-3,0],[3,9],[-3,-9],[-3,9]])translate([v[0],v[1],-1])cylinder(d=4.5,h=6,$fn=24);
 }
}
module rear_socket_contacts(){
 for(p=rear_sockets)rear_pose(p[0],p[1])for(i=[0:p[3]-1],j=[0:p[4]-1])
  // V24 has alternating populated positions in the specimen close-up.
  if(p[0]!=20 || (i+j)%2==0)
   translate([(i-(p[3]-1)/2)*(p[3]==5?3.5:2.54),(j-(p[4]-1)/2)*3.5,-2])cube([.65,.65,4]);
 rear_pose(205,41)for(v=[[3,-9],[-3,0],[3,9]])translate([v[0],v[1],-2])difference(){
  cylinder(d=4.5,h=3,$fn=28);translate([0,0,-.1])cylinder(d=3.3,h=3.2,$fn=24);
 }
 // Vertically mounted mains inlet: blades are inside the recessed shroud.
 rear_pose(130,40)for(v=[[-4,0],[4,-6],[4,6]])translate([v[0],v[1],-1])cube([.8,3,5],center=true);
}
module mains_outline(w,h){offset(r=1)polygon([[-w/2,-h/2+4],[-w/2+5,-h/2],[w/2-5,-h/2],[w/2,-h/2+4],[w/2,h/2-4],[w/2-5,h/2],[-w/2+5,h/2],[-w/2,h/2-4]]);}
module rear_power_black(){
 rear_pose(130,40)difference(){
  union(){linear_extrude(1.8)mains_outline(28,49);translate([0,0,-4])linear_extrude(8)mains_outline(23,31);}
  translate([0,0,-3])linear_extrude(10)mains_outline(17,25);
  for(y=[-22,22])translate([0,y,-1])cylinder(d=3.4,h=5,$fn=24);
 }
 for(z=[29,52])rear_pose(170,z){
  cylinder(d=15,h=1.4,$fn=48);
  translate([0,0,1.4])difference(){
   cylinder(d=12.5,h=2,$fn=48);
   for(a=[0,90])rotate([0,0,a])translate([0,0,1.3])cube([9,1.5,2],center=true);
  }
 }
}
module rear_blanking_plates(){
 for(p=[[-78,73],[-179,73],[-78,48]])rear_pose(p[0],p[1])translate([0,0,.8]){
  slab(85,18,1.2,1.5);translate([0,0,1.2])slab(83,16,.4,1.5);
 }
}
module rear_fasteners(){
 rear_pose(130,40)for(y=[-22,22])translate([0,y,1.8])screw(5,1);
 for(p=rear_sockets)rear_pose(p[0],p[1])for(side=[-1,1])translate([side*(p[5]/2+11),0,-1])screw(3,1);
 for(x=[-230,230])rear_pose(x,103)translate([0,0,2])screw(5,1);
}
module rear_nameplate(){rear_pose(24,72)translate([0,0,1.05])slab(75,16,.2,.15);}
module rear_text(x,z,t,size=3){translate([x,case_d/2-1.8,z])rotate([90,0,180])linear_extrude(.06)difference(){
 text(t,size=size,halign="center",font="Liberation Sans");
 offset(delta=-.11)text(t,size=size,halign="center",font="Liberation Sans");
 }}
module rear_legends(){
 for(p=[[10,56,"DISPLAY"],[20,29,"V24"],[-78,29,"PRINTER"],[-179,38,"FLOPPY-DISK"],[-78,60,"GRAF.-DISPLAY"],[205,70,"DISPLAY"],[130,72,"220V~"],[-179,52,"A"],[-23,71,"B"]])rear_text(p[0],p[1],p[2]);
 for(p=[[180,62,"F1"],[180,57,"T1,6"],[180,19,"F2"],[180,14,"T1,6"]])rear_text(p[0],p[1],p[2],2.3);
}
module rear_nameplate_ink(){
 // Clean printed field borders from 125413618; stamped values remain typeset.
 for(z=[74.8,68.8])translate([5,case_d/2-1.65,z])rotate([90,0,180])linear_extrude(.06)
  difference(){square([28,4.8],center=true);square([27.65,4.45],center=true);}

 for(p=[[45,74,"Typ W",2.5],[5,74,"1715/330",2.7],[42,68,"Masch.-Nr.",2.1],[5,68,"67581",2.7]])
 translate([p[0],case_d/2-1.65,p[1]])rotate([90,0,180])linear_extrude(.06)text(p[2],size=p[3],halign="center",font="Liberation Sans");
}
module specimen_shape(p){
 if(p=="rear-recesses")rear_recesses();
 if(p=="rear-socket-inserts")rear_socket_inserts();
 if(p=="rear-fasteners")rear_fasteners();
 if(p=="rear-nameplate")rear_nameplate();
 if(p=="rear-nameplate-ink")rear_nameplate_ink();
 if(p=="keyboard-controller-board")keyboard_controller_board();
 if(p=="keyboard-controller-chips")keyboard_controller_chips();
 if(p=="keyboard-controller-ceramic")keyboard_controller_ceramic();
 if(p=="keyboard-controller-rom-cover")keyboard_controller_rom_cover();
 if(p=="keyboard-controller-connectors")keyboard_controller_connectors();
 if(p=="keyboard-controller-caps")keyboard_controller_caps();
 if(p=="keyboard-controller-metal")keyboard_controller_metal();
 if(p=="keyboard-controller-ink")keyboard_controller_ink();
 if(p=="keyboard-insulators")keyboard_insulators();
 if(p=="keyboard-pcb-metal")keyboard_pcb_metal();
 if(p=="keyboard-controller-traces")keyboard_controller_traces();
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
