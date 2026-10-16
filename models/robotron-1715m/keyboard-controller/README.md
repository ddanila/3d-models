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
The initial transcription contains 68 components; the analog section remains
subject to review. Signal pins have electrical types. Power rails and semantic
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

## Electrical discrepancy under investigation

The directly transcribed A2.2B gate inverts IORQ for the 8282 strobe and LED latch
clock. A2.2C separately inverts A15 for output enable. This differs from the
emulator's A15-gated LED behavior. Multi-column sense combines active contacts
through the transistor front end, whereas the current emulator ANDs selected
matrix bytes. A1 also inverts WR directly, whereas the emulator limits output
strobes to an address range. The co-simulation harness records these differences;
do not change the transcription merely to match software. Reconciling the drawing,
reference firmware and actual specimen is required before promoting behavioral
changes. In particular, replacing LED behavior broke the existing S600 stable-LED
qualification and was not retained in the production emulator.

## Generated geometry review

Open `review.scad` for a standalone reconstruction view. It consumes only
KiCad-derived arrays for the outline, holes, pads, package positions and artwork.
Cyan lines are unresolved photo graphics; assigned copper uses a separate layer.
Package bodies in this review are nominal envelopes. The accepted museum model
is not replaced by this incomplete board.

`python3 tools/test_export.py` checks source/output hashes, asymmetric CPU/ROM
and pad-number landmarks, closed outline area and stale-file rejection. These
checks run in CI without KiCad. The initial SCAD export rendered successfully
with the Manifold backend. The Edge.Cuts loop is reconstructed by endpoint
connectivity, not by file order; unsupported open or branched outlines fail.

Pending promotion work: verify package orientation against independent photo
landmarks, place the remaining reference components, establish discrete lead
numbers, associate visible paths with nets, resolve airwires and review the
analog transcription and jumper representation. Full physical assembly migration
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
