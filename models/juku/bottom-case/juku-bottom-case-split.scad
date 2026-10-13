// Juku bottom case - 4-part split for small print beds
// Units: millimeters
//
// The assembled bottom case is 340 x 290 mm, which does not fit a 256 x 256 mm
// bed. This file reuses the one-piece model unchanged (via `use`) and cuts it
// into four staggered panels that are glued back together. The front and rear
// X seams are deliberately offset, replacing a single four-way crossing with
// two T-junctions. This makes the parts easier to align and lets the front pair
// and rear pair be assembled separately before those two halves are joined.
// The original juku-bottom-case.scad is NOT modified - if you have a printer
// with a large enough bed, just print that file instead and ignore this one.
//
// The seams are HALF-LAP joints worked into the 3 mm floor thickness: the cut
// steps in Z partway through the thickness and offsets sideways, so one piece
// carries the top shelf past the seam and the other the bottom shelf. The two
// shelves overlap and locate each other in Z, then get glued. Because the step
// sits inside the floor, the taller perimeter walls are simply cut straight
// (a butt joint) - no thin features to weaken them.
//
//   cross-section across a seam (3 mm thick):
//       LEFT  ###########
//             ###########            <- top shelf (left)
//             ------=========        <- step at lap_step
//                   =========        <- bottom shelf (right)  RIGHT
//             |<- lap_width ->|
//
// Render a single panel for export by overriding split_part on the CLI:
//   openscad -o fl.stl -D 'split_part="fl"' juku-bottom-case-split.scad
// Parts: fl = front-left, fr = front-right, bl = back-left, br = back-right.
// With the default split_part="all" the four panels render exploded apart.

use <juku-bottom-case.scad>

// --- Dimensions mirrored from juku-bottom-case.scad -------------------------
// `use` imports modules but not variables, so the handful of dimensions the
// split logic needs are repeated here. Keep these in sync with the source.
outside_width = 340;
outside_depth = 290;
case_thickness = 3;       // floor thickness the half-lap is worked into
bottom_chamfer = 8;

// --- Split parameters -------------------------------------------------------
// Cut planes are offset from the centre so they clear the centred logo/serial
// recesses, the front-centre lid-mount boss and every PCB-support boss. Keeping
// separate front/rear X planes avoids a four-way seam crossing.
split_x_front = 195;      // Front X cut: left 0..195, right 195..340
split_x_rear = 160;       // Rear X cut: left 0..160, right 160..340
split_y = 115;            // Y cut plane: front 0..115, rear 115..290
split_part = "all";       // "all" (exploded preview) | "fl" | "fr" | "bl" | "br"
split_kerf = 0.2;         // slip-fit gap removed on every mating face
split_preview_gap = 12;   // explode distance per panel in the "all" preview
bed_size = 256;           // print-bed edge used by the fit asserts

// --- Half-lap seam ----------------------------------------------------------
lap_width = 6;            // horizontal overlap of the two shelves
lap_step = 1.5;           // height of the step in the floor (1.5 = even halves;
                          // set 1.0 for a thinner bottom shelf)

big = 10 * (outside_width + outside_depth);

assert(
    split_x_front > bottom_chamfer
    && split_x_front < outside_width - bottom_chamfer
);
assert(
    split_x_rear > bottom_chamfer
    && split_x_rear < outside_width - bottom_chamfer
);
assert(split_y > bottom_chamfer && split_y < outside_depth - bottom_chamfer);
assert(split_kerf >= 0);
assert(lap_step > split_kerf && lap_step < case_thickness - split_kerf,
       "lap_step must leave material above and below the step");
assert(lap_width > split_kerf, "lap_width too small for the kerf");
// A panel's extent = nominal size + the shelf it laps past the seam.
assert(
    split_x_front + lap_width / 2 <= bed_size,
    "front-left panel too wide for the bed"
);
assert(
    outside_width - split_x_front + lap_width / 2 <= bed_size,
    "front-right panel too wide for the bed"
);
assert(
    split_x_rear + lap_width / 2 <= bed_size,
    "rear-left panel too wide for the bed"
);
assert(
    outside_width - split_x_rear + lap_width / 2 <= bed_size,
    "rear-right panel too wide for the bed"
);
assert(split_y + lap_width / 2 <= bed_size, "front panels too deep for the bed");
assert(outside_depth - split_y + lap_width / 2 <= bed_size, "rear panels too deep for the bed");

echo(str(
    "Panel footprints (mm, incl. lap): ",
    "FL ", split_x_front + lap_width / 2, " x ", split_y + lap_width / 2, ", ",
    "FR ", outside_width - split_x_front + lap_width / 2, " x ", split_y + lap_width / 2, ", ",
    "BL ", split_x_rear + lap_width / 2, " x ", outside_depth - split_y + lap_width / 2, ", ",
    "BR ", outside_width - split_x_rear + lap_width / 2, " x ", outside_depth - split_y + lap_width / 2,
    " - all must be <= ", bed_size
));

// Half-lap selector, canonical frame: the seam divides at x = pos and steps in
// Z at lap_step. `high` picks the x > pos side. The low side keeps the full
// thickness left of the seam plus a BOTTOM shelf reaching lap_width/2 past it;
// the high side keeps the full thickness right of the seam plus a TOP shelf
// reaching lap_width/2 the other way. Kerf is removed from every mating face.
module lap_half_canonical(pos, high) {
    h = split_kerf / 2;

    if (!high) {
        union() {
            // full thickness left of the (top) seam plane
            translate([-big, -big, -big])
                cube([big + pos - lap_width / 2 - h, 2 * big, 2 * big]);
            // bottom shelf, reaching lap_width/2 past the seam
            translate([-big, -big, -big])
                cube([big + pos + lap_width / 2 - h, 2 * big, big + lap_step - h]);
        }
    } else {
        union() {
            // full thickness right of the (bottom) seam plane
            translate([pos + lap_width / 2 + h, -big, -big])
                cube([2 * big, 2 * big, 2 * big]);
            // top shelf, reaching lap_width/2 the other way
            translate([pos - lap_width / 2 + h, -big, lap_step + h])
                cube([2 * big, 2 * big, 2 * big]);
        }
    }
}

// X-seam: divides left (low) / right (high), step in Z.
module xseam_side(pos, high) {
    lap_half_canonical(pos, high);
}

// Y-seam: same joint about the Y axis - build canonical, then swap X and Y.
module yseam_side(high) {
    multmatrix([[0, 1, 0, 0], [1, 0, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
        lap_half_canonical(split_y, high);
}

module panel(part) {
    is_left = (part == "fl" || part == "bl");
    is_front = (part == "fl" || part == "fr");
    split_x = is_front ? split_x_front : split_x_rear;

    intersection() {
        bottom_case();
        xseam_side(split_x, !is_left); // left  => low side
        yseam_side(!is_front);          // front => low side
    }
}

if (split_part == "all") {
    g = split_preview_gap;
    translate([-g, -g, 0]) panel("fl");
    translate([ g, -g, 0]) panel("fr");
    translate([-g,  g, 0]) panel("bl");
    translate([ g,  g, 0]) panel("br");
} else {
    panel(split_part);
}
