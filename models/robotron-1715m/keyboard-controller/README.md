# Keyboard controller electrical and physical reconstruction

Work in progress under the [museum implementation plan](https://github.com/ddanila/dac/blob/main/docs/robotron/keyboard-controller-plan.md).

The reference circuit is Zander drawing 56-330-4103-7. The photographed specimen
is marked 05-330-4102-8 1c and has a replacement EPROM, confirmed by the user on 2026-10-17; its contents are unread. Do not treat
the reference firmware or every reference component as identified specimen parts.

`evidence.json` records source hashes, uses and unresolved claims. The Zander
placement PDF is an unfinished layout with components outside the board and an
unrelated template title. It is not evidence for physical placement. The owner
top and underside photos are the placement and copper evidence.

The KiCad schematic will own electrical connectivity; the PCB will own physical
geometry. Exported JSON, HDL wiring and SCAD are derived artifacts. OpenSCAD retains
the surrounding mechanical assembly. Existing photo artwork remains unqualified
until connected to numbered pins and checked against the circuit.

Digital behavior, electrical connectivity and historical geometry are separate
qualification results. Unresolved routes and analog timing remain explicit.

## Second specimen photographs

The 25 photographs supplied on 2026-10-17 are explicitly a **different specimen**.
Their hashes, image-specific uses and specimen ID are in `evidence.json`; the
original ZIP hash and identity statement are in `comparisonSpecimens`. The photo
inventory retains original and metadata-stripped hashes. JPEG pixels were checked
identical during import. The comparison board carries the same visible
`05-330-4102` / `-8 B 1c` markings, but its EPROM label reads **S642**. No dump is
available, so that label neither identifies its contents nor qualifies the S600
reference firmware for either specimen.

| New photograph suffix | Useful observation | Remaining work |
| --- | --- | --- |
| 080342577, 080345436, 080347973, 080351042 | Four overlapping underside views expose solder joints and copper | Count pins independently, register each image, compare corresponding primary-board features |
| 080429077, 080434345 | CPU and DS8282D region with visible round terminals and raised resistor leads | Revisit the withdrawn CLK terminal interpretation; no replacement net assignment yet |
| 080431329.MP, 080502586 | Bridge at BR1's reference location, its attachments, adjacent resistor/capacitor and board marking | Trace both sides; construction appearance does not prove a factory opening procedure |
| 080411074, 080415534 | Keyboard connector mating face and bent leads | Map numbered contacts to board pads |
| 080406304, 080511382 | Cable entry, bracket and nearby components | Follow individual wires and filter connections |
| 080528765, 080531967, 080541857 | Transistor package faces, three-lead arrangement and lead entry | Identify each reference and verify package terminal mapping before placement |

All filenames begin `PXL_20261017_` and end `.jpg`. Sources with reference lists
are search aids for the depicted region; they do not assert that every candidate
reference has been identified. Original image coordinates must not be passed
through the first specimen's photo transforms. Matching board marks are evidence
of the family, not proof that all routing or fitted components are identical.

The first numbered comparison review is retained in
`evidence.json:routeReviews[0].comparisonReview`. The underside view shows a trace
from CPU pin 6 to a round terminal. In the top close-up, the likely counterpart
has a narrow trace passing between A4 leads 12 and 13 toward the package underside,
separate from the neighbouring lead-13 trace. This weakens the earlier apparent
D6-conflict interpretation. The coordinate record includes the pin-count basis,
four CPU corner joints, both observed polylines and pixel uncertainty. The
cross-side terminal match remains provisional; the hidden continuation is unknown.
The direct CPU-corner fit and four independent intermediate-pin checks are also
recorded there. The maximum check residual is 47.07 pixels; the proposed terminal
is 65.20 pixels from its projection. The terminal lies outside the CPU anchor hull,
and top lead feet obscure hole centres. This extrapolation is explicitly
unqualified for copper assignment and does not supply measured dimensions.
No primary-specimen CLK route is restored until correspondence is reconciled.

The user confirms that the primary museum ROM was replaced and may locate the
original later. ROM identity is a separate firmware question and is not a reason
to reject otherwise matching PCB evidence. No native geometry or pin map changed. Existing 25 assigned sections, 229 airwires and 33
unplaced schematic components remain the reconstruction's actual coverage.

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

Open `assembly-review.scad` for the current detailed museum controller alone,
including native resistor and C5.1–C5.4 bodies, pads and bent leads. Press F5 and
Home to preview and fit the board. Set `side="bottom"` for the underside;
`show_mounts` and `show_shield` optionally restore surrounding hardware. This
entry point reuses the full model's geometry and colors, with the board centered
at the origin. Photo estimates and unresolved artwork retain the qualifications
in this document; the assembly view does not establish electrical continuity.

Open `review.scad` for a standalone reconstruction view. It consumes only
KiCad-derived arrays for the outline, holes, pads, package positions and artwork.
Cyan lines are unresolved photo graphics; assigned copper uses a separate layer.
Detailed packages reuse the pinned KiCad body/lead meshes. The museum now consumes
the native DIP placement, numbered pads, outline and photo-artwork export. Other
discretes and mechanical details remain photo estimates. Generic procedural fanouts
were removed rather than presented as historical copper.

`python3 tools/test_export.py` checks source/output hashes, asymmetric CPU/ROM
and pad-number landmarks, closed outline area and stale-file rejection. The optional native
`tools/test_kicad.py` also exports an isolated board twice and compares every
generated file byte-for-byte, including the manifest, to check repeatability. These
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

### Local underside correspondence near A4

The A4-local audit in `bottom-landmarks.json` uses four corner pins and four
independent interior pins. Those checks are within 0.37 nominal mm. It projects
the upper/lower terminal pair near A4 close to the corresponding top-photo pair,
strengthening the candidate match for the A1:1 route endpoint. Both terminals
lie outside the anchor columns, so this remains extrapolation. Extending that
same fit toward a tentative terminal near A6 misses by more than 2 mm.
`generated/bottom-registration.json` retains all predictions, residuals and
bounds flags; the overlay marks local check pins orange and candidates magenta.
No copper or via was added by this audit, and board-wide registration remains
unqualified. A local fit must not silently replace the failing global audit.

### Factory placement drawing recovered

The manufacturer service drawing set supplies the populated placement drawing
63-330-4103-2 (PDF page 10, printed drawing 8) and schematic 56-330-4103-7 (PDF
page 11, printed drawing 9). `evidence.json` pins the source hash and records
BR1/BR2 photo location candidates and the differing A2 location labels. This is
a new usable reference; the previously rejected Zander placement sheet remains
unusable. Native bridge footprints are still unplaced: identifying a visible
link does not establish which terminal maps to the source or CPU net. Bridge
terminal correspondence remains provisional; the A2 correction is documented below.

### A2 reference placement correction

All twelve A2 NAND gate assignments in the factory schematic agree with the
reconstructed electrical netlist. The three physical placements were mislabeled:
A2.1 belongs across from A1 on the cable side of X1; A2.2 is beyond X1 on the
A4 edge; A2.3 is beyond X1 on the CPU edge. Native footprint poses and their photo
landmarks are corrected together. Pin numbers, schematic connectivity, HDL and
runtime behavior remain unchanged. `evidence.json` retains the former location
labels and the independent factory gate review. This corrects the reconstruction;
it does not establish a different historical circuit variant.

### Output pull-up resistor placement

R10.1 and R10.2 are placed from the original top-photo lead ends recorded in
`component-evidence.json`, using the factory drawing for identity. Pad 1 is the
shared supply-side lead (lower in the original photo); pad 2 is the signal-side
lead. The underside photo shows the supply connection toward A1:14. The paths
from the signal leads enter the obscured A1 region, so those nets remain
reference-derived, not continuity measurements. The 560-ohm values, hole/pad
sizes and body dimensions are reference/estimated values.

The native pad pairs now generate `controller_pcb_resistors`. OpenSCAD reuses the
existing body/lead model with those centres, angles and spacings; the two former
independent resistor estimates were removed. The photo report and overlay include
these lead endpoints separately from DIP fitting, with `independentValidation`
false: direct placement is not a held-out alignment test.

### Sensing resistor bank

R9.1–R9.8 follow the factory drawing's order across the bank. Original top-photo
lead endpoints now place all eight native footprints. Pad 1 is assigned to the
matrix-facing lower lead and pad 2 to the transistor-facing upper lead; these
row/base assignments are reference-derived, with hidden continuity unverified.
The eight independent legacy body placements were removed. Native pad geometry
now positions their bodies, leads, holes and lands through the same exporter as
the output pull-ups. The photographed blue collar is at the upper end except on
R9.7; the output pull-ups have it at the lower end. These ten native parts now
show one collar at the observed end, not two symmetric blue bands. Collar position
is appearance evidence, not polarity or a resistance measurement.

### Reset resistor placement candidates

Factory drawing 63-330-4103-2 (PDF page 10) identifies R3, R4.1, R5,
R6.1, R4.2, R7 and R8 in that order along the reset edge. The top photograph
shows all seven bodies and fourteen lead ends. `component-evidence.json` retains
the original pixel pairs as `placementCandidate.photoEndpoints`, ordered left
to right in the photograph, deliberately separate from numbered `photoPins`.
The visible 22K, 10K, 1K0 and 47K markings agree with the corresponding reference
values; neither these markings nor the blue collars establish measured resistance
or electrical polarity. Unreadable markings are recorded as null.

The legacy geometry contains only six resistor estimates in this area. Migrating
this group must therefore replace those six estimates with seven native parts,
not reuse their order as evidence. Before assigning pad numbers, review the
physical supply/reset terminals: the reference circuit puts R3/R4.1/R5/R6.1 on
+5V and R4.2/R7/R8 on GND at one end. Adjacency is insufficient evidence that
all seven terminals share a rail. Underside registration remains unqualified.
R3 and R4.1 have since been promoted to native placements (below); the other five
remain candidates. Electrical routing counts are unchanged.

### First reset resistor pair

R3 and R4.1 now use native KiCad pad positions from the recorded photo endpoints.
A visible top-side connection joins their right leads. The reference schematic
has only one net common to this pair, +5V, supporting assignment of the right
lead to pin 1 on both parts. The opposite reset-node assignments remain
reference-derived; no continuity measurement is claimed. This local top-photo
observation does not depend on the unqualified global underside registration.

The first two legacy resistor estimates were removed. Native geometry now drives
their bodies, leads, lands, holes and observed blue collar ends; R3 has its collar
at pin 2, R4.1 at pin 1. Twelve resistors are native and 47 components remain
unplaced. The shared copper is now traced into native tracks as described below.
R5 and the lower four reset resistors still require terminal review, and the
missing seventh reset resistor remains an explicit model gap.

### Reset supply copper

Five top-side native track segments join R3:1 to R4.1:1 on reference net +5V.
Three sections follow visible copper in the original top photograph; the two
short pad attachments are inferred because solder and leads obscure the exact
hole/copper boundary. `route-evidence.json` binds each UUID, geometry hash,
classification and original pixel segment to the pinned photo. The nominal
1.0 mm width and planar scale are estimates, not measured track dimensions.

The overlay was checked against the visible shared strip. This local connection
does not establish its feed or further continuation. There are now 13 assigned
segments (10 observed, 3 inferred), 233 airwires and the same single dangling
A1:1 track endpoint. The 294 legacy artwork segments remain unassigned graphics;
their appearance is not evidence of extra electrical connectivity.

### R5 supply extension

A closer review of the top photograph shows the same supply strip continuing to
R5's right lead above C4. R5 now has native placement, with right lead pin 1 on
+5V and left lead pin 2 on reference RESET_BIAS. Its 10K marking agrees with the
reference value. The left blue collar, pad positions and lead spacing now come
from the shared native geometry; its legacy placement was removed.

Two observed track segments extend the supply junction to R5, followed by one
inferred pad attachment. Each has pinned original-photo coordinates and a
geometry-bound evidence record. The connection behind C4 remains unresolved.
This brings the current totals to 13 native resistors, 46 unplaced components,
16 assigned copper sections (12 observed, 4 inferred), and 232 airwires. The
original A1:1 dangling endpoint and 294 unassigned artwork segments remain.
A graph check verifies that the local supply tree connects exactly the three
reviewed supply pads, without disconnected islands.

### R6.1 and the visible supply strip beside C4

The top photograph shows the supply strip continuing beside C4 to R6.1's right
lead. R6.1 is now a native component: pin 1 joins this supply strip and pin 2
follows reference RESET_BASE. The 1K0 marking supports the reference value; no
resistance or continuity measurement is claimed. Four observed track sections
and one inferred pad attachment extend the reviewed supply tree. Hidden branches
remain unassigned; the photograph establishes this visible strip only.

R6.1 was the omitted resistor in the legacy model. Its projected centre is
(-89.09, 12.89) nominal mm; the three remaining legacy reset estimates lie near
x=-86, -82 and -78, corresponding to R4.2, R7 and R8. Adding R6.1 therefore
increases the physical body count by one and removes no legacy entry. It uses
native pad positions, body/lead geometry and its observed left blue collar.

Current totals are 14 native resistors, 45 unplaced components, 21 assigned
copper sections (16 observed, 5 inferred), and 231 airwires. The supply graph
connects exactly the four reviewed supply pads. R4.2/R7/R8 remain candidates.

### Source review and remaining reset ground terminals

The manufacturer PDF contents (page 2) lists keyboard layout, populated controller
placement and schematic as drawings 7–9. Their PDF pages are 9–11, followed by a
handwritten key-matrix supplement on page 12. Review of these sheets and a contact
sheet of all 50 pages did not identify a keyboard solder-side copper drawing.
`evidence.json.sourceReviews` records the scope; this does not establish that no
other source contains such a drawing. The factory placement recovery supersedes
the earlier general placement-sheet gap; the separate Zander download remains
unusable as placement evidence.

R4.2, R7 and R8 remain unplaced. Their top-photo endpoint pairs are retained, but
the underside pad pattern is ambiguous among nearby resistor and transistor
joints. An extrapolated global photo transform is not sufficient to select a
row or assign the ground terminal. No new local fit, ground net assignment or
bottom copper was promoted from that comparison. Existing top supply routing
remains supported independently of this unresolved underside correspondence.

### CPU and oscillator resistor pair

R6.6 and R4.3 are now native footprints, using top-photo lead ends and factory
placement identities. The additional owner close-up PXL_20261012_123729356.jpg
supports orientation: R6.6's upper lead runs to A6:10 (FF_PULLUP), while its
lower lead joins the supply land beside A7:14. R4.3's upper lead runs toward
A7:11 (OSC1); its lower OSC_RC assignment follows the reference schematic, with
the continuation obscured by the capacitor and leads. These are photo-supported
reference assignments, not specimen continuity measurements.

The two bodies were absent from legacy geometry: their nominal centres are
(94.08, -3.05) and (113.74, -4.27) mm, distinct from the remaining legacy
estimates. No legacy entry was removed. Native pads now drive both bodies,
leads, holes, lands and their upper blue collars. Exact hole centres and body
dimensions remain estimated. Sixteen resistors are now native; 43 components
remain unplaced. No copper was added; 21 assigned sections and 231 airwires remain.

The close-up is pinned as `photo-cpu-oscillator-closeup`. Export now includes
every local evidence source in the freshness manifest and refuses regeneration
if a local source's content no longer matches its evidence hash. The perspective
close-up supports identification; the original top photo remains the planar
placement authority.

### LED series resistors beside X1

R11.1 and R11.2 now have native placements from their top-photo lead endpoints.
Factory placement identifies the cable-facing and CPU-facing parts respectively.
Their inner leads align with adjacent connector rows, consistent with schematic
X1:A5/A6: inner leads are assigned pin 2 (LED connector side), outer leads pin 1
(flip-flop output side). These assignments remain reference-derived; exact X1
pin registration and end-to-end continuity are not independently verified.

Both bodies were absent from the legacy model. No existing estimate was removed.
Native pads drive their bodies, leads, holes, lands and lower-end blue collars.
The 130-ohm reference value and estimated dimensions are not measurements.
Eighteen resistors are now native, with 41 components unplaced. No copper was
added; the 21 assigned sections and 231 airwires remain unchanged.

### A4 control pull-ups

R6.3 and R9.9 are now native components beside A2.2/A4, identified by factory
placement and top-photo endpoints. Their upper leads share a visible copper
link; +5V is their only common reference net, supporting pin 1 orientation.
Lower LATCH_OE_N and IO_ACTIVE assignments remain reference-derived, with complete
signal paths unverified. Both bodies were missing from legacy geometry, so no
legacy entries were removed. Native pads drive bodies, leads, holes, lands and
the lower blue collars. Dimensions and resistance remain unmeasured.

The shared link has one observed track section and two inferred pad attachments,
with original pixels and geometry-bound evidence. Its supply feed is unresolved.
It is a separate physical island on the same reference +5V net as the reset
supply tree; net selection may highlight both without implying a traced join.
Current totals: 20 native resistors, 39 unplaced components, 24 assigned copper
sections (17 observed, 7 inferred), 230 airwires, one existing A1 dangling endpoint.

### Native lead and solder export correction

A review after the resistor migrations found two omissions: native resistor pads
were missing from the underside solder generator, and the controller freshness
guard omitted the separate lead, resistor-body and resistor-band meshes. Rebuilding
the earlier nine-part set could therefore update the common source stamp while
leaving these meshes stale. Existing geometry checks did not detect that gap.

The solder generator now consumes every native resistor pad (currently 40), using
its hole and pad dimensions. All twelve affected mesh consumers now carry
individual `keyboardControllerMeshes` receipts binding mesh hashes to the three
controller source hashes. A partial export updates receipts only for meshes it
actually rebuilds; metadata validation requires every receipt to match current
sources and mesh content. Regression tests cover omitted lead/body/band/solder
meshes, mesh replacement, and missing legacy receipts.

When controller geometry changes, rebuild all names in
`tools/controller_mesh_contract.py:PARTS`, including `keyboard-controller-leads`,
`keyboard-controller-resistors` and `keyboard-controller-resistor-bands`. The old
common source stamp is retained for compatibility, but is no longer sufficient
to qualify the mesh set. Geometry remains photo-estimated, not measured solder
or lead dimensions.

### BR1 clock bridge and R10.3

BR1 and R10.3 now have photo-estimated native placements. The top photo identifies
both lead pairs; the underside shows a short connection joining their original-top
left terminals. Matching that local connection to the reference assigns BR1 pin 2
and R10.3 pin 2 to CLK, with BR1 pin 1 on OSC_OUT and R10.3 pin 1 on +5V.
These are reference-derived terminal assignments with local photo support, not
measured continuity to CPU pin 6 or A7 pin 8.

One inferred bottom CLK segment joins the native pads. Its topology is supported
by the local joint correspondence; its geometry uses the top-photo placement,
not the unqualified global underside fit. The recorded bottom pixels are direct
observations with uncertainty and do not promote that registration. BR1 exports
native pad holes, lands, solder and a nominal closed wire shape. Its construction,
bend, height and diameter remain estimates; no factory opening procedure is asserted.
R10.3 replaces its legacy body and uses native pads for all geometry consumers.

Current totals: 21 native resistors and one bridge, 37 unplaced components,
25 assigned sections (17 observed, 8 inferred), 229 airwires and one existing A1
dangling endpoint. Schematic connectivity and digital qualification are unchanged.
Validation: 21 export checks, native KiCad integration and four mesh-contract
checks pass. All twelve controller meshes are rebuilt together.

### Local underside projection and withdrawn CPU clock assignment

A separate CPU/A4 region maps the underside into native PCB coordinates.
Its four anchors are A5:40, A4:1, A4:10 and A5:21, in convex boundary order.
Six independent checks (A5:1/20/6/14 and A4:20/11) have maximum residual 0.661 mm
against the existing photo-estimated pads, within the existing 1.25 mm tolerance.
This reviewed local nominal projection is not measured board geometry and does
not qualify the failing global underside registration. Its scope ends at the
anchor hull. Geometric agreement does not prove that two conductors join.

The CPU-side CLK assignment introduced in 966ff11 is withdrawn. The bottom track
candidate ended at pixel (1354, 2811), projecting near top pixel (1529, 3054).
The nearby observed top terminal at (1527, 3048) appears to connect to A4:13 D6.
This conflicts with the tentative A5:6 CLK origin. The five assigned native
sections have been removed; original observations and retired UUIDs remain in
`evidence.json:routeReviews`. No replacement D6 assignment or via is asserted.
Sharper junction photographs or continuity measurements are needed to settle
pin/terminal correspondence and the apparent attachment. The earlier passing
geometry and consistency tests did not establish that electrical attachment.

Registered route validation rejects stale calibration, unqualified regions,
photo or native points outside the convex hull, observed geometry inconsistent
with the projection, and inferred attachments beyond the local tolerance.
Regression checks use synthetic geometry to exercise those guards and ensure
the withdrawn route never reappears as assigned copper. Local fit observations
remain available for further review without qualifying any disputed net.

Current totals: 25 assigned sections (17 observed, 8 inferred), 37 unplaced parts,
229 airwires and one unfinished A1 route endpoint. The BR1/R10.3 local connection
is unchanged. Schematic connectivity and digital qualification are unchanged.

## First native ceramic capacitor

C5.1 is placed from the primary photo: pin 1 at (1547, 1617), pin 2 at
(1550, 1674), and disc centre at (1585, 1650), with 8-pixel observation
uncertainty. Factory placement identifies the part between A1 and A2.1. Its
upper lead shares the R10 supply island; the lower lead is on the broad return
rail toward the two packages' pin 7. These are reference rail assignments, not
continuity measurements. The separate-specimen close-ups corroborate construction.

The native footprint origin records the body centre independently from its pads.
Generated SCAD now exports ceramic bodies and pads; board drilling, copper lands,
solder joints and bent leads use the same native endpoints. The former C5.1 body
placeholder is removed. Disc diameter 5.2 mm, thickness 1.2 mm, centre height
4.4 mm and lead/joint dimensions are nominal. C5.2–C5.4 also use native pad/body placement; C5.5 retains a legacy estimate. No copper route is added by this placement.

C5.2, C5.3 and C5.4 are identified by the factory placement drawing and primary
photo lead entries. For each, a visible rail supports one terminal assignment;
the other terminal follows the reference decoupling circuit. Hidden continuations
remain untraced and no copper is assigned by placing these parts. Component
evidence records the distinction. Their body centres remain independent of the
pads, with nominal disc and bent-lead geometry. C5.5 is not placed because the
primary photograph obscures a lead entry beside the electrolytic capacitor.

C5.4 uses a separate nominal 8.1 mm centre height because its photographed
projection overhangs A7. The initial shared 4.4 mm height intersected the nominal
DIP body in the close-up render; this clearance estimate removes the intersection
without moving native pads or the photo-derived body centre. Specimen stand-off
and tilt remain unmeasured.

## Reset resistor placement from shared underside strip (2026-10-17)

R4.2, R7 and R8 now use native pads rather than legacy visual placeholders.
The primary top photo supplies lead-entry coordinates; factory drawing
63-330-4103-2 supplies designator order. The primary underside and comparison
photo PXL_20261017_080351042 show a strip joining their inner ends, separate
from the adjacent R6.1 joint. GND is the only shared reference net, supporting
pin 2 at these inner ends. Individual pin-1 signals remain reference-informed;
no measured continuity or complete ground path is claimed. Comparison-specimen
coordinates are not used to place the primary board. No copper was added.

This places 24 resistors and leaves 30 schematic parts unplaced. Pad/drill and
body dimensions remain nominal. Blue collars preserve the observed end, not
polarity. The standalone `assembly-review.scad` inherits these changes.

## BR2 trace review from comparison photographs (2026-10-17)

`evidence.json` records `br2-terminal-order-review`: unnumbered top/underside
endpoint observations and a partial board-edge trace in the comparison specimen.
The path has not been followed continuously to A5:26 or V4.9:C. The absence of a
visible underside branch at CPU pin 26 does not mean the pin is disconnected;
its top-side attachment remains to be reviewed. Parallel traces and copper
visible through the board must not be silently joined across photographs.

These observations neither place BR2 nor assign a net, route or via. The museum
shows the review for BR2, CPU and reset-transistor selections. Endpoint order is
geometric, not electrical. Primary specimen correspondence and source/CPU side
identification remain open; closed-bridge continuity alone cannot resolve them.

## CPU pull-up lead observations (2026-10-17)

Factory placement identifies R6.4 nearer A4 and R6.5 nearer A6. The primary top
photo now records their visible lead ends as unnumbered candidates, with the
observed blue-collar end. These points are not qualified PCB holes. Comparison
photo 080434345 shows raised bends and body-to-hole offsets clearly; it is a
different specimen and supplies no primary-board coordinates. The apparent
crossings of leads and adjacent tracks do not establish soldered connections.

Both parts remain unplaced until board-entry points and supply/signal terminal
order can be resolved. The museum candidate view exposes the uncertainty without
creating native pad highlights. No geometry or electrical connectivity changes.
