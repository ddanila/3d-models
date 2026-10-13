# Juku models

Canonical home of the models moved from `ddanila/juku` on 2026-10-13.
Original geometry, STLs, photos, scripts and notes were preserved;
[migration.json](migration.json) records their source commit and hashes.

**Physical verification:** the keycap is printed and verified. The top case,
bottom case (including split panels) and legs are not yet confirmed.
See the [collection status catalogue](../../MODEL-STATUS.md).

OpenSCAD models for restoring and reproducing parts of the Juku computer.
Technical dimensions and modeling details are in [NOTES.md](NOTES.md).

> [!NOTE]
> This project is an experiment in creating medium-complexity 3D models
> with an LLM. The OpenSCAD code was written through Codex with almost no
> manual code edits.

## Models

### Keycap

The keycap has a dished top, rounded chamfered sides, a central spring rod,
contact pushers, and side latches that clip into the switch housing.

|  | Top | Bottom |
| --- | --- | --- |
| Original | ![Top of an original Juku keycap](keycap/original-top.jpg) | ![Bottom of an original Juku keycap](keycap/original-bottom.jpg) |
| Render | ![Top keycap render](keycap/preview-top.png) | ![Bottom keycap render](keycap/preview-bottom.png) |
| Print | ![Top of the printed keycap](keycap/printed-top.jpeg) | ![Bottom of the printed keycap](keycap/printed-bottom.jpeg) |

- Source: [`keycap/juku-keycap.scad`](keycap/juku-keycap.scad)
- Printable model: [`keycap/juku-keycap.stl`](keycap/juku-keycap.stl)

### Bottom Case

The bottom part of the computer case includes the PCB opening and guide,
leg mounting holes, and reinforced PCB support mounts.

| Interior | Underside (logo) | Rear edge (supports) |
| --- | --- | --- |
| ![Bottom case interior render](bottom-case/preview.png) | ![Bottom case underside render with logo](bottom-case/preview-logo.png) | ![Bottom case rear-edge render showing guide rails and support bosses](bottom-case/preview-supports.png) |

- Source: [`bottom-case/juku-bottom-case.scad`](bottom-case/juku-bottom-case.scad)
- Printable model: [`bottom-case/juku-bottom-case.stl`](bottom-case/juku-bottom-case.stl)

### Top Case

The top case is an open-bottom shell with a sloped keyboard face, keyboard
opening, side-wall chamfers, rear ventilation slots, a recessed logo area,
LED opening, and switch access opening.

| Exterior | Interior |
| --- | --- |
| ![Top case exterior render](top-case/preview.png) | ![Top case interior render](top-case/preview-bottom.png) |

- Source: [`top-case/juku-top-case.scad`](top-case/juku-top-case.scad)
- Printable model: [`top-case/juku-top-case.stl`](top-case/juku-top-case.stl)

### Legs

The rubber legs are simple stepped push-in feet matched to the bottom-case
mounting holes.

| Render |
| --- |
| ![Leg render](legs/preview.png) |

- Source: [`legs/juku-leg.scad`](legs/juku-leg.scad)
- Printable/reference model: [`legs/juku-leg.stl`](legs/juku-leg.stl)
- Assembly check: [`assembly/juku-bottom-with-legs.scad`](assembly/juku-bottom-with-legs.scad)

## Commands

```bash
# Open a model for interactive inspection.
./scripts/open-keycap.sh
./scripts/open-bottom-case.sh

# Validate both models without changing committed artifacts.
./scripts/check-render.sh

# Regenerate committed STL files and previews.
./scripts/export-stls.sh
./scripts/render-previews.sh

# Export the bottom-case XY projection for LibreCAD.
openscad-nightly \
    -o bottom-case/projection-xy.dxf \
    bottom-case/projection-xy.scad
```
