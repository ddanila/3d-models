// Danila's Robotron 1715 M exterior, reconstructed from 2026-10-09 photos.
// See README for measured vs inferred dimensions and unseen surfaces.
include <dimensions.scad>
include <keyboard-layout.scad>
part = "assembly";

module rounded(size,r=3) {
    hull() for(x=[r,size[0]-r],y=[r,size[1]-r],z=[r,size[2]-r])
        translate([x,y,z]) sphere(r=r,$fn=16);
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
        translate([-case_w/2-2,-160,5]) cube([10,32,18]);
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
module drives() {
    for(x=[-158,-4]) {
        translate([x,-case_d/2-2,81]) rotate([90,0,0]) slab(146,42,4,2);
        translate([x+45,-case_d/2-10,94]) rotate([0,-12,0]) cube([35,9,7],center=true);
    }
}
module switch_part(x,w,h) {
    translate([x,-case_d/2-4,17]) rotate([90,0,0]) slab(w,h,7,2);
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
            translate([-monitor_w/2,-monitor_d/2,0]) rounded([monitor_w,22,monitor_h],10);
            translate([-135,monitor_d/2-28,20]) rounded([270,28,240],10);
        }
        hull(){translate([-monitor_w/2+wall,-monitor_d/2+wall,wall])rounded([monitor_w-2*wall,22,monitor_h-2*wall],7);translate([-132,monitor_d/2-31,23])rounded([264,28,234],7);}
        translate([-139,-monitor_d/2-3,21]) rounded([278,60,238],8);
        for(i=[-12:12]) translate([i*10,70,monitor_h-24]) cube([4,60,40],center=true);
    }
}
module bezel() {
    translate([0,monitor_y-monitor_d/2-3,monitor_z+monitor_h/2]) rotate([90,0,0]) difference() {
        slab(303,264,9,15);
        translate([0,4,-1]) slab(268,221,12,22);
    }
}
module crt_rim() {
    translate([0,monitor_y-monitor_d/2-11,monitor_z+monitor_h/2+4]) rotate([90,0,0]) difference(){slab(269,222,5,23);translate([0,0,-1])slab(258,211,8,21);}
}
module crt_glass() {
    translate([0,monitor_y-monitor_d/2-12,monitor_z+monitor_h/2+4]) rotate([90,0,0]) slab(258,211,2,21);
}
module keyboard_shell() {
    translate([0,keyboard_y,0]) difference() {
        hull(){translate([0,-keyboard_d/2+4,8])cube([keyboard_w-6,8,16],center=true);translate([0,keyboard_d/2-4,20])cube([keyboard_w-6,8,40],center=true);}
        translate([0,0,25]) rotate([keyboard_slope,0,0]) slab(keyboard_w-12,keyboard_d-30,30,4);
        translate([80,55,-2]) cube([28,22,9],center=true);
    }
}
module keyboard_deck() {
    translate([0,keyboard_y,26]) rotate([keyboard_slope,0,0]) difference() {
        slab(keyboard_w-8,keyboard_d-34,4,5);
        for(k=keys) translate([k[0],k[1],-1]) slab(k[2]*keyboard_pitch-1,k[3]*keyboard_pitch-1,7,2);
    }
    translate([0,keyboard_y+87,37]) rotate([0,90,0]) cylinder(r=3,h=keyboard_w-24,center=true);
}
module cap(w,h,style) {
    difference(){hull(){slab(w,h,1,2);translate([0,0,7])
        if(style==1) slab(w-2,h-3,1,3);
        else scale([w-2,h-3,1]) cylinder(d=1,h=1,$fn=32);
    }translate([0,0,36])sphere(r=29,$fn=32);}
}
module keycaps(style) {
    translate([0,keyboard_y,28]) rotate([keyboard_slope,0,0])
        for(k=keys) if(k[4]==style) translate([k[0],k[1],0])cap(k[2]*keyboard_pitch-1.2,k[3]*keyboard_pitch-1.2,style);
}
module hardware() {
    // Neutral dark backing behind the vent bank, not an internal board model.
    translate([80,-case_d/2+12,40]) cube([150,2,80]);
    // Keyboard underside feet/fasteners observed in photographs.
    for(x=[-210,210],y=[-60,60]) translate([x,keyboard_y+y,-2])cube([27,10,4],center=true);
    for(x=[-244,-5,244],y=[-76,76])translate([x,keyboard_y+y,-1])cylinder(d=6,h=2);
    // Base-unit feet are provisional: no underside photo of that unit yet.
    for(x=[-225,225],y=[-170,170])translate([x,y,-9])cylinder(d=25,h=10);
    // Visible left-side keyboard cable plug, approximate exterior dimensions.
    translate([-case_w/2-17,-145,13]) rounded([27,30,18],2);
}
module shape(p) {
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
}
parts=["case-base","case-lid","fascia","drives","power","reset","pedestal","ring","monitor-shell","bezel","crt-rim","crt-glass","keyboard-shell","keyboard-deck","keys-black","keys-light","keys-red","hardware"];
colors=["Wheat","Wheat","Gray","#242627","#333839","#333839","Wheat","#333333","Wheat","#8c857a","#141919","#0b1712","#abb9bc","#242929","#202526","#bac1b8","#c6343b","#474b46"];
if(part=="assembly") for(i=[0:len(parts)-1]) color(colors[i]) shape(parts[i]);
else shape(part);
