# Danila’s Robotron 1715M

Parametric OpenSCAD reconstruction of Danila’s exterior with a provisional reference interior. Original model, scripts and owner photographs are MIT licensed (see LICENSE); the credited PCB photographs in `reference/oldcrap/` and `reference/robotrontechnik/` are excluded from MIT and retain their original rights (see their NOTICE.txt files). This is an editable museum reconstruction, not a scan, manufacturing drawing or validated replacement enclosure.

Open `model.scad` for the assembled system unit, monitor and keyboard. Set `part` to any entry in `parts` to inspect/export it separately. Coordinates are millimetres: X right, Y towards the rear, Z up. The keyboard is placed in front of the computer. [`robotron-1715m.stl.zip`](robotron-1715m.stl.zip) contains the full-resolution combined STL visual reference; the separate exports retain the switch and material boundaries used by the museum.

## Evidence and dimensions

The original [Robotron 1715/1715W manual, printed p.35 (PDF page 36)](https://xepb.org/robotron/docs/pc_manu.pdf#page=36), digitized by U. Zander, lists these nominal envelopes:

| Component | Width | Depth | Height |
| --- | ---: | ---: | ---: |
| System unit | 500 mm | 400 mm | 130 mm |
| Display | 320 mm | 350 mm | 330 mm |
| Keyboard | 500 mm | 200 mm | 40 mm |

These are family specifications, not new measurements of Danila’s specimen. The display height includes its stand; its shell and stand proportions are inferred from the photograph. Small projections and approximate feet can extend beyond nominal envelopes. The monitor insert uses Danila’s existing [measured ring](display-base-ring/): 175 mm OD, 169 mm ID, 5 mm high; its physical fit is still unverified.

The ruler photograph `PXL_20261009_132938614.jpg` provides an independent local scale. In a 1824 × 1373 display of that photo, the 200 and 100 mm ruler ticks are approximately x=405 and x=1380. Six number-row key intervals span approximately 1172 pixels, giving 1172 / 6 / 9.75 ≈ 20.0 mm. The model uses 20 mm pitch. Allow about ±1 mm for hand-picked landmarks, perspective and the ruler lying at a different height from the key centres. This is not submillimetre metrology.

Photos establish the two drives, 14 front vents, side vent banks, front switches, separate keyboard key groups, translucent function caps, red CE key, monitor bezel and blue tape, and keyboard underside. Wall thickness, curves, seams, feature locations and colors remain estimates. The keyboard layout represents 97 visible key positions. Keycaps are exported as seven reusable OpenSCAD profiles and instanced individually in the browser so the entire cap moves when pressed. Blank fillers and some indicator hardware remain incomplete. The October 12 owner photographs now establish the rear connectors, rectangular system feet, keyboard controller and monitor underside. Exact system logic-board revision and CRT electronics remain unverified. Reference electronics are now modeled, with their provenance recorded below. The documentation archive also contains electrical schematics; these are not dimensioned enclosure drawings. Its older 1715 schematics must not be mistaken for 1715M/W schematics.

Sources: [documentation index](https://xepb.org/robotron/docs.html), [manual](https://xepb.org/robotron/docs/pc_manu.pdf), [service manual](https://xepb.org/robotron/docs/pc_serv.pdf). Historical documents retain their original rights and are linked, not relicensed or bundled.

## Reference photos and consistent materials

`reference/photos.json` records the source archive and original/published SHA-256 hashes. `reference/photos/` contains losslessly sanitized JPEGs: EXIF, XMP, IPTC, comments and trailing motion video were removed, with decoded pixels checked against the originals. The original download was not modified. To reproduce sanitization after extracting the archive, run `python3 tools/import-photos.py /path/to/extracted/photos` from this model directory (requires Pillow).

OpenSCAD/STL stores geometry, not photographic materials. `browser/model.json` version 15 includes material profiles, transcribed legends, a small wordmark decal, reference-photo links, a live screen anchor and individually named power/reset meshes.

Full-panel photo skins are no longer used. The old underside crops contained a photographed cable and feet in addition to the modeled ones; removing them eliminates those duplicates and their baked shadows. There is now one continuous Bézier-routed lead, a modeled grommet, a hollow keyboard shell with a separate bottom plate, four rubber foot frames with metal inserts, six perimeter fasteners and a detailed exterior plug. The two drive fronts have recessed insertion slots/finger wells, rounded latch handles and separate red lenses. The monitor tape is a thin solid. Keycaps have square skirts, rounded shoulders and dished tops, including a stretched dish for long caps.

The palette and finish are visually estimated from the photographs, not colorimetrically calibrated. Browser paint, plastic, rubber, metal, lens and glass materials react to scene lighting; subtle procedural grain uses model-space millimetres, avoiding large repeated photo patches, seams and baked illumination. The fine grain is an approximation of the observed finish, not a photographic sample. Surface normals are smoothed with creases preserved. The original small `robotron 1715 M` wordmark remains a masked photo crop; owner drive plates and small TEAC board labels are also photo crops; it contains no modeled physical feature. Drive arrows and control labels are reconstructed markings. Key legends are transcribed into a transparent atlas placed on the dish surface; font shapes are approximations, not scans. Blank Shift/Space/Caps key tops remain blank. Input support is still separate from the visible legends.

The owner JPEGs and their original UV landmarks remain reference evidence, with no repainted or generated photograph pixels. Wear and scratches are deliberately omitted from new geometry. Clear keycap construction, cable route, connector dimensions and unseen hardware remain approximate. The model is a coherent reconstruction, not a scan of every mark on the specimen.

## October 12 specimen survey

All 175 images from `Photos-1-001 (5).zip` (172) and `(6).zip` (3) were reviewed. Danila explicitly licenses these photographs under MIT. `reference/owner-20261012.json` inventories every original with a SHA-256 hash; 28 complementary views are published in `reference/photos/`, losslessly stripped of private metadata. The original ZIPs remain untouched. The browser loads only the selected inspection references on demand.

`specimen-details.scad` reconstructs clean parts, using photos for shapes and component arrangement rather than full-panel skins. Paint loss, rust, dirt and scratches are not copied; the former keyboard corner-wear decal has been removed. Existing small maker-label crops remain documentary markings, not enclosure textures.

| Feature | Owner evidence | Reconstruction and limits |
| --- | --- | --- |
| Keyboard switch PCB and insulation | 123048886, 123103225, 123907435 | Broad PCB, mounting holes, insulating rails and separate narrow controller; simplified row buses/pads, not reconstructed electrical routing. |
| Keyboard controller | 123622947, 123631131, 123729356, 123648677 | Socketed UB880D, small DIP logic, ceramic EPROM package with blue window cover, connector, discrete components, electrolytics and shield clamp. Nominal 2.54 mm lead pitch; approximately 270 × 46 mm envelope inferred from package proportions. Placement, passive values and hidden routing are estimates. |
| Keyboard feet | 123257360, 123407648, 123440420 | Hollow rubber frames with metal channel inserts and slotted screws; no worn finish. Photo-scaled envelope approximately 32 × 11 mm; see `specimen-measurements.json`. |
| System feet | 131106217, 131117938 | Rectangular rubber frames replace provisional cylinders; metal channels and slotted screws. Dimensions remain estimated. |
| Monitor underside | 125038677, 125108737, 125132359.MP | Hollow annular pedestal, folded mounting brackets, two ribbed adjustment knobs, lower vent banks and cable outlet. Original 175/169 × 5 mm insert dimensions retained. |
| Rear panel | 125226422, 125256937, 125413618, 125417620 | DISPLAY, V24, PRINTER and three-row FLOPPY-DISK sockets, blanking plates, two fuse holders, three-pole monitor power outlet and mains inlet. Shown unplugged; contact sizes and panel placement are estimated. |

Filenames in the table abbreviate `PXL_20261012_<time>.jpg`. The underside photograph also corrects the cable guide to a folded bow-tie shape, approximately 57 × 37 mm around a 42 × 17 mm opening.

The model uses the existing family enclosure envelopes and owner ruler-derived key pitch; these new photos do not provide a fresh calibrated measurement of every feature. The keyboard controller is separated as a complete assembly in the browser’s open-keyboard view; this is an inspection arrangement, not its operating position.

**Keyboard ROM provenance:** Danila says the installed EPROM was transplanted from another board and works. Its visible package and blue window cover are reproduced. Neither its label nor successful operation proves its contents match the museum’s S600 reference ROM. No firmware binary or emulation behavior changes in this update.

The photographs do not expose this specimen’s system motherboard, PSU internals or CRT electronics. Their existing comparative references and credits remain in force; they are not reclassified as owner-verified hardware.

## Rebuild

Requires Python 3 and OpenSCAD with the Manifold backend (tested with 2026.10.05). From the repository root:

```sh
python3 models/robotron-1715m/tools/configure.py
python3 models/robotron-1715m/tools/export.py
openscad --backend Manifold --export-format binstl -o models/robotron-1715m/robotron-1715m.stl models/robotron-1715m/model.scad
python3 models/robotron-1715m/tools/package-assembly.py
openscad --backend Manifold -o models/robotron-1715m/preview.png --imgsize=1600,1200 --viewall --autocenter models/robotron-1715m/model.scad
```

`tools/configure.py` generates the shared keyboard geometry/UV table. `tools/export.py` exports body/detail meshes and two reusable mechanism prototypes and seven reusable keycap profiles with their hashes. `part="keycap"` and `key_index` select a local, origin-centred cap for export; assembly geometry stays fully assembled. The DAC repository imports the export with `python3 scripts/sync-robotron-model.py ../3d-models`, recording the source commit and checking hashes. Firmware and emulator code stay in their own repositories.

## Interaction metadata and keyboard evidence

### Keycap spring measurements (2026-10-10)

Danila reported the following measurements for the keycap springs of at least
one Robotron 1715 keyboard variant. The [keyboard photograph](reference/photos/PXL_20261010_131354451.jpg)
identifies the specimen; the [removed spring close-up](reference/photos/PXL_20261010_131835506.jpg)
preserves its winding and end details for further inspection.

| Measurement | Owner-reported value | Qualification |
| --- | --- | --- |
| Spring diameter | 13 mm | Outside/mean/inside diameter was not explicitly specified |
| Spring length | Approximately 23 mm | Removed spring shown; compression state during measurement not explicitly specified |
| Wire diameter | Approximately 0.35 mm | Rough measurement |

The close-up shows a cylindrical helical spring with tightly wound turns at
both ends and roughly five open turns between them (visual estimate only).
The exact total turn count, including end turns, remains unconfirmed; the
full-resolution photo is retained so it can be checked later. Neither photo
contains a ruler or caliper: the dimensions above come from Danila's report,
not a scale inferred from the images.

These measurements apply to the photographed variant and are not established
for every 1715/1715M keyboard or every key position. They are reference evidence;
the spring geometry now uses these dimensions provisionally: 13 mm is interpreted as outside diameter, five open turns plus two close end turns per end. The 12 mm installed height, 2.2 mm travel, stems, sockets and switch housings are estimates. The photographed spring keyboard has different keycaps from the museum specimen; this is family evidence, not proof of identical switches.
Both owner photos were imported losslessly with metadata removed and their
original/published hashes recorded in `reference/photos.json`.

A [printable hand-winding trial mandrel](keycap-spring-mandrel/README.md)
records the springback sizing calculation and a sample-based calibration
procedure. Its initial 6.4 mm shaft is an unvalidated estimate for 0.35 mm
music wire and a 13 mm finished outside diameter.

### Input behavior

`keyboard-layout.json` supplies stable IDs, physical positions, photo-reference landmarks, transcribed legends and the museum input adapter. The [original manual, printed pp.9–11](https://xepb.org/robotron/docs/pc_manu.pdf#page=10) supplies Tab, Insert/Delete, function-key and numeric-keypad codes; cursor directions agree with the existing core adapter. Numeric-pad digits have distinct codes, not ordinary ASCII digits. ET uses API input 13, translated by `robotron_key()` to the documented keyboard byte 9E. No historical document or firmware is bundled under this model’s MIT license.

89 positions have input behavior, including Shift/Ctrl/Caps Lock. ALT, ß, repeat R, SI/SO and four navigation symbols are explicitly unverified. Unverified shifted symbols also send no invented byte. Shift/Ctrl are visitor-side one-shot latches; Caps Lock is persistent until released or focus/reset/power changes. The browser’s Caps Lock lamp reflects that local input state, not feedback from the original keyboard controller. SI/SO’s alternate character-set protocol is not available through the current browser core API.

Each drive lamp and moving head follows that drive’s emulator state; rotor speed and track pitch use nominal TEAC references, not specimen measurements. Opening the case moves its lid and monitor visibly up and back together. A separate control lifts the drive assembly forward and up and separates the fascia and keyboard deck. The system-unit interior is reconstructed from comparative references; drive cables disconnect by default in the separated view, with an optional stretched-cable illustration. The external cable route and monitor-glass curvature remain estimates.

## Comparative references (2026-10-10)

Danila’s photographs remain authoritative for specimen appearance, tape, wordmark and keyboard legends. Other collections clarify family shapes, not this machine’s identity:

- [Robotrontechnik K7222.25 photographs](https://www.robotrontechnik.de/html/zubehoer/bildschirme.htm): bowed CRT outline, recessed surround and opened shell. The shell joint now sits halfway up the housing, following the owner’s correction.
- [MCbx PC 1715 collection](https://oldcomputer.info/8bit/robo1715/index.htm): comparative front view and curved glass; its keyboard variant does not replace our transcribed legends.
- [Oldcrap’s PC 1715 restoration](https://oldcrap.org/2017/12/26/robotron-1715/): exterior proportions and temporary interior reference photographs. This is another specimen and an earlier PC 1715, not verified M/W internals. DAC labels the open chassis and motherboard photos accordingly and loads them from their original host on request. The gallery loads its photographs externally. Two PCB photos are also stored as clearly credited reference textures, excluded from MIT; owner interior photos will supersede them.

`monitor-profile.json` is shared by OpenSCAD and the browser: a convex ellipsoid clipped to a bowed superellipse, with a rectangular active raster inset from the glass perimeter. Radii, bow and margins are visual estimates, not tube specifications. The browser uses a smooth version of that same surface for live pixels, with inactive glass around the raster so characters do not reach the curved corners. `tools/configure.py` also generates `monitor-profile.scad`.

## Provisional interior and PCB photography

The user authorized a reference reconstruction while photos of this specimen’s internals are pending. `interior.scad` provides drive bodies and mechanisms, their bracket, motherboard and controller, package bodies and leads, a folded PSU shield and cover, cooling fan, ribbon cables, power wiring and approximate keyboard board/switch housings. The PSU’s enclosed components are not modeled. Monitor reference electronics are now included as described below. This is a visual reconstruction, not a wiring or servicing guide.

The reusable `components/teac-fd55fv.scad` uses the [TEAC FD-55FV-13 specification Rev E, pp.101–103, Fig.101](https://retrocmp.de/fdd/teac/TEAC_FD55-FV.pdf#page=3): nominal body width 146 mm, depth 203 mm excluding connector projections, height 41.3 mm. The illustration distinguishes a wider projecting front bezel; the museum retains the owner-based front geometry. Head carriage, spindle clamp, stepper, solenoid, stamped deck and underside motor details follow Oldcrap’s top and underside pictures and remain approximate. The exact suffix of the owner’s drives is not verified.

`pcb-references.json` records original photo URLs, hashes, credits, pixel landmarks, board envelopes and raised package outlines. The browser uses the unmodified photos on both the board surface and the tops of the matching 3D packages; `tools/configure.py` generates the same package positions in `pcb-packages.scad`. The controller photo’s obstructing ribbon-cable patch is excluded from the texture geometry. No photographed cable is laid over a second modeled cable. Traces, markings and solder remain photographic; component heights and board mounting positions are estimates. These boards depict an earlier PC 1715 and are **not verified 1715M/W board layouts**.

The physical placement is scaled from the open-chassis photos inside the manual’s 500 × 400 × 130 mm enclosure. The drives are 203 mm deep behind the owner’s fascia; the PSU occupies the right compartment, fan between it and the logic/drive section. Cable routing and mounting clearances are approximate. `part="interior"` shows only these reference parts in OpenSCAD. DAC’s **Inside** view opens the system unit while keeping its lid and monitor visible above and behind it; **Lift drives and keyboard** separately lifts the drive assembly to expose more of the motherboard. Camera presets preserve these controls, and **Drives** gives a close-up of the mechanisms while the case is open. Photo credits remain visible during both inspections.

Five additional owner photographs downloaded on 2026-10-10 show the running CRT, bezel, stand and front panel in 2025. They are stored with the original owner photo set, with metadata removed losslessly and original/published hashes recorded. They confirm the English POWER marking and supply a new monitor reference. They contain no exposed system-unit PCB, so they do not supersede the comparative PCB textures. Append future owner photos from a dedicated directory using `python3 tools/import-photos.py /path/to/photos --append --source 'Owner photos, date'`.


## Opening the monitor

`monitor-interior.scad` adds the reference CRT funnel and neck, deflection yoke and windings, retaining band and metal support chassis, a vertical circuit board, neck board/socket, heat sinks, capacitors, slotted shielding and cable runs. Shape and arrangement follow [Robotrontechnik’s K7222.25 open-shell photographs](https://www.robotrontechnik.de/html/zubehoer/bildschirme.htm#k7222-25). These are visual estimates inside the known housing envelope, not measured tube specifications or a verified circuit assembly. K7222.25 housings could contain differing electronics; the exact board and tube in Danila’s monitor remain unverified.

The 012-6920 board photo is a credited comparative surface with its own NOTICE and source hash. Its crop excludes the photographed shield, which is modeled separately. It is not represented as a photo of this specimen. The CRT front remains the existing live curved display; the newly modeled funnel extends behind it. The shell now exports as `monitor-shell-lower` and `monitor-shell-upper`; DAC’s independent **Open monitor shell** control moves only the upper half and its tape. The complete monitor follows the system-unit lid when that cover opens. Opening either enclosure preserves the other’s state; camera presets no longer close enclosures. **Inside monitor** looks into the tube and electronics from behind.

## Owner keyboard connector (2026-10-10)

Five close-ups from `Photos-1-001 (3).zip` establish the tapered split housing, paired hooked release levers, three slotted screws with hexagonal nuts on the opposite face, cable entry and recessed two-row insert. These are modeled as geometry, with separate housing and insert colors. The plugged-in face is concealed by the system unit. The approximate 35 × 46 × 12 mm envelope, contact spacing and socket position are estimates: these photos contain no ruler and do not establish an electrical pinout. All five sanitized owner originals are retained as reference evidence.

## Owner drive evidence (received 2026-10-10)

Six photographs from `Photos-1-001 (4).zip` (filenames dated 2025-02-12) now replace the comparative drive-top evidence. Looking from the rear, the left drive has a Ratan Exports & Industries Ltd. “Assembled in India” sticker and the longer TEAC 15532092-00A sensor board; the right drive has a Robotron K 5601 plate, factory number 044713, and the shorter TEAC 15532064-00A board. Thus the K5601 is on the left when facing the computer. The Ratan model field is not legibly filled in. These markings do not establish that both drives are FD-55FV-13.

The shared 146 × 203 × 41.3 mm reference envelope is retained. The mechanism now follows the owner photographs: central slotted clamp bridge, lengthwise latch rod, head carriage and guide rails, stepper position, rear crossbar, card-edge connector, power socket, and different sensor-PCB outlines. Small dimensions, hidden parts and resting poses remain estimates. Main logic boards and monitor electronics still use credited comparative references.

`drive-labels.json` records the exact source quadrilaterals, positions, transcriptions and drive identities. DAC perspective-corrects only these small markings on the original unmodified photographs; it does not apply an entire mechanism photograph as a skin. The Robotron country line is typeset because a cable crosses the photograph there, preventing a photographed cable from appearing as an extra modeled wire. The serial, manufacturer text, Ratan sticker and TEAC markings retain photographed print and wear. Physical plates are in the OpenSCAD `drive-label-plates` part; photo materials are carried by the browser manifest because STL cannot store textures. All six owner originals are losslessly sanitized and retained in `reference/photos/`.

The drive spindle clamps and head carriages are separate OpenSCAD/browser parts.
`driveMotion` in the manifest records each spindle pivot and a nominal 79 × 25.4/96 = 20.902083 mm
head travel toward the hub. DAC drives their motion from each emulated unit's
motor/cylinder state and per-drive phase; 300 RPM and 96-tpi travel are reference values,
not measured motion of the owner's drives. Reduced-motion mode stops rotation
while retaining the current head position. The stationary deck and motors no
longer include duplicate carriage/clamp geometry. `tools/export.py --parts ...`
can regenerate named parts while retaining verified existing meshes; omit it for
a complete rebuild after general model changes.


## Detailed assembly revision (2026-10-11)

The browser manifest is now version 9. The canonical OpenSCAD source includes hollow
keycaps with stem sockets, a perforated keyboard plate, switch housings and reusable
spring/stem geometry. Browser springs compress with key presses and extend toward
an estimated free length when the caps are lifted. Hidden switch construction is
provisional; the spring dimensions come from the owner measurements above.

The owner drive overview (`PXL_20250212_094033966.jpg`) guided the stepped head
carriage, metal head shield, screws, sensor-board components, laminated stepper,
and separately movable clamp linkage. Browser latch release is an inspection aid,
not an emulator media-eject operation. Track pitch uses the TEAC nominal specification; carriage origin and clamp lift remain estimates.

Board standoffs, chassis brackets, fan fasteners and cable retainers provide visible
mounting relationships. Cable ends stay attached during separation using explanatory
stretching; the stretched lengths are not physical measurements or available slack.
The PSU internals remain unmodeled behind the shield rather than asserting a board
revision we have not seen.

The CRT funnel now has multiple taper sections; the monitor includes denser yoke
windings, a perforated neck socket, retaining collar, board mounts, resistors and
small capacitors. Additional online photographic references checked on 2026-10-11:

- [Robotrontechnik K7222.25 interior](https://www.robotrontechnik.de/bilder/Zubehoer/Bildschirme/K7222/K7222-25_innen_2_k.jpg)
- [Robotrontechnik open shell](https://www.robotrontechnik.de/bilder/Zubehoer/Bildschirme/K7222/K7222-25_innen_k.jpg)
- [Oldcrap PC1715 restoration](https://oldcrap.org/2017/12/26/robotron-1715/)

These reference machines are not Danila's specimen. No newly found third-party image
is bundled by this revision. Existing photographic PCB credits remain attached.
Exterior refinements include case seam ledges, recessed cover screw holes, hollow
caps and a tiny feathered owner-photo corner-wear patch. Feature placement remains
photo-estimated, not metrology. Springs/stems are shared browser instances to avoid
one draw call per mechanism; all corresponding shapes remain in OpenSCAD.


## Reusable component packages (2026-10-11)

The motherboard and controller use 132 photo-aligned KiCad DIP packages from seven
families (14, 16, 18, 20, 24, 28 and 40 pins), replacing the old box bodies and pin
strips. The old motherboard landmarks incorrectly spanned neighbouring chip rows;
they have been retraced, including four rows of eight memory packages. Package
choices and pin-one orientation remain provisional where the photo is ambiguous.
The nominal upstream shape is never stretched to fit a photographic rectangle.
This models another PC 1715, not a verified 1715M/W board revision.

The KiCad sources, pinned revision, original licence headers and credits are in
[components/kicad](components/kicad/NOTICE.txt). They and their derived library
meshes retain their upstream terms, not this project's MIT licence. Six original STEP files use GPL-3.0-or-later with a design exception; the
24-pin wide package uses CC BY-SA 4.0 with the KiCad exception. The upstream
collection licence is preserved as well. Original project code remains MIT.

`tools/convert-kicad.py` reproduces the material-separated STL meshes with CadQuery
2.5.2 / OCP 7.7.2. It checks shape validity, volume conservation and that the metal
mesh contains the expected number of leads. `tools/configure-pcb.py` produces the
shared OpenSCAD/browser placement records from `pcb-references.json`. Browser
rendering instances each body/lead family instead of issuing one draw per chip.

The 86 discrete components use original OpenSCAD geometry: axial resistor bodies
and leads, ceramic discs, electrolytic cans with top vents, and metal-can packages.
Positions follow visible landmarks; dimensions and electrical values are not
established. Resistor colour codes and unreadable chip identities are not invented.
The board photo surface omits the new component silhouettes; only photographed
markings are projected onto the DIP tops. Remaining unmodeled details can still
appear in the credited board photograph.

Rebuild placements and the complete assembly with:

```sh
python3 models/robotron-1715m/tools/configure-pcb.py
python3 models/robotron-1715m/tools/export.py
openscad --backend Manifold --export-format binstl -o models/robotron-1715m/robotron-1715m.stl models/robotron-1715m/model.scad
python3 models/robotron-1715m/tools/package-assembly.py
```

## Board construction and independent inspection (2026-10-11)

The motherboard and floppy controller now export independently. Set
`pcb_board="motherboard"` or `pcb_board="floppy-controller"` alongside a
`logic-*` part in OpenSCAD, or choose that board under **Inspect assembly** in
DAC. The assembly retains its reference positions; isolation hides obstructing
parts without inventing a physical removal path or moving attached wiring.

The 132 DIP bodies retain their pinned KiCad geometry. The converter now slices
individual STEP leads at the seating plane to derive hole centres, rather than
assuming nominal row spacing. `pcb-components.json` records 2,504 mounting
positions: 1,656 on the motherboard and 848 on the controller, including passive
and estimated connector tails. Each has a real 0.95 mm aperture, a 1.8 mm metal
pad/barrel and an underside solder fillet through a 1.6 mm board. These dimensions
are visual estimates, not recovered PCB fabrication data. Browser pads and
solder use two reusable meshes instanced per board; the combined STL includes
the solids. It is now about 92 MiB and is intended for offline inspection.

The comparative [Old Crap board photographs](https://oldcrap.org/2017/12/26/robotron-1715/)
were reviewed again. They support three additional yellow axial film capacitor
bodies and different electrolytic diameters, bringing the discrete population
to 89. Electrolytic height is estimated from diameter. Values, polarities and
resistor bands are not invented. The visible ICs do not justify adding ceramic
packages indiscriminately. Tape-obscured IC lettering is omitted; package
placements beneath that tape are still provisional. Socketed IC variants,
exact connector pin counts/keying and internal contacts require better evidence.

Two long connector housings now have divided cavities and separate contacts.
A smaller ribbon plug has a strain-relief bar at the existing cable endpoint.
Positions follow photographic landmarks or the existing illustrative cable
route; pitches and hidden contact shapes are provisional. Connector apertures
use the same mounting data as their tails. They do not assert an electrical
pinout or a verified mating part.

DAC extracts pale traces and markings from the unchanged source photo at runtime
onto a uniformly lit board substrate. The original photo shadows and board tint
are no longer painted across the whole board. Modeled component silhouettes and
connectors are masked; aperture cut-outs also apply to the artwork. This is
thresholded photographic artwork, not a traced netlist: some bright residual
features remain, hidden tracks cannot be recovered, and the underside has only
modeled pads/solder, with no invented routing. Full original credited images
remain available as evidence. The same third-party photograph exclusions apply
to this derived display; KiCad source and derived footprint data retain their
file-specific licences.

Validation: generated board apertures checked by ray tests at lead centres and
adjacent substrate, package bounds/intersections checked, individual-board
visibility and restoration tested in the browser, and combined OpenSCAD export
validated with the Manifold backend. Exact board revision, connector details,
IC sockets, original pad sizes and hidden routing await specimen photographs.

## Mechanical fit and inspection (2026-10-12)

`pcb-components.json` now records eight provisional mounting positions shared
with `pcb-components.scad`. Each board has four 3.4 mm clearance holes, washers,
screw shafts/heads and hollow hex standoffs ending at its underside. The
controller supports start at the lower board surface. Hardware exports per
board so it remains visible during isolation. Positions retain the existing
reference reconstruction; actual mounts, brackets and additional board-edge
cut-outs await specimen evidence. No extra edge profile has been invented.

The owner drive overview `PXL_20250212_094033966.jpg` and rear view
`PXL_20250212_094038758.jpg` guide the added rail saddles, moving bearing sleeves,
spindle retaining ring and small carriage spring detail. The old fixed crossbar
crossed the moving carriage path; saddles now sit beyond the original 35 mm
clearance envelope (the corrected 96-tpi head travel is 20.90 mm). Carriage sleeves move with the same head mesh, with 3.2 mm bores around
3 mm rails. Spring turns, clearances and retaining-ring size are estimates;
the drive geometry remains an illustrative reconstruction, not validated
mechanical kinematics. Existing clamp/latch motion is unchanged.

Rear ribbon plug housings now surround the reference board fingers. The cable
ends enter these housings, which include a strain-relief bar. Thirty-three fine
ridges across each 42 mm ribbon suggest the conductors without claiming a
verified cable pin count. The four power entry wells receive two black wires
and the red/yellow wires; colors and routing remain illustrative. New ridges
share the existing deformation rule, preserving drive and controller endpoints
when the drive assembly is lifted. Plug internal keying and contact geometry
are provisional; exploded views now park the disconnected plugs by default.

DAC adds a solder-side camera for either board, and a toggle that replaces
components/artwork with the unchanged credited source photograph for comparison.
The toggle returns to the component side; underside inspection turns it off.
Modeled underside tracks remain absent. Small pads, solder, contacts, IC leads
and ribbon ridges hide at distant zoom and reappear nearby; separate distance
thresholds prevent flickering. Canonical OpenSCAD/STL geometry is unchanged by
this display optimization.

Checks cover open mounting apertures and solid neighbouring substrate, reference
photo/artwork restoration without duplicate components, zoom-detail hysteresis,
idle rendering, assembly restoration and existing moving cable/head endpoints.
The combined Manifold export is valid (about 93 MiB). Browser meshes remain
separate; the combined STL is not downloaded by the exhibit.

## Guided exploration, motion and downloads (2026-10-12)

DAC highlights the head carriages, spindles, clamps/latches or either logic board
and links each selection to evidence notes. Top and rear drive views expose the
mechanisms and connectors. Highlighting is a reversible material overlay; it
does not replace the stored specimen colors or photographic evidence.

The mechanical demonstration has a manual phase control and an optional slow
12-second cycle. It changes only rendered head/spindle/clamp/latch poses, never
controller state, disk contents or emulator inputs. Turning it off restores
current live drive poses. Reduced-motion preference disables automatic cycling.
The cycle is explanatory, not a reconstruction of the original linkage timing.

Disconnected drive cables are now the default when separating the assembly.
The cable ends and their plug housings park 18 mm rearward while the drives lift;
the controller/PSU ends remain fixed. This short illustrative withdrawal replaces
the long stretched cables. It is not a solved flexible-cable simulation. The
checkbox can restore the previous stretched-cable illustration. New browser
checks verify parked-end alignment, fixed endpoints and restoration.

`tools/check-mechanics.py` tests the moving carriage and head shield against the
fixed frame, bridge, rails, motor, both board variants and fixed components at
all 80 emulated track positions. It found two positive-volume intersections:
the carriage's right tab intruded into a guide rod, and an obsolete fixed spring
occupied the moving assembly. The carriage now has clearance bores through all
tabs, and the duplicate spring was removed. `checks/mechanics.json` records zero
intersection volume at all 80 positions after correction. This bounded check
does not certify all contacts, continuous linkage motion, printability, or the
fit of unmeasured parts elsewhere in the computer. Existing browser checks cover
shared moving-head transforms and separation/restoration.

The browser distinguishes plated-steel-like, cast-alloy-like, solder and aged
plastic finishes. Roughness, metalness and subtle grain are visually estimated
from the owner photographs, not metallurgical identification or calibrated
measurements. No new specimen scratches or corrosion patterns were invented.

Run `python3 tools/export-downloads.py` after the normal geometry export to
rebuild four ZIPs under `browser/downloads/`: motherboard, floppy controller,
short-sensor-board drive 0 and long-sensor-board drive 1. Each includes a complete
geometry STL, an editable OpenSCAD wrapper, included source geometry, evidence
notes and licence texts. Drive downloads include the front face and latch;
photographic label print and textures are not represented in STL. The board
STLs retain assembly coordinates; drives use their local front-left-bottom
origin. ZIP timestamps are fixed for deterministic output. Their byte counts and
SHA-256 hashes are recorded in `browser/downloads.json`. Required KiCad meshes,
STEP originals and file-specific licence notices are included; original code
remains MIT. Photos and firmware are not bundled. Downloads are fetched only
when requested, not during museum rendering.

The 96-tpi correction changes animation metadata only, not the rest-pose STL.
`tools/check-mechanics.py` audits each of the 80 corrected positions. The emulator
exposes its motor-gated phase and stepwise cylinder position to DAC, replacing
independent browser rotation for the current core. This is synchronization with
the emulated model, not measured motor acceleration or index alignment.

### Upper head arm and inserted medium

The upper load arm is now a separate `drive-head-arm-*` mesh, removed from the
stationary carriage-metal mesh. `driveMotion` supplies its pivot; DAC tilts it
through an illustrative 0.08 radians according to the emulated head-load progress.
The pivot, lift and linkage remain estimates, pending specimen measurements.
The lower carriage continues to follow the 96-tpi radial travel independently.

`drive-medium-*` represents a thin exposed 130 mm flexible magnetic disk with hub
and index openings. Its geometry and markings are generic references, not a scan
of the owner's media. DAC shows it only with media inserted, rotating in phase
with the hub, and makes it translucent so the mechanisms remain inspectable.
The stationary paper jacket is deliberately omitted from this inspection view.
Drive downloads include the new editable parts. No new third-party assets were
imported; these additions are original MIT OpenSCAD geometry.

## Keycap side views and shared feet (October 12, second update)

The three MIT owner photographs in `Photos-1-001 (7).zip` show a distinct square key flange, a taller nearly vertical rounded black body and shallow dished top. Long black keys retain an elongated rounded body. Clear function keys use rounded rectangular shells around separate silver liners, with black legends beneath the clear top. The browser uses transparent glossy plastic (a lightweight alpha approximation, without refraction) and a separate metallic inlay; no photographed dirt or reflections are copied. Heights, wall thickness and dish curvature remain photo estimates, recorded in `specimen-measurements.json`. `cap_insert()` and the keycap-insert export keep the construction editable in OpenSCAD.

Danila confirms the case and keyboard feet are identical parts. Both now instantiate `specimen_foot()` and `specimen_foot_insert()` (32 × 11 × 4 mm estimated rubber envelope), replacing the earlier different case-foot estimate.

In the browser, opening the keyboard separates the mounting plate and switches from the broad PCB, turns that PCB over to expose the owner-photographed solder face, and lifts the narrow controller separately. This is an inspection arrangement; closing it restores the fitted positions. The simplified bus artwork is visual reference, not an electrical netlist.

### Opaque key sidewalls

The owner side views show continuous black plastic around the cylindrical and elongated key bodies. Their hollow undersides now follow the same capsule outline; the previous square cavity accidentally pierced the curved walls near its corners. This corrects geometry rather than hiding the holes with a material change. Clear function-key shells and silver inserts remain separate.

### Keyboard row placement (October 12, overhead comparison)

Owner photograph `PXL_20261012_123006039.jpg` supplies the row stagger and key-group spacing. ALT is one pitch, left Shift and the unlettered Caps key are 1.25 pitches, CTRL/right Shift/circled R/ET are 1.5 pitches, and the spacebar is eight. Separate half-pitch spacers sit beside SI/SO and ET. The 19.5 mm modeled pitch is a photo fit within the earlier ruler estimate of 20 ± 1 mm, not a measured manufacturing specification. The rows move forward to leave the photographed blue rear ledge and black front margin. Switches, plate holes, springs and solder pads share these coordinates. The broad board envelope remains an estimate.

The deck now has grouped openings instead of webs between every cap. The rear reinforcing recess is part of the painted metal shell. Both amber indicator lenses are represented; only Caps has a verified browser state connection, so the SI/SO lens is not animated. Black-key legends use larger photo-based proportions.

Danila subsequently measured the raised bodies: blank Shift caps are 18 mm wide, CTRL/ET and the other broad caps 23 mm, explicitly excluding the flange. `topWidth` records these independently of pitch/flange width and participates in exported mesh deduplication. The matching Caps/circled-R shapes use the same two families based on the photographs.

## Rear panel and flush reset (October 12 close-ups)

The rear uses the owner’s 125413618/125300878/125449006/125457861/125502437 photographs for recessed openings, pale keyed inserts, separate retaining blocks, plated contacts, blanking plates and engraved-style legends. The monitor outlet has three metal contact sleeves and two unplated alignment holes. The mains inlet is vertical, with a recessed shroud and two slotted mounting screws; both fuse caps have cross slots. V24’s alternating populated positions are visible in the close-up; other contact populations and hidden details remain approximations, not wiring documentation. The clean nameplate preserves **Typ W 1715/330, Masch.-Nr. 67581** without copying corrosion or wear.

Photo 124827690 shows a grey reset pad nearly flush with the lower front panel. It now has its own geometry and a real panel opening rather than reusing the protruding power rocker. The 16 × 16 mm pad and 0.4 mm face recess are photo estimates. Power and reset remain distinct pickable browser controls.


## Surface and joint review (October 12)

The mid-height monitor joint now has a continuous 2 mm gap and a separate dark
inner lip following the shell outline. Straight support strips previously broke
through the sidewalls near the rear. The gap and hidden lip remain estimates;
owner close-ups 125018215, 125021771 and 125025415 establish the visible dark joint,
not a measured fastening design. Opening the monitor keeps the lip with its
lower shell.

Owner photos 125413618 and 125300878 show outlined rear-panel lettering. The CAD
now uses narrow outline strokes and clean nameplate field borders. `rearMarkings`
is extracted from the same OpenSCAD text and coordinates for antialiased browser
lettering. The nameplate retains the specimen identifiers; no rust is modeled.

Paint, molded plastic, rubber and plated metal have separate finishes. The paint
uses fine procedural relief in model millimetres, while bare metal has stronger
reflections and the rubber remains matte. Roughness and relief are visual fits
to the owner photographs (including keyboard underside 133005363 and monitor
close-up 125021771), not calibrated measurements. Photographed lighting, dirt
and wear are not copied onto the panels.


### Keyboard margin and PCB follow-up

A second overhead comparison with owner photo 123006039 corrects the previous
19.5 mm fit to 19 mm pitch and a -230 mm column origin. This leaves about 16 mm
and 11 mm of black deck beside the left and right key flanges. The 18/23 mm
raised wide-key measurements are retained independently of their flange sizes.
Switches, deck cutouts and plate holes share the revised coordinates.

The broad board now includes clean, shaped underside buses, solder pads and
screw heads based on 123907435. The narrow controller includes metallic routing
and lead fan-outs based on 123622947. These are visually estimated details,
not validated electrical connectivity. In the museum's open keyboard view,
keys/deck move back and switches/springs move forward, leaving the PCB exposed;
the controller lifts out separately. Both amber lamps follow the firmware state.

### Monitor cabinet and external leads correction

Owner view `125018215` and the underside view `125132359.MP` show a rectangular
cabinet with parallel walls. Removed the old estimated 320-to-270 mm rear taper
and the rear height reduction; rounded edges, the hollow shell and mid-height
joint remain. The standalone OpenSCAD/STL and browser parts share this envelope.

Photos `125123660`, `125234638` and `125402713.MP` establish two captive leads,
the thicker pale power cable, thinner gray signal cable, upright RFT power plug
and locking signal backshell. Both now route from the boot beside the stand
to their corresponding DISPLAY connectors. Reconstructed clean plugs include
seams, screws, latch/bail details and a brown power-cable collar. Cable diameters
(8.4/5.6 mm), plug dimensions and slack remain photo estimates. Browser inspection
extends the leads to keep their monitor ends attached; that extension does not
assert a measured cable length. No wear or full-photo skins are added.

### Loose keycap reconstruction (October 12 evening)

The [standalone keycap](keycap/README.md) includes an editable OpenSCAD model,
closed one-piece STL and top/underside previews. The new loose-cap photos replace
the earlier guessed square stem with a circular cup and annular spring recess.
The thick skirt and pale inner core follow the owner photographs; local fit
dimensions remain estimates. Spring dimensions are now confirmed by the owner
as 13 mm outer diameter, 23 mm free length and **0.4 mm wire**, superseding the
earlier approximately 0.35 mm estimate.

### Rubber-contact mechanism and spring correction

[Separate switch parts and measured spring](key-switch/README.md) now accompany
the loose cap. Pale slotted guides and mounting flanges follow `190054608`;
Danila confirms rubber pads against paired PCB electrodes. The reconstruction
includes a moving insulating carrier and rubber disc, and two disconnected comb
electrodes per key. Their hidden geometry is approximate, not an electrical
netlist. Open keyboard shows the contact face; orbit below for the underside.

Black keycaps share the standalone geometry, with a thick skirt, pale core and
annular recess. The 18/23 mm raised wide-key widths are retained. Clear and red
key undersides remain the earlier provisional geometry, since the new photos
show only a loose black cap. Spring OD/free length/wire are now 13/23/0.4 mm;
installed height and travel remain inferred. The old 0.35 mm mandrel experiment
is retained as historical work, not validated tooling for the corrected spring.

The combined STL now exceeds GitHub's 100 MiB file limit, so it ships in a
lossless ZIP instead of reducing geometry detail. Extract it for the same STL
workflow. Standalone keycap and switch STLs remain directly downloadable.
