# Mechanical review and evidence limits

Use the [annotated photographs](mechanical-review.html) and
[planar comparisons](photo-comparisons/index.html) to review geometry against its
sources. Current configurations, checked pairs and results belong in the linked
reports; implementation history belongs in git.

| Question | Evidence | Boundary |
| --- | --- | --- |
| Do nominal assembled solids intersect? | [Assembly](assembly.json), [covers](covers.json) and `check-pcb-interfaces.py` | Only listed interfaces; touching is allowed. No tolerance-stack, contact-force or manufacturing-fit proof |
| Which motherboard mounts are supported? | [Mounting audit](mounting-audit.json) | Obscured mounts and hidden attachments remain unverified |
| Do inspection paths clear surrounding solids? | [Motion report](inspection-motion.json), [chart](inspection-motion.svg), [path definitions](../inspection-paths.json) | Sampled poses, not continuous swept volumes or a physical disassembly procedure |
| Which geometry has source attribution? | [Evidence rules](../evidence-map.json), [coverage audit](evidence-coverage.json) | Source coverage is not dimensional verification or printed-fit approval |
| Which parts move together? | [Relationships](../relationships.json), checked by `check-metadata.py` | Mechanical groups do not certify wiring, threads or hidden joints |

Photo fits may use the same points that establish placement. The fan comparison
has no independent holdouts; drive-adapter landmarks participate in fitting.
Planar overlays collapse depth, so pixel residuals cannot be reported as
millimetre tolerances. Hidden bends, supports and socket engagement remain estimates.

Controller bank and axial bodies can be photo-supported visual geometry without
numbered pads. The assembly audit checks their nominal clearances, not hidden
lead entries or electrical continuity. Use the
[controller guide](../keyboard-controller/README.md) for that distinction.

Inspection paths stage covers and boards to clear modeled contents. They do not
establish fastener removal, available cable slack, preload or a physical opening
sequence. `monitor-cable-paths.json` preserves CAD rest centre lines; the museum's
animated deformation is illustrative. Its separate cable audits cover selected
poses and retain exceptions, not all-parts collision or strain certification.

Reproduce from repository root:

```sh
python3 models/robotron-1715m/tools/check-pcb-interfaces.py
python3 models/robotron-1715m/tools/check-assembly.py
python3 models/robotron-1715m/tools/check-covers.py
python3 models/robotron-1715m/tools/compare-photos.py
python3 models/robotron-1715m/tools/check-inspection-motion.py
python3 models/robotron-1715m/tools/audit-evidence.py
```
