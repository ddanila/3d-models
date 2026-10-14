#!/usr/bin/env python3
"""Derive material-separated TO-92 meshes from the pinned KiCad STEP (not MIT).
Run with CadQuery 2.5.2 / OCP 7.7.2; preserves package geometry and board plane.
"""
from pathlib import Path
import hashlib, json
import cadquery as cq
root=Path(__file__).resolve().parents[1]/'components/kicad'
source=cq.importers.importStep(str(root/'source/TO-92_Inline.step')).val()
# Upstream fused model: body starts 2.5 mm above its seating plane.
cutter=cq.Workplane('XY').box(20,20,20).translate((0,0,12.5)).val()
body=source.intersect(cutter);leads=source.cut(cutter)
assert body.isValid() and leads.isValid() and len(leads.Solids())==3
assert abs(body.Volume()+leads.Volume()-source.Volume())<.001
record=dict(id='TO-92_Inline',licence='CC-BY-SA-4.0 with KiCad libraries exception',
    source='source/TO-92_Inline.step',placement='Generic package; specimen mould and lead bends provisional',meshes={})
for kind,shape in [('body',body),('leads',leads)]:
    shape=shape.translate((-1.27,0,0)); b=shape.BoundingBox()
    out=root/'meshes'/('TO-92_Inline-'+kind+'.stl')
    cq.exporters.export(shape,str(out),tolerance=.015,angularTolerance=.1)
    record['meshes'][kind]=dict(file='meshes/'+out.name,sha256=hashlib.sha256(out.read_bytes()).hexdigest(),
        bounds=[[b.xmin,b.ymin,b.zmin],[b.xmax,b.ymax,b.zmax]])
(root/'transistors.json').write_text(json.dumps(record,indent=2)+'\n')
print('TO-92: valid body, three separate leads; source volume preserved')
