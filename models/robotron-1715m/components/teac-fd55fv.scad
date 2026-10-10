// FD-55-family envelope reference, refined from Danila's two actual drives.
// Photos 20250212: K5601 / TEAC 15532064-00A and Ratan / 15532092-00A.
// Envelope 146 x 203 x 41.3 mm remains the TEAC drawing reference, not a measurement.
// Local front-left-bottom; x increases to the right when facing the computer.
teac_width=146; teac_depth=203; teac_height=41.3;
module teac_frame() {
    difference() {
        union() {
            cube([146,203,2]);
            for(x=[0,143])translate([x,0,0])cube([3,203,34]);
            translate([0,200,12])cube([146,3,26]);
            translate([4,4,28])cube([138,42,1.2]);
            translate([4,48,25])cube([138,2,7]);
            for(x=[5,133],y=[10,180])translate([x,y,2])cube([8,10,29]);
        }
        translate([70,64,-1])cylinder(d=78,h=4,$fn=64);
        translate([45,106,-1])cube([52,81,4]);
        for(x=[-1,142],y=[46,125])translate([x,y,16])rotate([0,90,0])cylinder(d=3,h=6,$fn=16);
        translate([119,199,23])rotate([-90,0,0])cylinder(d=5,h=5,$fn=20);
    }
    translate([4,50,24])difference(){cube([138,147,1.2]);
        translate([39,26,-1])cube([53,112,4]);
        translate([99,79,-1])cube([40,64,4]);
        translate([-1,81,-1])cube([31,62,4]);}
}
module teac_mechanism() {
    // Central slotted stamped bridge and spindle clamp.
    translate([52,48,31])difference(){cube([36,145,2]);
        translate([5,50,-1])cube([26,74,4]);
        translate([18,45,-1])cylinder(d=26,h=4,$fn=40);
        translate([18,137,-1])cylinder(d=11,h=4,$fn=24);}
    translate([70,59,28])cylinder(d=26,h=9,$fn=40);
    translate([70,59,37])cylinder(d=12,h=3,$fn=24);
    for(x=[46,92])translate([x,104,18])rotate([-90,0,0])cylinder(d=3,h=78,$fn=16);
    translate([46,144,18])cube([48,13,3]);
    translate([70,64,2])cylinder(d=76,h=6,$fn=48);
    translate([109,158,14])rotate([0,90,0])cylinder(d=18,h=8,$fn=32);
    // The latch rod runs from the bezel to the clamp linkage.
    translate([100,0,33])rotate([-90,0,0])cylinder(d=3,h=53,$fn=16);
    translate([66,46,33])cube([38,4,3]);
    for(x=[8,137],y=[12,95,190])translate([x,y,32])cylinder(d=5,h=1.5,$fn=20);
    for(y=[141:1.3:151])translate([73,y,28])rotate([-90,0,0])difference(){cylinder(d=5,h=.6,$fn=16);translate([0,0,-.1])cylinder(d=3,h=1,$fn=12);}
}
module teac_black() {
    translate([113,133,12])cube([25,46,23]); // laminated stepper body
    translate([59,119,22])cube([24,34,9]);   // head carriage
    translate([11,166,11])cube([18,14,13]);
    for(p=[[43,70],[12,28]])translate([p[0],p[1],32.6])cube([5,4,4]);
}
module teac_boards(long_board=false) {
    translate([5,119,5])cube([134,78,1.6]);
    // Two visibly different sensor-PCB outlines, rather than duplicate rectangles.
    translate([0,0,31])linear_extrude(1.6)polygon(long_board?
      [[5,7],[21,7],[21,52],[51,52],[51,74],[40,82],[40,108],[33,113],[33,130],[10,130],[5,125]]:
      [[5,7],[21,7],[21,52],[51,52],[51,75],[44,81],[8,81],[5,76]]);
    translate([43,195,4.8])cube([64,11,1.6]);
}
module teac_contacts() {
    for(i=[0:23])translate([45+i*2.54,198,6.4])cube([1.4,7,.2]);
    for(y=[14:7:70])translate([12,y,32.7])difference(){cylinder(d=2.3,h=.2,$fn=12);translate([0,0,-.1])cylinder(d=1,h=.5,$fn=8);}
    for(p=[[43,70],[12,28]])translate([p[0],p[1],32.6])cylinder(d=3,h=.7,$fn=16);
}
module teac_coils() {
    translate([28,145,20])difference(){cube([16,24,15]);translate([3,-1,3])cube([10,26,9]);}
    for(y=[146:2:167])translate([27,y,20])cube([18,.5,15]);
}
module teac_power_socket() {
    translate([9,196,3])difference(){cube([23,10,10]);translate([2,4,2])cube([19,7,6]);}
}
module teac_traces(long_board=false) {
    for(i=[0:4])translate([7+i*2.2,10,32.65])cube([.5,42+i*2,.12]);
    for(i=[0:4])translate([7+i*2.2,52+i*2,32.65])cube([31-i*2,.5,.12]);
    if(long_board)for(i=[0:4])translate([10+i*2.4,82,32.65])cube([.5,42-i*3,.12]);
}
