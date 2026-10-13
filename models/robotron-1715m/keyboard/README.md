# Keyboard review in OpenSCAD

Open [model.scad](model.scad) and press **F5**. This keyboard-only entry point
reuses the museum's canonical modules and key positions from `../model.scad`;
it does not copy the mechanical geometry into a separate model.

Use the Customizer's **Assembled**, **Exploded** or **Boards** preset, or change
`view` directly. `separation` controls the exploded spacing; zero restores the
assembled positions. Shell/deck/key/core/inlay/PCB/rubber colors are editable.
Clear keys have a separate silver inlay and configurable shell alpha.

- [Assembled preview](preview.png)
- [Low front preview](front.png)
- [Exploded preview with springs](exploded.png)
- [PCB/contact preview](boards.png)

Keep `show_springs=false` for quick exterior work; enable it to inspect mechanisms.
`draft=true` uses coarse spring tessellation. Key geometry retains the shared
model's tessellation. Hidden pale key cores are added in the exploded view.
The keyboard is centered locally, without the computer or monitor.

Legends are thin, flat **preview annotations**, not print geometry. They come from
`../keyboard-layout.json`; the helper below refreshes `legends.scad`. The default
`Arial Unicode MS` is installed on Danila's Mac and includes the special symbols.
Choose another installed Unicode font through `legend_font` on other computers.
No font files are distributed here. The browser retains its own curved legends.

From this directory:

```sh
python3 render.py --view assembled  # one quick color PNG
python3 render.py --view front      # check front fascia and deck joint
python3 render.py                   # all four review views
```

This uses the installed OpenSCAD build with the Manifold backend. On the current
Mac, all four previews take only a few seconds. It does not regenerate STLs,
rebuild the complete computer, sync DAC, or run browser/emulator CI. Review shape,
spacing, colors and internals here first; then export only the affected canonical
parts and sync the museum once the change is ready.

Edit shared mechanical dimensions in the parent SCAD files and `../keycap/` or
`../key-switch/`; edit key positions in `../tools/configure.py`, which generates both
`keyboard-layout.scad` and `keyboard-layout.json`, then refresh the preview legends. Colors changed here are review overrides: transfer approved
palette changes to the parent model/exporter before updating the museum.

OpenSCAD's [`color()`](https://files.openscad.org/documentation/manual/The_OpenSCAD_Language.html#color)
supports named colors, hexadecimal colors and RGBA transparency in F5 previews.
For example, `color("#202526") cap(...)` or `color([1,1,1,0.28]) cap(...)`.
STL does not carry color; keep the SCAD source and color PNGs for visual review.
Preview transparency is not a simulation of glass, metal reflection or rubber.
The assembled keyboard is a visual reference, not one printable part. Existing
photo-derived dimensions and hidden construction remain provisional.

The deck aperture is clipped behind the 3 mm front wall. Without this limit,
its tilted cutter removed the front fascia and exposed the PCB edge. The low
front preview checks that the shell closes beneath the deck.
