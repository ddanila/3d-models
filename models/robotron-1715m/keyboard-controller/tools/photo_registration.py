#!/usr/bin/env python3
"""Review numbered lead landmarks against PCB pads; optionally apply a rigid fit.
Photo annotations never become connectivity or a claim of measured dimensions.
"""
import argparse,hashlib,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def homography(src,dst):
 rows=[]
 for (x,y),(u,v) in zip(src,dst):
  rows.extend([[x,y,1,0,0,0,-u*x,-u*y,u],[0,0,0,x,y,1,-v*x,-v*y,v]])
 for i in range(8):
  pivot=max(range(i,8),key=lambda j:abs(rows[j][i]));rows[i],rows[pivot]=rows[pivot],rows[i]
  if abs(rows[i][i])<1e-12:raise ValueError('Degenerate photo registration')
  v=rows[i][i];rows[i]=[x/v for x in rows[i]]
  for j in range(8):
   if j!=i:
    v=rows[j][i];rows[j]=[a-v*b for a,b in zip(rows[j],rows[i])]
 return [r[-1] for r in rows]+[1]
def project(h,p):
 x,y=p;d=h[6]*x+h[7]*y+h[8]
 return [(h[0]*x+h[1]*y+h[2])/d,(h[3]*x+h[4]*y+h[5])/d]
def rigid_fit(src,dst):
 if len(src)!=len(dst) or len(src)<3:raise ValueError('At least three paired landmarks required')
 center=lambda p:[sum(q[i]for q in p)/len(p)for i in range(2)]
 a,b=center(src),center(dst)
 dot=sum((x[0]-a[0])*(y[0]-b[0])+(x[1]-a[1])*(y[1]-b[1])for x,y in zip(src,dst))
 cross=sum((x[0]-a[0])*(y[1]-b[1])-(x[1]-a[1])*(y[0]-b[0])for x,y in zip(src,dst))
 angle=math.atan2(cross,dot);c,s=math.cos(angle),math.sin(angle)
 def transform(p):return [b[0]+c*(p[0]-a[0])-s*(p[1]-a[1]),b[1]+s*(p[0]-a[0])+c*(p[1]-a[1])]
 return angle,transform

def review(layout):
 evidence=json.loads((ROOT/'photo-landmarks.json').read_text());h=homography(evidence['photoCorners'],evidence['modelCorners']);inverse=homography(evidence['modelCorners'],evidence['photoCorners'])
 placed={c['ref']:c for c in layout['components']};rows=[]
 for ref,record in sorted(evidence['components'].items()):
  c=placed[ref];pads={p['pin']:p['position']for p in c['pads']}
  pins=[{'pin':pin,'photoPixel':p,'photoModel':project(h,p),'pcbModel':pads[pin]}for pin,p in record['pins'].items()]
  src=[p['pcbModel']for p in pins];dst=[p['photoModel']for p in pins];angle,transform=rigid_fit(src,dst)
  checks=[{'pin':pin,'photoPixel':p,'photoModel':project(h,p),'pcbModel':pads[pin],'heldOut':True}for pin,p in record.get('checkPins',{}).items()]
  for p in pins+checks:p['residualMm']=math.dist(p['pcbModel'],p['photoModel']);p['pcbPixel']=project(inverse,p['pcbModel'])
  rows.append({'ref':ref,'pins':pins,'checkPins':checks,'rmsResidualMm':math.sqrt(sum(p['residualMm']**2 for p in pins)/len(pins)),'maxResidualMm':max(p['residualMm']for p in pins+checks),'fitMaxResidualMm':max(math.dist(transform(p['pcbModel']),p['photoModel'])for p in pins+checks),'proposedPosition':transform(c['position']),'rotationDeltaDegrees':math.degrees(angle),'status':'photo-estimated'})
 return {'schema':1,'scope':evidence['scope'],'photoSha256':hashlib.sha256((ROOT/evidence['photo']).read_bytes()).hexdigest(),'toleranceMm':evidence['maxResidualMm'],'components':rows,'withinPhotoTolerance':all(c['maxResidualMm']<=evidence['maxResidualMm']for c in rows)}

def svg(report):
 e=json.loads((ROOT/'photo-landmarks.json').read_text());w,h=e['imageSize'];out=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}">',f'<image href="../{e["photo"]}" width="{w}" height="{h}"/>']
 for c in report['components']:
  for p in c['pins']+c['checkPins']:
   x,y=p['photoPixel'];a,b=p['pcbPixel'];out.append(f'<path d="M{x},{y} L{a},{b}" stroke="yellow" stroke-width="3"/><circle cx="{x}" cy="{y}" r="9" fill="none" stroke="lime" stroke-width="3"/><circle cx="{a}" cy="{b}" r="5" fill="red"/><text x="{x+14}" y="{y}" fill="white" stroke="black" stroke-width=".3" font-size="15">{c["ref"]}:{p["pin"]}</text>')
 return '\n'.join(out+['</svg>'])+'\n'

def selected_fits(report,refs):
 available={c['ref']for c in report['components']}
 if refs and set(refs)-available:raise ValueError('Unknown or unreviewed references: '+', '.join(sorted(set(refs)-available)))
 rows=[c for c in report['components']if not refs or c['ref']in refs]
 if not rows:raise ValueError('No reviewed placements selected')
 for c in rows:
  if c['fitMaxResidualMm']>report['toleranceMm'] or abs(c['rotationDeltaDegrees'])>20:raise ValueError('Review inconsistent landmark fit for '+c['ref'])
 return rows

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--apply',action='store_true');parser.add_argument('--refs',nargs='+');a=parser.parse_args()
 layout=json.loads((ROOT/'generated/layout.json').read_text());report=review(layout)
 if a.apply:
  try:report['components']=selected_fits(report,a.refs)
  except ValueError as e:raise SystemExit(str(e))
  from export import check
  check()
  import pcbnew as pcb
  board=pcb.LoadBoard(str(ROOT/'controller.kicad_pcb'));fps={f.GetReference():f for f in board.GetFootprints()}
  for c in report['components']:
   f=fps[c['ref']];x,y=c['proposedPosition'];f.SetPosition(pcb.VECTOR2I(round((x+150)*1e6),round((50-y)*1e6)));f.SetOrientationDegrees(f.GetOrientationDegrees()+c['rotationDeltaDegrees']);f.SetField('Evidence','photo-landmarks.json: '+c['ref']+'; nominal envelope, not metrology')
  pcb.SaveBoard(str(ROOT/'controller.kicad_pcb'),board)
  print('Applied rigid photo fits to native PCB. Regenerate exports and review overlays.')
 else:
  print(json.dumps({c['ref']:round(c['maxResidualMm'],3) for c in report['components']},indent=2))
if __name__=='__main__':main()
