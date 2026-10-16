# Mechanical evidence review — canonical v48

Reviewed 2026-10-16 against the owner's photographs. [Annotated photographs](mechanical-review.html) and [regenerated current-model comparisons](photo-comparisons/index.html) are the review artifacts. No geometry changes were justified by this pass; no printed-and-verified status changed.

| Area | Evidence and result | Boundary |
|---|---|---|
| Keyboard PCB supports | Owner 123106382 shows separate bent leaves; matrix/controller support and fastener intersections pass | Hidden attachments and bends remain estimates |
| Cable and rubber | Owner 123539882 shows two-flange grommet, restraint and shield termination; cable/board/chip/clamp and rubber/support intersections pass | Cable flex and contact force unmeasured |
| Motherboard mounts | 072654600 identifies one open hole and one occupied hole; `mounting-audit.json` retains each classification | Two legacy right-side mounts remain obscured and unverified |
| Drive adapter | Owner 150520316 underside and existing planar comparison retain opposed holes and ribbon exit | Fitted points are not independent dimensional validation; unseen spacers unresolved |
| Package clearance | `check-pcb-interfaces.py` passes 138 packages; nominal lead/board/socket interfaces checked | Artwork and nominal package pitch do not establish circuit continuity |
| Cover fit | System lid/base, keyboard shell/bottom and monitor upper/lower intersections are zero | Touching permitted; not a tolerance-stack, fastening or manufacturing fit test |

`check-assembly.py`: **54 selected pairs pass**, intersection tolerance 0.001 mm³. `check-covers.py`: **3 cover pairs pass**. Reports: [assembly.json](assembly.json), [covers.json](covers.json). Only the listed pairs are checked. Moving cable shapes, fastening preload, thermal clearances and hidden joints are outside scope.

The keyboard comparison had stale generated geometry and was regenerated from the current canonical model. Planar overlays collapse depth: their pixel residuals must not be reported as millimetre tolerances. The fan view has no independent holdouts; drive-adapter landmarks participate in fitting. Keep these distinctions when using comparisons to propose future edits.

Reproduce from repository root:

```sh
python3 models/robotron-1715m/tools/check-pcb-interfaces.py
python3 models/robotron-1715m/tools/check-assembly.py
python3 models/robotron-1715m/tools/check-covers.py
python3 models/robotron-1715m/tools/compare-photos.py
```

## Sampled inspection motion — 2026-10-16

`tools/check-inspection-motion.py` samples 41 positions for each of the system
cover, monitor upper cover, keyboard controller and keyboard matrix, plus controller against the moving matrix. The initial
straight controller path crossed the rear shell at 20% (426.483 mm³) and 30%
(2978.941 mm³); see [initial results](inspection-motion-before.json) and
[initial chart](inspection-motion-before.svg). A lift-first attempt cleared the
bare board, but checking its packages/connectors/leads found a 26.297 mm³ contact
with the shelf at 10%. No enclosure or PCB geometry was trimmed to hide it.

The first revised path cleared the enclosure, but a second check found a
265.801 mm³ controller/matrix intersection at 40% separation. The canonical
[inspection paths](../inspection-paths.json) now stage the layers: open them during
the first half, move the raised matrix 60 mm forward, move the controller 16 mm
forward and lift it 70 mm before moving it rearward, then return the matrix to its
usual inspection position. Final positions are unchanged; components and cable
endpoints follow their respective boards.

The final [205 samples](inspection-motion.json) and [chart](inspection-motion.svg)
at 2.5% intervals are clear below 0.001 mm³, including the controller's attached
components against both the shell and moving matrix. Covers currently jump to
their open pose; keyboard separation is animated. These are museum inspection
paths, not instructions for physically opening the specimen.

This checks the named solids against their enclosure and the two boards against each other,
not every pair in the
assembly or continuous swept volume. Fasteners, available cable slack and
physical fit remain unverified. DAC's separate cable geometry tests sample 21
positions in connected and parked modes; their recorded PSU-entry exceptions
remain explicit. Canonical CAD stays v48 and no print-verification status changes.

[Evidence colour rules](../evidence-map.json) distinguish supplied dimensions,
owner-photo reconstruction, comparative references and unmapped geometry. These
are independent of the model registry's printed-and-verified classification.

## Staged cover motion and evidence audit (October 16)

The expanded `inspection-motion.json` now tests seven pairs at 41 positions
(287 samples). Case lid, inserts, fixings and fascia are checked against the
PSU chassis/cover, fan frame, logic boards and connectors. The monitor upper
shell is additionally checked against the tube, yoke, chassis, boards,
components, capacitors and shield. The first diagonal paths intersected these
contents (`cover-motion-before.json`); canonical paths now lift fully before
translating. All 287 sampled intersections are below 0.001 mm³. DAC animates
these paths, including reverse movement and attached visual elements.

This remains sampled museum motion, not a physical disassembly procedure or
continuous swept-volume proof. It does not cover all solids or establish cable
slack, fastener removal or the exact physical separation sequence. No geometry
or STL changed, and no model gained printed-and-verified status.

`tools/audit-evidence.py` records ordered source-rule coverage in
`evidence-coverage.json`: all 197 exported parts have a mapping, with overlaps
listed explicitly. Display-controller parts use their own specimen photo;
owner-confirmed sheet thickness is separated from estimated bends and joins.
Runtime-generated meshes are audited in DAC. Source coverage is not dimensional
verification. Generic hardware remains a comparative reference.

## Component relationships and monitor lead references

`relationships.json` groups the keyboard matrix supports/fasteners, controller
mounts, cable restraint, monitor captive leads/plugs and drive adapter/ribbon
parts. These are mechanical, photo-referenced relationships; they do not certify
pin wiring, electrical continuity, thread sizes or hidden joints. Each group's
part names and source photo are checked by `tools/check-metadata.py`.

`monitor-cable-paths.json` records the exact Bezier control points and nominal
radii from `monitor-cables.scad`; the cheap metadata check detects divergence.
DAC uses these as the rest centerlines and rotates tube cross sections during
inspection, preserving their shape instead of stretching vertices by height.
The browser's deformation is an illustrative inspection route, not new CAD or
an estimate of available physical cable length. No STL or physical verification
status changes. DAC's `docs/robotron/monitor-cable-audit.json` reports 164 sampled
poses for endpoint attachment, bend radius and direction change; it is not an
all-parts collision or strain certificate.
