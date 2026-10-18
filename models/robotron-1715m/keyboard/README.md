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
- [Side profile](side.png)
- [Underside preview](underside.png)
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
python3 render.py                   # all six review views
```

Rendering uses OpenSCAD's Manifold backend. Review shape, spacing, colours and
internals here, then export affected canonical parts and synchronize the museum.
Preview rendering does not regenerate museum assets.

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

## Construction and evidence

Caps and SI/SO indicator lenses attach to fixed deck carriers. `caps_led_on` and
`siso_led_on` select static preview colours; they do not simulate emitted light or
emulator state. The browser creates these lenses at runtime.

Owner photos `123247922` and `123319025` show rubber strips along the cable
opening and a grooved cable bush in a folded support. The controller overlaps the
matrix PCB's rear edge, with its cable end toward the opening. Docking depth and
hidden connector engagement remain unverified; no unseen inter-board cable is
inferred.

Inside photos `PXL_20261012_123048886.jpg` and `PXL_20261012_123907435.jpg`
establish the light shell's open lower rim, separate lid and individual tabs.
The owner specified approximately 1 mm sheet for the shell and lid. Tab geometry,
seams and local bends remain estimates. The black deck is an open folded 1 mm
sheet with an owner-specified 8 mm skirt and 1 mm gap above the base. Its planes
follow the keyboard tilt. The black deck's rounded perimeter remains a visual
estimate, separate from the light shell's bends.

The owner specified a base profile rising from 15 mm at the front to 29 mm at the
black panel's rear edge, then remaining level to the back. The rear shelf and
pencil trough are horizontal; the trough is pressed, not a through-hole. Other
profile details use `PXL_20261013_084425145.jpg` and remain photo estimates.
Editable geometry and derived dimensions live in the shared SCAD sources.

Danila accepted the exterior at commit `cf7e113` as broadly correct. Preserve
that visual baseline while refining internals; acceptance does not establish
manufacturing fit or approve hidden construction.

Owner `123103225` supplies the matrix connector's molded 2У0 marking. Supports,
fasteners, insulating sheet and board artwork are reviewed through the
[parent reference guide](../reference-guide.md) and evidence manifests. The
[controller guide](../keyboard-controller/README.md) owns controller placement
and pad interpretation; nominal support heights remain estimated.

The underside photographs do not expose bare switch contact faces. Comb
electrodes and short matrix routes are functional illustrations, not photo-traced
contact patterns. Preserve that distinction when reviewing the board preset.
