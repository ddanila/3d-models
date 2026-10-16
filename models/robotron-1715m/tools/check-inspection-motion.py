#!/usr/bin/env python3
"""Sample museum inspection translations; never infer physical disassembly fit."""
from pathlib import Path
import json, subprocess, tempfile, struct, html
root=Path(__file__).resolve().parents[1]
def volume(path):
 b=path.read_bytes();total=0
 for i in range(struct.unpack_from('<I',b,80)[0]):
  a,c,d=[struct.unpack_from('<3f',b,84+i*50+12+j*12) for j in range(3)]
  total+=a[0]*(c[1]*d[2]-c[2]*d[1])+a[1]*(c[2]*d[0]-c[0]*d[2])+a[2]*(c[0]*d[1]-c[1]*d[0])
 return abs(total/6)
cases=[('system-lid','case_lid();','case_base();',[0,400,180]),('monitor-upper','monitor_upper();','union(){monitor_lower();monitor_joint_lip();}',[0,-210,155]),('keyboard-controller','union(){keyboard_controller_board();keyboard_controller_chips();keyboard_controller_ceramic();keyboard_controller_rom_cover();keyboard_controller_connectors();keyboard_controller_caps();keyboard_controller_metal();}','keyboard_shell();',[0,160,70]),('keyboard-matrix','keyboard_pcb();','keyboard_shell();',[0,0,22])]
cases.append(('controller-matrix',cases[2][1],'keyboard_pcb();',[0,160,70]))
cases += [
 ('system-contents','union(){case_lid();case_lid_inserts();case_lid_fixings();fascia();}','union(){psu_cover();psu_chassis();fan_frame();logic_boards();logic_connectors();}',[0,400,180]),
 ('monitor-contents','monitor_upper();','union(){tube_funnel();tube_neck();monitor_yoke();monitor_chassis();monitor_boards();monitor_components();monitor_capacitors();monitor_shield();}',[0,-210,155]),
]
paths=json.loads((root/'inspection-paths.json').read_text())
def offset(name,t,delta):
 name={'system-contents':'system-lid','monitor-contents':'monitor-upper'}.get(name,name);points=paths.get(name,[[0,0,0],delta]);u=t*(len(points)-1);i=min(int(u),len(points)-2)
 return [round(a+(b-a)*(u-i),5) for a,b in zip(points[i],points[i+1])]
results=[]
with tempfile.TemporaryDirectory() as tmp:
 for name,moving,fixed,delta in cases:
  for step in range(41):
   t=step/40;position=offset('keyboard-controller' if name=='controller-matrix' else name,t,delta)
   stationary=f'translate({offset("keyboard-matrix",t,[0,0,22])}){{{fixed}}}' if name=='controller-matrix' else fixed
   src=Path(tmp)/'check.scad';out=Path(tmp)/'check.stl';out.unlink(missing_ok=True)
   src.write_text(f'include <{root}/model.scad>\nintersection(){{translate({position}){{{moving}}}{stationary}}}')
   run=subprocess.run(['openscad','--backend','Manifold','--export-format','binstl','-D','part="audit"','-o',str(out),str(src)],capture_output=True,text=True)
   if run.returncode and 'Current top level object is empty' not in run.stderr:raise RuntimeError(run.stderr)
   v=volume(out) if out.exists() else 0;results.append(dict(part=name,fraction=t,translationMm=position,intersectionMm3=round(v,6),clear=v<.001));print(name,t,round(v,6),flush=True)
report=dict(scope='287 sampled translations every 2.5% (keyboard layers, matrix and controller follow canonical staged waypoints) between museum inspection poses. System and monitor covers now animate along these canonical translations in DAC. Keyboard separation remains staged. Added cover attachments against PSU/logic solids and monitor upper cover against tube/chassis/components. These are museum translations, not physical hinges. Tests named moving solids against their enclosure and controller against the concurrently moving matrix, including controller packages/connectors/leads; touching allowed. Fasteners must be removed for physical disassembly. Cable deformation is qualified separately in DAC cable-geometry.spec.js at 21 positions in connected/parked modes; available physical slack remains unmeasured.',toleranceMm3=.001,results=results,allSamplesClear=all(r['clear'] for r in results))
(root/'checks/inspection-motion.json').write_text(json.dumps(report,indent=2)+'\n')
svg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 540"><rect width="1000" height="540" fill="#182329"/><g fill="white" font-family="sans-serif"><text x="20" y="30" font-size="21">Inspection translation clearance · sampled every 2.5%</text>'
for row,(name,*_) in enumerate(cases):
 y=95+row*55;svg+=f'<text x="20" y="{y+19}">{name}</text>'
 for point in [r for r in results if r['part']==name]:
  x=220+point['fraction']*700;colour='#67cc9a' if point['clear'] else '#f17b69';svg+=f'<rect x="{x}" y="{y}" width="14" height="28" fill="{colour}"><title>{point["fraction"]:.0%}: {point["intersectionMm3"]} mm³</title></rect>';svg+=(f'<text x="{x}" y="{y-5}" font-size="11">{point["fraction"]:.0%}</text>' if round(point["fraction"]*40)%4==0 else '')
svg+='<text x="20" y="520">Green: below 0.001 mm³. Red: intersection. Samples do not certify continuous physical fit.</text></g></svg>'
(root/'checks/inspection-motion.svg').write_text(svg)
print('Clear:',report['allSamplesClear'])
