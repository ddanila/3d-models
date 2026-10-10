// Provisional K7222.25 interior, based on Robotrontechnik open-shell photos.
// Tube and component dimensions are photo estimates; not a verified board revision.
module monitor_upper() {
    intersection(){monitor_shell();translate([-500,-500,monitor_z+monitor_h*.5])cube([1000,1000,500]);}
}
module monitor_lower() {
    intersection(){monitor_shell();translate([-500,-500,0])cube([1000,1000,monitor_z+monitor_h*.5]);}
}
module tube_funnel() {
    hull(){translate([0,-138,324])rotate([-90,0,0])linear_extrude(2)crt_outline(258,211);
        translate([0,54,324])rotate([-90,0,0])cylinder(d=51,h=3,$fn=64);}
}
module tube_neck() {
    translate([0,55,324])rotate([-90,0,0])cylinder(d=27,h=88,$fn=48);
}
module monitor_yoke() {
    translate([0,30,324])rotate([-90,0,0])difference(){cylinder(d1=84,d2=49,h=37,$fn=48);translate([0,0,-1])cylinder(d1=65,d2=29,h=40,$fn=48);}
    translate([0,141,324])rotate([-90,0,0])cylinder(d=39,h=12,$fn=24);
}
module monitor_coils() {
    for(a=[0:15:345]) hull(){translate([42*cos(a),32,324+42*sin(a)])sphere(r=1.4,$fn=8);translate([25*cos(a),66,324+25*sin(a)])sphere(r=1.4,$fn=8);}
    // High-voltage winding in the screened right-hand compartment.
    translate([100,92,302])rotate([0,90,0])difference(){cylinder(d=49,h=21,$fn=32);translate([0,0,-1])cylinder(d=21,h=23,$fn=24);}
}
module monitor_chassis() {
    for(x=[-133,127]){
        translate([x,-128,209])cube([6,290,8]);
        translate([x,-128,433])cube([6,290,5]);
        for(y=[-125,151])translate([x,y,209])cube([6,8,229]);
    }
    for(y=[-124,149])translate([-130,y,209])cube([260,7,5]);
    translate([-130,149,284])cube([260,6,12]);
    // Tube retaining band just behind the glass.
    translate([0,-132,324])rotate([-90,0,0])linear_extrude(6)difference(){crt_outline(264,217);crt_outline(258,211);}
}
module monitor_boards() {
    translate([-127,-65,220])cube([1.6,215,195]);
    translate([-24,145,300])cube([48,1.6,48]);
}
module monitor_components() {
    // Heat sinks and a small neck-board socket, matching the visible assemblies.
    for(y=[-42,7])translate([-121,y,259])difference(){cube([18,42,49]);
        for(z=[5:6:43])translate([8,-1,z])cube([12,44,2]);}
    translate([-18,147,307])cube([36,12,34]);
    translate([105,70,275])cube([17,49,51]);
}
module monitor_capacitors() {
    for(p=[[-32,373],[8,373],[42,371],[78,251],[110,254]])
        translate([-124,p[0],p[1]])rotate([0,90,0])cylinder(d=13,h=25,$fn=20);
}
module monitor_shield() {
    translate([83,18,247])difference(){cube([43,140,157]);translate([2,2,-1])cube([39,136,156]);
        for(y=[28:11:146])translate([-1,y-18,143])cube([45,6,8]);
        for(y=[28:11:146])translate([-1,y-18,10])cube([3,6,130]);}
}
module monitor_wires() {
    wire_run([[-122,105,256],[-60,130,254],[29,130,291],[21,91,327],[16,62,344]],1.2);
    wire_run([[-122,30,272],[-84,15,291],[-55,54,324],[-26,65,340]],1.2);
    wire_run([[103,85,353],[63,31,400],[42,-14,410],[36,-42,404]],2);
    translate([36,-42,404])scale([1,1,.35])sphere(d=24,$fn=32);
}
module monitor_interior_shape(p) {
    if(p=="monitor-shell-upper")monitor_upper();
    if(p=="monitor-shell-lower")monitor_lower();
    if(p=="tube-funnel")tube_funnel();
    if(p=="tube-neck")tube_neck();
    if(p=="monitor-yoke")monitor_yoke();
    if(p=="monitor-coils")monitor_coils();
    if(p=="monitor-chassis")monitor_chassis();
    if(p=="monitor-boards")monitor_boards();
    if(p=="monitor-components")monitor_components();
    if(p=="monitor-capacitors")monitor_capacitors();
    if(p=="monitor-shield")monitor_shield();
    if(p=="monitor-wires")monitor_wires();
}
