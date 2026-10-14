#!/usr/bin/env python3
"""Generate keyboard package paths and footprints from the pinned KiCad library."""
from pathlib import Path
import json
root=Path(__file__).resolve().parents[1]
models=json.loads((root/'components/kicad/models.json').read_text())
rows=[]
for m in models:
    if m['pins'] not in [14,16,20,24,40]: continue
    rows.append([m['pins'],m['meshes']['body']['file'],m['meshes']['leads']['file'],
        [[y,-x] for x,y in m['footprint']],m['bodyHeight']])
(root/'controller-package-data.scad').write_text('// Generated: pinned KiCad packages rotated -90 degrees; see NOTICE.\ncontroller_packages='+json.dumps(rows)+';\n')
print('Keyboard packages and footprints:',len(rows))
