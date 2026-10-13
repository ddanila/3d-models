# Juku Modeling Notes

## OpenSCAD command

OpenSCAD is installed through Snap as `openscad-nightly`, not `openscad`.

```bash
openscad-nightly --version
```

If a plain `openscad` command is useful, add this alias to `~/.bashrc`:

```bash
alias openscad=openscad-nightly
```

On macOS the binary is inside the app bundle: `/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD`.

## Repository layout

Each modeled component keeps its source and generated artifacts together:

| Component | Source | Generated artifacts |
| --- | --- | --- |
| Keycap | `keycap/juku-keycap.scad` | `keycap/juku-keycap.stl`, `keycap/preview-*.png` |
| Bottom case | `bottom-case/juku-bottom-case.scad` | `bottom-case/juku-bottom-case.stl`, `bottom-case/preview.png` |
| Legs | `legs/juku-leg.scad` | `legs/juku-leg.stl` |

Regenerate STL files with `./scripts/export-stls.sh` and previews with
`./scripts/render-previews.sh`. Generated model artifacts should not be
edited by hand.

The preview script renders above the target resolution and downscales to
1600x1200 because OpenSCAD's CLI renders without antialiasing. It uses
OpenSCAD's built-in `Monotone` color scheme so subtraction-cut surfaces do
not get a distinct back-face color.

`keycap/original-*.jpg` are reference photos of an original keycap.
`keycap/printed-*.jpeg` are photos of a real resin print, with metadata
stripped.

## Iteration workflow

After each modeling change:

1. Render the SCAD file to an STL to catch syntax and geometry errors.

   ```bash
   ./scripts/check-render.sh
   ```

2. Confirm OpenSCAD reports a manifold 3D object with `Status: NoError`.

3. Open the SCAD file in OpenSCAD for manual review from a normal desktop terminal or the application launcher.

   ```bash
   ./scripts/open-keycap.sh
   ./scripts/open-bottom-case.sh
   ```

Codex can run the automated render check reliably. It can also attempt to launch the OpenSCAD UI, but Snap/desktop session handling may make that window flash briefly or disappear, so manual review is best started from the user's desktop session.

## Modeling notes

Large spheres used for shallow cuts need a high local segment count. A large-radius sphere with the global `$fn = 48` can technically intersect the model but look flat in OpenSCAD because the visible patch is a low-resolution facet. Use a local `$fn`, for example:

```scad
sphere(r = top_dish_radius, $fn = top_dish_segments);
```

## Bottom case dimensions

All dimensions are in millimeters.

| Dimension | Value |
| --- | ---: |
| Outer width (X) | 340 |
| Outer depth (Y) | 290 |
| Outer height (Z) | 18 |
| Case thickness | 3 |
| Front and side bottom chamfer | 8 at 45 degrees |
| Top rim chamfer | 3 at 45 degrees, downward toward outside |
| Rear PCB opening | 300 wide x 12 high, centered horizontally and open at top |
| Rear outer guide rail | 312 long x 4 deep x 15 high |
| Rear guide channel | 2 deep, with the case floor at its bottom |
| Rear inner guide rail | 306 long x 3 deep x 15 high |
| Leg hole centers | 15 from each adjacent outer edge |
| Leg through-hole | 3.5 diameter |
| Leg exterior counterbore | 5 diameter x 1.5 deep |
| Leg interior reinforcement | 7 diameter x 1.5 high |
| Leg through-hole depth | 4.5 including floor and reinforcement boss |
| Leg hole cylinder segments | 128 |
| PCB support through-hole | 3.5 diameter |
| PCB support exterior nut pocket | Hexagonal, 6 across flats x 3 deep |
| PCB support interior reinforcement | 12 diameter x 3 high |
| PCB support rear row centers | X: 25, 129, 233, 315; Y: 272 |
| PCB support side centers | X: 25, 315; Y: 152 |
| PCB support front row centers | X: 25, 120, 215, 315; Y: 32 |
| Lid mount side centers | X: 7, 333; Y: 25, 265 |
| Lid mount front center | X: 170; Y: 7 |
| Lid mount through-hole | 3 diameter |
| Lid mount exterior recess | 8 wide x 6.5 deep, round-ended and projected to outer edge |
| Lid mount interior reinforcement | 13 diameter x 7 high, clipped to D shape |
| Logo plaque | 30 wide x 10 deep x 0.6 recessed into underside |
| Logo plaque front offset | 50 to front edge |
| Logo relief | 0.6 above recessed plaque floor, flush with underside |
| Serial plate recess | 30 wide x 20 deep x 0.6 recessed into underside |
| Serial plate recess gap | 20 behind Estron plaque |

The case is an open-top shell with 3 mm walls and floor. The front and both
sides have an 8 mm external bottom chamfer; the rear remains square. The
inner chamfer is offset to keep the sloped material 3 mm thick. The top rim
slopes from the inside lip downward and outward across the full wall
thickness. A rectangular PCB opening is centered horizontally in the rear
wall and extends downward from the top edge. The maximum outer envelope
starts at the origin.

The experimental PCB guide aligns vertically with the rear opening. Its
outer face aligns with the exterior rear face. Moving inward, the
arrangement is a 4 mm rail, a 2 mm channel, and a 3 mm rail. Both rails are
centered; the outer rail extends 3 mm farther at each end, where square
mirrored bridges close the channel. The 300 mm opening is cut through the
rear wall and the complete guide depth from Z=6 to Z=18. The guide extends
down to the inner floor at Z=3, leaving a continuous 3 mm-high base beneath
the opening. Its exterior top edge has the same 3 mm, 45-degree chamfer as
the case rim.

Four leg mounting holes are positioned symmetrically near the corners. Each
has a through-hole, a concentric counterbore entering from the exterior
underside, and a concentric reinforcement boss rising from the inner floor.
The mounting interface dimensions are shared from
`bottom-case/leg-interface.scad` so the leg model and assembly check fail at
render time if the mating diameters or heights drift apart.

The rubber/latex/silicone leg is a stepped push-in part. From exterior to
interior it has a 10 diameter x 3 high foot, a 5 diameter x 1.5 high
counterbore plug, a 3.5 diameter x 3 high stem through the case floor, and a
6 diameter x 2 high inner retaining head.

Ten PCB supports form three centered rows. The rear and front rows have four
supports each, while the middle row has one support at each shared outer X
coordinate. Each support has a through-hole, a 3 mm-deep hexagonal nut
pocket entering from the exterior underside, and a 12 mm-diameter
reinforcement boss rising 3 mm from the inner floor.

Five top-lid mounts sit in the front and side bottom-chamfer bands. Four are
paired near the front and rear ends of the side walls, and one is centered
on the front wall. Their inner bosses and exterior recesses have round inner
ends with straight projections toward the adjacent wall, forming D-shaped
profiles.

The exterior underside has a centered 30 x 10 mm logo plaque whose front
edge is 50 mm from the front of the case. Its background is recessed 0.6 mm
into the case, leaving the imported Estron letters and decorative lines
standing 0.6 mm above the plaque floor, flush with the original underside.
The vector source is `bottom-case/estron-logo.dxf`.

A second plain rectangular recess for the model and serial-number plate is
centered on the underside. It measures 30 x 20 mm, has the same 0.6 mm
depth, and starts 20 mm behind the rear edge of the Estron plaque.
