# Robotron 1715 loose keycap

[Keycap STL](keycap.stl) · [OpenSCAD model](model.scad) · [Shared geometry](geometry.scad)

Clean reconstruction of Danila's loose black `5 / %` key from
`Photos-1-001 (9).zip`, photos `185824256`, `185826600`, `185834871`, `185855185`.
The older `(8)` ZIP contains the same four cap photos. References are in
`../reference/photos/`. Owner photographs and this original geometry are MIT.

The cap has a thick rounded square skirt, a slightly tapered raised touch
surface, shallow dish, pale internal core, annular spring recess and a central
round blind cup. The previous square stem socket was unsupported by these photos
and is absent. The STL is one connected, closed body; no printed legend is baked
into it, so it can also serve as a blank replacement. `part="preview"` shows the
black shell and pale core separately; STL itself cannot retain colors.

The cup now includes an inward latch ring with a beveled entry and a steeper
retaining shoulder, plus an axial orientation rib toward one skirt corner.
These details follow the underside photos and owner review; their dimensions
remain provisional. The ring projects 0.45 mm radially into the 9 mm bore
(8.1 mm throat). The orientation rib projects 0.6 mm inward and is 1.2 mm wide,
with a beveled entry. Its default angle is 135 degrees toward the -X/+Y corner.
Adjust the `latch_*` and `key_*` parameters in `model.scad` for fit;
`part="section"` exposes both features in a cutaway. The STL includes both.

The owner confirmed the underside diameters and 15 mm round body outside
diameter on 2026-10-13. The spring recess sits only in the square base; it does
not extend into the raised round body. The owner supplied a 5 mm recess depth and requested equal base and raised-body
heights. Keeping the estimated 11.4 mm total gives 5.7 mm each, leaving 0.7 mm
above the spring seat. The round body tapers from 15 mm at its lower end to
14.4 mm near the top, followed by the small rim bevel. The 0.6 mm diameter
reduction is provisional and adjustable with `body_taper`. Other dimensions remain
**estimates**. No fit allowance is added to the supplied diameters.

| Feature | mm |
| --- | ---: |
| Square skirt | 17.8 × 17.8 |
| Total height | 11.4 |
| Square base / raised body height (equal, provisional) | 5.7 / 5.7 |
| Lower round body diameter (owner; excluding base collar) | 15 |
| Upper round body diameter (provisional; before rim bevel) | 14.4 |
| Spring recess depth (owner) | 5 |
| Spring recess inside diameter (owner) | 15 |
| Central support outer / inner diameter (owner) | 11 / 9 |

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
