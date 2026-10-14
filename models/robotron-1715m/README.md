# Danila’s Robotron 1715M

The canonical OpenSCAD source for Danila’s museum machine and the DAC browser export. Geometry uses millimetres: X right, Y rear, Z up. Open [model.scad](model.scad) for the complete machine, or [keyboard/model.scad](keyboard/model.scad) for fast colored keyboard review. Select a named `part` to export it independently.

## Current reconstruction

The main unit, monitor and keyboard enclosures use the owner-confirmed 1 mm bent painted sheet. The system fascia has a thin face with folded returns; the monitor bezel is hollow, and the roof vents penetrate the shell. Local bend radii remain estimates. The exterior follows Danila’s photographs, with clean paint, plastic, rubber and metal rather than full-panel photo skins or copied wear. Small manufacturer labels use credited local photo crops. The keyboard’s approved exterior dimensions and separate sheet-metal layers are documented in the [keyboard workflow](keyboard/README.md). Interior dimensions remain provisional unless explicitly measured. The latest owner keycap correction is shared by the assembled keyboard: 15 mm round body, 15/11/9 mm underside diameters, 5 mm spring recess and tapered crown. The 18/23 mm wide-key dimensions describe the lower raised body.

The front controls follow owner photos `PXL_20261012_124827690.jpg` and `PXL_20261009_133019620.jpg`: one curved double-headed arrow per drive, sloping finger scoops, plain black-plastic levers, and RESET / OFF / ON / POWER legends. The textured clear power rocker sits behind a real opening in the 1 mm front sheet, with a separate dark switch housing. Scoop depth, rocker recess and local radii are photo estimates. Markings are canonical OpenSCAD geometry, not duplicate browser overlays.

The October 13 inserted-disk views (`113529099`, `113537277`) now set a 7 mm deeper media/mechanism datum, longer projecting lever boss, flush activity lenses and a higher upper finger recess. The entire lever sweep clears the inserted jacket; hub, clamp, head and label positions move together. The fascia returns reach the enclosure instead of leaving an open horizontal slot. The monitor surround follows the rolled perimeter and dished inner return in `133017092` / `125018215`. Local depths and angles remain photo estimates.

The keyboard controller is oriented with its input end toward the actual cable opening (`123907435`). A continuous internal lead reaches its shield clamp, passing through a round grooved black bush captured in a 1 mm bent metal support (`123539882`); the rectangular opening has bare edges. The plug has the asymmetric housing, screw layout and offset cable outlet from `090425989` / `090431122`. DAC preserves the input connection when separating the keyboard for inspection.

The system unit has a W/M motherboard with integrated A44 U8272 and 32 RAM packages, plus a separate display controller mounted component-side down. [board-layout.json](board-layout.json) records the shared placement, sources and uncertainty. There are 118 nominal KiCad DIP packages and 2,274 lead apertures. The October 14 component-side photographs locate 39 display-board ICs, including three UL6516D memories and the SAB8275P, red upright capacitors and the white wound component. Generated P01–P39 IDs identify photo positions, not printed board designators. Mainboard positions still follow the W drawing and await full photo calibration. R19/R102 and C90/C91 follow the documented CPU/DMA adjacency, with estimated positions and no invented electrical values. Unidentified footprints retain generic labels. Clean chip legends identify documented devices; illustrative copper routes are not a netlist.

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
