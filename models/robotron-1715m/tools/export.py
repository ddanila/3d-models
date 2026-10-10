#!/usr/bin/env python3
"""Export OpenSCAD parts plus photo UV metadata for DAC (Python 3, OpenSCAD)."""
import hashlib, json, re, subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[1]
source=(root/'model.scad').read_text()
parts=json.loads(re.search(r'parts=(\[.*?\]);',source).group(1))
colors=json.loads(re.search(r'colors=(\[.*?\]);',source).group(1))
colors=[{'Wheat':'#b6ae93','Gray':'#767871'}.get(c,c) for c in colors]
out=root/'browser'; (out/'meshes').mkdir(exist_ok=True,parents=True)
records=[]
for name,color in zip(parts,colors):
    if name.startswith('keys-'):continue
    path=out/'meshes'/f'{name}.stl'
    result=subprocess.run(['openscad','--backend','Manifold','--export-format','binstl','-D',f'part="{name}"','-o',str(path),str(root/'model.scad')],capture_output=True,text=True)
    if result.returncode or 'ERROR:' in result.stderr: raise RuntimeError(result.stderr)
    assert path.stat().st_size>84,name
    records.append(dict(name=name,file=f'meshes/{name}.stl',color=color,sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    print(name,path.stat().st_size,flush=True)
keys=json.loads((root/'keyboard-layout.json').read_text())
key_meshes=[];variants={}
for i,k in enumerate(keys):
    variant=(k['width'],k['height'],k['style'])
    if variant not in variants:
        name='keycap-'+str(len(variants));variants[variant]=name
        path=out/'meshes'/f'{name}.stl'
        r=subprocess.run(['openscad','--backend','Manifold','--export-format','binstl','-D','part="keycap"','-D',f'key_index={i}','-o',str(path),str(root/'model.scad')],capture_output=True,text=True)
        if r.returncode or 'ERROR:' in r.stderr:raise RuntimeError(r.stderr)
        key_meshes.append(dict(name=name,file=f'meshes/{name}.stl',sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    k['mesh']=variants[variant]
# UV corners are TL, TR, BR, BL, normalized from the unmodified photographs.
def patch(name,photo,position,size,crop,rotation=[90,0,0]):
    return dict(name=name,photo='PXL_20261009_'+photo+'.jpg',position=position,size=size,rotation=rotation,uv=[[x/1824,y/1373] for x,y in crop])
# Only the small original wordmark remains photographic. All physical features
# are geometry; photos are separate reference evidence, never enclosure skins.
patches=[patch('brand','133022597',[-160,-209.2,48],[110,11],[(420,925),(1050,917),(1048,985),(425,990)])]
patches[0]['ink']=True
materials={
    'paint':dict(roughness=.78,metalness=.08,grain=.028,grainScale=2.7),
    'plastic':dict(roughness=.68,metalness=0,grain=.022,grainScale=3.5),
    'key':dict(roughness=.4,metalness=0,grain=.01,grainScale=4.0,clearcoat=.18),
    'clear-key':dict(roughness=.29,metalness=0,grain=.006,grainScale=4.0,clearcoat=.65),
    'rubber':dict(roughness=.92,metalness=0,grain=.015,grainScale=4.0),
    'metal':dict(roughness=.38,metalness=.72,grain=.008,grainScale=5.0),
    'lens':dict(roughness=.24,metalness=0,clearcoat=.8),
    'glass':dict(roughness=.16,metalness=.05,clearcoat=1),
    'tape':dict(roughness=.93,metalness=0,grain=.016,grainScale=3.0),
}
for r in records:
    n=r['name'];m='paint'
    if n in ['drives','drive-insets','drive-latches','power','reset','keyboard-deck','keyboard-fillers','cable-plug']:m='plastic'
    if n in ['hardware','keyboard-feet','keyboard-grommet','cable','ring']:m='rubber'
    if n in ['keyboard-metal','plug-screws']:m='metal'
    if n.startswith('drive-led'):m='lens'
    if n in ['crt-rim','crt-glass']:m='glass'
    if n=='monitor-tape':m='tape'
    r['material']=m
references=['PXL_20261009_'+n+'.jpg' for n in ['133017092','133019620','132919894','133022597','133005363','133001660','133028313','133032874','132916421.MP']]
manifest=dict(version=4,units='mm',scale=.0025,materials=materials,parts=records,keys=keys,keyMeshes=key_meshes,keyboard=dict(y=-355,z=28,slope=6,pitch=20.0),screen=json.loads((root/'monitor-profile.json').read_text())['glass'],patches=patches,references=references,source='https://github.com/ddanila/3d-models/tree/main/models/robotron-1715m')
(out/'model.json').write_text(json.dumps(manifest,indent=2)+'\n')
