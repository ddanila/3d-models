# ПК8010 Корвет

Replacement parts modeled from supplied measurements for the right side of
the ПК8010 Корвет.

| Part | Dimensions and features | Printable STL |
| --- | --- | --- |
| [Button](pk8010-korvet-button/) | Ø7.6 × 17 mm; Ø3.8 mm blind bore, 14 mm deep | [Button STL](pk8010-korvet-button/pk8010-korvet-button.stl) |
| [Side lid](pk8010-korvet-side-lid/) | 154 × 26 mm base, 5.4 mm total height; Ø10 mm button hole, decorative grooves, finger recess opening to bottom edge | [Lid STL](pk8010-korvet-side-lid/pk8010-korvet-side-lid.stl) |
| [Keycap — prototype](pk8010-korvet-keycap/) | ↑/8; estimated 17.8 mm base, measured 5.5 × 3.5 mm socket | [Keycap STL](pk8010-korvet-keycap/pk8010-korvet-keycap.stl) |
| [Wide SHIFT keycap — prototype](pk8010-korvet-shift-keycap/) | РГ / SHIFT; estimated 30 × 17.8 mm base, distinct row tilt, provisional socket | [SHIFT STL](pk8010-korvet-shift-keycap/pk8010-korvet-shift-keycap.stl) |

Each part directory contains editable `model.scad`, printing notes, and a
preview. The lid's left groove is 115 mm long and its right groove is 7 mm;
both are measured inward from the raised section's edges.

[Local reference material](reference/README.md) contains keyboard and case
photos plus related third-party CAD files collected for keycap research.

From the repository root:

```bash
./scripts/open.sh pk8010-korvet/pk8010-korvet-button
./scripts/open.sh pk8010-korvet/pk8010-korvet-side-lid
./scripts/check-render.sh
```
