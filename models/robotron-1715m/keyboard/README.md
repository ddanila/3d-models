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
python3 render.py                   # all five review views
```

This uses the installed OpenSCAD build with the Manifold backend. On the current
Mac, all five previews take only a few seconds. It does not regenerate STLs,
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

The deck aperture is clipped behind the 1 mm front wall. Without this limit,
its tilted cutter removed the front fascia and exposed the PCB edge. The low
front preview checks that the shell closes beneath the deck.

Caps and SI/SO indicator lenses are included in the assembled and exploded views,
attached to their fixed deck carriers. `caps_led_on` and `siso_led_on` select static
lit colors; OpenSCAD does not simulate emitted light or emulator state. Both lenses
remain visible when off. Their positions and provisional 4 mm spherical shape
match the existing browser model; they were previously browser-only additions.
The shared full-machine SCAD assembly includes them too. Browser export still
leaves these separate lenses to the runtime, avoiding duplicate geometry.

The underside cable opening has two opposing folded rubber strips, with the
short metal edges exposed, following owner photo `PXL_20261009_133005363.jpg`.
It is not a four-sided boot like the monitor outlet. Use
`python3 render.py --view underside` to inspect this detail.

The light shell now ends at a straight, open lower rim above the separate bottom
lid, with six individual screw tabs. Inside photos `PXL_20261012_123048886.jpg`
and `PXL_20261012_123907435.jpg` establish this construction. The previous
spherical rounding rolled the shell underneath and is removed. Plan corner
bend radius is approximately 5 mm, while the top-to-wall bend is approximately
1 mm per owner feedback; tab dimensions and the 0.2 mm lid seam remain modeling estimates.
The light shell walls, sloped skin, rear ledge and lid tabs use the owner’s
approximately 1 mm sheet thickness. The separate bottom lid is also 1 mm thick, per owner confirmation.
The shell rim and mounting tabs sit at 1.2 mm, preserving the estimated 0.2 mm seam.

The black deck has a rolled top perimeter rather than a sharp extruded edge:
approximately 6 mm plan corners and a 2 mm top-edge radius, visually fitted to
owner photos `PXL_20261012_123006039.jpg` and `PXL_20261009_132919894.jpg`.
These black-deck radii are estimates, separate from the light sheet-metal shell’s
5 mm corner bends and approximately 1 mm top bend / sheet thickness.

Owner correction: the black deck is an open folded **1 mm sheet**, with a
uniform **8 mm** skirt height and a **1 mm** gap above the light base. Its top
and bottom planes are parallel (both follow the keyboard tilt); it is not a
wedge. The deck top and key mechanism datum stay in place while the skirt
extends downward. The light base is trimmed to the parallel seating plane.
The outer 2 mm / inner 1 mm top bends preserve 1 mm material thickness.
