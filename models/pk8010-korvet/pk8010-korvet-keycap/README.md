# Корвет ПК8010 keycap — first review prototype

Parametric reconstruction of the photographed ↑/8 keycap, with a hollow tapered
shell, cylindrical top dish, rectangular blind mounting socket, reinforcing
webs, and recessed legends suitable for paint filling.

Review: [top preview](preview.png), [side preview](preview-side.png),
[underside preview](preview-underside.png),
and [printable STL](pk8010-korvet-keycap.stl).

| Parameter | Current prototype | Basis |
| --- | --- | --- |
| Socket opening | 5.5 × 3.5 mm | User measurement |
| Base | 17.8 × 17.8 mm | Ruler-photo estimate |
| Top outline | 12.8 × 14 mm | Provisional |
| Nominal top height | 12 mm | Provisional; shallow dish across the width |
| Top offset along Y | +1.9 mm (toward arrow tip) | Align +Y edges so this face is parallel to XZ |
| Top tilt | 0° | User correction: parallel to base in side view |
| Dish depth | 0.6 mm | Provisional |
| Shell wall / roof | 1.1 / 1.4 mm | Provisional |
| Socket wall | 1 mm | Provisional |
| Socket bottom above skirt | 1 mm | Provisional |
| Socket insertion depth | 8 mm | Provisional |
| Legend engraving depth | 0.35 mm | Modeling choice |

Edit parameters at the top of [model.scad](model.scad). +Y points toward the
arrow tip, and the skirt bottom is Z=0. The socket's long side runs left/right
by default; change `socket_rotation` to 90 if the original uses the other
orientation. `socket_clearance` adds to each complete opening dimension;
it defaults to zero. `engrave_legend = false` produces a blank keycap.

The top stays level from front to rear. Its offset is derived from the base and
top depths so the arrow-tip side (+Y) is vertical, parallel to XZ.
The numeral 8 side (−Y) slopes inward. The shallow concavity across the width remains.
This profile incorporates the user's review correction to the initial tilted-top
version; the measured socket opening remains 5.5 × 3.5 mm.

The internal webs are a simplified support structure, not an exact tracing
of the original molding. The legends are approximations. This first version
is for shape and fit review; height, socket depth and orientation need checking
against the original. See the [reference photographs](../reference/user-photos/README.md).

## First print: PLA, 0.4 mm nozzle

Print upright as modeled, with the open underside toward the bed and the ↑/8
legend facing upward. These are starting settings for the prototype, not a
physically tested print profile.

| Setting | Starting value |
| --- | --- |
| Layer height | 0.12 mm |
| Walls | 3; variable-width/Arachne preferred |
| Top/bottom thickness | 0.8–1 mm |
| Infill | 20%; most of this small shell will be walls |
| Outer-wall speed | 25–30 mm/s |
| Brim | 3 mm, outside only |
| Part cooling | Full after the first few layers |
| Temperature | Filament's PLA preset; 210°C nozzle / 60°C bed as a starting point |
| Supports | Build plate only, targeted under socket rim and internal roof/webs |
| Support top contact gap | 0.2 mm |
| Support interface layers | 2 |

The socket's lower rim begins 1 mm above the bed: it needs support. Inspect the
sliced layers to ensure the rim is supported from below. Block support inside
the 5.5 × 3.5 mm blind socket bore; its ceiling should bridge the short span,
but this needs checking in the slicer and on the first print. Trapped support
would be difficult to remove and could interfere with the switch fit.

Print one sample, remove the brim and supports, and check the fit gently before
forcing the cap onto the switch. The opening has zero added clearance. If it is
too tight, adjust `socket_clearance` in small increments (for example 0.1 mm),
then export again; do not scale the whole keycap to correct the socket fit.

Background: [Prusa PLA guidance](https://help.prusa3d.com/article/pla_2062)
and [support settings](https://help.prusa3d.com/article/support-material_1698).

## Validation

Rendered with OpenSCAD's Manifold backend; STL exported with CGAL and validated
with an edge/connectivity check:
one closed connected mesh, 3,012 triangles. Exported bounds are
17.8 × 17.8 × 12.012 mm. Physical fit has not yet been tested.

Open from the repository root:

```sh
./scripts/open.sh pk8010-korvet/pk8010-korvet-keycap
```

To reproduce the validated STL from this model directory, select CGAL explicitly:

```sh
openscad --backend CGAL --export-format binstl \
  -o pk8010-korvet-keycap.stl model.scad
```
