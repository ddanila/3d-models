#!/usr/bin/env python3
"""Project actual exported STL triangles into manually aligned owner-photo planes.
Standard-library only; output is a review aid, never a dimensional certificate.
"""
from pathlib import Path
import json, struct, math, html
root=Path(__file__).resolve().parents[1];config=json.loads((root/'photo-alignment.json').read_text())
out=root/'checks/photo-comparisons';out.mkdir(parents=True,exist_ok=True)
def solve(a,b):
 rows=[list(x)+[v] for x,v in zip(a,b)]
 for i in range(len(b)):
  j=max(range(i,len(b)),key=lambda j:abs(rows[j][i]));rows[i],rows[j]=rows[j],rows[i]
  q=rows[i][i];rows[i]=[v/q for v in rows[i]]
  for j in range(len(b)):
   if j!=i:
    q=rows[j][i];rows[j]=[x-q*y for x,y in zip(rows[j],rows[i])]
 return [r[-1] for r in rows]
def homography(anchors):
 a=[];b=[]
 for (x,y),(u,v) in anchors:
  a.extend([[x,y,1,0,0,0,-u*x,-u*y],[0,0,0,x,y,1,-v*x,-v*y]]);b.extend([u,v])
 return solve(a,b)+[1]
def project(h,p):
 x,y=p;q=h[6]*x+h[7]*y+1
 return [(h[0]*x+h[1]*y+h[2])/q,(h[3]*x+h[4]*y+h[5])/q]
reports=[];sections=[]
for view in config['views']:
 h=homography(view['anchors']);polygons=[]
 for name,color in view['meshes']:
  raw=(root/'browser/meshes'/f'{name}.stl').read_bytes()
  for i in range(struct.unpack_from('<I',raw,80)[0]):
   vertices=[struct.unpack_from('<3f',raw,84+50*i+12+12*j) for j in range(3)]
   if 'clipX' in view and any(v[0]>view['clipX'] for v in vertices):continue
   pts=[project(h,[v[a] for a in view['axes']]) for v in vertices]
   area=abs(sum(pts[j][0]*pts[(j+1)%3][1]-pts[(j+1)%3][0]*pts[j][1] for j in range(3)))
   if area<.1:continue
   polygons.append(f'<polygon points="{" ".join(f"{x:.2f},{y:.2f}" for x,y in pts)}" fill="{color}"/>')
 overlay=[];residuals=[]
 for point in view['holdouts']:
  x,y=project(h,point['model']);u,v=point['photo'];error=math.hypot(x-u,y-v)
  residuals.append(dict(name=point['name'],residualPixels=round(error,2)))
  overlay.append(f'<circle cx="{u}" cy="{v}" r="10" fill="none" stroke="#00ffff" stroke-width="4"/><path d="M{x-10},{y}h20 M{x},{y-10}v20" stroke="#ff6b00" stroke-width="4"/>')
 model=''.join(polygons);photo=f'<image href="../../reference/photos/{view["photo"]}" width="1824" height="1373"/>'
 def svg(body):return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1824 1373">{body}</svg>'
 (out/f'{view["name"]}-model.svg').write_text(svg(model))
 (out/f'{view["name"]}-overlay.svg').write_text(svg(photo+f'<g opacity=".45">{model}</g>'+''.join(overlay)))
 reports.append(dict(name=view['name'],homography=h,reviewResiduals=residuals,limitations=view['limitations']))
 overlay_view=svg(photo+f'<g opacity=".45">{model}</g>'+''.join(overlay))
 sections.append(f'<h2>{view["name"]}</h2><p>{html.escape(view["limitations"])}</p><div><img src="../../reference/photos/{view["photo"]}"><img src="{view["name"]}-model.svg">{overlay_view}</div>')
(out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Robotron photo / mesh review</title><style>body{background:#202426;color:#eee;font:16px system-ui;margin:24px}div{display:flex}img,svg{width:33.33%;object-fit:contain;background:#ddd}</style><h1>Owner photo · exported mesh · overlay</h1><p>'+html.escape(config['status'])+'</p>'+''.join(sections))
(out/'alignment.json').write_text(json.dumps(reports,indent=2)+'\n')
print(f'Wrote {len(reports)} reproducible photo/STL comparisons to',out)
