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
// Central blind cup with an inward annular latch lip. The underside photographs
// 185834871 / 185855185 and owner's description support the ring, but its exact
// profile and dimensions are provisional. Z increases inward from the opening.
// A long entry bevel leads to a short throat, then a steep retaining shoulder.
module keycap_cup_void(depth, bore=8.6, lip=.45, lip_start=.8,
                       lead=1.0, land=.25, shoulder=.2,
                       orientation_key=[.6,1.2,.5,135]) {
    assert(lip >= 0 && lip < bore/2);
    assert(lip_start >= 0 && lead > 0 && land >= 0 && shoulder > 0);
    assert(lip_start+lead+land+shoulder < depth);
    difference() {
    rotate_extrude($fn=keycap_facets) polygon([
        [0,-.05], [bore/2,-.05],
        [bore/2,lip_start],
        [bore/2-lip,lip_start+lead],
        [bore/2-lip,lip_start+lead+land],
        [bore/2,lip_start+lead+land+shoulder],
        [bore/2,depth], [0,depth]
    ]);
    // Leave an axial anti-rotation rib on the cup wall, toward one skirt
    // corner. Photo location/profile are approximate; angle is viewed from +Z.
    // Vector: radial projection, tangential width, entry depth, angle.
    key_projection=orientation_key[0];
    key_width=orientation_key[1];
    key_start=orientation_key[2];
    assert(key_projection >= 0 && key_projection < bore/2);
    assert(key_width > 0 && key_width < bore);
    assert(key_start >= 0 && key_start+.5 < depth);
    if(key_projection > 0) rotate([0,0,orientation_key[3]])
        hull() {
            // Short bevel at the mouth eases entry into the mating keyway.
            translate([bore/2-.05,-key_width/2,key_start])
                cube([.25,key_width,.02]);
            translate([bore/2-key_projection,-key_width/2,key_start+.5])
                cube([key_projection+.2,key_width,depth-key_start-.5+.05]);
        }
    }
}
module keycap_volume(w=17.8,h=17.8,top_w=13.8,top_h=13.8,height=11.4,skirt=4,
                     latch_projection=.45,latch_start=.8,latch_lead=1.0,
                     latch_land=.25,latch_shoulder=.2,
                     orientation_key=[.6,1.2,.5,135]) {
    difference(){
        keycap_outer(w,h,top_w,top_h,height,skirt);
        // The photographed white core has two concentric recesses; both close
        // below the crown, leaving one connected part for a single-material STL.
        translate([0,0,-.05])difference(){
            cylinder(d1=13.6,d2=13.3,h=height-2.15,$fn=keycap_facets);
            translate([0,0,-.1])cylinder(d=10.4,h=height,$fn=keycap_facets);
        }
        keycap_cup_void(height-1.85, lip=latch_projection,
            lip_start=latch_start, lead=latch_lead,
            land=latch_land, shoulder=latch_shoulder, orientation_key=orientation_key);
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
module keycap_white_core(w=17.8,h=17.8,top_w=13.8,top_h=13.8,height=11.4,skirt=4,
                        latch_projection=.45,latch_start=.8,latch_lead=1.0,
                        latch_land=.25,latch_shoulder=.2,
                     orientation_key=[.6,1.2,.5,135]) {
    intersection(){
        keycap_volume(w,h,top_w,top_h,height,skirt,
            latch_projection,latch_start,latch_lead,latch_land,latch_shoulder,orientation_key);
        keycap_core_region(w,h,height);
    }
}
module keycap_black_shell(w=17.8,h=17.8,top_w=13.8,top_h=13.8,height=11.4,skirt=4,
                         latch_projection=.45,latch_start=.8,latch_lead=1.0,
                         latch_land=.25,latch_shoulder=.2,
                     orientation_key=[.6,1.2,.5,135]) {
    difference(){
        keycap_volume(w,h,top_w,top_h,height,skirt,
            latch_projection,latch_start,latch_lead,latch_land,latch_shoulder,orientation_key);
        keycap_core_region(w,h,height);
    }
}
