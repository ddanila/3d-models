include <geometry.scad>
part="assembly"; // spring, guide, mount, carrier, rubber, contacts, assembly
if(part=="spring")contact_spring();
if(part=="guide")switch_guide();
if(part=="mount")switch_mount();
if(part=="carrier")translate([0,0,10.4])contact_carrier();
if(part=="rubber")translate([0,0,11.2])contact_rubber();
if(part=="contacts")contact_electrodes();
if(part=="assembly") {
    color("#30312d")switch_mount();
    color("Ivory")translate([0,0,1.7])switch_guide();
    color("Silver")translate([0,0,2])contact_spring();
    color("Ivory")translate([0,0,13.4])contact_carrier();
    color("#30322d")translate([0,0,13.4])contact_rubber();
}
