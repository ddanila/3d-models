# Danila’s Robotron 1715M

The canonical OpenSCAD source for Danila’s museum machine and the DAC browser export. Geometry uses millimetres: X right, Y rear, Z up. Open [model.scad](model.scad) for the complete machine, or [keyboard/model.scad](keyboard/model.scad) for fast colored keyboard review. Select a named `part` to export it independently.

## Case-mounted keyboard supports and formed bezel, v47

Owner close-ups `123106382` / `123109703` show separate bent metal tabs at
multiple levels. `123114519` / `123122852` / `123126017` show slotted brown edge
strips and screws facing the removable keyboard lid. These now replace the
illustrative floating cylindrical PCB supports: six drilled leaves support the
matrix assembly at its edge strips, with returns meeting the case wall or rear
shelf, and two lower rear leaves support the controller. The leaves stay with
the case during DAC disassembly; screws and insulating strips follow the boards.
The six existing matrix apertures remain open, not occupied by invented spacers.
Visible construction follows the photos; hidden attachment footprints, support
lengths and bend radii remain nominal rather than measured fabrication details.

The [bezel close-up](reference/photos/PXL_20261012_125012845.jpg) shows a rounded
raised border, inward step, recessed land and final lip at the CRT. The bezel is
now one continuous closed skin with a nominal 1 mm rear offset along its surface
normals, rather than overlapping separately modeled rings. Cross-section depths
and radii remain photo estimates. The seven additional owner close-ups are
published with metadata stripped; no wear is copied into the geometry.

The accepted exterior keyboard dimensions and physical-verification records
remain unchanged. Review the installed board, case mounts and front-oblique
monitor views before changing these supports or the bezel profile.

## Photo corrections, v46

Compared with Danila's own [connector](reference/photos/PXL_20261010_090425989.jpg),
[controller component face](reference/photos/PXL_20261012_123622947.jpg),
[bottom lid](reference/photos/PXL_20261012_123319025.jpg) and
[monitor edge](reference/photos/PXL_20261012_125018215.jpg):

- Both drive arrows retain their two ends, but each head has only its outer
  triangular half, as visible in `PXL_20261013_113537277.jpg`. The inside edge
  continues into the tip without a second barb. Drive downloads include the marks.
- The plug now has rounded release fingers, recessed moulded channels, visible
  coil springs with relieved seats, and a projecting grey contact insert.
- The controller resistor bank runs across the board, with additional axial
  resistors and staggered transistors placed from the photograph. Capacitors
  follow the four visible cans. Leads, apertures and solder joints share positions.
- Component-side routes are recorded in [keyboard-artwork.json](keyboard-artwork.json)
  and projected by the same generator as the underside. Edge tracks retain a
  nominal 0.5 mm margin. This is visible artwork, not a verified circuit/netlist.
- The replacement ROM has a blue cover and separate paper identifier; legible
  board identification is clean CAD lettering, without photographed wear.
- The 1 mm bottom plate has clipped corners and occupied foot fasteners beside
  the open holes. Its insulating sheet uses a darker brown phenolic finish.
- The monitor's bowed dark glass perimeter is wider and glossier, with an
  overlapping formed-sheet bezel return. A separate front-oblique review checks
  the glass junction as well as the existing side-profile view.

Photo registration, spring dimensions, lead bends and optical properties remain
estimates. Three CPU/ROM-end resistor positions were adjusted within the photo
fit to clear nominal package bodies. No physical verification status changed.
The accepted keyboard shell/deck dimensions remain unchanged.

## Current reconstruction

The main unit, monitor and keyboard enclosures use the owner-confirmed 1 mm bent painted sheet. The system fascia has a thin face with folded returns; the monitor bezel is hollow, and the roof vents penetrate the shell. Local bend radii remain estimates. The exterior follows Danila’s photographs, with clean paint, plastic, rubber and metal rather than full-panel photo skins or copied wear. Small manufacturer labels use credited local photo crops. The keyboard’s approved exterior dimensions and separate sheet-metal layers are documented in the [keyboard workflow](keyboard/README.md). Interior dimensions remain provisional unless explicitly measured. The latest owner keycap correction is shared by the assembled keyboard: 15 mm round body, 15/11/9 mm underside diameters, 5 mm spring recess and tapered crown. The 18/23 mm wide-key dimensions describe the lower raised body.

The front controls follow owner photos `PXL_20261012_124827690.jpg` and `PXL_20261009_133019620.jpg`: one curved double-headed arrow per drive, sloping finger scoops, plain black-plastic levers, and RESET / OFF / ON / POWER legends. The textured clear power rocker sits behind a real opening in the 1 mm front sheet, with a separate dark switch housing. Scoop depth, rocker recess and local radii are photo estimates. Markings are canonical OpenSCAD geometry, not duplicate browser overlays.

The October 13 inserted-disk views (`113529099`, `113537277`) now set a 7 mm deeper media/mechanism datum, longer projecting lever boss, flush activity lenses and a higher upper finger recess. The entire lever sweep clears the inserted jacket; hub, clamp, head and label positions move together. The fascia returns reach the enclosure instead of leaving an open horizontal slot. The monitor surround follows the rolled perimeter and dished inner return in `133017092` / `125018215`. Local depths and angles remain photo estimates.

The keyboard controller is oriented with its input end toward the actual cable opening (`123907435`). A continuous internal lead reaches its shield clamp, passing through a round grooved black bush captured in a 1 mm bent metal support (`123539882`); the rectangular opening has two rubber strips along its long edges. The plug has the asymmetric housing, screw layout and offset cable outlet from `090425989` / `090431122`. DAC preserves the input connection when separating the keyboard for inspection.

The system unit has a W/M motherboard with integrated A44 U8272 and 32 RAM packages, plus a separate display controller mounted component-side down. [board-layout.json](board-layout.json) records the shared placement, sources and uncertainty. There are <!-- pcb-counts -->138 nominal KiCad DIP packages and 2,568 lead apertures<!-- /pcb-counts -->. The October 14 component-side photographs locate 39 display-board ICs, including three UL6516D memories and the SAB8275P, red upright capacitors and the white wound component. Generated P01–P39 IDs identify photo positions, not printed board designators. Photo-registered mainboard packages and connectors use the v41 two-photo, six-package nominal-pitch calibration below. Other positions retain W drawing estimates; board edges and hidden mounts remain unmeasured. R19/R102 and C90/C91 follow the documented CPU/DMA adjacency, with estimated positions and no invented electrical values. Unidentified footprints retain generic labels. Clean chip legends reproduce only owner-photo-supported markings; schematic designators remain inspection metadata. Illustrative copper routes are not a netlist.

The [October 14 photo inventory](reference/owner-20261014.json) records 52 new owner photographs, with 22 selected originals published after metadata removal. These show this exact museum specimen. The drive carrier now has thin folded returns and underside windows exposing the large motor rotors; those rotors share the emulator-driven spindle motion. Their dimensions remain photo estimates. Owner photographs establish the drive adapters, their two mounting holes, cover stiffeners, fan retention and PSU access cover. The fan now has five swept blades and a broader hub matching the visible specimen; blade curvature remains estimated. Ribbon plugs now enter the pale adapter sockets; the fan aperture is concentric with the rotor/frame. The display controller’s visible board number does not prove an exact schematic revision match. Hidden monitor electronics remain comparative, and enclosed PSU electronics are not reconstructed.

The family manual gives nominal envelopes of 500 × 400 × 130 mm (system), 320 × 350 × 330 mm (monitor including stand), and 500 × 200 × 40 mm (keyboard). These are family specifications, not new measurements of this specimen. See the [original manual, printed p.35](https://xepb.org/robotron/docs/pc_manu.pdf#page=36) and [W drawings](https://xepb.org/robotron/docs/1715w.zip). The [TEAC specification](https://www.bitsavers.org/pdf/teac/FD-55FV-13_Specification_Rev_E.pdf) documents 2.54 mm signal-contact pitch; adapter-board dimensions remain estimated.

The keyboard matrix PCB now has the stepped connector tongue and separate pale
socket with bent contacts visible in `123048886` / `123103225`. The tongue sits
on the photographed side when viewed from underneath. Its location is fitted to
the board photo, but the detached controller's mating/docking arrangement remains
unverified; no connecting ribbon or electrical pinout is invented. Grey axial
resistors with blue end bands are separate from the brown ceramic components.
The quick SCAD review now includes the PCB supports, washers and contact routes
and preserves the controller's distinct laminate colour. Rounded lid tabs and
the painted 1 mm keyboard support plate retain the accepted exterior envelope.

## Evidence and verification

[Evidence categories](evidence.json) distinguish **your specimen**, **documented W/M design**, and **comparative estimate**. Physical status is separate: photographs and visual approval never confer **printed and verified**. The repository’s model-status registry is authoritative. These assembled electronics remain physically unverified.

Owner photographs and original work are MIT. Imported KiCad packages retain their licences/design exceptions and notices; archived third-party photographs retain their original rights. See [KiCad notices](components/kicad/NOTICE.txt), [comparative board history](reference/comparative-1715-boards.json), and the reference-directory notices. The keyboard EPROM was transplanted from another board; its appearance does not establish a firmware dump identity.

## Repeatable review

- [Photo / exported mesh / overlay comparisons](checks/photo-comparisons/index.html): fan, adapter and keyboard matrix board, generated from [stored landmarks](photo-alignment.json). Open locally in a browser. Planar projection flattens depth; fitted anchors and adjusted hole residuals are review aids, not independent dimensional validation.
- [Assembly fit report](checks/assembly.json): plug/socket plastic, fan/frame and airway, board mounting holes, boards/bracket/shield, and discrete-component/chip-body clearance. Only the listed pairs are checked; touching surfaces are permitted. Contacts entering plugs are intentional.
- [Drive motion report](checks/mechanics.json): all 80 modeled head positions against the fixed mechanism. It does not certify every linkage or physical tolerance.
- [Historical development notes](HISTORY.md): dated decisions and superseded layouts, kept out of the current specification.

## Photo-directed browser review

[review-views.json](review-views.json) stores six camera poses in canonical
millimetres: drive front, keyboard matrix underside, controller, cable entry,
plug and monitor profile. The browser manifest carries the same configuration.
From DAC, start `npm run dev -- --port 4173`, then run:

```sh
node scripts/review-robotron.mjs http://127.0.0.1:4173 /tmp/dac-robotron-review ../3d-models/models/robotron-1715m
```

Open `/tmp/dac-robotron-review/index.html` for owner-photo/render pairs. It loads
the actual DAC model, records its canonical revision and mesh hashes, and renders
fixed poses without running the emulator. Use it after geometry/material edits;
it is a local review aid, not another CI job or pixel-perfect photograph match.
Lighting is neutral and includes underside fill. Camera perspective, hidden
controller docking and board routing remain estimates. The planar matrix overlay
provides a separate outline/connector comparison; its fitted residual is not
independent validation. Physical verification status is unchanged.

## Rebuild and publish

Requires Python 3 and OpenSCAD with the Manifold backend. From the repository root:

```sh
python3 models/robotron-1715m/tools/configure-pcb.py
python3 models/robotron-1715m/tools/export.py
python3 models/robotron-1715m/tools/check-assembly.py
python3 models/robotron-1715m/tools/compare-photos.py
python3 models/robotron-1715m/tools/export-downloads.py
openscad --backend Manifold --export-format binstl -o models/robotron-1715m/robotron-1715m.stl models/robotron-1715m/model.scad
python3 models/robotron-1715m/tools/package-assembly.py
python3 scripts/model-status.py
```

Use `export.py --parts NAME ...` for a bounded mesh rebuild; it refreshes manifest hashes. Run `configure.py` when changing the keyboard configuration. The [combined STL ZIP](robotron-1715m.stl.zip) is a visual assembly reference; per-assembly downloads preserve sources. STL does not preserve OpenSCAD colors.

After committing canonical changes, run `python3 scripts/sync-robotron-model.py ../3d-models` in DAC. It verifies hashes and records the exact source commit. Firmware and emulator code stay in their own repository. DAC loads all interior geometry before showing the model as ready, preserving the view through closed-case openings. Repeated package instances share geometry. Optional inspection photographs load on demand; visual geometry is never deferred until a cover opens.

### Drawing and component audit — export v36

`hardware-audit.json` records the W/M motherboard and CRT drawing numbers,
keyboard schematic, connector identities, evidence boundaries and remaining
emulation work. `board-layout.json` now carries per-chip inspection text,
owner-photo links and original drawing links for the museum. Museum P numbers
on the display board are placement identifiers, **not** schematic designators.
The owner display PCB reads **1.93.310402.1 B 2**; exact equivalence to the W CRT
drawing remains unverified. Mainboard RAM labels now reflect the photographed
M4164B-12 population (32 × 64 Kbit = 256 KiB); CTC labels reflect UA857D.
Positions/references inherited from the W drawing remain estimates, rather
than claiming a complete calibrated reconstruction of this specimen.

The keyboard's eleven photo-positioned three-lead transistor bodies now use
KiCad's pinned `TO-92_Inline.step`, with its rounded back, flat face and separate
metal leads. `tools/convert-transistors.py` preserves the upstream shape and
checks solid validity, three leads and volume conservation. `transistors.json`
records mesh hashes/bounds; upstream STEP, credits and licences are preserved.
This is a generic package match, not proof of the DDR electrical type or exact
mould/lead bends. The keyboard schematic identifies eight SC308C input stages
and three oscillator transistors; photographed substitute identities remain
unverified. Imported geometry retains its upstream licence, not MIT.

The controller has matching drilled lead holes, a thin open saddle clamp with
mounting ears, and white/black/pink/blue incoming wires following the owner
photo's colors. Routes and terminations remain visual estimates, not a verified
pinout. Cover fixings are open 1 mm stamped tabs with fixing holes, following
PXL_20261013_150144938.jpg. Wear is not reproduced. Exterior keyboard dimensions
and the accepted sheet bends are unchanged. Detached controller-to-matrix
mechanical docking still needs confirmation; no speculative cable was added.

Validation: STEP split invariants, selected solid-clearance checks, repeatable
owner-photo review views and browser instance-picking tests. These checks are
**not physical print/fit verification**; model verification classifications
remain unchanged.


### Photo registration and keyboard packages — export v37

The 32 RAM bodies and two CTCs now follow the visible owner motherboard photo
PXL_20261014_072654600.jpg. The CTCs are stacked along the board rather than
side by side. `motherboardPhotoRegistration` in `board-layout.json` retains the
review-image coordinates, scale assumption and scope. This registration uses
the existing provisional 250 mm board width; it is not a measured/calibrated
camera reconstruction. Four large processor-area packages also use owner-photo registration; smaller unregistered components retain drawing estimates.
RAM reference-to-position correspondence follows the W drawing and remains
provisional even though the photographed package population is known.

Keyboard controller DIP bodies and leads now reuse the pinned KiCad packages.
`tools/configure-keyboard-components.py` generates the rotated footprints from
upstream lead coordinates, so drilled holes, solder eyes and packages agree.
Socketed CPU/EPROM seating is separate from soldered logic. The transplanted
ceramic EPROM retains its photographed body/cover rather than becoming a black
plastic DIP. Ink heights follow the new package tops. Package geometry and
footprints retain the upstream licences in `components/kicad/NOTICE.txt`.

Top and underside controller artwork now has stepped edge buses and diagonal
breaks based on PXL_20261012_123622947.jpg and PXL_20261012_123648677.jpg, with
solder eyes for all transistor leads. Solder eyes stay separate at 1.27 mm
transistor pitch. These clean polylines are visual approximations, not a traced
netlist; hidden lead bends and exact copper widths remain unverified.
The accepted keyboard exterior and physical verification classifications are
unchanged. Check package/board clearance with `tools/check-assembly.py` and
compare the canonical review views against the owner photographs.

### Pin-pitch registration, connector construction and finishes — export v38

`tools/register-processor-photo.py` reproduces a local projective fit from four
DMA DIP-40 lead centres in PXL_20261014_073200542.jpg. The reference dimensions
are nominal 2.54 mm lead pitch and 15.24 mm row spacing, not new measurements.
`processorPinRegistration` records image size, selected points, transform and
component centres. The rear-facing photo basis also corrects the earlier mirrored motherboard placement; board-attached holes, pads and connectors move together, and ribbon ends follow their socket. Pin-one orientation remains provisional. Eleven package positions and the long socket now use this
fit. Reference-designator correspondence, lead picking and extrapolation remain
provisional. Obscured mounts and unregistered parts are not relocated by guess.

The keyboard controller connector follows the closed, segmented pale bridge
visible in PXL_20261012_123622947.jpg. Connector and resistor tails now share
board apertures and underside solder eyes. The matrix socket remains a separate
photo-based assembly: detached photographs do not establish exact mating
orientation, so no invented cable or forced docking has been added.

Canonical material profiles distinguish tinned leads, solder, phenolic board,
ceramic, IC moulding and painted metal. The browser uses the same profiles for
instanced ICs. They describe clean finishes, without copied wear or baked photo
lighting. The accepted exterior and printed/verified classifications are unchanged.

### v39: photographed board detail and cable endpoints

Owner `PXL_20261014_073200542.jpg` supplies 26 manually selected visible copper
segments, the visible `25.8` board marking, eleven small component positions and
the motherboard ribbon socket. `board-layout.json` retains the image coordinates
and the existing nominal DIP-pitch homography. Copper is clean shallow geometry
under a green mask finish; it is a partial visual reconstruction, not a netlist.
No wear, hidden connections, inferred resistor values or invented reference
labels were added. Four earlier upper-board capacitor estimates remain marked.

The ribbon ends now meet a seated plug in that socket. The plug clears the
socket dividers; intermediate cable bends remain provisional. Physical
printed-and-verified classifications are unchanged. Rebuild with
`tools/configure-pcb.py`, the normal export/package tools, and run
`tools/check-assembly.py` before importing into DAC.

### v40: component population, sockets and continuous harness

Owner `PXL_20261014_073200542.jpg` now registers nine formerly estimated package
placements and twenty additional visible packages. New `PHOTO-*` identifiers
are visual anchors, not schematic references. Nominal package sizes, pin-one
orientation and unresolved reference correspondence remain explicit estimates.
Three pale open-frame IC sockets lift the CPU, FDC and EPROM packages; their
contact tails, board holes and solder eyes remain aligned. The pale blocks near
the lower center are modeled as jumper links, not a guessed ribbon connector.
An old unsupported connector placeholder is omitted where the photo shows chips.
Selected film capacitors, cans and resistors fill the visible lower/right areas;
an ambiguous leaning can was left out rather than given a conflicting mount.

Ribbon geometry now forms a continuous board → drive 1 → drive 0 chain, with
rounded folds and constant-width sections. Ridges and the edge stripe follow the
same section directions. Exact intermediate folds and available slack are not
measured. Drive power wells contain nominal recessed crimp contacts. Browser
separation moves the complete drive-to-drive span together and anchors board/PSU
ends. Existing washers/supports remain estimated; no additional hidden mounting
hardware or electrical values are invented. Physical print verification is unchanged.

### v41: two-photo registration and visible board detail

Six nominal lead rectangles (three per photo) now establish separate projective
fits for the RAM and processor photographs. The common upper CTC joins the two
planes; the unused lower CTC agrees to 1.15 mm. Fit residuals are 0.36 mm and
0.07 mm respectively, **not dimensional accuracy guarantees**. The four observed
edge points disagree with a perfect rectangle by several millimetres. The board uses a 251 × 368 mm rectangular envelope containing those edge picks,
rounded outward to whole millimetres. This is a photo estimate, not a measured
outline. Hidden mounts retain their provisional positions. All photo-registered packages, passives, visible
connector centres and artwork use the new transforms. Unregistered packages
remain drawing estimates. See [observations](board-photo-observations.json) and
[calibration report](checks/board-calibration.json).

Reproduce with `python tools/calibrate-board.py --apply` (NumPy and SciPy), then
`python tools/configure-pcb.py`. Both commands are idempotent. Legacy registration
scripts record earlier passes; do not run them over the calibrated layout.
The original pixels and nominal lead pitches remain available for review.

Readable specimen legends replace several generic labels, including M2716-1F1,
UA858D and UA8560D. The serial chip's corner pin-one feature faces opposite the
DMA chip; circular mould ejector marks are not treated as pin-one indicators.
Covered CPU/FDC markings remain unverified. Additional visible copper segments
and twenty circular tinned lands are geometry, not whole-photo skins or an
inferred netlist. Wear and tape texture are not copied into the clean model.

Board download STLs now include sockets, contacts, jumpers, artwork and lands,
as well as their editable sources. `tools/check-metadata.py` verifies generated
README counts, browser counts/evidence, mesh/download hashes and key source files
inside every archive. Run it after `tools/export-downloads.py`; it needs only
Python's standard library. Physical print verification is unchanged.

The browser export also carries the canonical subdivided ribbon paths. DAC moves
section centres and rotates their cross sections without widening the 33 mm
ribbon or separating its conductor stripes. The board-end route passes around
the rear edge of the display PCB instead of through its substrate. Intermediate
folds and the extension in a separated view remain illustrative, not measured
cable slack. Geometry checks sample 21 positions in both connected and parked
states against both PCB substrates, chip bodies and the drive-carrier envelope.

### v42: component evidence, mounting and cable clearance

Chip metadata now separates photographed markings from schematic identity.
Only observed markings are printed on package surfaces; the DAC atlas preserves
letter proportions and complete strings. Component inspection pairs a crop of
the original owner photo with a rotatable clean nominal package, retaining the
full-photo and drawing links. Crop bounds provide context, not metrology.

The [mounting audit](checks/mounting-audit.json) records two visible open holes
and an upper-edge screw/washer. Open holes no longer receive invented fasteners;
two obscured legacy mounting positions remain estimates. Underside spacers and
threads have not been measured. Keyboard controller end holes are paired and
open in the detached-board photo. Matrix-board corners have a small estimated
radius and the connector carries its visible `2У0` mould legend. The approved
keyboard exterior is unchanged. Hidden switch contacts and controller-to-matrix
mating are still illustrative/unresolved.

Ribbon routing now clears the rear case edge and avoids intersecting its other
span, including separated/disconnected inspection poses. The photographed
terminal positions are preserved; intervening folds and animated slack remain
estimates. DAC tests cover full-width strip crossings, connector envelopes,
case returns and PSU boundaries across 21 poses in each connection state.
Two power-harness entry zones still intersect the modeled solid PSU wall:
local geometry/photos do not yet establish the aperture shape. These are
explicit audit exceptions, not claims of correct feed-throughs.

No additional part is classified as physically printed and verified.

### v43: installed keyboard board and cable entry

Owner photos `123048886`, `123907435` and `123319025` establish the installed
orientation: the narrow controller overlaps the rear edge of the matrix PCB,
with its connector aligned to the matrix socket. The cable opening sits to its
left in typing coordinates. Its folded, notched sheet-metal support is on the
short edge toward the controller, holding the round grooved bush horizontally.
Two separate rubber strips wrap the opening’s long edges; the brown insulating
sheet lies on the inner bottom cover. These replace the previous mirrored
placement and incorrect bare-edge interpretation. Positions and mating depth
remain photo estimates, not measured fits or print verification. The browser’s
separated view keeps the bush end anchored while the cable follows the board.

### v44: keyboard construction and board finish

The bottom lid now has three front-edge slots and four hollow pressed foot
pockets with a nominal 1 mm floor, following owner `123319025`. Two controller
screws and their visible retaining straps follow installed photo `123907435`;
the unused holes remain open. End solder rings now use the same coordinates as
the actual holes. Hidden threads and strap attachment details are unverified.

The cable termination has a clean braided shield pigtail, broad tinned land and
solder termination based on `123539882`, without copying frayed strands or wear.
The jacket now reaches the exit of its saddle clamp.

`keyboard-artwork.json` records 26 matrix and 43 controller underside route
segments against owner photos `123048886` and `123648677`. Rebuild the projected
polylines with `python3 tools/configure-keyboard-artwork.py`. Matrix solder
points use irregular photographed positions and rounded joints instead of a
grid of screw heads. These are visual centre-line estimates: obscured paths,
exact pad shapes and circuit continuity remain unverified. Photographic
perspective and assumed PCB envelopes limit their dimensional accuracy.

The matrix laminate is greener with restrained light transmission in DAC; the
controller has a separate warmer, rougher fibreglass finish. Thin-laminate
translucency uses restrained alpha blending, avoiding a whole-scene refraction
pass for a mostly obscured PCB. Colour and optical
properties are visual estimates, not measured material data. OpenSCAD shows
the same nominal colours; STL carries geometry only. No physical verification
status changed.
