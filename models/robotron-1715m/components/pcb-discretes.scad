// Reference-photo discrete components. Dimensions are estimates, values unknown.
// Local Y is the long axis; leads pass through the board plane.
module pcb_passive_pose(kind) {
    for(c=pcb_passives)if(c[0]==kind && pcb_selected(c[4]))translate(c[1])rotate([0,0,c[2]])rotate([c[7]==-1?180:0,0,0])let($can_d=c[5],$can_h=c[6])children();
}
module axial_body() {
    translate([0,-3.15,2])rotate([-90,0,0])union(){
        cylinder(d=2.5,h=6.3,$fn=20);
        for(z=[.15,5.7])translate([0,0,z])cylinder(d=2.65,h=.45,$fn=20);
    }
}
module ceramic_body() {
    translate([0,0,4])rotate([0,90,0])scale([1,1,.45])sphere(d=$can_d,$fn=24);
}
module electrolytic_body() {
    difference(){cylinder(d=$can_d,h=$can_h,$fn=24);translate([0,0,$can_h-.4])cylinder(d=$can_d-.8,h=1,$fn=24);}
}
module crystal_body() {
    translate([0,0,1])linear_extrude(5)offset(r=2)square([1,6],center=true);
    translate([0,0,.6])linear_extrude(.5)offset(r=2.4)square([1,6],center=true);
}
module film_body() {
    // Red upright rectangular capacitors in the owner's component-side photos.
    translate([0,0,4.2])rotate([0,12,0])cube([1.4,5.5,5.5],center=true);
}
module wound_core(d=20) {
    rotate_extrude($fn=48)translate([d*.36,0,0])circle(r=d*.14,$fn=12);
    for(a=[0:20:340])rotate([0,0,a])translate([d*.36,0,0])rotate([90,0,0])
        rotate_extrude($fn=20)translate([d*.155,0,0])circle(r=.35,$fn=8);
}
module logic_inductors(){
    if(pcb_selected("display-controller"))translate([-40.4,140,36])wound_core(20);
    if(pcb_selected("motherboard"))translate([8,80,17])wound_core(9);
}
module passive_leads() {
    pcb_passive_pose("resistor")for(side=[-1,1])scale([1,side,1]){
        translate([0,3,2])rotate([-90,0,0])cylinder(d=.55,h=1.5,$fn=10);
        translate([0,4.5,-2])cylinder(d=.55,h=4,$fn=10);
        translate([0,4.5,2])sphere(d=.55,$fn=10);
    }
    for(kind=["ceramic","electrolytic","crystal","film"])pcb_passive_pose(kind)for(y=[-1.25,1.25])translate([0,y,-2])cylinder(d=.55,h=6,$fn=10);
    pcb_passive_pose("electrolytic")translate([0,0,$can_h-.4])difference(){cylinder(d=$can_d-.8,h=.3,$fn=24);translate([-3,-.2,.1])cube([6,.4,1]);translate([-.2,-3,.1])cube([.4,6,1]);}
}
module logic_discretes(p) {
    if(p=="logic-inductors")logic_inductors();
    if(p=="logic-film")pcb_passive_pose("film")film_body();
    if(p=="logic-resistors")pcb_passive_pose("resistor")axial_body();
    if(p=="logic-ceramics")pcb_passive_pose("ceramic")ceramic_body();
    if(p=="logic-electrolytics")pcb_passive_pose("electrolytic")electrolytic_body();
    if(p=="logic-crystals")pcb_passive_pose("crystal")crystal_body();
    if(p=="logic-passive-leads")passive_leads();
}
