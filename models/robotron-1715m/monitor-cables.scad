// Owner 125123660 / 125132359: two captive leads through the underside boot.
// 125234638 / 125402713: power plug and locking signal backshell.
// Diameters, slack and local plug dimensions are photo estimates. Clean condition.
function monitor_bezier(p,t)=pow(1-t,3)*p[0]+3*pow(1-t,2)*t*p[1]+3*(1-t)*t*t*p[2]+t*t*t*p[3];
module monitor_lead(curves,r) {
    for(p=curves)wire_run([for(i=[0:24])monitor_bezier(p,i/24)],r);
}
module monitor_power_lead() {
    monitor_lead([
      [[104,43,182],[104,43,150],[130,170,150],[145,227,155]],
      [[145,227,155],[167,280,166],[205,280,152],[205,250,128]],
      [[205,250,128],[205,225,108],[205,221,91],[205,221,72]]
    ],4.2);
}
module monitor_signal_lead() {
    monitor_lead([
      [[112,67,182],[112,67,153],[110,183,153],[118,229,154]],
      [[118,229,154],[129,295,149],[102,292,66],[67,269,48]],
      [[67,269,48],[51,259,41],[42,230,43],[29,230,43]]
    ],2.8);
}
module monitor_plug_bodies() {
    // Upright RFT power plug: shell halves, recesses and raised clean emblem.
    rear_pose(205,41)difference(){
      translate([0,-3,3])slab(23,56,24,3);
      translate([0,-3,14.8])slab(24,57,.45,3);
      for(x=[-6,6],y=[-21,17])translate([x,y,24])cylinder(d=4.2,h=5,$fn=20);
    }
    rear_pose(205,41)translate([0,3,27])linear_extrude(.35)rotate(90)text("RFT",size=4,halign="center",valign="center",font="Liberation Sans:style=Bold");
    // Signal backshell: broad mating edge, narrower cable end and side latches.
    translate([10,198,43])difference(){
      linear_extrude(17,center=true)polygon([[-23,0],[23,0],[23,25],[16,34],[-14,34],[-23,24]]);
      translate([0,0,-.2])cube([60,80,.4],center=true);
    }
    for(x=[-17,37])translate([x,198,43]){
      translate([-1.2,0,-4])cube([2.4,27,8]);
      translate([-2.7,-2,-4])cube([5.4,4,8]);
    }
}
module monitor_plug_metal() {
    rear_pose(205,41)for(x=[-6,6],y=[-21,17])translate([x,y,24])difference(){
      cylinder(d=3.5,h=1,$fn=20);translate([0,0,1])cube([4,.6,1],center=true);
    }
    // Power connector retaining bail; signal backshell slotted screws.
    wire_run([[192,220,29],[191,226,37],[191,226,60],[195,220,66]],.8);
    wire_run([[218,220,29],[219,226,37],[219,226,60],[215,220,66]],.8);
    for(x=[-7,27],y=[204,223])translate([x,y,51.5])difference(){
      cylinder(d=4,h=.8,$fn=20);translate([0,0,.8])cube([5,.65,.8],center=true);
    }
}
module monitor_plug_collars() {
    translate([205,221,69])difference(){slab(18,18,4,3);translate([0,0,-1])cylinder(d=8.4,h=6,$fn=24);}
}
module monitor_external_shape(p) {
    if(p=="monitor-power-lead")monitor_power_lead();
    if(p=="monitor-signal-lead")monitor_signal_lead();
    if(p=="monitor-plug-bodies")monitor_plug_bodies();
    if(p=="monitor-plug-metal")monitor_plug_metal();
    if(p=="monitor-plug-collars")monitor_plug_collars();
}
