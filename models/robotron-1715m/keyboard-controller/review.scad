// Standalone electrical reconstruction review; does not replace qualified museum geometry.
include <generated/controller.scad>
$fn=20;
side="top"; // [top,bottom]
show_unresolved_artwork=true;
module route(a,h=.08){for(i=[0:len(a[0])-2])hull()for(j=[i,i+1])translate(concat(a[0][j],[0]))cylinder(d=a[1],h=h);}
module board(){difference(){
 linear_extrude(1.6)polygon(controller_pcb_outline);
 for(p=controller_pcb_holes)translate([p[0],p[1],-1])cylinder(d=p[2],h=4);
}}
rotate(side=="bottom"?[180,0,0]:[0,0,0]){
 color("#9e9a79")board();
 for(z=[-.08,1.6])color("#d8c98e")translate([0,0,z])for(p=controller_pcb_pads)translate([p[0],p[1],0])difference(){cylinder(d=p[2],h=.08);translate([0,0,-.1])cylinder(d=.85,h=.3);}
 color("#b87b32"){
  translate([0,0,1.6])for(a=controller_pcb_top_copper)route(a);
  translate([0,0,-.08])for(a=controller_pcb_bottom_copper)route(a);
 }
 // Cyan review graphics have no assigned net and are NOT verified copper.
 if(show_unresolved_artwork)color("#50b5c8"){
  translate([0,0,1.7])for(a=controller_pcb_top_art)route(a,.03);
  translate([0,0,-.15])for(a=controller_pcb_bottom_art)route(a,.03);
 }
 color("#22252b")for(p=controller_pcb_dips)translate([p[0],p[1],1.6])rotate([0,0,p[5]])translate([-(p[2]/2*2.54)/2,-(p[3]-1)/2,0])cube([p[2]/2*2.54,p[3]-1,3]);
}
