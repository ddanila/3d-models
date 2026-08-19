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
