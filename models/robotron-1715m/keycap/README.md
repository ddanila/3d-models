# Robotron 1715 loose keycap

[Keycap STL](keycap.stl) · [OpenSCAD model](model.scad) · [Shared geometry](geometry.scad)

Clean reconstruction of Danila's loose black `5 / %` key from
`Photos-1-001 (9).zip`, photos `185824256`, `185826600`, `185834871`, `185855185`.
The older `(8)` ZIP contains the same four cap photos. References are in
`../reference/photos/`. Owner photographs and this original geometry are MIT.

The cap has a thick rounded square skirt, a nearly cylindrical raised touch
surface, shallow dish, pale internal core, annular spring recess and a central
round blind cup. The previous square stem socket was unsupported by these photos
and is absent. The STL is one connected, closed body; no printed legend is baked
into it, so it can also serve as a blank replacement. `part="preview"` shows the
black shell and pale core separately; STL itself cannot retain colors.

The cup now includes an inward latch ring with a beveled entry and a steeper
retaining shoulder, plus an axial orientation rib toward one skirt corner.
These details follow the underside photos and owner review; their dimensions
remain provisional. The ring projects 0.45 mm radially into the 8.6 mm bore
(7.7 mm throat). The orientation rib projects 0.6 mm inward and is 1.2 mm wide,
with a beveled entry. Its default angle is 135 degrees toward the -X/+Y corner.
Adjust the `latch_*` and `key_*` parameters in `model.scad` for fit;
`part="section"` exposes both features in a cutaway. The STL includes both.

Initial dimensions are **photo estimates**, not caliper measurements:

| Feature | mm |
| --- | ---: |
| Square skirt | 17.8 × 17.8 |
| Total height | 11.4 |
| Skirt height | 4.0 |
| Raised top diameter | 13.8 |
| Spring recess diameter | 13.6 at entry, 13.3 deeper inside |
| Central cup outer / inner diameter | 10.4 / 8.6 |

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
