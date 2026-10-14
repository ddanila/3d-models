#!/usr/bin/env python3
"""Reproduce local pin-pitch registration; no board-size or ref-identity claim."""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
f=root/'board-layout.json';d=json.loads(f.read_text());b=d['boards'][0]
# The owner photograph looks from the rear: image-right is canonical -X.
# Correct the earlier positive-X registration once, without reflecting packages.
# Pin-one orientation remains provisional; rotate symmetric package bodies.
if not d.get('motherboardRearPhotoBasis'):
 for c in b['components']+b['passives']+b['connectors']:
  c['position'][0]=round(-212-c['position'][0],3)
  c['rotation']=(180-c['rotation'])%360
 b['mounts']=[[-212-x,y] for x,y in b['mounts']]
 d['motherboardRearPhotoBasis']='Image right maps to canonical -X; v37 positive-X placement corrected about board centre X=-106 mm.'
# Coordinates on a 1600x1205 review image; DMA DIP-40 outer lead centres.
# 19 intervals x 2.54 mm, with nominal 15.24 mm row pitch.
photo=[[625,388],[694,385],[694,621],[622,621]]
anchor=[-91.276,65.101]
model=[[anchor[0]-x,anchor[1]+y] for x,y in [(-7.62,-24.13),(7.62,-24.13),(7.62,24.13),(-7.62,24.13)]]
rows=[]
for (x,y),(u,v) in zip(photo,model):
 rows.extend([[x,y,1,0,0,0,-u*x,-u*y,u],[0,0,0,x,y,1,-v*x,-v*y,v]])
for i in range(8):
 pivot=max(range(i,8),key=lambda j:abs(rows[j][i]));rows[i],rows[pivot]=rows[pivot],rows[i]
 scale=rows[i][i];rows[i]=[v/scale for v in rows[i]]
 for j in range(8):
  if j!=i:
   scale=rows[j][i];rows[j]=[v-scale*w for v,w in zip(rows[j],rows[i])]
h=[r[-1] for r in rows]+[1]
def project(p):
 x,y=p;z=h[6]*x+h[7]*y+1
 return [round((h[0]*x+h[1]*y+h[2])/z,3),round((h[3]*x+h[4]*y+h[5])/z,3)]
centres={'A1':[808,503],'A2':[658,503],'A3':[952,503],'A44':[1080,503],
 'A114':[790,300],'A11':[1180,824],
 'A6':[498,278],'A45':[490,403],'A8':[490,510],'A9':[490,608],'A10':[490,708]}
for c in b['components']:
 if c['ref'] not in centres:continue
 c['position'][:2]=project(centres[c['ref']]);c['photoCentre']=centres[c['ref']]
 c['status']='Local owner-photo pin-pitch registration; package pitch nominal, reference correspondence provisional'
 c['inspection']['photo']='20261014_073200542'
 c['inspection']['evidence']='Owner photograph + W/M documentation; photo-estimated placement'
 c['inspection']['text']=c['inspection']['text'].split(' Package position registered')[0].split(' Position uses a local')[0]+' Position uses a local projective fit to nominal DIP-40 lead pitch in owner photo 073200542. Reference correspondence and exact dimensions remain provisional.'
# The visible long left socket; 32 two-row contacts, identity not inferred.
b['connectors'][2].update(position=project([278,685])+[13.6],status='Owner-photo position; nominal 2.54 mm pitch; connector identity provisional')
d['processorPinRegistration']=dict(photo='PXL_20261014_073200542.jpg',reviewResolution=[1600,1205],photoPoints=photo,modelPoints=model,homography=h,centres=centres,scope='Local projective correction from nominal DMA DIP-40 pitch. Lead-centre picking, nominal row spacing, lens distortion and extrapolation remain uncertain; global board dimensions not calibrated.')
f.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
print('Registered eleven processor-area packages and one long socket')
