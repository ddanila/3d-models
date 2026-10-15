#!/usr/bin/env python3
"""Generate shared OpenSCAD/browser W/M packages and holes from board-layout.json."""
import json,math,re
from pathlib import Path
root=Path(__file__).resolve().parents[1]
layout=json.loads((root/'board-layout.json').read_text())
models=json.loads((root/'components/kicad/models.json').read_text());lookup={m['id']:i for i,m in enumerate(models)}
instances=[];passives=[];footprints=[];mounts=[];connectors=[];sockets=[]
def pins(position,angle,side,points,board):
 a=math.radians(angle)
 for x,y in points:
  y*=side
  footprints.append([position[0]+x*math.cos(a)-y*math.sin(a),position[1]+x*math.sin(a)+y*math.cos(a),position[2],board,side])
for b in layout['boards']:
 name=b['name']
 for c in b['components']:
  m=models[lookup[c['model']]]
  position=list(c['position']);position[2]+=c.get('socketHeight',0)*c['side']
  instances.append(dict(c,position=position,id=name+'-'+c['ref'],board=name,top=m['bodyHeight'],markings=False))
  if c.get('socketHeight'):sockets.append([c['position'],c['rotation'],name,c['side'],m['rowSpacing'],m['pins'],c['socketHeight'],m['footprint']])
  pins(c['position'],c['rotation'],c['side'],m['footprint'],name)
 for c in b['passives']:
  passives.append([c['kind'],c['position'],c['rotation'],[0,0],name,c['diameter'],c['height'],c['side']])
  pitch=9 if c['kind']=='resistor' else 2.5
  pins(c['position'],c['rotation'],c['side'],[[0,-pitch/2],[0,pitch/2]],name)
 for c in b['connectors']:
  if c.get('hidden'):continue
  connectors.append([c['position'],c['n'],c['rotation'],name,c['side']])
  pins(c['position'],c['rotation'],c['side'],[[x,(i-(c['n']-1)/2)*2.54] for x in [-1.27,1.27] for i in range(c['n'])],name)
 for i,(x,y) in enumerate(b['mounts']):mounts.append([x,y,1 if name=='motherboard' else 13.6,b['origin'][2]+1.6,name,b.get('mountEvidence',[{}]*len(b['mounts']))[i].get('occupied',True)])
data=dict(version=4,boards=layout['boards'],sources=layout['sources'],limitations=layout['limitations'],mounts=mounts,models=models,instances=instances,footprints=footprints,credit='KiCad DIP models: Maurice (easyw), see components/kicad/NOTICE.txt. Layout: original Robotron W drawings and Danila’s MIT owner photographs; dimensions and exact revision remain provisional.',licence='See each model licence: GPL-3.0-or-later with design exception, or CC-BY-SA-4.0 with KiCad exception.',sourceRevision=json.loads((root/'components/kicad/sources.json').read_text())['revision'])
(root/'pcb-components.json').write_text(json.dumps(data,indent=2)+'\n')
arrays=dict(pcb_visible_lands=layout['motherboardArtwork'].get('lands',[]),pcb_component_models=[[m['meshes']['body']['file'],m['meshes']['leads']['file']] for m in models],pcb_component_instances=[[lookup[p['model']],p['position'],p['rotation'],p['board'],p['side']] for p in instances],pcb_jumpers=layout["motherboardJumpers"]["position"],pcb_sockets=sockets,pcb_mounts=mounts,pcb_footprints=footprints,pcb_passives=passives,pcb_connectors=connectors,pcb_boards=[[b['name'],b['origin'],b['size']] for b in layout['boards']],pcb_motherboard_routes=layout['motherboardArtwork']['paths'],pcb_motherboard_markings=[[v['text'],v['position'],v['height'],v['rotation']] for v in layout['motherboardArtwork']['markings']],pcb_ribbon_socket=layout['boards'][0]['connectors'][1]['position'],pcb_display_routes=layout['displayRoutes'])
(root/'pcb-components.scad').write_text('// Generated from board-layout.json; nominal packages, estimated layout.\n'+''.join(k+'='+json.dumps(v)+';\n' for k,v in arrays.items()))
print(len(instances),'W/M packages;',len(footprints),'lead holes')

readme=root/'README.md'
text=f"<!-- pcb-counts -->{len(instances)} nominal KiCad DIP packages and {len(footprints):,} lead apertures<!-- /pcb-counts -->"
readme.write_text(re.sub(r'<!-- pcb-counts -->.*?<!-- /pcb-counts -->',text,readme.read_text()))
