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

Photos establish the two drives, 14 front vents, side vent banks, front switches, separate keyboard key groups, translucent function caps, red CE key, monitor bezel and blue tape, and keyboard underside. Wall thickness, curves, seams, feature locations and colors remain estimates. The keyboard layout represents 97 visible key positions. Keycaps are exported as seven reusable OpenSCAD profiles and instanced individually in the browser so the entire cap moves when pressed. Blank fillers and some indicator hardware remain incomplete. Case rear connectors, system-unit underside, internal electronics and monitor rear details are unverified and intentionally incomplete. The documentation archive also contains electrical schematics; these are not dimensioned enclosure drawings. Its older 1715 schematics must not be mistaken for 1715M/W schematics.

Sources: [documentation index](https://xepb.org/robotron/docs.html), [manual](https://xepb.org/robotron/docs/pc_manu.pdf), [service manual](https://xepb.org/robotron/docs/pc_serv.pdf). Historical documents retain their original rights and are linked, not relicensed or bundled.

## Reference photos and consistent materials

`reference/photos.json` records the source archive and original/published SHA-256 hashes. `reference/photos/` contains losslessly sanitized JPEGs: EXIF, XMP, IPTC, comments and trailing motion video were removed, with decoded pixels checked against the originals. The original download was not modified. To reproduce sanitization after extracting the archive, run `python3 tools/import-photos.py /path/to/extracted/photos` from this model directory (requires Pillow).

OpenSCAD/STL stores geometry, not photographic materials. `browser/model.json` version 3 adds material profiles, transcribed legends, a small wordmark decal, reference-photo links, a live screen anchor and individually named power/reset meshes.

Full-panel photo skins are no longer used. The old underside crops contained a photographed cable and feet in addition to the modeled ones; removing them eliminates those duplicates and their baked shadows. There is now one continuous Bézier-routed lead, a modeled grommet, a hollow keyboard shell with a separate bottom plate, four rubber foot frames with metal inserts, six perimeter fasteners and a detailed exterior plug. The two drive fronts have recessed insertion slots/finger wells, rounded latch handles and separate red lenses. The monitor tape is a thin solid. Keycaps have square skirts, rounded shoulders and dished tops, including a stretched dish for long caps.

The palette and finish are visually estimated from the photographs, not colorimetrically calibrated. Browser paint, plastic, rubber, metal, lens and glass materials react to scene lighting; subtle procedural grain uses model-space millimetres, avoiding large repeated photo patches, seams and baked illumination. The fine grain is an approximation of the observed finish, not a photographic sample. Surface normals are smoothed with creases preserved. The original small `robotron 1715 M` wordmark remains a masked photo crop; it contains no modeled physical feature. Drive arrows and control labels are reconstructed markings. Key legends are transcribed into a transparent atlas placed on the dish surface; font shapes are approximations, not scans. Blank Shift/Space/Caps key tops remain blank. Input support is still separate from the visible legends.

The owner JPEGs and their original UV landmarks remain reference evidence, with no repainted or generated photograph pixels. Exact wear/scratches, clear keycap construction, cable route, connector dimensions and unseen hardware remain approximate. The model is a coherent reconstruction, not a scan of every mark on the specimen.

## Rebuild

Requires Python 3 and OpenSCAD with the Manifold backend (tested with 2026.10.05). From the repository root:

```sh
python3 models/robotron-1715m/tools/configure.py
python3 models/robotron-1715m/tools/export.py
openscad --backend Manifold --export-format binstl -o models/robotron-1715m/robotron-1715m.stl models/robotron-1715m/model.scad
openscad --backend Manifold -o models/robotron-1715m/preview.png --imgsize=1600,1200 --viewall --autocenter models/robotron-1715m/model.scad
```

`tools/configure.py` generates the shared keyboard geometry/UV table. `tools/export.py` exports 28 body/detail meshes and seven reusable keycap profiles with their hashes. `part="keycap"` and `key_index` select a local, origin-centred cap for export; assembly geometry stays fully assembled. The DAC repository imports the export with `python3 scripts/sync-robotron-model.py ../3d-models`, recording the source commit and checking hashes. Firmware and emulator code stay in their own repositories.

## Interaction metadata and keyboard evidence

`keyboard-layout.json` supplies stable IDs, physical positions, photo-reference landmarks, transcribed legends and the museum input adapter. The [original manual, printed pp.9–11](https://xepb.org/robotron/docs/pc_manu.pdf#page=10) supplies Tab, Insert/Delete, function-key and numeric-keypad codes; cursor directions agree with the existing core adapter. Numeric-pad digits have distinct codes, not ordinary ASCII digits. ET uses API input 13, translated by `robotron_key()` to the documented keyboard byte 9E. No historical document or firmware is bundled under this model’s MIT license.

89 positions have input behavior, including Shift/Ctrl/Caps Lock. ALT, ß, repeat R, SI/SO and four navigation symbols are explicitly unverified. Unverified shifted symbols also send no invented byte. Shift/Ctrl are visitor-side one-shot latches; Caps Lock is persistent until released or focus/reset/power changes. The browser’s Caps Lock lamp reflects that local input state, not feedback from the original keyboard controller. SI/SO’s alternate character-set protocol is not available through the current browser core API.

The first drive lamp reflects the core’s aggregate disk-transfer counter (only one disk is mounted); it does not claim to reproduce drive-select or motor timing. The assembly view separates exterior components for inspection. It does not invent boards or wiring inside the empty enclosure. The external cable route and monitor-glass curvature remain estimates.
