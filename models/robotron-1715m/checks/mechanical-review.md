# Mechanical evidence review — canonical v48

Reviewed 2026-10-16 against the owner's photographs. [Annotated photographs](mechanical-review.html) and [regenerated current-model comparisons](photo-comparisons/index.html) are the review artifacts. No geometry changes were justified by this pass; no printed-and-verified status changed.

| Area | Evidence and result | Boundary |
|---|---|---|
| Keyboard PCB supports | Owner 123106382 shows separate bent leaves; matrix/controller support and fastener intersections pass | Hidden attachments and bends remain estimates |
| Cable and rubber | Owner 123539882 shows two-flange grommet, restraint and shield termination; cable/board/chip/clamp and rubber/support intersections pass | Cable flex and contact force unmeasured |
| Motherboard mounts | 072654600 identifies one open hole and one occupied hole; `mounting-audit.json` retains each classification | Two legacy right-side mounts remain obscured and unverified |
| Drive adapter | Owner 150520316 underside and existing planar comparison retain opposed holes and ribbon exit | Fitted points are not independent dimensional validation; unseen spacers unresolved |
| Package clearance | `check-pcb-interfaces.py` passes 138 packages; nominal lead/board/socket interfaces checked | Artwork and nominal package pitch do not establish circuit continuity |
| Cover fit | System lid/base, keyboard shell/bottom and monitor upper/lower intersections are zero | Touching permitted; not a tolerance-stack, fastening or manufacturing fit test |

`check-assembly.py`: **54 selected pairs pass**, intersection tolerance 0.001 mm³. `check-covers.py`: **3 cover pairs pass**. Reports: [assembly.json](assembly.json), [covers.json](covers.json). Only the listed pairs are checked. Moving cable shapes, fastening preload, thermal clearances and hidden joints are outside scope.

The keyboard comparison had stale generated geometry and was regenerated from the current canonical model. Planar overlays collapse depth: their pixel residuals must not be reported as millimetre tolerances. The fan view has no independent holdouts; drive-adapter landmarks participate in fitting. Keep these distinctions when using comparisons to propose future edits.

Reproduce from repository root:

```sh
python3 models/robotron-1715m/tools/check-pcb-interfaces.py
python3 models/robotron-1715m/tools/check-assembly.py
python3 models/robotron-1715m/tools/check-covers.py
python3 models/robotron-1715m/tools/compare-photos.py
```
