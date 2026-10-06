# Oral-B five-brush shelf stand

Five toothbrush supports on a flat 3.2 mm base, with two screw holes for
attaching it to a shelf. The surrounding water-catching pool is removed.
The original raised feet remain under the pegs to preserve the brush seating
and clearance provided by the downloaded stand.

| Parameter | Value |
| --- | ---: |
| Brush count | 5, in one row |
| Center spacing | 40 mm |
| Base | 214 × 36 × 3.2 mm |
| Base corner radius | 4 mm |
| Overall height | Approximately 20.94 mm |
| Screw holes | Two Ø4 mm through-holes, without countersinks |
| Screw centers | X = 7 and 207 mm, Y = 18 mm |
| Brush centers | X = 27, 67, 107, 147, 187 mm; Y = 18 mm |

Hole diameter and brush spacing are editable dimensions. The screw heads
sit on top of the base. The initial print was reported satisfactory on
2026-10-06; adjust these dimensions if using different screws or brushes.

## Source geometry

Based on **Oral-B Toothbrush Stand w/ Elongated Support** by **fgoyti**:
<https://www.thingiverse.com/thing:4808551>, itself a remix of
<https://www.thingiverse.com/thing:1478249>.

The download's `oralb_longer3.stl` is preserved in `reference/`, together with
its original README and license notice (Creative Commons Attribution –
Non-Commercial). This adaptation retains that attribution and noncommercial
restriction; the downloaded notice does not specify a license version.

`model.scad` imports only the central support region of the original mesh,
cropped to a 15 mm radius above its pool floor, then places five copies on
a new parametric base. This preserves the shaped peg, taper, rounded tip,
and foot without approximating the mating geometry. Keep the reference STL
alongside the source when editing or rendering. The exported STL is standalone.

## Printing and editing

Print flat as modeled, with the pegs upward. No supports are expected to be
needed. The imported peg retains the original designer's brush interface;
compatibility with other Oral-B handle models has not been established.
Set `brush_count = 1` for a smaller fit trial if desired.

```bash
./scripts/open.sh oral-b-five-brush-stand
```

Printable file: [oral-b-five-brush-stand.stl](oral-b-five-brush-stand.stl).
