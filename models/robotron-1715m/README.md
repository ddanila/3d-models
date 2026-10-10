# Danila’s Robotron 1715M

Parametric OpenSCAD reconstruction of Danila’s exterior with a provisional reference interior. Original model, scripts and owner photographs are MIT licensed (see LICENSE); the credited PCB photographs in `reference/oldcrap/` and `reference/robotrontechnik/` are excluded from MIT and retain their original rights (see their NOTICE.txt files). This is an editable museum reconstruction, not a scan, manufacturing drawing or validated replacement enclosure.

Open `model.scad` for the assembled system unit, monitor and keyboard. Set `part` to any entry in `parts` to inspect/export it separately. Coordinates are millimetres: X right, Y towards the rear, Z up. The keyboard is placed in front of the computer. `robotron-1715m.stl` is a combined visual reference; the separate exports retain the switch and material boundaries used by the museum.

## Evidence and dimensions

The original [Robotron 1715/1715W manual, printed p.35 (PDF page 36)](https://xepb.org/robotron/docs/pc_manu.pdf#page=36), digitized by U. Zander, lists these nominal envelopes:

| Component | Width | Depth | Height |
| --- | ---: | ---: | ---: |
| System unit | 500 mm | 400 mm | 130 mm |
| Display | 320 mm | 350 mm | 330 mm |
| Keyboard | 500 mm | 200 mm | 40 mm |

These are family specifications, not new measurements of Danila’s specimen. The display height includes its stand; its shell and stand proportions are inferred from the photograph. Small projections and approximate feet can extend beyond nominal envelopes. The monitor insert uses Danila’s existing [measured ring](../robotron-1715m-display-base-ring/): 175 mm OD, 169 mm ID, 5 mm high; its physical fit is still unverified.

The ruler photograph `PXL_20261009_132938614.jpg` provides an independent local scale. In a 1824 × 1373 display of that photo, the 200 and 100 mm ruler ticks are approximately x=405 and x=1380. Six number-row key intervals span approximately 1172 pixels, giving 1172 / 6 / 9.75 ≈ 20.0 mm. The model uses 20 mm pitch. Allow about ±1 mm for hand-picked landmarks, perspective and the ruler lying at a different height from the key centres. This is not submillimetre metrology.

Photos establish the two drives, 14 front vents, side vent banks, front switches, separate keyboard key groups, translucent function caps, red CE key, monitor bezel and blue tape, and keyboard underside. Wall thickness, curves, seams, feature locations and colors remain estimates. The keyboard layout represents 97 visible key positions. Keycaps are exported as seven reusable OpenSCAD profiles and instanced individually in the browser so the entire cap moves when pressed. Blank fillers and some indicator hardware remain incomplete. Case rear connectors, system-unit underside, the exact internal board revision and monitor rear details are unverified. Reference electronics are now modeled, with their provenance recorded below. The documentation archive also contains electrical schematics; these are not dimensioned enclosure drawings. Its older 1715 schematics must not be mistaken for 1715M/W schematics.

Sources: [documentation index](https://xepb.org/robotron/docs.html), [manual](https://xepb.org/robotron/docs/pc_manu.pdf), [service manual](https://xepb.org/robotron/docs/pc_serv.pdf). Historical documents retain their original rights and are linked, not relicensed or bundled.

## Reference photos and consistent materials

`reference/photos.json` records the source archive and original/published SHA-256 hashes. `reference/photos/` contains losslessly sanitized JPEGs: EXIF, XMP, IPTC, comments and trailing motion video were removed, with decoded pixels checked against the originals. The original download was not modified. To reproduce sanitization after extracting the archive, run `python3 tools/import-photos.py /path/to/extracted/photos` from this model directory (requires Pillow).

OpenSCAD/STL stores geometry, not photographic materials. `browser/model.json` version 6 adds material profiles, transcribed legends, a small wordmark decal, reference-photo links, a live screen anchor and individually named power/reset meshes.

Full-panel photo skins are no longer used. The old underside crops contained a photographed cable and feet in addition to the modeled ones; removing them eliminates those duplicates and their baked shadows. There is now one continuous Bézier-routed lead, a modeled grommet, a hollow keyboard shell with a separate bottom plate, four rubber foot frames with metal inserts, six perimeter fasteners and a detailed exterior plug. The two drive fronts have recessed insertion slots/finger wells, rounded latch handles and separate red lenses. The monitor tape is a thin solid. Keycaps have square skirts, rounded shoulders and dished tops, including a stretched dish for long caps.

The palette and finish are visually estimated from the photographs, not colorimetrically calibrated. Browser paint, plastic, rubber, metal, lens and glass materials react to scene lighting; subtle procedural grain uses model-space millimetres, avoiding large repeated photo patches, seams and baked illumination. The fine grain is an approximation of the observed finish, not a photographic sample. Surface normals are smoothed with creases preserved. The original small `robotron 1715 M` wordmark remains a masked photo crop; it contains no modeled physical feature. Drive arrows and control labels are reconstructed markings. Key legends are transcribed into a transparent atlas placed on the dish surface; font shapes are approximations, not scans. Blank Shift/Space/Caps key tops remain blank. Input support is still separate from the visible legends.

The owner JPEGs and their original UV landmarks remain reference evidence, with no repainted or generated photograph pixels. Exact wear/scratches, clear keycap construction, cable route, connector dimensions and unseen hardware remain approximate. The model is a coherent reconstruction, not a scan of every mark on the specimen.

## Rebuild

Requires Python 3 and OpenSCAD with the Manifold backend (tested with 2026.10.05). From the repository root:

```sh
python3 models/robotron-1715m/tools/configure.py
python3 models/robotron-1715m/tools/export.py
openscad --backend Manifold --export-format binstl -o models/robotron-1715m/robotron-1715m.stl models/robotron-1715m/model.scad
openscad --backend Manifold -o models/robotron-1715m/preview.png --imgsize=1600,1200 --viewall --autocenter models/robotron-1715m/model.scad
```

`tools/configure.py` generates the shared keyboard geometry/UV table. `tools/export.py` exports 63 body/detail meshes and seven reusable keycap profiles with their hashes. `part="keycap"` and `key_index` select a local, origin-centred cap for export; assembly geometry stays fully assembled. The DAC repository imports the export with `python3 scripts/sync-robotron-model.py ../3d-models`, recording the source commit and checking hashes. Firmware and emulator code stay in their own repositories.

## Interaction metadata and keyboard evidence

`keyboard-layout.json` supplies stable IDs, physical positions, photo-reference landmarks, transcribed legends and the museum input adapter. The [original manual, printed pp.9–11](https://xepb.org/robotron/docs/pc_manu.pdf#page=10) supplies Tab, Insert/Delete, function-key and numeric-keypad codes; cursor directions agree with the existing core adapter. Numeric-pad digits have distinct codes, not ordinary ASCII digits. ET uses API input 13, translated by `robotron_key()` to the documented keyboard byte 9E. No historical document or firmware is bundled under this model’s MIT license.

89 positions have input behavior, including Shift/Ctrl/Caps Lock. ALT, ß, repeat R, SI/SO and four navigation symbols are explicitly unverified. Unverified shifted symbols also send no invented byte. Shift/Ctrl are visitor-side one-shot latches; Caps Lock is persistent until released or focus/reset/power changes. The browser’s Caps Lock lamp reflects that local input state, not feedback from the original keyboard controller. SI/SO’s alternate character-set protocol is not available through the current browser core API.

The first drive lamp reflects the core’s aggregate disk-transfer counter (only one disk is mounted); it does not claim to reproduce drive-select or motor timing. Opening the case moves its lid and monitor visibly up and back together. A separate control lifts the drive assembly forward and up and separates the fascia and keyboard deck. The system-unit interior is reconstructed from comparative references; cables are hidden in the separated view rather than stretched between parts. The external cable route and monitor-glass curvature remain estimates.

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
