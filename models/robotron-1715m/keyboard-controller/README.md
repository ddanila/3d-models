# Keyboard controller reconstruction

The native KiCad files describe the reference circuit and a partial reconstruction
of the museum board. Physical routing, dimensions, discrete pin mapping and
specimen timing remain incomplete. The board is not fabrication-ready.

## Review

Open `assembly-review.scad` for the detailed museum controller. Press F5 and Home;
set `side="bottom"` for its underside. `show_mounts` and `show_shield` restore the
surrounding hardware. `review.scad` shows the native electrical geometry separately.
Cyan artwork is unassigned and makes no connectivity claim.

Open `controller.kicad_pro` in KiCad 10 to edit the electrical reconstruction.
Unplaced components are parked outside the outline. The nominal board size is
270 × 46 mm; this is not a specimen measurement. Board exports use millimetres
and a common top-view frame; transforms and conventions are in `generated/layout.json`.

## Authorities

| Information | Editable source / generated review |
| --- | --- |
| Components, numbered pins and nets | `controller.kicad_sch`, local `kbd.kicad_sym`; `generated/connectivity.json` |
| Outline, footprints, holes and copper | `controller.kicad_pcb`; `generated/layout.json` and `generated/controller.scad` |
| Source provenance, variants and unresolved interpretations | `evidence.json`, `component-evidence.json` |
| Photo observations and registration | `photo-landmarks.json`, `bottom-landmarks.json`; generated registration JSON/SVG |
| Route provenance tied to native geometry | `route-evidence.json` |
| Assembly and mechanical estimates | `../specimen-details.scad` |
| Current ERC/DRC findings and export hashes | `generated/qualification.json`, `generated/manifest.json` |

Keep derived inventories in these artifacts. Git history records implementation
changes; this guide records the workflow and interpretation limits.

## Evidence boundaries

The primary museum board and comparison photographs are distinct specimens.
`evidence.json` pins their sources, markings and hashes. Comparison photographs
can clarify construction but require independent registration and an explicit
routing comparison before transferring geometry. The museum ROM was replaced;
its contents remain unread. A comparison ROM label does not identify either dump.

The Zander circuit is the digital reference. Published WR/RD and oscillator
variants remain separate in `referenceVariants`; do not combine them to fit the
emulator. Factory placement drawings establish reference identities where visible.
The matrix and lamps beyond X1 are external to the controller reconstruction.

Top-photo fits and bounded local underside fits support placement review. Global
underside registration remains unqualified. Raised leads and sockets can hide hole
centres; a successful local fit cannot establish copper attachment or board scale.
Superseded CPU clock and BR2 interpretations remain in `evidence.json:routeReviews`.
No withdrawn CLK assignment is restored merely because nearby traces align.

Transistor body observations in `component-evidence.json:visualBodyCandidate`
produce `controller_visual_transistors` only while the corresponding native parts
are unplaced. These named photo estimates replace the anonymous visual list.
Their body axes are projected from primary-photo observations; height, flat-face
polarity, illustrative holes and leads do not assign electrical pads. Native placement still requires individual lead identification.

The L3/12 body dimensions come from pinned SC236/SC308 device drawings in
`packageReferences`. SC308 has a centre emitter; SC236 has a centre base.
Drawing-view terminal order does not establish installed orientation. Imported
TO-92 assets retain their original credits even though these bodies no longer
use them. R6.4/R6.5 lead-end candidates likewise do not establish hidden holes.

BR1 separates oscillator and CPU clock; BR2 separates reset source and CPU reset.
Their terminal numbers are reconstruction identifiers. Virtual bridge isolation
is tested digitally, but the reviewed sources do not prescribe physical bridge
opening. Closed-link continuity alone cannot establish source-side terminal order.

Every native copper UUID requires an observed, inferred or unresolved review,
source hashes, a locator and `geometrySha256`. Geometry or net changes invalidate
the review. Observed tracks require their side's photo; observed vias require both
sides. This enforces provenance completeness, not the truth of an interpretation.
Unassigned photo artwork is not electrical copper.

## Regenerate and check

From this directory, use Python with KiCad's `pcbnew` module for native export
and integration tests. Set `KICAD_CLI` if necessary. On macOS:

```sh
/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 tools/export.py
/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 tools/test_kicad.py
python3 tools/export.py --check
python3 tools/test_export.py
python3 tools/photo_registration.py
```

`photo_registration.py --apply --refs A1 ...` applies explicitly selected fits
only after independent landmarks pass. Regenerate exports after applying fits.
The native test checks repeatability, curved tracks, through vias and pad/net
mismatch rejection. Standard-Python freshness checks run in CI; native KiCad
integration is a separate local check. Unsupported zones, blind vias, internal
tracks and invalid outlines fail explicitly. ERC's RD_N and SHIELD exceptions
are recorded individually; outstanding DRC findings remain failures.

After geometry changes, use `../tools/export.py --parts` with the affected part
names, refresh all controller mesh receipts when shared SCAD inputs change, then
run `../tools/test_controller_mesh_contract.py`, `../tools/export-downloads.py`
and `../tools/check-metadata.py`. Review both sides before accepting new baselines.
Commit CAD before running the museum sync scripts; they reject dirty or stale
sources. Compatible revisions belong in the museum source manifests.

Digital comparisons and specimen evidence collection are documented in the
museum's `docs/robotron/keyboard-controller-progress.md` and
`keyboard-controller-verification.md`. Logical reference agreement does not
qualify analog behavior, exact CPU cycle timing or specimen firmware.
