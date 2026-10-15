// Owner photographs, 2026-10-12. Original MIT geometry, clean condition.
// Feature dimensions/positions are estimates, not an electrical reconstruction.
// Component pitch is nominal 2.54 mm; board envelope inferred from DIP-40.
module keyboard_controller_pose() {
    translate([keyboard_controller_x,keyboard_y+keyboard_controller_y,keyboard_controller_z]) children();
}
// x,y,pins,row spacing; positions follow 123622947, not a generic chip grid.
controller_dips=[[62,8,40,15.24],[20,-12,14,7.62],[20,12,14,7.62],
 [57,-12,20,7.62],[89,-12,16,7.62],[114,-12,14,7.62],[-48,-12,16,7.62],[-48,12,14,7.62]];
include <controller-package-data.scad>
function controller_package(p)=[for(m=controller_packages)if(m[0]==p[2])m][0];
function controller_seat(p)=p[2]==40 || p[2]==24 ? 2.8 : 1.6;
function controller_pin(p,q)=[p[0]+q[0],p[1]+q[1]];
module owner_dip_body(p) {
 translate([p[0],p[1],controller_seat(p)])rotate([0,0,-90])import(controller_package(p)[1]);
}
module owner_dip_pins(p) {
 translate([p[0],p[1],controller_seat(p)])rotate([0,0,-90])import(controller_package(p)[2]);
}
// Owner 123622947: staggered transistor population, not a rectangular grid.
// KiCad generic TO-92; no unverified electrical type or DDR mould identity.
controller_transistors=[[-120,4,0],[-113,-7,25],[-109,-15,25],
 [-105,-7,25],[-101,-10,25],[-97,-7,25],[-93,-10,25],[-89,-7,25],
 [-105,10,-25],[-100,11,-25],[-101,17,-25]];
module controller_transistor_pose(p){translate([p[0],p[1],1.6])rotate([0,0,p[2]])children();}
// Shared tail locations keep board apertures, joints and lead endpoints aligned.
controller_connector_tails=[for(i=[0:12],side=[-1,1])[-25+i*2.54,3+side*7]];
controller_resistor_tails=[for(x=[-80,-74,-68,-62,-56,-50,-44,-38],y=[-11,3])[x,y]];
// Paired end holes in detached photo 123622947; installed retainers are separate.
controller_end_holes=[for(x=[-133,133],y=[10,17.5])[x,y]];
module keyboard_controller_board(){keyboard_controller_pose()difference(){
 translate([-135,-23,0])cube([270,46,1.6]);
 for(p=controller_end_holes)translate(concat(p,[-1]))cylinder(d=3.2,h=4,$fn=24);
 for(p=concat(controller_connector_tails,controller_resistor_tails))translate([p[0],p[1],-1])cylinder(d=.85,h=4,$fn=16);
 for(p=controller_transistors)controller_transistor_pose(p)for(x=[-1.27,0,1.27])translate([x,0,-2])cylinder(d=.85,h=4,$fn=12);
 for(p=concat(controller_dips,[[114,8,24,15.24]]),q=controller_package(p)[3])
   translate(concat(controller_pin(p,q),[-1]))cylinder(d=1.05,h=4,$fn=16);
}}
module keyboard_controller_chips(){keyboard_controller_pose(){
 for(p=controller_dips)owner_dip_body(p);
 // Socket below the photographed UB880D and socket below replacement EPROM.
 for(p=[[62,8,54,19],[114,8,34,19]])translate([p[0],p[1],1.6])difference(){slab(p[2],p[3],1.2,.6);slab(p[2]-4,p[3]-4,2,.4);}
 for(p=controller_transistors)controller_transistor_pose(p)import("components/kicad/meshes/TO-92_Inline-body.stl");
}}
module keyboard_controller_ceramic(){keyboard_controller_pose(){
 translate([114,8,2.8])slab(32,13.5,3.5,.7);
 // Small ceramic discs beside the logic; axial resistors have their own finish.
 for(p=[[-40,-4],[13,-5],[38,-6],[78,-3],[105,-3]])
  translate([p[0],p[1],3])rotate([90,0,0])cylinder(d=3.8,h=1.2,$fn=24);
}}
module keyboard_controller_rom_cover(){keyboard_controller_pose()translate([112,8,6.35])slab(18,13,.15,.2);}
module keyboard_controller_connectors(){keyboard_controller_pose(){
 // Owner 123622947: pale closed bridge with moulded divisions and end ears.
 // Contact entry is on the side; the top is not an open rectangular trough.
 translate([-10,3,1.6])difference(){
  union(){slab(38,10,6,.5);slab(46,6,2,.5);}
  for(i=[0:11])translate([-13.7+i*2.54,0,5.7])cube([.18,10.2,.7],center=true);
  for(i=[0:12],side=[-1,1])translate([-15+i*2.54,side*4.7,2.6])cube([1,1.4,1.2],center=true);
 }
}}
module keyboard_controller_caps(){keyboard_controller_pose(){
 for(p=[[-124,10],[-118,-13],[-106,16],[-92,-15],[130,-10]])translate([p[0],p[1],1.6])cylinder(d=5,h=9,$fn=24);
}}
module keyboard_controller_metal(){keyboard_controller_pose(){
 for(p=controller_dips)owner_dip_pins(p);
 for(p=controller_transistors)controller_transistor_pose(p)import("components/kicad/meshes/TO-92_Inline-leads.stl");
 owner_dip_pins([114,8,24,15.24]);
 for(i=[0:12],s=[-1,1])translate([-25+i*2.54,3+s*2.54,2])cylinder(d=.65,h=4,$fn=8);
 for(p=[[-124,10],[-118,-13],[-106,16],[-92,-15],[130,-10]])translate([p[0],p[1],10.65])cylinder(d=4.5,h=.2,$fn=24);
 // Cable shield clamp, folded over the incoming lead.
 // Thin saddle, open below, with separate mounting ears (owner photo).
 translate([-125,0,4.5])intersection(){
  difference(){rotate([0,90,0])cylinder(r=3.9,h=8,center=true,$fn=48);rotate([0,90,0])cylinder(r=2.9,h=10,center=true,$fn=48);}
  translate([-5,-5,0])cube([10,10,5]);
 }
 for(s=[-1,1])translate([-125,s*3.4,1.6]){
  translate([-4,-.5,0])cube([8,1,2.9]);
  difference(){translate([-4,min(0,s*6),0])cube([8,6,1]);translate([0,s*3,-1])cylinder(d=2.8,h=3,$fn=24);}
 }
 translate([-125,-6.4,2.6])screw(4.5,1);
 // End holes are visibly unoccupied in the detached-board photograph.
}}
module keyboard_controller_ink(){keyboard_controller_pose(){
 translate([62,8,6.49])linear_extrude(.08)text("UB880D",size=3,halign="center",valign="center",font="Liberation Sans");
 // Only legible markings from owner photo 123622947; uncertain identities omitted.
 for(p=[[20,12,"К555ЛА9"],[20,-12,"К555ЛА9"],[-48,12,"К555ЛА9"],[89,-12,"К155ТМ2"],[114,-12,"К555ЛА7"]])
   translate([p[0],p[1],5.29])linear_extrude(.06)text(p[2],size=1.65,halign="center",valign="center",font="Liberation Sans");
 translate([128,8,6.35])slab(4,12,.12,.1);
}}
module keyboard_insulators(){
 translate([0,keyboard_y,28+keyboard_z_shift])rotate([keyboard_slope,0,0])translate([0,0,-16.718])for(y=[-75,43])translate([0,y,0])slab(482,10,1.5,.5);
}
// Visible underside buses from 123907435. This is artwork, not a netlist.
// Long paths and staggered diagonal jogs follow owner underside photo 123907435.
// Photo-derived geometry only: not a traced or continuity-tested circuit.
include <keyboard-artwork.scad>
module board_trace(path,width=.75,height=.12){
 for(i=[0:len(path)-2])hull()for(j=[i,i+1])translate([path[j][0],path[j][1],0])cylinder(d=width,h=height,$fn=12);
}
module keyboard_matrix_artwork(){keyboard_matrix_pose()translate([0,0,-14.998]){
 for(path=matrix_photo_paths)board_trace(path,.95,.08);
 for(path=matrix_photo_paths)for(i=[0,len(path)-1])translate(path[i])cylinder(d=2.1,h=.08,$fn=16);
}}
module keyboard_pcb_metal(){keyboard_matrix_pose(){
 // Owner photo 123048886: irregularly spaced solder joints, not screw heads.
 for(p=matrix_photo_pads)translate([p[0],p[1],-14.998])scale([1,1,.35])sphere(d=2.2,$fn=20);
 for(path=matrix_photo_paths)for(i=[0,len(path)-1])translate([path[i][0],path[i][1],-15.06])difference(){
  cylinder(d=1.2,h=.14,$fn=16);translate([0,0,-.1])cylinder(d=.5,h=.4,$fn=12);
 }
}}
// Routes digitized as clean polylines from owner 123622947 (top) and
// 123648677 (underside). Broad buses and diagonal breaks are photo estimates;
// hidden paths and electrical continuity have not been reconstructed.
module keyboard_controller_traces(){keyboard_controller_pose(){
 for(i=[0:4])translate([0,0,1.62])board_trace([
  [-128,-21+i*1.2],[-59-i*2,-21+i*1.2],[-51-i*2,-13+i*1.2],
  [-32,-13+i*1.2],[-26,-19+i*1.2],[25,-19+i*1.2],
  [31,-13+i*1.2],[88,-13+i*1.2],[96,-21+i*1.2],[129,-21+i*1.2]],.48,.08);
 // The broad top rail steps around the matrix connector and EPROM socket.
 translate([0,0,1.62])board_trace([[-84,1],[-57,1],[-53,6],[-34,6],[-30,13],
  [12,13],[16,4],[33,4],[38,-1],[93,-1],[97,-2],[129,-2]],1.4,.08);
 for(p=concat(controller_dips,[[114,8,24,15.24]]),q=controller_package(p)[3])
  let(v=controller_pin(p,q),side=q[1]<0?-1:1)
  translate([0,0,1.62]){
   translate(v)difference(){cylinder(d=1.7,h=.1,$fn=20);cylinder(d=1.05,h=.2,$fn=16);}
   board_trace([v,[v[0],v[1]+side*1.7],[v[0]+1.2,v[1]+side*2.9]],.45,.08);
  }
 // Manually registered underside segments, including the outer bus and CPU fanout.
 for(path=controller_photo_paths)translate([0,0,-.10])board_trace(path,.35,.10);
 for(path=controller_photo_paths)for(i=[0,len(path)-1])translate([path[i][0],path[i][1],-.10])cylinder(d=.9,h=.10,$fn=12);
 // Staggered transistor-stage routes and plated eyes (no invented values).
 for(p=controller_transistors)controller_transistor_pose(p)
  for(x=[-1.27,0,1.27])translate([x,0,-.1])difference(){cylinder(d=1.2,h=.1,$fn=20);cylinder(d=.85,h=.2,$fn=16);}
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
  slab(85,18,1,1.5); // Same 1 mm painted sheet as the rear panel.
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
 if(p=="keyboard-controller-leads")keyboard_controller_leads();
 if(p=="keyboard-entry-choke")keyboard_entry_choke();
 if(p=="keyboard-controller-resistors")keyboard_controller_resistors();
 if(p=="keyboard-controller-resistor-bands")keyboard_controller_resistor_bands();
 if(p=="keyboard-matrix-socket")keyboard_matrix_socket();
 if(p=="keyboard-matrix-contacts")keyboard_matrix_contacts();
 if(p=="keyboard-controller-board")keyboard_controller_board();
 if(p=="keyboard-controller-chips")keyboard_controller_chips();
 if(p=="keyboard-controller-ceramic")keyboard_controller_ceramic();
 if(p=="keyboard-controller-rom-cover")keyboard_controller_rom_cover();
 if(p=="keyboard-controller-connectors")keyboard_controller_connectors();
 if(p=="keyboard-controller-caps")keyboard_controller_caps();
 if(p=="keyboard-controller-metal")keyboard_controller_metal();
 if(p=="keyboard-controller-ink")keyboard_controller_ink();
 if(p=="keyboard-insulators")keyboard_insulators();
 if(p=="keyboard-controller-solder")keyboard_controller_solder();
 if(p=="keyboard-pcb-supports")keyboard_pcb_supports();
 if(p=="keyboard-pcb-fasteners")keyboard_pcb_fasteners();
 if(p=="keyboard-entry-wires")keyboard_entry_wires();
 if(p=="keyboard-entry-black")keyboard_entry_wires(1);
 if(p=="keyboard-entry-pink")keyboard_entry_wires(2);
 if(p=="keyboard-entry-blue")keyboard_entry_wires(3);
 if(p=="keyboard-contact-routes")keyboard_contact_routes();
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

// Insulating shoulder washers/supports aligned with the PCB's six real holes.
// Photo 123907435 establishes retained fasteners and dark insulating strips;
// diameters and stand-off height are estimates, not measured replacement parts.
module keyboard_pcb_supports(){
 translate([0,keyboard_y,28+keyboard_z_shift])rotate([keyboard_slope,0,0])
 for(x=[-220,0,220],y=[-65,33])translate([x,y,-18.418])difference(){
   cylinder(d=7,h=3.5,$fn=24);translate([0,0,-.1])cylinder(d=3.2,h=4,$fn=20);
 }
}
module keyboard_pcb_fasteners(){
 translate([0,keyboard_y,28+keyboard_z_shift])rotate([keyboard_slope,0,0])
 for(x=[-220,0,220],y=[-65,33])translate([x,y,-13.318]){
   difference(){cylinder(d=6,h=.4,$fn=24);translate([0,0,-.1])cylinder(d=3.2,h=.6,$fn=20);}
   translate([0,0,.4])screw(5,1);
 }
}
// Short lead bundle and strain relief at the owner-photographed controller entry.
// Routes are visual estimates; no undocumented electrical pinout is asserted.
module keyboard_entry_wires(i=0){keyboard_controller_pose()
 wire_run([[-121,-2+i*1.5,4.5],[-119,-7+i*3,6],[-116,-7+i*3,3]],.55);
}
module keyboard_contact_routes(){
 translate([0,keyboard_y,28+keyboard_z_shift])rotate([keyboard_slope,0,0])
 for(k=keys)translate([k[0],k[1],-13.31])for(side=[-1,1])
   board_trace([[side*2,0],[side*5,0],[side*6,3]],.5,.02);
}

// Clean lead-aligned underside joints and plated barrels. The original photo
// establishes soldered through-hole construction; joint profiles are estimates.
module controller_solder_eye(x,y,hole=1.05,outer=2.1){translate([x,y,-.55])difference(){
 union(){cylinder(d1=hole+.2,d2=outer,h=.55,$fn=24);translate([0,0,.5])cylinder(d=min(1.6,outer),h=1.7,$fn=20);}
 translate([0,0,-.1])cylinder(d=hole,h=2.4,$fn=16);
}}
module keyboard_controller_solder(){keyboard_controller_pose(){
 for(p=concat(controller_dips,[[114,8,24,15.24]]),q=controller_package(p)[3])
  let(v=controller_pin(p,q))controller_solder_eye(v[0],v[1]);
 for(p=controller_transistors)translate([p[0],p[1],0])rotate([0,0,p[2]])
  for(x=[-1.27,0,1.27])controller_solder_eye(x,0,.85,1.2);
 for(p=concat(controller_connector_tails,controller_resistor_tails))controller_solder_eye(p[0],p[1],.85,1.7);
 for(p=controller_end_holes)translate([p[0],p[1],-.15])difference(){cylinder(d=3.8,h=.15,$fn=24);translate([0,0,-.1])cylinder(d=3.2,h=.6,$fn=16);}
}}

// Bent connector tails and axial leads visible in 123622947. Nominal diameters.
module keyboard_controller_leads(){keyboard_controller_pose(){
 for(i=[0:12],side=[-1,1])wire_run([[-25+i*2.54,3+side*2.54,4],[-25+i*2.54,3+side*7,2.2],[-25+i*2.54,3+side*7,-.5]],.28);
 for(x=[-80,-74,-68,-62,-56,-50,-44,-38])for(y=[-9,1])
  wire_run([[x,y,3],[x,y+(y<0?-2:2),3],[x,y+(y<0?-2:2),-.5]],.25);
}}
module keyboard_entry_choke(){keyboard_controller_pose(){
 translate([-115,3,4])rotate([90,0,0])difference(){cylinder(d=7,h=4,$fn=32);translate([0,0,-1])cylinder(d=3.2,h=6,$fn=24);}
 for(i=[0:3])wire_run([[-118+i,4,4],[-118+i,3,8],[-118+i,-2,8],[-118+i,-3,3]],.3);
}}

// Owner matrix-board socket: stepped pale body, mounting ears, recessed mouth
// and two rows of bent contacts. Envelope and seating depth are photo estimates.
module keyboard_matrix_pose(){
 translate([0,keyboard_y,28+keyboard_z_shift])rotate([keyboard_slope,0,0])children();
}
module keyboard_matrix_socket(){keyboard_matrix_pose()
 translate([85,48,-20.918])difference(){
  union(){slab(42,10,6,.6);translate([0,-1,0])slab(34,14,6,.6);slab(52,8,2,.6);}
  translate([0,0,-.1])slab(30,2.2,4,.3);
  // Molded connector legend visible in owner 123103225, clean relief only.
  translate([0,-3.6,.24])rotate([0,180,180])linear_extrude(.25)text("2У0",size=2.1,halign="center",valign="center",font="Liberation Sans:style=Bold");
  for(x=[-23,23])translate([x,1,-1])cylinder(d=2.8,h=8,$fn=20);
 }}
module keyboard_matrix_contacts(){keyboard_matrix_pose(){
 // Visible tails turn toward the board's long trace buses. No pinout implied.
 for(i=[0:12],row=[0:1])let(x=85+(i-6)*2.54,y=39-row*2.54){
  wire_run([[x,44,-18],[x,y,-18],[x,y,-14.98]],.23);
  translate([x,y,-15.38])difference(){cylinder(d=1.7,h=.45,$fn=16);cylinder(d=.55,h=.5,$fn=12);}
 }
}}

// Owner 123622947: grey axial resistor bodies and blue end bands, separate from
// the brown ceramic EPROM. Values are deliberately not inferred from colours.
module keyboard_controller_resistors(){keyboard_controller_pose()
 for(x=[-80,-74,-68,-62,-56,-50,-44,-38])translate([x,-2,3])rotate([90,0,0])
  cylinder(d=2.3,h=6,$fn=24);
}
module keyboard_controller_resistor_bands(){keyboard_controller_pose()
 for(x=[-80,-74,-68,-62,-56,-50,-44,-38],y=[-2.35,-7.35])translate([x,y,3])rotate([90,0,0])
  difference(){cylinder(d=2.34,h=.55,$fn=24);translate([0,0,-.1])cylinder(d=2.28,h=.8,$fn=24);}
}

// Installed photo 123907435: one retained screw in each paired end-hole group.
// Visible straps only; unseen threads and chassis attachment remain unmeasured.
module keyboard_controller_mounts(){keyboard_controller_pose()
 for(x=[-133,133])translate([x,17.5,0]){
  translate([0,0,-.15])rotate([180,0,0]){
   difference(){cylinder(d=5.4,h=.45,$fn=24);translate([0,0,-.1])cylinder(d=3.2,h=.7,$fn=20);}
   translate([0,0,.45])screw(4.6,1);
  }
  cylinder(d=2.8,h=2.6,$fn=20);
  translate([0,3,1.6])difference(){slab(7,14,1,1);translate([0,-3,-.1])cylinder(d=3.2,h=1.3,$fn=20);}
 }
}
// Clean braided shield pigtail, not the individual frayed strands in 123539882.
// The braid leaves the stripped jacket and terminates on the broad tinned land.
module keyboard_controller_shield(){keyboard_controller_pose(){
 for(hand=[-1,1],strand=[0:3])wire_run([for(i=[0:24])let(t=i/24,a=hand*t*720+strand*90)
  [-122-8*min(1,t*2)+.6*cos(a),-1+13*t,5.2-2.6*t+.6*sin(a)]],.12);
 translate([-130,12,2.31])scale([1.3,1,.35])sphere(d=4,$fn=28);
 // Broad solderable ground land, clean nominal surface.
 difference(){
  translate([-131,14,1.61])slab(8,16,.12,.4);
  for(p=controller_end_holes)translate([p[0],p[1],1.5])cylinder(d=3.2,h=.5,$fn=24);
 }
}}
