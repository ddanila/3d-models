// Proposed reference electrical geometry; not the historical specimen or a fabrication release.
include <generated/controller.scad>
side="top"; // [top,bottom]
show_proposed=true;
$fn=20;
module stroke(points,width,z) {
    for(i=[0:len(points)-2]) hull() {
        translate([points[i][0],points[i][1],z]) cylinder(h=.035,d=width);
        translate([points[i+1][0],points[i+1][1],z]) cylinder(h=.035,d=width);
    }
}
module reference_board() {
    color([.12,.32,.22]) difference() {
        linear_extrude(1.6) polygon(reference_outline);
        for(p=reference_pads) if(p[4]>0) translate([p[0],p[1],-.1]) cylinder(h=1.8,d=p[4]);
        for(v=reference_vias) translate([v[0],v[1],-.1]) cylinder(h=1.8,d=v[3]);
    }
    for(p=reference_pads) for(z=[-.035,1.6]) color([.85,.7,.3])
        translate([p[0],p[1],z]) linear_extrude(.035) difference() {
            scale([p[2],p[3]]) circle(d=1);
            if(p[4]>0) circle(d=p[4]);
        }
    for(r=reference_routes) if(show_proposed || !r[3])
        color(r[3]?[1,.45,.15]:[.3,.8,1]) stroke(r[0],r[1],r[2]?1.6:-.035);
    for(v=reference_vias) for(z=[-.035,1.6]) color([1,.45,.15])
        translate([v[0],v[1],z]) difference() {
            cylinder(h=.035,d=v[2]);
            translate([0,0,-.01]) cylinder(h=.06,d=v[3]);
        }
}
rotate([side=="bottom"?180:0,0,0]) reference_board();
