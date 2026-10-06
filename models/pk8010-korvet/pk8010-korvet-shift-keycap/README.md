# Корвет ПК8010 РГ / SHIFT keycap

First review prototype of the wider key photographed in the second archive.
It has a different row profile from the ↑/8 key: the top slopes down toward
the rear (+Y), with both rear and front walls sloping inward.
The top retains a shallow dish across its width.

Review: [top](preview.png), [side](preview-side.png),
[underside](preview-underside.png), [STL](pk8010-korvet-shift-keycap.stl),
and [editable model](model.scad).

| Parameter | Prototype value | Basis |
| --- | --- | --- |
| Base width × depth | 30 × 17.8 mm | Ruler-photo estimates |
| Top outline | 26 × 13.5 mm | Photo estimate |
| Nominal top height | 11.5 mm | Provisional |
| Top tilt | −7° about X | Side-photo estimate; front higher than rear |
| Rear wall inset | 1 mm at upper blank | Provisional amount; user confirmed this wall also leans |
| Top offset | About +1.20 mm along Y | Derived from rear wall inset |
| Dish depth | 0.6 mm | Provisional |
| Socket opening | 5.5 × 3.5 mm, centered | Borrowed from ↑/8; unconfirmed for this key |
| Socket bottom / insertion depth | 1 / 8 mm | Borrowed from ↑/8; unconfirmed |
| Shell wall / roof | 1.1 / 1.4 mm | Provisional |
| Engraving depth | 0.35 mm | Modeling choice |

All dimensions are editable at the top of `model.scad`. The legends are
approximations of РГ, SHIFT, and the outlined double arrow. Set
`engrave_legend = false` for a blank version. +Y is the upper edge of the
upright legends; the word SHIFT is on the −Y side.

`rear_inset` controls the upper/rear wall's lean away from the vertical XZ
plane independently of `top_tilt`, which controls the finger surface's tilt.
The 1 mm inset is an initial estimate for review, not a measured value.

The [five source photos](../reference/wide-key-photos/README.md) show no
underside, so the single mounting socket and supporting webs are provisional.
There is no evidence yet for additional stabilizer mounts. Do not treat the
socket arrangement or the photo-derived angle as confirmed measurements.

Use the [PLA / 0.4 mm nozzle starting settings](../pk8010-korvet-keycap/README.md#first-print-pla-04-mm-nozzle)
from the smaller key: upright, 0.12 mm layers, 3 walls, and targeted supports
under the raised socket rim and roof. Block supports inside the socket bore.
This wider roof needs its own support-preview check. Physical fit is untested.

Rendered with OpenSCAD's Manifold backend and exported with CGAL. The STL passes
edge and connectivity checks: one closed connected mesh, 3,816 triangles,
with bounds of 30.0 × 17.8 × 12.286 mm.

From the repository root:

```sh
./scripts/open.sh pk8010-korvet/pk8010-korvet-shift-keycap
```

To export from this directory:

```sh
openscad --backend CGAL --export-format binstl \
  -o pk8010-korvet-shift-keycap.stl model.scad
```
