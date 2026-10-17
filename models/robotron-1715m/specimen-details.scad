// Owner photographs, 2026-10-12. Original MIT geometry, clean condition.
// Feature dimensions/positions are estimates, not an electrical reconstruction.
// Component pitch is nominal 2.54 mm; board envelope inferred from DIP-40.
module keyboard_controller_pose() {
    translate([keyboard_controller_x,keyboard_y+keyboard_controller_y,keyboard_controller_z]) children();
}
// Native PCB owns DIP and placed resistor geometry, pads, outline and artwork.
// Unplaced/discrete reconstruction remains explicitly photo-estimated below.
include <keyboard-controller/generated/controller.scad>
function controller_dip(ref)=[for(p=controller_pcb_dips)if(p[4]==ref)p][0];
controller_dips=[for(p=controller_pcb_dips)if(p[4]!="A8")p];
controller_rom=controller_dip("A8");
module controller_rom_pose(z){translate([controller_rom[0],controller_rom[1],z])rotate([0,0,controller_rom[5]])children();}
include <controller-package-data.scad>
function controller_package(p)=[for(m=controller_packages)if(m[0]==p[2])m][0];
function controller_seat(p)=p[2]==40 || p[2]==24 ? 2.8 : 1.6;
function controller_pin(p,q)=[p[0]+q[0]*cos(p[5])-q[1]*sin(p[5]),p[1]+q[0]*sin(p[5])+q[1]*cos(p[5])];
module owner_dip_body(p) {
 translate([p[0],p[1],controller_seat(p)])rotate([0,0,p[5]-90])import(controller_package(p)[1]);
}
module owner_dip_pins(p) {
 translate([p[0],p[1],controller_seat(p)])rotate([0,0,p[5]-90])import(controller_package(p)[2]);
}
// Owner 123622947: staggered transistor population, not a rectangular grid.
// KiCad generic TO-92; no unverified electrical type or DDR mould identity.
controller_transistors=[[-118.395, -12.014, 0], [-104.408, -12.666, 25], [-99.738, -12.884, 25], [-93.813, -6.933, 25], [-88.123, -6.539, 25], [-82.426, -6.145, 25], [-77.894, -5.533, 25], [-97.96, 8.316, -25], [-92.928, 10.056, -25]];
module controller_transistor_pose(p){translate([p[0],p[1],1.6])rotate([0,0,p[2]])children();}
// Shared tail locations keep board apertures, joints and lead endpoints aligned.
controller_connector_tails=[for(i=[0:12],side=[-1,1])[-25+i*2.54,3+side*7]];
// Photo projected resistor positions; three ROM/CPU-end placements adjusted
// within the approximate photo registration to clear nominal package bodies.
controller_legacy_resistors=[[-86.028, 13.759, 87.631, 11.611], [-82.182, 13.59, 87.642, 11.616], [-78.334, 13.421, 87.647, 11.62], [68.794, -5.2, 84.875, 8.317], [80.052, -4, 1.38, 9.676], [128, -8.522, 86.55, 9.355]];
// Placed sensing resistors and output pull-ups inherit native pad geometry.
controller_resistors=concat(controller_legacy_resistors,controller_pcb_resistors);
function resistor_end(p,s)=[p[0]+s*p[3]/2*cos(p[2]),p[1]+s*p[3]/2*sin(p[2])];
controller_legacy_resistor_tails=[for(p=controller_legacy_resistors,s=[-1,1])resistor_end(p,s)];
controller_resistor_tails=concat(controller_legacy_resistor_tails,[for(p=controller_pcb_resistor_pads)[p[0],p[1]]]);
// Paired end holes in detached photo 123622947; installed retainers are separate.
controller_end_holes=[for(x=[-133,133],y=[10,17.5])[x,y]];
module keyboard_controller_board(){keyboard_controller_pose()difference(){
 linear_extrude(1.6)polygon(controller_pcb_outline);
 for(p=controller_end_holes)translate(concat(p,[-1]))cylinder(d=3.2,h=4,$fn=24);
 for(p=concat(controller_connector_tails,controller_legacy_resistor_tails))translate([p[0],p[1],-1])cylinder(d=.85,h=4,$fn=16);
 for(p=controller_transistors)controller_transistor_pose(p)for(x=[-1.27,0,1.27])translate([x,0,-2])cylinder(d=.85,h=4,$fn=12);
 for(p=concat(controller_pcb_dip_pads,controller_pcb_resistor_pads))translate([p[0],p[1],-1])cylinder(d=p[2],h=4,$fn=16);
}}
module keyboard_controller_chips(){keyboard_controller_pose(){
 for(p=controller_dips)owner_dip_body(p);
 // Socket below the photographed UB880D and socket below replacement EPROM.
 for(ref=["A5","A8"])let(p=controller_dip(ref),length=ref=="A5"?54:34)translate([p[0],p[1],1.6])rotate([0,0,p[5]])difference(){slab(length,19,1.2,.6);slab(length-4,15,2,.4);}
 for(p=controller_transistors)controller_transistor_pose(p)import("components/kicad/meshes/TO-92_Inline-body.stl");
}}
module keyboard_controller_ceramic(){keyboard_controller_pose(){
 controller_rom_pose(2.8)slab(32,13.5,3.5,.7);
 // Small ceramic discs beside the logic; axial resistors have their own finish.
 for(p=[[-40,-4],[13,-5],[38,-6],[78,-3],[105,-3]])
  translate([p[0],p[1],3])rotate([90,0,0])cylinder(d=3.8,h=1.2,$fn=24);
}}
module keyboard_controller_rom_cover(){keyboard_controller_pose()controller_rom_pose(6.35)translate([-2,0,0])slab(18,13,.15,.2);}
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
 for(p=[[-114.695, 3.019], [-106.445, -2.752], [-101.335, 18.111], [132, -4.5]])translate([p[0],p[1],1.6])cylinder(d=5,h=9,$fn=24);
}}
module keyboard_controller_metal(){keyboard_controller_pose(){
 for(p=controller_dips)owner_dip_pins(p);
 for(p=controller_transistors)controller_transistor_pose(p)import("components/kicad/meshes/TO-92_Inline-leads.stl");
 owner_dip_pins(controller_rom);
 for(i=[0:12],s=[-1,1])translate([-25+i*2.54,3+s*2.54,2])cylinder(d=.65,h=4,$fn=8);
 for(p=[[-114.695, 3.019], [-106.445, -2.752], [-101.335, 18.111], [132, -4.5]])translate([p[0],p[1],10.65])cylinder(d=4.5,h=.2,$fn=24);
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
 let(p=controller_dip("A5"))translate([p[0],p[1],6.49])rotate([0,0,p[5]])linear_extrude(.08)text("U880D",size=3,halign="center",valign="center",font="Liberation Sans");
 // Only legible markings from owner photo 123622947; uncertain identities omitted.
 for(mark=[["A2.2","К555ЛА9"],["A2.1","К555ЛА9"],["A2.3","К555ЛА9"],["A6","К155ТМ2"],["A7","К555ЛА3"]])
   let(p=controller_dip(mark[0]))translate([p[0],p[1],5.29])rotate([0,0,p[5]])linear_extrude(.06)text(mark[1],size=1.65,halign="center",valign="center",font="Liberation Sans");
 controller_rom_pose(6.35)translate([12.2,0,0])slab(7.2,12,.12,.1);
 translate([-10,-16,1.72])linear_extrude(.06)text("5891",size=2.2,halign="center",font="Liberation Sans");
 translate([114,-20,1.72])linear_extrude(.06)text("05-330-4102",size=1.6,halign="center",font="Liberation Sans");
}}
// Owner 123114519 / 123126017: slotted brown edge strips with retained screws.
keyboard_mount_x=[-210,0,210];
keyboard_mount_rows=[-76,44];
module keyboard_insulators(){keyboard_matrix_pose()
 for(y=keyboard_mount_rows)translate([0,y,-16.418])difference(){
  slab(482,10,1.5,.5);
  for(x=keyboard_mount_x)hull()for(d=[0,6])translate([x,sign(y)*d,-.1])cylinder(d=3.2,h=1.7,$fn=24);
 }
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
// Clip only unassigned photo graphics at the physical board edge. The native
// review retains registration overshoot for inspection; this does not route it.
module controller_photo_art(paths,z,height){translate([0,0,z])intersection(){
 linear_extrude(height)polygon(controller_pcb_outline);
 union()for(a=paths)board_trace(a[0],a[1],height);
}}
module keyboard_controller_traces(){keyboard_controller_pose(){
 // Native KiCad review graphics retain their unresolved status. No generic
 // fanouts are invented to connect them to pads.
 controller_photo_art(controller_pcb_top_art,1.62,.08);
 controller_photo_art(controller_pcb_bottom_art,-.10,.10);
 for(a=controller_pcb_top_copper)translate([0,0,1.62])board_trace(a[0],a[1],.08);
 for(a=controller_pcb_bottom_copper)translate([0,0,-.10])board_trace(a[0],a[1],.10);
 for(p=controller_pcb_dip_pads)translate([p[0],p[1],1.62])difference(){cylinder(d=1.7,h=.1,$fn=20);cylinder(d=p[2],h=.2,$fn=16);}
 for(p=controller_legacy_resistor_tails)translate([p[0],p[1],1.62])difference(){cylinder(d=1.9,h=.1,$fn=16);cylinder(d=.85,h=.2,$fn=12);}
 for(p=controller_pcb_resistor_pads)translate([p[0],p[1],1.62])difference(){scale([p[3],p[4],1])cylinder(d=1,h=.1,$fn=20);cylinder(d=p[2],h=.2,$fn=16);}
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

// Case-mounted bent sheet supports, not floating cylindrical PCB spacers.
// Owner close-ups 123106382/123109703 and 123114519/123126017 establish
// separate tab levels and slotted edge-strip fasteners. Hidden attachment areas
// and exact bend radii remain nominal; original paint damage is not reproduced.
function matrix_mount_world(y,z)=[keyboard_y+y*cos(keyboard_slope)-z*sin(keyboard_slope),
  28+keyboard_z_shift+y*sin(keyboard_slope)+z*cos(keyboard_slope)];
module keyboard_mount_leaf(length=20,width=10,hole=3.2){
 difference(){
  linear_extrude(1)hull(){translate([-width/2,0])square([width,.01]);translate([0,length-width/2])circle(d=width,$fn=32);}
  translate([0,length-width/2,-.1])cylinder(d=hole,h=1.2,$fn=24);
 }
}
module keyboard_pcb_supports(){
 // Six leaves run from the shell wall to the edge strips. Each ends in a
 // rounded drilled tongue; its upright return actually meets the case wall.
 for(x=keyboard_mount_x,y=keyboard_mount_rows)let(p=matrix_mount_world(y,-14.918),
  wall_y=keyboard_y+(y<0?-99:68),reach=abs(wall_y-p[0])+4.5){
  translate([x,wall_y,p[1]])rotate([0,0,y<0?0:180])keyboard_mount_leaf(reach,9);
  translate([x-4.5,wall_y-(y>0?1:0),p[1]])cube([9,1,y>0?27-p[1]:5]);
  // Rear return meets the underside of the case shelf; front meets its wall.
  if(y>0)translate([x-4.5,wall_y-1,27])cube([9,7,1]);
 }
 // Two lower rear tabs support the narrow controller at its paired end holes.
 for(x=[keyboard_controller_x-133,keyboard_controller_x+133])
  let(y=keyboard_y+keyboard_controller_y+17.5,z=keyboard_controller_z+1.6){
   translate([x,keyboard_y+99,z])rotate([0,0,180])keyboard_mount_leaf(keyboard_y+99-y+5);
   translate([x-5,keyboard_y+98,z])cube([10,1,6]);
  }
}
module keyboard_pcb_fasteners(){keyboard_matrix_pose()
 for(x=keyboard_mount_x,y=keyboard_mount_rows)translate([x,y,-16.418]){
  // Heads face the removable bottom lid; shafts enter the case-mounted leaves.
  translate([0,0,-.4])difference(){cylinder(d=6,h=.4,$fn=24);translate([0,0,-.1])cylinder(d=3.2,h=.6,$fn=20);}
  translate([0,0,-.4])rotate([180,0,0])screw(5,1);
  cylinder(d=2.8,h=2.5,$fn=20);
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
 for(p=controller_pcb_dip_pads)controller_solder_eye(p[0],p[1],p[2]);
 for(p=controller_transistors)translate([p[0],p[1],0])rotate([0,0,p[2]])
  for(x=[-1.27,0,1.27])controller_solder_eye(x,0,.85,1.2);
 for(p=concat(controller_connector_tails,controller_legacy_resistor_tails))controller_solder_eye(p[0],p[1],.85,1.7);
 for(p=controller_end_holes)translate([p[0],p[1],-.15])difference(){cylinder(d=3.8,h=.15,$fn=24);translate([0,0,-.1])cylinder(d=3.2,h=.6,$fn=16);}
}}

// Bent connector tails and axial leads visible in 123622947. Nominal diameters.
module keyboard_controller_leads(){keyboard_controller_pose(){
 for(i=[0:12],side=[-1,1])wire_run([[-25+i*2.54,3+side*2.54,4],[-25+i*2.54,3+side*7,2.2],[-25+i*2.54,3+side*7,-.5]],.28);
 for(p=controller_resistors,s=[-1,1])let(end=resistor_end(p,s))
  wire_run([[p[0]+s*2.6*cos(p[2]),p[1]+s*2.6*sin(p[2]),3.2],[end[0],end[1],3.2],[end[0],end[1],-.5]],.25);
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
 for(p=controller_resistors)translate([p[0],p[1],3.2])rotate([0,0,p[2]])rotate([0,90,0])cylinder(d=2.3,h=5.2,center=true,$fn=24);
}
module keyboard_controller_resistor_bands(){keyboard_controller_pose()
 for(p=controller_resistors,s=len(p)>5 && p[5]!=0 ? [p[5]] : [-1,1])translate([p[0],p[1],3.2])rotate([0,0,p[2]])translate([s*2.1,0,0])rotate([0,90,0])
  difference(){cylinder(d=2.34,h=.55,center=true,$fn=24);cylinder(d=2.28,h=.8,center=true,$fn=24);}
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
  // The sheet support remains attached to the case in keyboard_pcb_supports().
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

// Owner ROM paper identifier; crisp clean text, no photographed staining.
module keyboard_controller_rom_ink(){keyboard_controller_pose()
 controller_rom_pose(6.49)translate([12.2,0,0])rotate([0,0,90])linear_extrude(.05)text("642",size=2.8,halign="center",valign="center",font="Liberation Sans");
}
