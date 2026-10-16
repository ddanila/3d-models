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
