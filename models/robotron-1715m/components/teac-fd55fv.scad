// TEAC FD-55FV-13 reference reconstruction. Local origin: body front-left-bottom.
// Nominal envelope 146 x 203 x 41.3 mm: TEAC specification Rev E, pp.101–103.
// Mechanism details are estimated from Oldcrap's top/underside photographs.
// Front bezel is supplied separately by the specimen-specific parent model.
teac_width=146; teac_depth=203; teac_height=41.3;
module teac_frame() {
    difference() {
        union() {
            cube([146,203,2]);
            for(x=[0,143])translate([x,0,0])cube([3,203,32]);
            for(y=[0,200])translate([0,y,0])cube([146,3,18]);
            for(x=[5,133],y=[10,180])translate([x,y,2])cube([8,10,32]);
        }
        translate([73,64,-1])cylinder(d=78,h=4,$fn=64);
        translate([42,110,-1])cube([60,65,4]);
        for(x=[-1,142],y=[46,125])translate([x,y,16])rotate([0,90,0])cylinder(d=3,h=6,$fn=12);
    }
    // Stamped top deck, with carriage and motor openings.
    translate([4,6,29])difference(){cube([138,185,1.2]);
        translate([43,66,-1])cube([49,112,4]);
        translate([0,135,-1])cube([39,52,4]);
        translate([105,120,-1])cube([35,58,4]);}
}
module teac_mechanism() {
    // Clamping bridge, guide rails and head carriage (static reference pose).
    translate([66,72,31])difference(){cube([31,114,2]);translate([15,44,-1])cylinder(d=23,h=4,$fn=32);}
    translate([80,72,28])cylinder(d=25,h=9,$fn=40);
    translate([80,72,37])cylinder(d=12,h=3,$fn=24);
    for(x=[49,104])translate([x,109,18])rotate([-90,0,0])cylinder(d=3,h=76,$fn=12);
    translate([45,134,18])cube([63,16,3]);
    translate([73,63,2])cylinder(d=76,h=6,$fn=48);
    translate([20,162,6])cylinder(d=30,h=20,$fn=32);
    translate([17,27,33])rotate([0,90,0])cylinder(d=2.4,h=108,$fn=12);
    translate([43,0,31])cube([3,68,5]);
    for(x=[8,137],y=[12,95,190])translate([x,y,32])cylinder(d=5,h=1.5,$fn=16);
}
module teac_black() {
    translate([5,144,13])cube([28,37,22]);
    translate([65,137,22])cube([29,23,12]);
    translate([109,159,9])cube([21,31,22]);
    translate([54,198,2])cube([62,7,5]);
    for(p=[[12,26],[14,51],[115,141]])translate([p[0],p[1],9])cube([12,18,4]);
}
module teac_boards() {
    translate([5,120,5])cube([134,77,1.6]);
    translate([126,6,31])cube([14,70,1.6]);
    translate([99,64,31])cube([41,20,1.6]);
    translate([60,195,4.8])cube([51,11,1.6]);
}
module teac_contacts() {
    for(i=[0:16])translate([62+i*2.54,198,6.4])cube([1.4,7,.2]);
    for(y=[12:7:72])translate([134,y,32.7])cylinder(d=2,h=.3,$fn=8);
    for(x=[17:4:41])translate([x,203,8])rotate([-90,0,0])cylinder(d=1.8,h=5,$fn=8);
}
module teac_coils() {
    translate([110,157,14])difference(){cube([19,22,18]);translate([4,-1,4])cube([11,24,10]);}
    for(y=[158:2:177])translate([109,y,14])cube([21,.5,18]);
}
