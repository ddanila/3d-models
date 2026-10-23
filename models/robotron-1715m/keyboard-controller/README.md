# Keyboard controller reconstruction

The root KiCad files describe the reference circuit and partial historical PCB.
`reference/` contains a separate proposed implementation of the same netlist.
Its geometry is not specimen evidence; dimensions, package adapters, device dynamics
and specimen timing remain unqualified. Neither variant is fabrication-ready.

## Review

Open `assembly-review.scad` for the detailed museum controller. Press F5 and Home;
set `side="bottom"` for its underside. `show_mounts` and `show_shield` restore the
surrounding hardware. `review.scad` shows the native electrical geometry separately.
Cyan artwork is unassigned and makes no connectivity claim.

Open `controller.kicad_pro` in KiCad 10 to edit the electrical reconstruction.
Unplaced components are parked outside the outline. Board dimensions remain
estimates, not specimen measurements. Exports use millimetres
and a common top-view frame; transforms and conventions are in `generated/layout.json`.

Open [the connection-review sheet](review/connection-review.html) for annotated
serial-output and X1 evidence, reference endpoints and distinguishing observations.
X1 serves the key matrix and LEDs; XT1 is the host cable. Edit the review questions
in `connection-review.json`, then run `python3 tools/connection_review.py`.
The generator reads canonical route/pin evidence and does not modify the PCB.
Projected search circles include held-out registration checks; they locate
occlusions and do not establish joints, layer transitions or connectivity.
`clock-continuation.json` records the resistor-bank fit, exposed top spans and
outer underside lane used by the clock connection review. Hidden spans remain
open joins; these observations do not assign a clock net or filter winding.
`output-assembly.json` records the primary filter envelope, visible joint rows and
raised wire arcs. Its generated visual assembly has no electrical pin assignments;
XT1's inherited native coordinates remain reference placeholders.
`cable-copper.json` records an anonymous underside graph; the generated report
retains connected groups, winding-pairing alternatives and registration checks.
Its board projection is illustrative and must not become numbered pads or native
electrical routes while registration and terminal identities remain unresolved.
`supply-review.json` selects canonical supply observations and held-out resistor
checks for that report. Filter predictions are outside the fits’ anchor hulls;
local fit agreement does not identify a winding or connect the shield to ground.
`filter-registration.json` matches the primary filter joint rows using held-out
inner joints. The generated local fit is bounded by the outer joints; projected
underside spans are not top copper or native electrical routes.

## Proposed reference PCB

Open `reference/controller.kicad_pcb` for the proposed layout and
`reference/review.scad` for its electrical geometry. Orange copper is proposed;
blue geometry retains an exact match to a historical source item. The historical
board and its evidence ledger remain separate. Reference completion does not
reduce unresolved historical joins.

Edit `reference/implementation.json` for proposed placements and routing constraints.
Use `tools/reference_board.py --prepare /tmp/robotron-reference/controller.kicad_pcb`
with KiCad Python to generate a starting board and DSN. The routing boundary is
inset to respect native edge clearance; disable the router's automatic neckdown.
The retained `reference/routing-receipt.json` identifies the router and inputs.
Import a session with `--import-session FILE --input-board FILE --output-board FILE`;
this rejects changes to terminal identities or placements beyond interchange
precision. Then run `tools/reference_board.py` to export and check the committed
reference board, or `--check` for standard-Python freshness validation.

The proposed discrete and filter footprints are electrical adapters. Their semantic
pin order is explicit; they do not establish original hole entries, installed
orientation, winding identity or mechanical fit. The existing HDL comparisons
apply to the shared schematic connectivity, not the proposed copper's parasitics.

## Authorities

| Information | Editable source / generated review |
| --- | --- |
| Components, numbered pins and nets | `controller.kicad_sch`, local `kbd.kicad_sym`; `generated/connectivity.json` |
| Outline, footprints, holes and copper | `controller.kicad_pcb`; `generated/layout.json` and `generated/controller.scad` |
| Source provenance, variants and unresolved interpretations | `evidence.json`, `component-evidence.json` |
| Photo observations and registration | `photo-landmarks.json`, `bottom-landmarks.json`; generated registration JSON/SVG |
| Route provenance tied to native geometry | `route-evidence.json` |
| Assembly and mechanical estimates | `../specimen-details.scad` |
| Current ERC/DRC findings and export hashes | `generated/qualification.json`, `generated/manifest.json` |

Keep derived inventories in these artifacts. Git history records implementation
changes; this guide records the workflow and interpretation limits.

## Evidence boundaries

The primary museum board and comparison photographs are distinct specimens.
`evidence.json` pins their sources, markings and hashes. Comparison photographs
can clarify construction but require independent registration and an explicit
routing comparison before transferring geometry. The museum ROM was replaced;
its contents remain unread. A comparison ROM label does not identify either dump.

The Zander circuit is the digital reference. Published WR/RD and oscillator
variants remain separate in `referenceVariants`; do not combine them to fit the
emulator. Factory placement drawings establish reference identities where visible.
The matrix and lamps beyond X1 are external to the controller reconstruction.

Top-photo fits and bounded local underside fits support placement review. Global
underside registration remains unqualified. `top-copper-landmarks.json` and
`generated/top-registration.json` bound top copper independently of raised lead
observations; failed extrapolation checks remain visible. Raised leads and sockets can hide hole
centres; a successful local fit cannot establish copper attachment or board scale.
The eye-based fit holds out independent solder eyes and composes with qualified
underside placement only inside the intersection of their domains. Eye matches
do not establish net identity; nearby lanes must still be traced independently.
Superseded CPU clock and BR2 interpretations remain in `evidence.json:routeReviews`.
No withdrawn CLK assignment is restored merely because nearby traces align.

Body-only photo observations and package dimensions are recorded in
`component-evidence.json`, with device drawing sources in `packageReferences`.
They support visual estimates without assigning electrical pads.
`generated/layout.json:visualNetworks` and `visualAxials` export unplaced bodies
and raised lead observations separately. Their leads stop above the board without
invented holes, solder joints or terminal numbering. Raised lead ends
do not establish hidden holes, and drawing-view pin order does not establish
installed orientation. Preserve component asset credits during migration.

BR1 separates oscillator and CPU clock; BR2 separates reset source and CPU reset.
Their terminal numbers are reconstruction identifiers. Observed bridge geometry
can be represented as unassigned artwork before source/CPU terminal order is
resolved; do not attach guessed pads or nets to make it look complete. Generated
`layout.json:visualBridges` preserves these wire observations independently of
native footprints; review views show them in cyan. Virtual bridge isolation
is tested digitally, but the reviewed sources do not prescribe physical bridge
opening. Closed-link continuity alone cannot establish source-side terminal order.

Every historical native copper UUID requires an observed, inferred or unresolved review,
source hashes, a locator and `geometrySha256`. Geometry or net changes invalidate
the review. Observed tracks require their side's photo; observed vias require both
sides. This enforces provenance completeness, not the truth of an interpretation.
Unassigned photo artwork is not electrical copper.

`bus-review.json` retains partial bus paths with unresolved cross-side joins.
Its reference nets and terminal pairs are review targets, not assigned copper
or complete connections. `generated/bus-review.json` adds a local cross-side
search overlay for ROM-side eyes beneath the installed CPU body. Latch reviews
retain separate candidate eyes and covered exits. Neither identifies a via
or establishes continuity. Assigned cross-side joints carry separate top and
bottom registration checks; solder-obscured attachments and unmeasured via
dimensions remain inferred.
Before promotion, verify the photographed centreline,
pad positions and local registration independently; a model short alone does
not identify which of those is wrong.

`generated/connector-review.json` checks X1's native reference pads against
locally registered underside joints. `generated/connector-terminals.json` retains
row-order alternatives constrained by resistor and COL11 attachments; the two
row directions are tested independently. Assembly leads consume native positions
for mapped contacts. A8 remains unclassified visual geometry because it is absent
from the reference schematic. Raised top-side bends are not hole centres; housing
dimensions, lead heights and hole diameters remain estimates.

## Native routing audit

`generated/routing-audit.json` reports same-net copper islands, their terminals,
route evidence groups and KiCad unconnected items. It includes off-board
placeholder pads. Use remaining pad-group links and fully connected multi-pin
nets to track native routing separately from photo reconstruction and simulation;
floating track fragments do not count as connected pads.

## Regenerate and check

From this directory, use Python with KiCad's `pcbnew` module for native export
and integration tests. Set `KICAD_CLI` if necessary. On macOS:

```sh
/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 tools/export.py
/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 tools/test_kicad.py
python3 tools/export.py --check
python3 tools/test_export.py
python3 tools/photo_registration.py
```

`photo_registration.py --apply --refs A1 ...` applies explicitly selected fits
only after independent landmarks pass. Regenerate exports after applying fits.
CI runs standard-Python freshness checks and a separate native
job using the [KiCad 10 stable Ubuntu packages](https://www.kicad.org/download/ubuntu/).
The native job records tool versions and regenerates only temporary copies; it
does not replace the committed exports. Unsupported zones, blind vias, internal
tracks and invalid outlines fail explicitly. ERC's RD_N and SHIELD exceptions
are recorded individually; outstanding DRC findings remain failures.

After geometry changes, use `../tools/export.py --parts` with the affected part
names, refresh all controller mesh receipts when shared SCAD inputs change, then
run `../tools/test_controller_mesh_contract.py`, `../tools/export-downloads.py`
and `../tools/check-metadata.py`. Review both sides before accepting new baselines.
Commit CAD before running the museum sync scripts; they reject dirty or stale
sources. Compatible revisions belong in the museum source manifests.

Digital comparisons and specimen evidence collection are documented in the
museum's [status guide](https://github.com/ddanila/dac/blob/main/docs/robotron/keyboard-controller-progress.md)
and [verification guide](https://github.com/ddanila/dac/blob/main/docs/robotron/keyboard-controller-verification.md). Logical reference agreement does not
qualify analog behavior, exact CPU cycle timing or specimen firmware.

### Populated reference assembly

Open `reference/review.scad` with `show_components=true`. `reference/assembly.json`
defines proposed package choices; `tools/reference_assembly.py` derives numbered
lead paths and body poses from the routed pads, reusing the pinned DIP bodies and
manufacturer L3/12 dimensions. Regenerate with that tool; use `--check` to reject
stale exports. `reference/signal-paths.json` supplies netlist-checked walkthroughs
for the museum.

The generated review checks body envelopes, leads against foreign body envelopes, board
overhang, nominal drill allowance and 3D lead-to-lead surface clearance.
Intentional bridge/same-net contacts are separate from unintended contacts.
These modeled clearances do not qualify manufacturing tolerances, bend radii or enclosure fit.
R2 and the separate filter-winding bodies remain surrogates; shared-core geometry
and coupling are unresolved. These reference adapters do not establish historical
footprints or fabrication readiness.
