# Models

Create one directory per model, using a short kebab-case name:

```text
models/example-part/
  model.scad
  README.md
```

The repository scripts treat `model.scad` as the printable entry point and
generate `example-part.stl` and `preview.png` beside it. Supporting `.scad`
files may live in the same directory; reusable modules shared by multiple
models belong in the top-level `lib/` directory.

Group related models under a device directory, for example:

```text
models/pk8010-korvet/
  README.md
  pk8010-korvet-button/
    model.scad
    pk8010-korvet-button.stl
    preview.png
    README.md
  pk8010-korvet-side-lid/
    model.scad
    pk8010-korvet-side-lid.stl
    preview.png
    README.md
```

Batch scripts discover models recursively. Keep model directory names unique
across groups, since STL names and temporary render-check filenames use those
names. Open a grouped model with `./scripts/open.sh group/model-name`.
