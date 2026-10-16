#!/usr/bin/env python3
"""Cheap consistency check; no OpenSCAD or browser required."""
import hashlib,json,re,zipfile
from pathlib import Path
root=Path(__file__).resolve().parents[1]
def read(p):return json.loads((root/p).read_text())
pcb=read('pcb-components.json');model=read('browser/model.json')
for name in ['specimen-details.scad','keyboard-controller/generated/controller.scad','controller-package-data.scad']:
 assert model.get('keyboardControllerSource',{}).get(name)==hashlib.sha256((root/name).read_bytes()).hexdigest(),'stale controller browser meshes: '+name
counts={'packages':len(pcb['instances']),'leadHoles':len(pcb['footprints'])}
assert model['pcbComponents']==pcb,'stale browser PCB metadata'
assert model['hardwareAudit']==read('hardware-audit.json'),'stale hardware evidence'
assert model['evidence']==read('evidence.json'),'stale evidence labels'
assert model['componentCounts']==counts,'stale component counts'
text=f"<!-- pcb-counts -->{counts['packages']} nominal KiCad DIP packages and {counts['leadHoles']:,} lead apertures<!-- /pcb-counts -->"
assert text in (root/'README.md').read_text(),'stale README counts'
for item in model['parts']+model['keyMeshes']+read('browser/downloads.json'):
 p=root/'browser'/item['file'];blob=p.read_bytes()
 assert hashlib.sha256(blob).hexdigest()==item['sha256'],str(p)+' checksum mismatch'
 if 'bytes' in item:assert len(blob)==item['bytes'],str(p)+' size mismatch'
for item in read('browser/downloads.json'):
 with zipfile.ZipFile(root/'browser'/item['file']) as z:
  for name in ['board-layout.json','pcb-components.json','hardware-audit.json','README.md','interior.scad','model.scad','pcb-components.scad']:
   assert z.read('source/'+name)==(root/name).read_bytes(),item['name']+': stale '+name
  wrapper=z.read('model.scad').decode()
  if item['name']=='motherboard':
   for name in ['logic-ic-sockets','logic-ic-contacts','logic-jumpers','logic-visible-lands']:
    assert 'shape("'+name+'")' in wrapper,'missing downloadable geometry '+name
names={p['name'] for p in model['parts']}
for group in read('relationships.json')['groups']:
 assert group['kind']=='mechanical', 'relationship must not imply an unverified electrical net'
 assert set(group['members'])<=names, group['title']+': unknown model part'
 assert (root/'reference/photos'/('PXL_'+group['photo']+'.jpg')).is_file(),group['title']+': missing source photo'
scad=(root/'monitor-cables.scad').read_text()
for name,lead in read('monitor-cable-paths.json')['leads'].items():
 block=scad.split('module '+name.replace('-','_')+'() {')[1].split('\n}')[0]
 curves=json.loads(block.split('monitor_lead(')[1].rsplit(',',1)[0].strip())
 assert curves==lead['curves'],name+': centerline differs from canonical SCAD'
print('PASS counts, evidence, meshes and self-contained download sources')
