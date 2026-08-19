# 3D models

A collection of unrelated 3D-printable models, primarily authored in
[OpenSCAD](https://openscad.org/).

Each model lives in its own directory under `models/`. A model directory has
a canonical `model.scad` entry point; generated STL and preview files live next
to it:

```text
models/
  model-name/
    model.scad
    model-name.stl
    part-lid.scad   # optional additional printable part
    model-name-lid.stl
    assembly.scad   # optional assembled preview scene
    preview.png
    preview-assembly.png
    README.md       # optional model-specific notes
```

Shared OpenSCAD modules can live under `lib/`. Keep them outside `models/` so
the batch scripts do not treat them as standalone models.

## Requirements

- `openscad-nightly` or `openscad`
- ImageMagick (`magick`) or macOS `sips` for downscaling preview renders

## Commands

```bash
# Open one model interactively, by directory name or path.
./scripts/open.sh model-name
./scripts/open.sh models/model-name/model.scad

# Validate every model without changing committed artifacts.
./scripts/check-render.sh

# Regenerate each model's binary STL.
./scripts/export-stls.sh

# Regenerate each model's preview image.
./scripts/render-previews.sh
```

The batch commands discover `models/*/model.scad` and optional
`models/*/part-*.scad` printable parts automatically. An `assembly.scad` scene
is rendered to `preview-assembly.png` when present.

## Models

- [`usb-serial-adapter-case`](models/usb-serial-adapter-case/) — open-top case
  for the DIYMORE FT232BM/BL USB to RS232/UART TTL/RS485 adapter
