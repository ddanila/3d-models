// Owner loose-cap photographs, 2026-10-12. Millimetres; local underside is Z=0.
// No square/cross stem: circular central cup surrounded by an annular spring seat.
// Fit dimensions are photo estimates, parameterized for later physical measurement.
keycap_facets=96;
module keycap_outline(w,h,r) { hull()for(x=[-w/2+r,w/2-r],y=[-h/2+r,h/2-r])translate([x,y])circle(r=r,$fn=keycap_facets); }
module keycap_slab(w,h,z,t,r) { translate([0,0,z])linear_extrude(t)keycap_outline(w,h,r); }
module keycap_outer(w=17.8,h=17.8,top_w=13.8,top_h=13.8,height=11.4,skirt=4) {
    union(){
        keycap_slab(w,h,0,skirt,1.3);
        hull(){
            keycap_slab(top_w+1.4,top_h+1.4,skirt-.15,.2,min(top_w,top_h)/2);
            keycap_slab(top_w+.65,top_h+.65,skirt+.5,.2,min(top_w,top_h)/2);
        }
        hull(){
            keycap_slab(top_w+.65,top_h+.65,skirt+.5,.15,min(top_w,top_h)/2);
            keycap_slab(top_w+.2,top_h+.2,height-.3,.1,min(top_w,top_h)/2);
            keycap_slab(top_w,top_h,height-.1,.1,min(top_w,top_h)/2);
        }
    }
}
module keycap_volume(w=17.8,h=17.8,top_w=13.8,top_h=13.8,height=11.4,skirt=4) {
    difference(){
        keycap_outer(w,h,top_w,top_h,height,skirt);
        // The photographed white core has two concentric recesses; both close
        // below the crown, leaving one connected part for a single-material STL.
        translate([0,0,-.05])difference(){
            cylinder(d1=13.6,d2=13.3,h=height-2.15,$fn=keycap_facets);
            translate([0,0,-.1])cylinder(d=10.4,h=height,$fn=keycap_facets);
        }
        translate([0,0,-.05])cylinder(d=8.6,h=height-1.8,$fn=keycap_facets);
        // Almost-flat touch face with a shallow central dish and a rounded rim.
        scale([top_w/13.8,top_h/13.8,1])rotate_extrude($fn=keycap_facets)
            polygon(concat([[0,height+20],[40,height+20]],
                [for(r=[40:-.5:0])[r,height+131.82-sqrt(132*132-r*r)]]));
    }
}
module keycap_core_region(w=17.8,h=17.8,height=11.4) {
    union(){
        keycap_slab(w-1.3,h-1.3,-.02,3.4,.8);
        translate([0,0,-.02])cylinder(d=13.8,h=height-1.1,$fn=keycap_facets);
    }
}
module keycap_white_core(w=17.8,h=17.8,top_w=13.8,top_h=13.8,height=11.4,skirt=4) {
    intersection(){keycap_volume(w,h,top_w,top_h,height,skirt);keycap_core_region(w,h,height);}
}
module keycap_black_shell(w=17.8,h=17.8,top_w=13.8,top_h=13.8,height=11.4,skirt=4) {
    difference(){keycap_volume(w,h,top_w,top_h,height,skirt);keycap_core_region(w,h,height);}
}
