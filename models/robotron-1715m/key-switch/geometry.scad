// Owner: spring OD 13 mm, free length 23 mm, round wire 0.4 mm.
// Photo-estimated: five active turns, three close turns at each end.
// All other dimensions, installed compression and actuator travel are provisional.
spring_od=13; spring_wire=.4; spring_free=23; spring_installed=19.6;
module contact_spring(height=spring_free,segments=48,sides=12) {
    turns=11; steps=turns*segments; radius=(spring_od-spring_wire)/2;
    close_pitch=spring_wire+.005;
    function center_z(t)=t<3 ? spring_wire/2+t*close_pitch :
        t>8 ? height-spring_wire/2-(turns-t)*close_pitch :
        spring_wire/2+3*close_pitch+(t-3)*(height-spring_wire-6*close_pitch)/5;
    polyhedron(points=[for(i=[0:steps],j=[0:sides-1])let(t=turns*i/steps,a=t*360,b=j*360/sides)
      [(radius+spring_wire/2*cos(b))*cos(a),(radius+spring_wire/2*cos(b))*sin(a),center_z(t)+spring_wire/2*sin(b)]],
      faces=concat([for(i=[0:steps-1],j=[0:sides-1])[i*sides+j,i*sides+(j+1)%sides,(i+1)*sides+(j+1)%sides,(i+1)*sides+j]],
        [[for(j=[sides-1:-1:0])j]],[[for(j=[0:sides-1])steps*sides+j]]),convexity=12);
}
// Switch local origin: top of black mounting flange, white cage starts at Z=0.
module switch_guide() {
    difference(){
      union(){cylinder(d=12,h=2,$fn=48);translate([0,0,2])cylinder(d=11.8,h=6.4,$fn=48);}
      translate([0,0,-.1])cylinder(d=8.5,h=3,$fn=48);
      translate([0,0,2])cylinder(d=10.7,h=7,$fn=48);
      for(y=[-6,6])translate([0,y,6.7])cube([3.2,4,4],center=true);
    }
}
module switch_mount() {
    difference(){
      linear_extrude(1.7)offset(r=.9,$fn=24)square([15.2,15.2],center=true);
      translate([0,0,-.1])cylinder(d=8.5,h=2,$fn=48);
      for(x=[-6.4,6.4],y=[-6.4,6.4])translate([x,y,-.1])cylinder(d=1.8,h=2,$fn=16);
    }
}
// Moving insulating carrier; two retaining tabs match the visible central features.
// Origin is the cap underside, matching the museum's existing key coordinate frame.
module contact_carrier() {
    translate([0,0,-10.4])cylinder(d=8.1,h=8,$fn=40);
    for(y=[-2.7,2.7])translate([0,y,-2.5])linear_extrude(3.5)offset(r=.45,$fn=20)square([2.3,1.4],center=true);
}
module contact_rubber() {
    translate([0,0,-11.04])cylinder(d=7.8,h=.64,$fn=48);
}
// Two isolated comb electrodes. Owner confirms remote-control-style pads;
// finger shape/count and surface finish are illustrative, not a traced netlist.
module contact_electrodes(thickness=.06) {
    linear_extrude(thickness)intersection(){
      circle(d=7.6,$fn=48);
      union(){
        for(side=[-1,1])translate([side*2.3,0])square([.55,8],center=true);
        for(i=[-2:2])translate([-.35,i*1.4])square([4.2,.5],center=true);
        for(i=[-2:1])translate([.35,i*1.4+.7])square([4.2,.5],center=true);
      }
    }
}
