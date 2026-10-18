# Robotron 1715 loose keycap

[Keycap STL](keycap.stl) · [OpenSCAD model](model.scad) · [Shared geometry](geometry.scad)

Clean reconstruction of Danila's loose black `5 / %` key from
`Photos-1-001 (9).zip`, photos `185824256`, `185826600`, `185834871`, `185855185`.
The older `(8)` ZIP contains the same four cap photos. References are in
`../reference/photos/`. Owner photographs and this original geometry are MIT.

The cap has a thick rounded square skirt, a slightly tapered raised touch
surface, shallow dish, pale internal core, annular spring recess and a central
round blind cup. The STL is one connected, closed body; no printed legend is baked
into it, so it can also serve as a blank replacement. `part="preview"` shows the
black shell and pale core separately; STL itself cannot retain colors.

The cup includes an inward latch ring with a beveled entry and a steeper
retaining shoulder, plus an axial orientation rib toward one skirt corner.
These details follow the underside photos and owner review; their dimensions
remain provisional. Adjust the `latch_*` and `key_*` parameters in `model.scad` for fit;
`part="section"` exposes both features in a cutaway. The STL includes both.

The owner confirmed a 15 mm lower round-body diameter, 15 mm spring recess
inside diameter and 11 / 9 mm central-support outer / inner diameters on
2026-10-13. The owner also supplied a 5 mm recess depth and requested equal
base and raised-body heights. The recess stays within the square base. Total
height, taper and retention details remain estimates; edit their parameters in
`model.scad`. No fit allowance is added to supplied diameters.

The owner's measured spring is 13 mm **outer** diameter, 23 mm free length,
0.4 mm wire. The recess provides nominal room for that spring. Its actual fit,
retention, material shrinkage and printing clearances have not been verified on
the machine. Parameters are editable; this is a first fit prototype.

Export (from this directory):

```sh
openscad --backend Manifold --export-format binstl -o keycap.stl model.scad
```

The default orientation has the skirt underside at Z=0 and the touch face upward.
The recessed underside will need an appropriate slicer support/bridge strategy.
