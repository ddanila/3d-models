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
    path=out/'meshes'/f'{name}.stl'
    result=subprocess.run(['openscad','--backend','Manifold','--export-format','binstl','-D',f'part="{name}"','-o',str(path),str(root/'model.scad')],capture_output=True,text=True)
    if result.returncode or 'ERROR:' in result.stderr: raise RuntimeError(result.stderr)
    assert path.stat().st_size>84,name
    records.append(dict(name=name,file=f'meshes/{name}.stl',color=color,sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    print(name,path.stat().st_size,flush=True)
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
manifest=dict(version=1,units='mm',scale=.0025,parts=records,keys=json.loads((root/'keyboard-layout.json').read_text()),keyboard=dict(y=-355,z=28,slope=6,pitch=20.0),screen=dict(position=[0,-158.2,324],size=[248,201]),patches=patches,source='https://github.com/ddanila/3d-models/tree/main/models/robotron-1715m')
(out/'model.json').write_text(json.dumps(manifest,indent=2)+'\n')
