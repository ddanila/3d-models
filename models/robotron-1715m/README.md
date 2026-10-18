# Danila’s Robotron 1715M

Canonical OpenSCAD sources for the museum machine and DAC browser model. Geometry
uses millimetres: X right, Y rear, Z up. Open [model.scad](model.scad) for the machine
or [keyboard/model.scad](keyboard/model.scad) for keyboard review. Select a named
`part` for an independent export.

## Reconstruction and evidence

Owner photographs establish appearance and visible construction. Hidden joins,
board dimensions, cable slack, material properties and mechanical motion remain
estimates unless the evidence explicitly records measurements. Clean geometry
omits wear; small maker-label crops retain their source credits. The enclosed PSU
is not reconstructed, and concealed monitor electronics use comparative evidence.

The [evidence manifest](evidence.json) distinguishes specimen observations,
documented W/M design and comparative estimates. Physical verification is separate:
photographs, visual approval and simulation do not confer **printed and verified**
status. The repository model-status registry owns that classification.

| Review question | Authoritative record or guide |
| --- | --- |
| Which photos, specimens and rights support the model? | [Reference inventories](reference/), [source interpretation](reference-guide.md) |
| Which board identities and placements are supported? | [Board layout](board-layout.json), [hardware audit](hardware-audit.json) |
| How are motherboard photo coordinates registered? | [Observations](board-photo-observations.json), [calibration](checks/board-calibration.json) |
| Which controller pads and routes have electrical evidence? | [KiCad controller guide](keyboard-controller/README.md) |
| Which keyboard dimensions and switch details are measured? | [Keyboard](keyboard/README.md), [keycap](keycap/README.md), [switch](key-switch/README.md) |
| Which interfaces and motion have been checked? | [Assembly](checks/assembly.json), [PCB interfaces](checks/pcb-interfaces.json), [mechanics](checks/mechanics.json) |
| Which assets and sources does the museum consume? | [Browser manifest](browser/model.json), [download receipts](browser/downloads.json) |

Controller KiCad files own numbered pins, nets and reconstructed copper. Other
photo artwork is visual evidence, not a verified netlist. Photo-position IDs do not
necessarily identify schematic references. Package pin-one orientation and hidden
mounts remain provisional where photographs cannot distinguish them.

Owner photographs and original work are MIT. Imported KiCad packages retain their
file-specific licences and exceptions; see [notices](components/kicad/NOTICE.txt).
Third-party photographs and historical documents retain their original rights and
reference-directory notices. Do not replace comparative credits with specimen claims.

## Review

[Stored views](review-views.json) provide reproducible camera poses. From DAC,
start `npm run dev -- --port 4173`, then run:

```sh
node scripts/review-robotron.mjs http://127.0.0.1:4173 /tmp/dac-robotron-review ../3d-models/models/robotron-1715m
```

Open `/tmp/dac-robotron-review/index.html` for photo/render pairs with source and
mesh identities. Review both sides and installed interfaces after geometry changes.
[Planar overlays](checks/photo-comparisons/index.html) provide a separate comparison;
fit residuals do not establish independent dimensional accuracy. Nominal pin pitch
constrains registration but does not measure the specimen's outline.

Assembly and motion reports cover the listed interfaces and sampled poses only.
They do not prove continuous collision freedom, flexible-cable behavior or actual
fit. Separated museum views may stretch cables illustratively; this is not measured
available slack.

## Rebuild and publish

Requires Python 3 and OpenSCAD with the Manifold backend. From the repository root:

```sh
python3 models/robotron-1715m/tools/configure-pcb.py
python3 models/robotron-1715m/tools/export.py
python3 models/robotron-1715m/tools/check-assembly.py
python3 models/robotron-1715m/tools/check-pcb-interfaces.py
python3 models/robotron-1715m/tools/compare-photos.py
python3 models/robotron-1715m/tools/export-downloads.py
python3 models/robotron-1715m/tools/check-metadata.py
openscad --backend Manifold --export-format binstl -o models/robotron-1715m/robotron-1715m.stl models/robotron-1715m/model.scad
python3 models/robotron-1715m/tools/package-assembly.py
python3 scripts/model-status.py
```

Use `export.py --parts NAME ...` for bounded mesh rebuilds. Shared controller SCAD
changes require all consuming meshes and receipts to be refreshed as described in
the [controller guide](keyboard-controller/README.md#regenerate-and-check).
Editable downloads include documentation: regenerate them after changing bundled
source guides, even when geometry is unchanged. STL stores geometry, not colour,
materials or firmware. The combined STL ZIP is a visual assembly reference.

From the model directory, `tools/calibrate-board.py --apply` (NumPy/SciPy) followed
by `tools/configure-pcb.py` updates motherboard photo placement. Do not run legacy
registration scripts over this calibration. `tools/configure.py` updates keyboard
configuration and monitor profile; `tools/configure-keyboard-artwork.py` projects
visual artwork. Controller electrical geometry follows its native KiCad workflow.

After committing canonical changes, run `python3 scripts/sync-robotron-model.py
../3d-models` from DAC. Controller metadata also uses the synchronization steps in
the [museum guide](https://github.com/ddanila/dac/blob/main/docs/robotron/keyboard-controller-progress.md).
Source manifests record compatible revisions. Implementation history belongs in git.
