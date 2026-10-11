// Reference-photo discrete components. Dimensions are estimates, values unknown.
// Local Y is the long axis; leads pass through the board plane.
module pcb_passive_pose(kind) {
    for(c=pcb_passives)if(c[0]==kind)translate(c[1])rotate([0,0,c[2]])children();
}
module axial_body() {
    translate([0,-3.15,2])rotate([-90,0,0])union(){
        cylinder(d=2.5,h=6.3,$fn=20);
        for(z=[.15,5.7])translate([0,0,z])cylinder(d=2.65,h=.45,$fn=20);
    }
}
module ceramic_body() {
    translate([0,0,4])rotate([0,90,0])scale([1,1,.45])sphere(d=5.5,$fn=24);
}
module electrolytic_body() {
    difference(){cylinder(d=6.3,h=10,$fn=32);translate([0,0,9.6])cylinder(d=5.5,h=1,$fn=32);}
}
module crystal_body() {
    translate([0,0,1])linear_extrude(5)offset(r=2)square([1,6],center=true);
    translate([0,0,.6])linear_extrude(.5)offset(r=2.4)square([1,6],center=true);
}
module passive_leads() {
    pcb_passive_pose("resistor")for(side=[-1,1])scale([1,side,1]){
        translate([0,3,2])rotate([-90,0,0])cylinder(d=.55,h=1.5,$fn=10);
        translate([0,4.5,-2])cylinder(d=.55,h=4,$fn=10);
        translate([0,4.5,2])sphere(d=.55,$fn=10);
    }
    for(kind=["ceramic","electrolytic","crystal"])pcb_passive_pose(kind)for(y=[-1.25,1.25])translate([0,y,-2])cylinder(d=.55,h=6,$fn=10);
    pcb_passive_pose("electrolytic")translate([0,0,9.6])difference(){cylinder(d=5.5,h=.3,$fn=32);translate([-3,-.2,.1])cube([6,.4,1]);translate([-.2,-3,.1])cube([.4,6,1]);}
}
module logic_discretes(p) {
    if(p=="logic-resistors")pcb_passive_pose("resistor")axial_body();
    if(p=="logic-ceramics")pcb_passive_pose("ceramic")ceramic_body();
    if(p=="logic-electrolytics")pcb_passive_pose("electrolytic")electrolytic_body();
    if(p=="logic-crystals")pcb_passive_pose("crystal")crystal_body();
    if(p=="logic-passive-leads")passive_leads();
}
