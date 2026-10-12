// Owner spring: 13 mm nominal diameter, ~0.35 wire, ~23 free length.
// Interpreted as OD; 12 mm installed height and switch/stem seating estimated.
module key_spring(height=12) {
    // Five open turns, two close turns at each end. Continuous closed mesh.
    steps=216; sides=6; radius=(13-.35)/2; wire=.35;
    function z(t)=t<2 ? t*wire : t>7 ? height-wire-(9-t)*wire : 2*wire+(t-2)*(height-5*wire)/5;
    polyhedron(points=[for(i=[0:steps],j=[0:sides-1])let(t=9*i/steps,a=t*360,b=j*360/sides)
        [(radius+wire/2*cos(b))*cos(a),(radius+wire/2*cos(b))*sin(a),z(t)+wire/2*sin(b)]],
        faces=concat([for(i=[0:steps-1],j=[0:sides-1])[i*sides+j,i*sides+(j+1)%sides,(i+1)*sides+(j+1)%sides,(i+1)*sides+j]],
        [[for(j=[sides-1:-1:0])j]],[[for(j=[0:sides-1])steps*sides+j]]),convexity=12);
}
module key_stem() {
    translate([-1.5,-1.5,-11])cube([3,3,13]);
    translate([0,0,-1.5])difference(){cylinder(d=12.6,h=.9,$fn=32);translate([0,0,-.1])cylinder(d=7.5,h=2,$fn=24);}
}
module switch_housing() {
    difference(){union(){translate([-7.3,-7.3,0])cube([14.6,14.6,2]);cylinder(d=9,h=8,$fn=24);}
        translate([-1.8,-1.8,-1])cube([3.6,3.6,11]);}
}
module keyboard_mechanisms() {
    translate([0,keyboard_y,28])rotate([keyboard_slope,0,0])for(k=keys)translate([k[0],k[1],0]){
        color("Silver")translate([0,0,-12])key_spring();color("Ivory")key_stem();
    }
}
module keyboard_plate() {
    translate([0,keyboard_y,17])rotate([keyboard_slope,0,0])difference(){
        translate([0,-16,0])slab(484,114,1.2,3);for(k=keys)translate([k[0],k[1],-1])cylinder(d=10,h=4,$fn=20);
        for(x=[-225,225],y=[-55,45])translate([x,y,-1])cylinder(d=3.4,h=4,$fn=16);
    }
}
module logic_mounts() {
    for(p=pcb_mounts)if(pcb_selected(p[4]))translate([p[0],p[1],p[2]]){
        // Hex support ends at the board underside; screw crosses the clearance hole.
        difference(){cylinder(d=6,h=p[3]-p[2]-1.6,$fn=6);translate([0,0,-.1])cylinder(d=2.6,h=p[3]-p[2],$fn=16);}
        translate([0,0,p[3]-p[2]])difference(){cylinder(d=6,h=.45,$fn=24);translate([0,0,-.1])cylinder(d=3.4,h=.7,$fn=16);}
        translate([0,0,p[3]-p[2]-3])cylinder(d=2.8,h=3.5,$fn=16);
        translate([0,0,p[3]-p[2]+.45])screw(4.8,1.5);
    }
}
module chassis_fasteners() {
    for(x=[-241,236],y=[-180,165])translate([x,y,4]){
        difference(){cube([5,16,25]);translate([-1,8,19])rotate([0,90,0])cylinder(d=3.4,h=8,$fn=16);}
        translate([2.5,8,-2])screw(4,1.4);
    }
    for(x=[-232,72],y=[-179,-20])translate([x,y,55])screw(5,1.4);
    for(y=[80,137])translate([68,y,29])rotate([0,90,0])screw(5,2);
    // Cable retainers along the PSU partition; provisional routing.
    for(y=[24,48])translate([91,y,58])difference(){cube([7,5,12]);translate([-1,-1,2])cube([6,7,8]);}
}
module monitor_fasteners() {
    for(x=[-126,126],z=[218,429])translate([x,-124,z])rotate([90,0,0]){
        difference(){cube([12,12,2],center=true);cylinder(d=3.5,h=5,center=true,$fn=16);}
        translate([0,0,1])screw(5,1.6);
    }
    for(y=[-55,137],z=[229,403])translate([-133,y,z])rotate([0,90,0]){
        cylinder(d=6,h=6,$fn=6);translate([0,0,9])screw(4,1.3);
    }
}
module monitor_passives() {
    // Visible component groupings from K7222.25 reference photos, not a circuit netlist.
    for(p=[[-46,325],[-30,325],[-12,320],[31,284],[58,284],[91,338],[111,338]])
        translate([-122,p[0],p[1]]){
            rotate([90,0,0])cylinder(d=3.5,h=10,$fn=12);
            for(y=[-11,1])translate([-2,y,-.3])cube([3,1,.6]);
        }
    for(p=[[-15,399],[18,399],[65,348],[100,293]])translate([-123,p[0],p[1]])rotate([0,90,0])cylinder(d=7,h=4,$fn=16);
    for(y=[-43,6])translate([-101,y+12,269])cube([2,13,19]);
}
module monitor_socket() {
    translate([0,143,324])rotate([-90,0,0])difference(){cylinder(d=37,h=9,$fn=40);translate([0,0,-1])cylinder(d=27,h=12,$fn=32);
        for(a=[0:40:320])translate([15.5*cos(a),15.5*sin(a),-1])cylinder(d=1.8,h=12,$fn=12);}
    // Neck retaining collar.
    translate([0,93,324])rotate([-90,0,0])difference(){cylinder(d=32,h=7,$fn=40);translate([0,0,-1])cylinder(d=27.5,h=9,$fn=32);}
}
module assembly_details(p) {
    if(p=="prototype-spring")key_spring();
    if(p=="prototype-stem")key_stem();
    if(p=="keyboard-plate")keyboard_plate();
    if(p=="logic-mounts")logic_mounts();
    if(p=="chassis-fasteners")chassis_fasteners();
    if(p=="monitor-fasteners")monitor_fasteners();
    if(p=="monitor-passives")monitor_passives();
    if(p=="monitor-socket")monitor_socket();
    if(p=="drive-board-components")drive_pair()teac_components();
    for(i=[0:1]){
        if(p==str("drive-head-arm-",i))translate([[-231,-77][i],-203,60])teac_head_arm();
        if(p==str("drive-medium-",i))translate([[-231,-77][i],-203,60])teac_medium();
        if(p==str("drive-clamp-",i))translate([[-231,-77][i],-203,60])teac_clamp();
        if(p==str("drive-head-metal-",i))translate([[-231,-77][i],-203,60])teac_head_metal();
    }
}
