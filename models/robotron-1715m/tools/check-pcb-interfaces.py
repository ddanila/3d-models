#!/usr/bin/env python3
"""Nominal package/footprint audit; no assertion about hidden specimen wiring."""
import json,math
from pathlib import Path
root=Path(__file__).resolve().parents[1]
data=json.loads((root/'pcb-components.json').read_text())
models={m['id']:m for m in data['models']}; rows=[]
for board in data['boards']:
 for component in board['components']:
  model=models[component['model']];a=math.radians(component['rotation']);x,y,z=component['position'];side=component['side']
  holes=[p for p in data['footprints'] if p[3]==board['name']]
  distances=[]
  for px,py in model['footprint']:
   py*=side;wx=x+px*math.cos(a)-py*math.sin(a);wy=y+px*math.sin(a)+py*math.cos(a)
   distances.append(min(math.dist((wx,wy,z),p[:3]) for p in holes))
  instance=next(p for p in data['instances'] if p['board']==board['name'] and p['ref']==component['ref'])
  lift=component.get('socketHeight',0)
  pose_ok=abs(instance['position'][2]-(z+side*lift))<1e-6 and instance['rotation']==component['rotation']
  rows.append(dict(board=board['name'],ref=component['ref'],model=model['id'],pins=model['pins'],rotation=component['rotation'],socketHeight=lift,maxLeadToHoleErrorMm=max(distances),passed=max(distances)<.01 and pose_ok and len(distances)==model['pins']))
report=dict(scope='Nominal DIP lead/hole XY and board-face Z, socket lift, package rotation consistency. Pin-one orientation still requires individual specimen evidence; this is not electrical or physical verification.',packages=len(rows),passed=all(r['passed'] for r in rows),results=rows)
(root/'checks/pcb-interfaces.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS' if report['passed'] else 'FAIL',len(rows),'package interfaces')
if not report['passed']:raise SystemExit(1)
