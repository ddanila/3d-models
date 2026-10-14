#!/usr/bin/env python3
"""Tessellate the pinned KiCad STEP collection with CadQuery 2.5.2 / OCP 7.7.2.
Install into a separate venv: pip install cadquery==2.5.2
Source data and derived meshes retain the upstream licences; this converter is MIT.
"""
from pathlib import Path
import hashlib,json,struct
import cadquery as cq
root=Path(__file__).resolve().parents[1]/'components/kicad'
records=[]
for path in sorted((root/'source').glob('DIP-*.step')):
    name=path.stem; pins=int(name.split('-')[1].split('_')[0]); width=float(name.split('_W')[1][:-2])
    source=cq.importers.importStep(str(path)).val()
    b=source.BoundingBox();cx=(b.xmin+b.xmax)/2;cy=(b.ymin+b.ymax)/2
    walls=[f.BoundingBox() for f in source.Faces() if f.Area()>8 and f.BoundingBox().zmin>=.379]
    xmin=min(f.xmin for f in walls);xmax=max(f.xmax for f in walls)
    # These upstream DIP models fuse body and leads. A cut at the plastic side
    # walls separates watertight material meshes without changing outer geometry.
    cutter=cq.Workplane('XY').box(xmax-xmin, b.ylen+2, b.zlen+2).translate(((xmin+xmax)/2,(b.ymin+b.ymax)/2,(b.zmin+b.zmax)/2)).val()
    body=source.intersect(cutter);leads=source.cut(cutter)
    assert body.isValid() and leads.isValid()
    assert len(leads.Solids())==pins, (name,len(leads.Solids()))
    assert abs(body.Volume()+leads.Volume()-source.Volume())<.01
    # Intersect each lead at the seating plane: footprint follows actual STEP,
    # including the 24-pin model's slightly non-nominal row spacing.
    plane=cq.Workplane('XY').box(b.xlen+4,b.ylen+4,.02).translate((cx,cy,0)).val()
    footprint=[]
    for lead in leads.Solids():
        q=lead.intersect(plane).BoundingBox()
        footprint.append([round((q.xmin+q.xmax)/2-cx,6),round((q.ymin+q.ymax)/2-cy,6)])
    footprint.sort()
    meshes={}
    for kind,shape in [('body',body),('leads',leads)]:
        centered=shape.translate((-cx,-cy,0));out=root/'meshes'/f'{name}-{kind}.stl'
        cq.exporters.export(centered,str(out),tolerance=.025,angularTolerance=.15)
        blob=out.read_bytes();count=struct.unpack_from('<I',blob,80)[0]
        vertices=[struct.unpack_from('<3f',blob,84+i*50+12+j*12) for i in range(count) for j in range(3)]
        bounds=[[min(v[k] for v in vertices) for k in range(3)],[max(v[k] for v in vertices) for k in range(3)]]
        meshes[kind]=dict(file='components/kicad/meshes/'+out.name,sha256=hashlib.sha256(blob).hexdigest(),bounds=bounds)
    bb=meshes['body']['bounds']
    licence='GPL-3.0-or-later with design exception' if 'GNU General Public License' in path.read_text() else 'CC-BY-SA-4.0 with KiCad libraries exception'
    records.append(dict(id=name,pins=pins,rowSpacing=width,pitch=2.54,footprint=footprint,licence=licence,bodyHeight=bb[1][2],bodySize=[bb[1][0]-bb[0][0],bb[1][1]-bb[0][1]],meshes=meshes))
    print(name,len(body.Solids()),len(leads.Solids()),flush=True)
(root/'models.json').write_text(json.dumps(records,indent=2)+'\n')
