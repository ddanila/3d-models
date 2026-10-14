# Danila’s Robotron 1715M

The canonical OpenSCAD source for Danila’s museum machine and the DAC browser export. Geometry uses millimetres: X right, Y rear, Z up. Open [model.scad](model.scad) for the complete machine, or [keyboard/model.scad](keyboard/model.scad) for fast colored keyboard review. Select a named `part` to export it independently.

## Current reconstruction

The exterior follows Danila’s photographs, with clean paint, plastic, rubber and metal rather than full-panel photo skins or copied wear. Small manufacturer labels use credited local photo crops. The keyboard’s approved exterior dimensions and separate sheet-metal layers are documented in the [keyboard workflow](keyboard/README.md). Interior dimensions remain provisional unless explicitly measured.

The system unit has a W/M motherboard with integrated A44 U8272 and 32 RAM packages, plus a separate display controller mounted component-side down. [board-layout.json](board-layout.json) records the shared placement, sources and uncertainty. There are 106 nominal KiCad DIP packages and 2,082 lead apertures. R19/R102 and C90/C91 follow the documented CPU/DMA adjacency, with estimated positions and no invented electrical values. Unidentified footprints retain generic labels. Clean chip legends identify documented devices; illustrative copper routes are not a netlist.

Owner photographs establish the drive adapters, their two mounting holes, cover stiffeners, fan retention and PSU access cover. The fan now has five swept blades and a broader hub matching the visible specimen; blade curvature remains estimated. Ribbon plugs now enter the pale adapter sockets; the fan aperture is concentric with the rotor/frame. The display controller’s visible board number does not prove an exact schematic revision match. Hidden monitor electronics remain comparative, and enclosed PSU electronics are not reconstructed.

The family manual gives nominal envelopes of 500 × 400 × 130 mm (system), 320 × 350 × 330 mm (monitor including stand), and 500 × 200 × 40 mm (keyboard). These are family specifications, not new measurements of this specimen. See the [original manual, printed p.35](https://xepb.org/robotron/docs/pc_manu.pdf#page=36) and [W drawings](https://xepb.org/robotron/docs/1715w.zip). The [TEAC specification](https://www.bitsavers.org/pdf/teac/FD-55FV-13_Specification_Rev_E.pdf) documents 2.54 mm signal-contact pitch; adapter-board dimensions remain estimated.

## Evidence and verification

[Evidence categories](evidence.json) distinguish **your specimen**, **documented W/M design**, and **comparative estimate**. Physical status is separate: photographs and visual approval never confer **printed and verified**. The repository’s model-status registry is authoritative. These assembled electronics remain physically unverified.

Owner photographs and original work are MIT. Imported KiCad packages retain their licences/design exceptions and notices; archived third-party photographs retain their original rights. See [KiCad notices](components/kicad/NOTICE.txt), [comparative board history](reference/comparative-1715-boards.json), and the reference-directory notices. The keyboard EPROM was transplanted from another board; its appearance does not establish a firmware dump identity.

## Repeatable review

- [Photo / exported mesh / overlay comparisons](checks/photo-comparisons/index.html): fan and adapter, generated from [stored landmarks](photo-alignment.json). Open locally in a browser. Planar projection flattens depth; fitted anchors and adjusted hole residuals are review aids, not independent dimensional validation.
- [Assembly fit report](checks/assembly.json): plug/socket plastic, fan/frame and airway, board mounting holes, boards/bracket/shield, and discrete-component/chip-body clearance. Only the listed pairs are checked; touching surfaces are permitted. Contacts entering plugs are intentional.
- [Drive motion report](checks/mechanics.json): all 80 modeled head positions against the fixed mechanism. It does not certify every linkage or physical tolerance.
- [Historical development notes](HISTORY.md): dated decisions and superseded layouts, kept out of the current specification.

## Rebuild and publish

Requires Python 3 and OpenSCAD with the Manifold backend. From the repository root:

```sh
python3 models/robotron-1715m/tools/configure-pcb.py
python3 models/robotron-1715m/tools/export.py
python3 models/robotron-1715m/tools/check-assembly.py
python3 models/robotron-1715m/tools/compare-photos.py
python3 models/robotron-1715m/tools/export-downloads.py
openscad --backend Manifold --export-format binstl -o models/robotron-1715m/robotron-1715m.stl models/robotron-1715m/model.scad
python3 models/robotron-1715m/tools/package-assembly.py
python3 scripts/model-status.py
```

Use `export.py --parts NAME ...` for a bounded mesh rebuild; it refreshes manifest hashes. Run `configure.py` when changing the keyboard configuration. The [combined STL ZIP](robotron-1715m.stl.zip) is a visual assembly reference; per-assembly downloads preserve sources. STL does not preserve OpenSCAD colors.

After committing canonical changes, run `python3 scripts/sync-robotron-model.py ../3d-models` in DAC. It verifies hashes and records the exact source commit. Firmware and emulator code stay in their own repository. DAC loads keyboard, monitor and each logic board on demand and shares repeated package geometry.
