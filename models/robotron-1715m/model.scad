// Danila's Robotron 1715 M with a provisional reference interior.
// See README for measured vs inferred dimensions and unseen surfaces.
include <dimensions.scad>
include <keycap/geometry.scad>
keycap_facets=32;
include <keyboard-layout.scad>
include <monitor-profile.scad>
include <interior.scad>
include <monitor-interior.scad>
include <monitor-cables.scad>
include <assembly-details.scad>
include <specimen-details.scad>
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
    for(x=[-245,243])translate([x,-188,34])cube([2,376,7]);
    difference() {
        translate([-case_w/2,-case_d/2,0]) rounded([case_w,case_d,seam_z],4);
        translate([-case_w/2+wall,-case_d/2+wall,wall]) cube([case_w-2*wall,case_d-2*wall,seam_z]);
        for(x=[-224,224],y=[-170,170])translate([x,y,-1])cylinder(d=8,h=3,$fn=24);
        rear_enclosure_openings();
        translate([-208,-case_d/2+5,17])rotate([90,0,0])slab(17.5,17.5,10,2);
        for(y=[-95:10:15]) side_slot(y,22,20);
        for(y=[90:10:190]) side_slot(y,22,20);
        translate([-case_w/2-2,-164,15]) cube([10,38,14]);
    }
}
module case_lid() {
    // Owner 150009163: two shallow folded stiffening channels under the roof.
    for(x=[-80,80])translate([x,-184,case_h-wall-5])difference(){
        cube([8,368,5]);translate([1,-1,-1])cube([6,370,5]);
    }
    difference() {
        translate([-case_w/2,-case_d/2,seam_z+1]) rounded([case_w,case_d,case_h-seam_z-1],5);
        translate([-case_w/2+wall,-case_d/2+wall,seam_z-2]) cube([case_w-2*wall,case_d-2*wall,case_h-seam_z-wall+2]);
        translate([-case_w/2-1,-case_d/2-1,seam_z]) cube([case_w+2,wall+3,case_h]);
        rear_enclosure_openings();
        for(y=[-165:10:-35]) side_slot(y,72,42);
        for(y=[50:10:180]) side_slot(y,72,42);
        for(x=[-232,232])translate([x,case_d/2+1,64])rotate([90,0,0])cylinder(d=6,h=5,$fn=24);
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
module drives(unit=-1) {
    for(x=unit<0?[-158,-4]:[[-158,-4][unit]]) translate([x,-case_d/2-6,81]) rotate([90,0,0]) difference() {
        slab(146,42,2.5,2);
        translate([0,8,-1]) slab(140,3.5,5,1);
        translate([4,-2,-1]) slab(41,25,5,1.5);
        translate([-60,15,-1]) slab(11,4,5,.7);
    }
}
module drive_insets(unit=-1) {
    for(x=unit<0?[-158,-4]:[[-158,-4][unit]]) translate([x,-case_d/2-3,81]) rotate([90,0,0]) {
        difference(){slab(144,40,1,1);translate([0,8,-1])slab(140,3.5,3,1);}
        // Recessed central finger well, with the insertion slot above it.
        translate([4,-3,1]) slab(39,20,1,1);
    }
}
module drive_lever_outline() {
    offset(r=.8)offset(delta=-.8)union(){
        circle(d=12,$fn=48);
        polygon([[0,6],[13,0],[30,2],[30,-5],[0,-6]]);
    }
}
module drive_latches(unit=-1) {
    for(x=unit<0?[-158,-4]:[[-158,-4][unit]]) translate([x+45,-case_d/2-9,92]) rotate([90,0,0]) {
        cylinder(d=13,h=2,$fn=48);
        linear_extrude(5)drive_lever_outline();
    }
}
module drive_latch_trim(unit) {
    translate([[-158,-4][unit]+45,-case_d/2-9,92]) rotate([90,0,0])
        translate([0,0,5.05])linear_extrude(.25)difference(){
            drive_lever_outline();offset(delta=-.45)drive_lever_outline();
        }
}
module drive_direction(unit) {
    translate([[-158,-4][unit]+45,-case_d/2-8.7,77])rotate([90,0,0])linear_extrude(.12){
        difference(){circle(r=12,$fn=64);circle(r=10.8,$fn=64);translate([-15,0])square([30,16]);translate([-15,-15])square([15,30]);}
        polygon([[0,-9],[0,-14],[-5,-11.5]]);
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
// Nearly flush grey reset pad from owner close-up 124827690.
module reset_pad(){
 translate([-208,-case_d/2+1.2,17])rotate([90,0,0])slab(16,16,.8,1.7);
}
module pedestal() {
    // Owner underside shows an open annular stand, not a solid puck.
    translate([0,monitor_y,case_h+ring_h])difference(){
        cylinder(d1=171,d2=160,h=45,$fn=96);
        translate([0,0,-1])cylinder(d1=165,d2=154,h=47,$fn=96);
    }
}
module ring() {
    translate([0,monitor_y,case_h]) difference(){cylinder(d=ring_od,h=ring_h);translate([0,0,-1])cylinder(d=ring_id,h=ring_h+2);}
}
// Both shell halves and their inner mating lip share this tapered envelope.
module monitor_envelope() {
    // Owner side/underside views: parallel cabinet walls, rounded edges only.
    translate([-monitor_w/2,-monitor_d/2,0])rounded([monitor_w,monitor_d,monitor_h],10);
}
module monitor_shell() {
    translate([0,monitor_y,monitor_z]) difference() {
        monitor_envelope();
        translate([-monitor_w/2+wall,-monitor_d/2+wall,wall])rounded([monitor_w-2*wall,monitor_d-2*wall,monitor_h-2*wall],7);
        translate([-139,-monitor_d/2-3,21]) rounded([278,60,238],8);
        // Side/rear shell joint visible in the owner photograph.
        translate([-monitor_w/2-1,-monitor_d/2-1,monitor_h*monitor_seam_fraction-1]) cube([monitor_w+2,monitor_d+2,2]);
        for(i=[-12:12]) translate([i*10,70,monitor_h-24]) cube([4,60,40],center=true);
        // Two underside banks and the cable outlet, from 125132359.MP.
        for(x=[-117,117],i=[-8:8])translate([x,i*8,-2])slab(42,4,35,1.9);
        translate([108,25,-2])slab(29,58,wall+4,1);
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
    sheet = 1; // Owner estimate: painted sheet metal, not a thick molded shell.
    difference(){
        union(){
            translate([0,keyboard_y,0]) difference() {
                // Straight lower rim above the separate 1 mm lid. Only the
                // 5 mm plan bends and 1 mm top bends are independent.
                // Clipping below the rim prevents a rolled-under bottom edge.
                intersection() {
                    translate([0,0,1.2])slab(keyboard_w-6,keyboard_d,40,5);
                    // Offset a smaller wedge by 1 mm: a genuine round bend
                    // along the sloping top, independent of the 5 mm plan corners.
                    minkowski(){
                        intersection(){
                            translate([0,0,0])slab(keyboard_w-8,keyboard_d-2,keyboard_rear_height-1,4);
                            translate([0,0,keyboard_deck_z])rotate([keyboard_slope,0,0])
                                translate([-keyboard_w,-keyboard_d,-100])cube([2*keyboard_w,2*keyboard_d,94]);
                        }
                        sphere(r=1,$fn=24);
                    }
                }
                // One continuous sloping 1 mm skin, including the exposed rear
                // shelf: owner side photo PXL_20261013_084425145.
                intersection() {
                    translate([0,0,-3])slab(keyboard_w-6-2*sheet,keyboard_d-2*sheet,keyboard_rear_height+3-sheet,5-sheet);
                    translate([0,0,keyboard_deck_z])rotate([keyboard_slope,0,0])
                        translate([-keyboard_w,-keyboard_d,-100])cube([2*keyboard_w,2*keyboard_d,94]);
                }
                // The tilted deck aperture must not cut through the vertical
                // front fascia: its tall cutter leans forward as Z increases.
                // Preserve the same 1 mm front wall as the hollow interior.
                intersection() {
                    translate([0,-20,-5]) rotate([keyboard_slope,0,0]) slab(keyboard_w-12,158,70,4);
                    translate([-keyboard_w,-keyboard_d/2+sheet,-10])
                        cube([keyboard_w*2,keyboard_d*2,100]);
                }
            }
            // Owner inside views 123048886 / 123907435: individual lid tabs,
            // not a continuous bottom flange. Align holes with the separate lid.
            for(x=[-218,0,218],side=[-1,1])
                translate([x,keyboard_y+side*92,1.2])difference(){
                    slab(10,15,sheet,1);
                    translate([0,-side*5,-1])cylinder(d=3.5,h=4,$fn=24);
                }
            // Pressed pencil trough: a closed 1 mm floor below the shelf.
            // Depth is photo-estimated; this is not a through opening.
            translate([0,keyboard_y+81,keyboard_rear_height-3])
                slab(keyboard_w-40,12,3,5.9);
        }
        // Leave the trough floor and 1 mm side walls intact.
        translate([0,keyboard_y+81,keyboard_rear_height-2])
            slab(keyboard_w-42,10,4,4.9);
    }
}
module keyboard_bottom() {
    translate([0,keyboard_y,0]) difference() {
        union(){slab(keyboard_w-12,keyboard_d-7,1,5);
            for(x=[-200,200],y=[-65,65])translate([x,y,-1.2])slab(39,15,2,5);}
        translate([80,55,-3])slab(42,20,8,2);
        for(x=[-218,0,218],y=[-87,87])translate([x,y,-2])cylinder(d=3.5,h=6);
    }
}
module specimen_foot() {
    difference(){slab(32,11,4,1.3);translate([0,0,-1])slab(25,7,3.5,.7);}
}
module specimen_foot_insert() {
    translate([0,0,1.8])slab(24,5,1,.4);
    for(side=[-1,1])translate([0,side*2.4,2.2])cube([24,.8,1.4],center=true);
    translate([0,0,1])screw(3,1.2);
}
module keyboard_feet() {
    for(x=[-200,200],y=[-65,65])translate([x,keyboard_y+y,-5])specimen_foot();
}
module screw(d=5,h=1.7) {
    difference(){cylinder(d=d,h=h,$fn=32);translate([-d/2,-.45,-.1])cube([d,.9,.7]);}
}
module keyboard_metal() {
    for(x=[-200,200],y=[-65,65])translate([x,keyboard_y+y,-5])specimen_foot_insert();
    for(x=[-218,0,218],y=[-87,87])translate([x,keyboard_y+y,0]){
        translate([0,0,-.7])cylinder(d=7,h=.8,$fn=32);
        translate([0,0,-2.1])difference(){cylinder(d=5.5,h=1.5,$fn=6);translate([-3,-.45,-.1])cube([6,.9,.8]);}
    }
}
module keyboard_grommet() {
    // Owner photo PXL_20261009_133005363: two opposing rubber strips,
    // with bare metal on the short edges, not a continuous rectangular boot.
    // Photo ratios: ~57 x 37, opening ~42 x 17.
    translate([80,keyboard_y+55,-2]) {
        for(side=[-1,1])translate([0,side*9.5,0])slab(42,2,2,.3);
        for(side=[-1,1])scale([1,side,1])translate([0,10,0])rotate([-18,0,0])
            linear_extrude(1.6)polygon([[-21,0],[21,0],[28.5,8.5],[-28.5,8.5]]);
    }
}
// Owner: folded 1 mm sheet, uniform 8 mm skirt height. The existing
// key/deck top datum stays at local Z=4; the open skirt ends at Z=-4.
// Both edges follow the same plane, so this is not a wedge.
module keyboard_deck_envelope(w,h,r,bottom,top,roll) {
    slab_height=top-roll-bottom;
    translate([0,0,bottom])slab(w,h,slab_height,r);
    for(a=[0:5:85])hull()for(b=[a,a+5])let(inset=roll*(1-cos(b)))
        translate([0,0,top-roll+roll*sin(b)-.01])
            slab(w-2*inset,h-2*inset,.01,r-inset);
}
module keyboard_deck_blank() {
    w=keyboard_w-8; h=158;
    difference(){
        // Owner visual trial: 5 mm outside radius in plan and across the top.
        keyboard_deck_envelope(w,h,5,-4,4,5);
        // Inner bend is offset 1 mm from the outer bend and top skin.
        keyboard_deck_envelope(w-2,h-2,4,-5,3,4);
    }
}
module keyboard_deck() {
    translate([0,keyboard_y,26+keyboard_z_shift]) rotate([keyboard_slope,0,0]) difference() {
        translate([0,-20,0])keyboard_deck_blank();
        // Contiguous row openings, matching the photographed stepped main block.
        for(row=[0:4])let(ks=[for(k=keys)if(abs(k[1]-(22-row*keyboard_pitch))<.1 && k[0]<100)k],
            lo=row==2 ? -230 : min([for(k=ks)k[0]-k[2]*keyboard_pitch/2]),
            hi=row==0 ? 83.5 : max([for(k=ks)k[0]+k[2]*keyboard_pitch/2]))
            translate([(lo+hi)/2,22-row*keyboard_pitch,-1])slab(hi-lo+.6,keyboard_pitch+.6,7,1);
        for(p=[[126.25,57],[173.75,19],[216.5,38]])
            translate([p[0],-16,-1])slab(p[1]+.6,95.6,7,1);
    }
}
// Match the museum's existing indicator lenses; dimensions remain provisional.
// Keep these separate from the dark fixed carriers and moving keycaps.
module keyboard_indicator(i) {
    p = i==0 ? [-225.25,-16] : [69.25,22];
    translate([0,keyboard_y,28+keyboard_z_shift]) rotate([keyboard_slope,0,0])
        translate([p[0],p[1],3.5]) sphere(r=2,$fn=32);
}
module keyboard_indicators() {
    color("#89621d")for(i=[0:1])keyboard_indicator(i);
}
module keyboard_fillers() {
    translate([0,keyboard_y,28+keyboard_z_shift]) rotate([keyboard_slope,0,0]) {
        // Half-pitch indicator carriers and paired spacers beside SI/SO and ET.
        for(p=[[-225.25,-16],[69.25,22],[78.75,22],[17,-54],[26.5,-54]])
            translate([p[0],p[1],0])slab(8.3,17.8,3,1.5);
    }
}
// Owner side views 135524773/135528166/135532764: square flange,
// nearly vertical rounded body and shallow dish. Dimensions remain estimates.
module cap_dish(w,h,drop=0) {
    translate([0,0,69-drop])scale([max(1,(w-4)/16),max(1,(h-4)/16),1])sphere(r=60,$fn=96);
}
module cap_insert(w,h) {
    // Silver liner inside the clear function-key shell; separate export/material.
    difference(){
        translate([0,0,1.8])slab(w-2.6,h-2.6,7.1,1.5);
        cap_dish(w,h,.8);
        translate([0,0,1.7])slab(w-4.4,h-4.4,4.8,1);
    }
}
module cap(w,h,style,top_width=0) {
    tw=top_width>0 ? top_width : w-4;
    th=h-4;
    if(style==0)keycap_black_shell(w,h,tw,th);
    else difference(){
        union(){
            slab(w,h,1.5,1.7);
            if(style>0)hull(){
                translate([0,0,1.5])slab(w-.4,h-.4,.2,2);
                translate([0,0,9.4])slab(w-1,h-1,.1,2.2);
            }
            else hull(){
                translate([0,0,1.5])slab(tw+.8,th+.8,.2,min(tw+.8,th+.8)/2-.1);
                translate([0,0,9.4])slab(tw,th,.1,min(tw,th)/2-.1);
            }
        }
        cap_dish(style>0 ? w : tw+4,h);
        // Thin clear shell; opaque caps retain their moulded hollow underside.
        if(style==1)translate([0,0,-.1])slab(w-2,h-2,8.2,1.3);
        // Follow the capsule outline: a square cavity breaks through the
        // cylindrical wall near its corners, exposing the mechanism below.
        else if(style==2)translate([0,0,-.1])slab(w-6,h-6,6,1);
        else translate([0,0,-.1])slab(tw-2,th-2,6,min(tw-2,th-2)/2-.1);
    }
    // Clear/red key underside remains provisional pending equivalent loose-cap photos.
    if(style!=0)difference(){translate([0,0,-2])cylinder(d=7,h=6,$fn=24);translate([0,0,-2.1])cube([3.3,3.3,9],center=true);}
}
module keycaps(style) {
    translate([0,keyboard_y,28+keyboard_z_shift]) rotate([keyboard_slope,0,0])
        for(k=keys) if(k[4]==style) translate([k[0],k[1],0]){cap(k[2]*keyboard_pitch-1.2,k[3]*keyboard_pitch-1.2,style,k[5]);if(style==0)color("Ivory")keycap_white_core(k[2]*keyboard_pitch-1.2,k[3]*keyboard_pitch-1.2,k[5]>0?k[5]:k[2]*keyboard_pitch-5.2,k[3]*keyboard_pitch-5.2);if(style==1)color("Silver")cap_insert(k[2]*keyboard_pitch-1.2,k[3]*keyboard_pitch-1.2);}
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
    translate([0,monitor_y-120,monitor_z+monitor_h+.02])rotate([0,0,-3])slab(52,9,.3,.5);
}
module hardware() {
    // Owner confirms these are the same inserts as the keyboard feet.
    for(x=[-225,225],y=[-170,170])translate([x,y,-3])specimen_foot();
}
module shape(p) {
    specimen_shape(p);
    if(p=="specimen-sleeve")teac_storage_sleeve();
    if(p=="specimen-switch-guide")translate([0,0,-11.3])switch_guide();
    if(p=="specimen-switch-mount")translate([0,0,-13])switch_mount();
    if(p=="specimen-switch-contacts")translate([0,0,-13.3])contact_electrodes();
    if(p=="specimen-switch-pcb")translate([-10,-10,-14.918])cube([20,20,1.6]);
    for(i=[0:1]){
      if(p==str("drive-shaft-",i))translate([[-231,-77][i],-203,60])teac_latch_shaft();
      if(p==str("drive-release-",i))translate([[-231,-77][i],-203,60])teac_release_rail();
    }
    assembly_details(p);
    interior_shape(p);
    for(i=[0:1])if(p==str("drive-latch-",i))drive_latches(i);
    monitor_interior_shape(p);
    monitor_external_shape(p);
    for(i=[0:1]){if(p==str("drive-latch-trim-",i))drive_latch_trim(i);if(p==str("drive-direction-",i))drive_direction(i);}
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
    if(p=="reset")reset_pad();
    if(p=="pedestal")pedestal();
    if(p=="ring")ring();
    if(p=="monitor-shell")monitor_shell();
    if(p=="bezel")bezel();
    if(p=="crt-rim")crt_rim();
    if(p=="crt-glass")crt_glass();
    if(p=="keyboard-shell")keyboard_shell();
    if(p=="keyboard-deck")keyboard_deck();
    if(p=="keyboard-indicators")keyboard_indicators();
    if(p=="keys-black")keycaps(0);
    if(p=="keys-light")keycaps(1);
    if(p=="keys-red")keycaps(2);
    if(p=="hardware")hardware();
    if(p=="cable")cable();
    if(p=="keycap-core")let(k=keys[key_index])keycap_white_core(k[2]*keyboard_pitch-1.2,k[3]*keyboard_pitch-1.2,k[5]>0?k[5]:k[2]*keyboard_pitch-5.2,k[3]*keyboard_pitch-5.2);
    if(p=="keycap-insert")let(k=keys[key_index])cap_insert(k[2]*keyboard_pitch-1.2,k[3]*keyboard_pitch-1.2);
    if(p=="keycap")let(k=keys[key_index])cap(k[2]*keyboard_pitch-1.2,k[3]*keyboard_pitch-1.2,k[4],k[5]);
}
parts=["case-base", "case-lid", "fascia", "drives", "power", "reset", "pedestal", "ring", "monitor-shell-lower", "bezel", "crt-rim", "crt-glass", "keyboard-shell", "keyboard-deck", "keys-black", "keys-light", "keys-red", "hardware", "cable", "drive-insets", "drive-latch-0", "drive-led-0", "drive-led-1", "keyboard-bottom", "keyboard-feet", "keyboard-metal", "keyboard-grommet", "keyboard-fillers", "cable-plug", "plug-screws", "monitor-tape", "drive-frames", "drive-mechanisms", "drive-motors", "drive-boards", "drive-contacts", "drive-coils", "drive-bracket", "logic-boards", "logic-chips", "logic-pins", "logic-connectors", "psu-chassis", "psu-cover", "fan-frame", "fan-rotor", "ribbon-cables", "ribbon-stripes", "power-wires-red", "power-wires-black", "power-wires-yellow", "keyboard-pcb", "keyboard-switches", "monitor-shell-upper", "tube-funnel", "tube-neck", "monitor-yoke", "monitor-coils", "monitor-chassis", "monitor-boards", "monitor-components", "monitor-capacitors", "monitor-shield", "monitor-wires", "plug-insert", "drive-power-sockets", "drive-traces", "drive-label-plates", "drive-spindle-0", "drive-spindle-1", "drive-head-0", "drive-head-1", "drive-latch-1", "drive-clamp-0", "drive-clamp-1", "drive-head-metal-0", "drive-head-metal-1", "drive-board-components", "logic-mounts", "chassis-fasteners", "keyboard-plate", "monitor-fasteners", "monitor-passives", "monitor-socket", "prototype-spring", "prototype-stem", "logic-resistors", "logic-ceramics", "logic-electrolytics", "logic-crystals", "logic-passive-leads", "logic-film", "logic-pads", "logic-solder", "logic-connector-contacts", "prototype-pcb-pad", "prototype-pcb-solder", "ribbon-ridges", "drive-cable-plugs", "drive-head-arm-0", "drive-head-arm-1", "drive-medium-0", "drive-medium-1", "keyboard-controller-board", "keyboard-controller-chips", "keyboard-controller-ceramic", "keyboard-controller-rom-cover", "keyboard-controller-connectors", "keyboard-controller-caps", "keyboard-controller-metal", "keyboard-controller-ink", "keyboard-insulators", "keyboard-matrix-artwork", "system-foot-metal", "monitor-under-controls", "monitor-stand-metal", "rear-socket-bodies", "rear-socket-contacts", "rear-power-black", "rear-blanking-plates", "rear-legends", "rear-panel", "rear-recesses", "rear-socket-inserts", "rear-fasteners", "rear-nameplate", "rear-nameplate-ink", "monitor-joint-lip", "keyboard-pcb-metal", "keyboard-controller-traces", "monitor-power-lead", "monitor-signal-lead", "monitor-plug-bodies", "monitor-plug-metal", "monitor-plug-collars", "keyboard-guides", "keyboard-contact-pads", "prototype-rubber", "drive-diskette-0", "drive-diskette-1", "drive-diskette-label-0", "drive-diskette-label-1", "drive-latch-trim-0", "drive-latch-trim-1", "drive-direction-0", "drive-direction-1", "drive-shaft-0", "drive-shaft-1", "drive-release-0", "drive-release-1", "keyboard-pcb-supports", "keyboard-pcb-fasteners", "keyboard-entry-wires", "keyboard-contact-routes", "keyboard-controller-solder", "drive-protect-tab-0", "drive-protect-tab-1", "keyboard-controller-leads", "keyboard-entry-choke", "monitor-mount-pads", "monitor-cable-clips", "fan-retainers", "fan-cushions", "psu-grommets", "drive-adapter-boards", "drive-adapter-traces", "drive-adapter-sockets"];
colors=["Wheat", "Wheat", "#8d887a", "#242627", "#333839", "#74776f", "Wheat", "#333333", "Wheat", "#8c857a", "#141919", "#0b1712", "#9daeb1", "#242929", "#202526", "#bac1b8", "#c6343b", "#242725", "#b7b3a0", "#101312", "#242827", "#590b0b", "#590b0b", "#9daeb1", "#252928", "#96988f", "#30312e", "#242929", "#c3b995", "#96988f", "#487eac", "#a2a4a0", "#bec2bd", "#282c2b", "#28675a", "#b3a775", "#9e793b", "#afb4ae", "#386349", "#25292b", "#b3b8b4", "#b1b5a1", "#a2a6a3", "#b5b9b2", "#303634", "#282d2a", "#a0a59b", "#975b50", "#9e3930", "#252a28", "#b6a05b", "#91ae94", "#30352f", "Wheat", "#363d3a", "#78765f", "#38372e", "#ae7545", "#a3a79c", "#486551", "#343835", "#438c9b", "#979e92", "#b2a374", "#969782", "#d0c6a4", "#78a58d", "#c2bba4", "#a8aaa4", "#a8aaa4", "#30322f", "#30322f", "#242827", "#b5b9b2", "#b5b9b2", "#b5b9b2", "#b5b9b2", "#282c2b", "#b5b9b2", "#94978e", "#242929", "#b5b9b2", "#bd9867", "#c3bbaa", "#8c8c81", "#ded6be", "#71917c", "#aa622e", "#282a28", "#9c9d91", "#b8b7ac", "#c9b95a", "#b4a576", "#aaa99c", "#b9b7ac", "#b4a576", "#aaa99c", "#b0b3a9", "#353936", "#b5b9b2", "#b5b9b2", "#46322a", "#46322a", "#aaa982", "#272a2b", "#ad8875", "#168dcc", "#c4ceca", "#23383b", "#b8bbb4", "#c8c8bd", "#59424a", "#487856", "#b5b9b2", "#252928", "#b5b9b2", "#a5aaa2", "#b5ad7f", "#252928", "#babdb7", "#777362", "#a9a18c", "#181c1c", "#c4c1a8", "#b7b8ae", "#bfc1b8", "#343b39", "#34362f", "#bec4bd", "#b8beb7", "#b7b8ad", "#747f85", "#bfc3ab", "#92968c", "#80654e", "#d9d9c8", "#363833", "#30322d", "#242321", "#242321", "#d8d4bf", "#d8d4bf", "#a6a7a0", "#a6a7a0", "#d0d2c7", "#d0d2c7", "#a6a7a0", "#a6a7a0", "#a6a7a0", "#a6a7a0", "#59424a", "#b8bbb4", "#c6c5bb", "#487856", "#b8bbb4", "#b4b5ad", "#b4b5ad", "Silver", "#35352f", "#292d29", "#b7b9b1", "#afb7aa", "#c8bd8e", "#292d2c", "#70444b", "#b9c1b7", "#c9c7ae"];
if(part=="assembly") { for(i=[0:len(parts)-1]) if(parts[i]!="prototype-spring" && parts[i]!="prototype-stem" && parts[i]!="prototype-rubber" && parts[i]!="prototype-pcb-pad" && parts[i]!="prototype-pcb-solder") color(colors[i]) shape(parts[i]); keyboard_mechanisms(); keyboard_indicators(); }
else if(part=="interior") { keyboard_mechanisms(); for(i=[31:len(parts)-1]) if(parts[i]!="monitor-shell-upper" && parts[i]!="prototype-spring" && parts[i]!="prototype-stem" && parts[i]!="prototype-rubber" && parts[i]!="prototype-pcb-pad" && parts[i]!="prototype-pcb-solder") color(colors[i]) shape(parts[i]); }
else shape(part);
