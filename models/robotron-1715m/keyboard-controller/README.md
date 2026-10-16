# Keyboard controller electrical and physical reconstruction

Work in progress under the [museum implementation plan](https://github.com/ddanila/dac/blob/main/docs/robotron/keyboard-controller-plan.md).

The reference circuit is Zander drawing 56-330-4103-7. The photographed specimen
is marked 062-330-4102 and has an unidentified replacement EPROM. Do not treat
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
standard Python. New vias/arcs currently cause export to fail explicitly rather
than lose geometry. These exporter features still need implementation before
routing can rely on them.

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
