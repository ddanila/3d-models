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
patches=[]
for i,x in enumerate([-158,-4]):
    patches.append(patch('drive-'+str(i),'133022597',[x,-206.2,81],[144,40],[(366,601),(1530,592),(1490,855),(395,857)]))
patches.append(patch('brand','133022597',[-160,-209.2,48],[110,11],[(420,925),(1050,917),(1048,985),(425,990)]))
patches.append(patch('power-label','133019620',[207,-209.2,32],[45,7],[(1240,1034),(1450,1034),(1450,1070),(1240,1070)]))
patches.append(patch('keyboard-bottom-left','133001660',[-125,-355,-.2],[244,194],[(112,91),(1440,99),(1432,1163),(126,1154)],[180,0,0]))
patches.append(patch('keyboard-bottom-right','133005363',[119,-355,-.2],[244,194],[(151,78),(1530,91),(1504,1147),(158,1134)],[180,0,0]))
patches.append(patch('monitor-tape','133017092',[0,-95,460.2],[52,9],[(818,228),(1013,255),(999,264),(798,238)],[0,0,0]))
patches.append(patch('case-right-paint','133028313',[250.2,0,83.5],[380,85],[(665,485),(1288,48),(1288,335),(666,1000)],[90,90,0]))
# Neutral paint samples (sRGB averages of 30x30 original-pixel windows).
# Display-space sample centres: (750,530), (1200,210), (1200,380), (750,830).
patches[-1]['paint']=[[.805,.8092,.7942],[.6814,.6852,.6614],[.6632,.6643,.6378],[.7782,.7845,.7735]]
for p in patches:
    p['ink']=p['name'] in ['brand','power-label']
    p['feather']=not p['ink'] and not p['name'].startswith('drive')
manifest=dict(version=2,units='mm',scale=.0025,parts=records,keys=keys,keyMeshes=key_meshes,keyboard=dict(y=-355,z=28,slope=6,pitch=20.0),screen=dict(position=[0,-158.2,324],size=[248,201],radius=20,bulge=3.5),patches=patches,source='https://github.com/ddanila/3d-models/tree/main/models/robotron-1715m')
(out/'model.json').write_text(json.dumps(manifest,indent=2)+'\n')
