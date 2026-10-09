# Danila’s Robotron 1715M

Parametric OpenSCAD exterior reconstructed from Danila’s twelve photographs dated 2026-10-09. Original model, scripts and owner photographs are MIT licensed (see LICENSE). This is an editable museum reconstruction, not a scan, manufacturing drawing or validated replacement enclosure.

Open `model.scad` for the assembled system unit, monitor and keyboard. Set `part` to any entry in `parts` to inspect/export it separately. Coordinates are millimetres: X right, Y towards the rear, Z up. The keyboard is placed in front of the computer. `robotron-1715m.stl` is a combined visual reference; the separate exports retain the switch and material boundaries used by the museum.

## Evidence and dimensions

The original [Robotron 1715/1715W manual, printed p.35 (PDF page 36)](https://xepb.org/robotron/docs/pc_manu.pdf#page=36), digitized by U. Zander, lists these nominal envelopes:

| Component | Width | Depth | Height |
| --- | ---: | ---: | ---: |
| System unit | 500 mm | 400 mm | 130 mm |
| Display | 320 mm | 350 mm | 330 mm |
| Keyboard | 500 mm | 200 mm | 40 mm |

These are family specifications, not new measurements of Danila’s specimen. The display height includes its stand; its shell and stand proportions are inferred from the photograph. Small projections and approximate feet can extend beyond nominal envelopes. The monitor insert uses Danila’s existing [measured ring](../robotron-1715m-display-base-ring/): 175 mm OD, 169 mm ID, 5 mm high; its physical fit is still unverified.

The ruler photograph `PXL_20261009_132938614.jpg` provides an independent local scale. In a 1824 × 1373 display of that photo, the 200 and 100 mm ruler ticks are approximately x=405 and x=1380. Six number-row key intervals span approximately 1172 pixels, giving 1172 / 6 / 9.75 ≈ 20.0 mm. The model uses 20 mm pitch. Allow about ±1 mm for hand-picked landmarks, perspective and the ruler lying at a different height from the key centres. This is not submillimetre metrology.

Photos establish the two drives, 14 front vents, side vent banks, front switches, separate keyboard key groups, translucent function caps, red CE key, monitor bezel and blue tape, and keyboard underside. Wall thickness, curves, seams, feature locations and colors remain estimates. The keyboard layout currently represents 97 visible key positions; blank fillers and indicator hardware are not fully reconstructed. Case rear connectors, system-unit underside, internal electronics and monitor rear details are unverified and intentionally incomplete. The documentation archive also contains electrical schematics; these are not dimensioned enclosure drawings. Its older 1715 schematics must not be mistaken for 1715M/W schematics.

Sources: [documentation index](https://xepb.org/robotron/docs.html), [manual](https://xepb.org/robotron/docs/pc_manu.pdf), [service manual](https://xepb.org/robotron/docs/pc_serv.pdf). Historical documents retain their original rights and are linked, not relicensed or bundled.

## Photos and browser skins

`reference/photos.json` records the source archive and original/published SHA-256 hashes. `reference/photos/` contains losslessly sanitized JPEGs: EXIF, XMP, IPTC, comments and trailing motion video were removed, with decoded pixels checked against the originals. The original download was not modified. To reproduce sanitization after extracting the archive, run `python3 tools/import-photos.py /path/to/extracted/photos` from this model directory (requires Pillow).

OpenSCAD/STL stores geometry, not photographic materials. `browser/model.json` adds colors, keycap UV coordinates, photo patches, a live screen anchor and individually named power/reset meshes. The museum maps the original JPEG pixels using these coordinates; no invented/repainted legends or AI textures are used. Keyboard underside photographs include baked lighting and the photographed cable. The drive-face crop is reused for the second drive; that is a reconstruction approximation. Full enclosure photogrammetry and seamless, lighting-corrected textures remain future work.

## Rebuild

Requires Python 3 and OpenSCAD with the Manifold backend (tested with 2026.10.05). From the repository root:

```sh
python3 models/robotron-1715m/tools/configure.py
python3 models/robotron-1715m/tools/export.py
openscad --backend Manifold --export-format binstl -o models/robotron-1715m/robotron-1715m.stl models/robotron-1715m/model.scad
openscad --backend Manifold -o models/robotron-1715m/preview.png --imgsize=1600,1200 --viewall --autocenter models/robotron-1715m/model.scad
```

`tools/configure.py` generates the shared keyboard geometry/UV table. `tools/export.py` exports 18 separate STL meshes and their hashes. The DAC repository imports the export with `python3 scripts/sync-robotron-model.py ../3d-models`, recording the source commit and checking hashes. Firmware and emulator code stay in their own repositories.
