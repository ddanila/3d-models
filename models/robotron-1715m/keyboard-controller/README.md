# Keyboard controller electrical and physical reconstruction

Work in progress under the [museum implementation plan](https://github.com/ddanila/dac/blob/main/docs/robotron/keyboard-controller-plan.md).

The reference circuit is Zander drawing 56-330-4103-7. The photographed specimen
is marked 05-330-4102-8 1c and has an unidentified replacement EPROM. Do not treat
the reference firmware or every reference component as identified specimen parts.

`evidence.json` records source hashes, uses and unresolved claims. The published
placement PDF is an unfinished layout with components outside the board and an
unrelated template title. It is not evidence for physical placement. The owner
top and underside photos are the placement and copper evidence.

The KiCad schematic will own electrical connectivity; the PCB will own physical
geometry. Exported JSON, HDL wiring and SCAD are derived artifacts. OpenSCAD retains
the surrounding mechanical assembly. Existing photo artwork remains unqualified
until connected to numbered pins and checked against the circuit.

Digital behavior, electrical connectivity and historical geometry are separate
qualification results. Unresolved routes and analog timing remain explicit.

## Native KiCad authorities

Open `controller.kicad_pro` in KiCad 10. The schematic is now the editable
connectivity authority, with local numbered-pin symbols in `kbd.kicad_sym`.
The reviewed transcription contains 70 components, including BR1/BR2. The reset
connections were corrected against Zander; analog timing remains unqualified. Signal pins have electrical types. Power rails and semantic
transistor/diode terminals are explicit, but their physical package pin mappings
are unresolved. `XT1` preserves the source drawing's `XT` cable interface under
a KiCad-compatible numbered reference. The matrix and lamps beyond X1 are external.

The board uses nominal 270 × 46 mm dimensions inherited from the model. It places
the reference DIP packages and two connector placeholders at existing photo
estimates. Other components are parked below the outline, not silently placed.
Existing artwork is on Dwgs.User (top) and Cmts.User (bottom), with no electrical
net assignment. The board is unrouted and is not fabrication ready.

Run `tools/export.py` using a Python interpreter with KiCad's `pcbnew` module;
set `KICAD_CLI` if the command is not on PATH. On macOS:

```sh
/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 tools/export.py
python3 tools/export.py --check
```

The exporter verifies every PCB pad against schematic connectivity and emits
`generated/connectivity.json`, layout metadata, SCAD arrays, a two-sided SVG
review, qualification results and source/output hashes. `--check` needs only
standard Python. Circular arcs are sampled with a 0.025 mm chord-error target, and through vias
retain copper diameter and drill geometry. Zones, blind vias and internal-layer
tracks fail explicitly rather than silently disappear.

The initial ERC has two isolated-label warnings: the unused CPU RD_N output and
the cable shield boundary. DRC reports unresolved airwires and silk placement
issues; see `generated/qualification.json`. These are recorded failures, not
waived manufacturing checks. Schematic/PCB net agreement does not validate the
transcription or identify the specimen's circuitry.

## Digital reference qualification

The digital peripheral reference agrees with the corrected emulator on
131,072 bus transactions, including memory-write serial clocks, and the TV80/S600
workload's 390 serial bits and 11,971 raw LED state records. The earlier A15-gated
LED behavior, narrow input/output decode and ANDed columns were emulator errors
relative to this drawing. Display indicators use a separate, explicitly approximate
2 ms peak hold. CPU phase offsets and analog behavior remain unqualified; logical
agreement with a reference is not identification of the photographed specimen.

## Generated geometry review

Open `review.scad` for a standalone reconstruction view. It consumes only
KiCad-derived arrays for the outline, holes, pads, package positions and artwork.
Cyan lines are unresolved photo graphics; assigned copper uses a separate layer.
Detailed packages reuse the pinned KiCad body/lead meshes. The museum now consumes
the native DIP placement, numbered pads, outline and photo-artwork export. Other
discretes and mechanical details remain photo estimates. Generic procedural fanouts
were removed rather than presented as historical copper.

`python3 tools/test_export.py` checks source/output hashes, asymmetric CPU/ROM
and pad-number landmarks, closed outline area and stale-file rejection. These
checks run in CI without KiCad. The initial SCAD export rendered successfully
with the Manifold backend. The Edge.Cuts loop is reconstructed by endpoint
connectivity, not by file order; unsupported open or branched outlines fail.

Pending promotion work: verify package orientation against independent photo
landmarks, place the remaining reference components, establish discrete lead
numbers, associate visible paths with nets, resolve airwires and verify the
analog component types and physical bridge state. Full discrete-component migration
and continuity qualification remain open; successful exports do not close them.

## Additional source review

Full-resolution top and underside owner photos establish **05-330-4102-8 1c**,
correcting the older model-derived `062-330-4102` identification. The kbdbabel
drawing names the same board family/revision, but its output-clock connection
uses RD rather than Zander's WR and its ROM is labeled 2732. These are recorded
as source disagreements, not resolved by selecting whichever matches software.
The current HDL remains explicitly the Zander reference circuit. The canonical model inscription is corrected to `05-330-4102`; the clearly
visible end logic chip is marked `К555ЛА3`, correcting its earlier transcription.

Run `tools/test_kicad.py` with KiCad's Python for an additional integration test:
a temporary PCB with a curved track and through via must export correctly, and
a deliberate pad/net mismatch must be rejected. This test does not edit the
canonical PCB. The source PDF is linked and hashed in `evidence.json`; its stated
CC-BY-SA 3.0 attribution is retained there and it is not redistributed here.

## Photo landmark alignment and model migration

`photo-landmarks.json` records raw image pixels for nine packages, including
held-out lead landmarks on all nine. `generated/photo-registration.json` reports
residuals against the nominal board plane; the companion SVG overlays observed
points (green) and PCB pads (red) on the original photo. All nine rigid fits pass the
1.25 mm review tolerance. A4 was corrected after re-reading the last leads and
adding four held-out intermediate leads; its maximum residual is 0.554 mm.
This loose photo tolerance does not establish fabrication dimensions or continuity.
A8 uses visible package/socket leads; the PCB hole centres remain obscured.
Discrete lead numbering remains outside this qualification.

`tools/photo_registration.py` reviews the current fit; KiCad Python with `--apply
--refs A1 ...` can apply explicitly selected acceptable fits to the native PCB,
after which exports must be regenerated. Fit inputs and photo hashes are pinned.
The schematic remains the connectivity authority; landmark data contains no nets.

Reference labels are on F.Fab and evidence fields are hidden metadata, not invented
historical silkscreen. This removes the earlier placeholder-text DRC failures:
there are zero other DRC violations, but **234 unconnected items remain**. The
board is still unrouted and not fabrication ready. The accepted model now uses
generated DIP placements/pin counts (A1/A6 corrected to DIP-14), pads, outline and
artwork. The CPU socket and ink follow its placement. Native generated arrays also
drive the ROM body/socket/cover/ink transforms. Existing discrete visuals remain
separate pending physical reference identification.

The museum clips unassigned photo graphics to the board outline for rendering.
Five projected top-artwork endpoint occurrences overshoot the nominal outline;
the native review preserves them so registration error remains inspectable.
Clipping is not a continuity or routing correction.


## Reset and clock isolation bridges

BR1 separates A7:8 from A5:6 (CLK). BR2 separates V4.9:C from A5:26
(active-low RESET). Both are closed bridges in the reference drawing. Opening
one permits independent stimulus on the CPU side while isolating its onboard
source. This test use follows from the circuit; the reviewed handbook sections
do not prescribe a bridge-opening test procedure. Physical locations, bridge
construction and state on the specimen still need identification. Numbered
terminals 1/2 are reconstruction identifiers, not observed pad markings.

The reset review corrected V3.1:C to +5V, V3.2:C to the V4.9 base, R5 to
V3.2:B, V1.2:A to C2's positive node, and C1's lower terminal to the reset
output. BR2 now separates that output from the CPU reset net. The review also
corrected X1:A9 and R6.5 to BUSRQ, separate from WAIT/INT/NMI and CLK.
Regression checks preserve these connections and both bridge boundaries.

The [Robotron service handbook](https://www.tiffe.de/Robotron/PC1715/PC-1715-Servicemanual.pdf#page=91),
printed pp. 89–92, independently supports WR serial synchronization, active-high
matrix sensing and IORQ-clocked LED latches. It specifies about 100 ms reset
hold and a 700 kHz ±10% clock. Its oscillator diagram uses different component
references, gate pins and capacitance from Zander; these values are documented
reference expectations, not specimen measurements or a reason to merge circuits.
`evidence.json` retains the handbook hash and the service-interface mapping.

Photo-fit application now checks held-out landmarks as well as fitted points and
rejects unknown references before writing the PCB. A good fit of selected corner
points cannot silently override a failing independent landmark.

The cable review corrected the filter winding references and swapped the erroneous
XT1 ground/clock assignment: L1.1 carries TA_TAKT to XT1:B2; L1.2 carries GND to
XT1:A3; L1.3 carries +5V to XT1:B4; L1.4 carries TA_DATEN to XT1:A1. These are
Zander's terminal labels; verify connector orientation before physical probing.


## Underside registration audit

`bottom-landmarks.json` identifies four anchor pads and six independent check pads
in the original underside photograph. `generated/bottom-registration.svg` shows
anchors in cyan, check observations in green and projected PCB pads in red.
The reflected homography uses the current KiCad placements as its target, so it
checks relative registration rather than measured board dimensions. After recounting the CPU rows, all six PCB-relative checks fail the unchanged
1.25 mm tolerance, at about 1.41–1.70 mm. Earlier lower CPU checks selected features
below the twenty-pin rows; the superseded observations remain in the evidence.
`generated/bottom-registration.json` retains residuals and both transform matrices.
This audit does not move the PCB, warp artwork or authorize net assignments.

A8's package notch and pin-one dot are visible above its blue tape. Its corrected
photo-estimated placement uses four corner leads and four held-out right-side
leads; the maximum residual is about 1.11 mm. The socket obscures board holes and
the replacement EPROM identity remains unread. Orientation is now photo-supported,
while exact package-to-board alignment and firmware identity remain open.


The `crossPhoto` report independently maps the underside photograph to the original
top-photo observations using the same four anchors. It does not target the rigid
PCB footprint positions. A1 checks agree within 0.41 nominal mm; corrected CPU
checks span 0.89–1.28 mm. This distinguishes direct image correspondence from the
additional discrepancy introduced by nominal calibration and rigid package fitting.
Top leads/socket surfaces can obscure hole centres, so this comparison still does
not establish a measured board plane or authorize copper assignment. The original
1.25 mm tolerance remains unchanged. Obtain physical dimensions and review more
shared pads before promoting a global registration.

### Copper evidence contract

`route-evidence.json` assigns a review to every native track, arc and through-via
UUID. The exporter refuses missing or orphaned records. Each record contains
`status` (`observed`, `inferred`, or `unresolved`), a review `detail`, source
citations (`id`, pinned `sha256`, and a pixel-region/page `locator`), and
`geometrySha256`, calculated by `tools/route_evidence.py:geometry_sha` from the
exported geometry. Moving, resizing, flipping or changing a route's net invalidates
its review. The annotated record survives in `generated/layout.json` and the
museum sidecar. Native KiCad copper remains the geometry authority.

An observed track requires a citation to its side's photo; an observed through-via
requires both sides. This checks provenance completeness, not truth: review must
still establish the visible route and distinguish geometric observation from
measured electrical continuity. Inferred and unresolved records also require
sources and an explanation. Unassigned photo artwork remains outside this ledger
and cannot become electrical copper merely by receiving an annotation.

The first assigned route is the partial top track from A1 pin 1 around X1 to a
round terminal near A4 (original top-photo pixels 1241,2966). Seven segments follow
visible copper; the short pad-to-visible-lead attachment is inferred because the
fitted hole centre is obscured. Width 0.35 mm is estimated. The native route uses
`/WR_N`, the reference schematic net at A1:1; the CPU endpoint and the specimen's
WR/RD disagreement remain unresolved. No via is asserted at the terminal until
its underside correspondence is established. DRC therefore retains one
`track_dangling` finding and 234 airwires. This is an intentionally partial route,
not fabrication-ready routing. The 294 legacy artwork segments remain unassigned.

`generated/photo-registration.svg` now overlays the native route on the source
photo: magenta for observed sections, orange for the inferred attachment. The
geometric review drawing also includes assigned copper. Route evidence retains
original pixel segment endpoints and the source photo hash for review.
