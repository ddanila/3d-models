// Standalone electrical reconstruction review; does not replace qualified museum geometry.
include <generated/controller.scad>
include <../controller-package-data.scad>
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
 for(z=[-.08,1.6])color("#d8c98e")translate([0,0,z])for(p=controller_pcb_pads)translate([p[0],p[1],0])difference(){cylinder(d=p[2],h=.08);translate([0,0,-.1])cylinder(d=p[5],h=.3);}
 color("#b87b32"){
  translate([0,0,1.6])for(a=controller_pcb_top_copper)route(a);
  translate([0,0,-.08])for(a=controller_pcb_bottom_copper)route(a);
 }
 // Cyan review graphics have no assigned net and are NOT verified copper.
 if(show_unresolved_artwork)color("#50b5c8"){
  for(b=controller_visual_bridges)translate([0,0,2.4])route([[b[0],b[1]],.5],.1);
  translate([0,0,1.7])for(a=controller_pcb_top_art)route(a,.03);
  translate([0,0,-.15])for(a=controller_pcb_bottom_art)route(a,.03);
 }
 for(p=controller_pcb_dips)for(pkg=controller_packages)if(pkg[0]==p[2])
  translate([p[0],p[1],1.6])rotate([0,0,p[5]-90]){
   color("#22252b")import(str("../",pkg[1]));
   color("#b8b8b2")scale([1,p[6]/2.54,1])import(str("../",pkg[2]));
  }
}
