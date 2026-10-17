"""Independent underside registration audit. Does not assign or move copper."""
import hashlib,json,math
from pathlib import Path
from photo_registration import homography,project
ROOT=Path(__file__).resolve().parents[1]
def review(layout):
 e=json.loads((ROOT/'bottom-landmarks.json').read_text())
 pads={(c['ref'],p['pin']):p['position']for c in layout['components']for p in c['pads']}
 anchors=e['anchors'];checks=e['checks']
 if len(anchors)!=4 or not checks:raise ValueError('Four anchors and independent check pads required')
 keys=lambda rows:[(p['ref'],p['pin'])for p in rows]
 if len(set(keys(anchors+checks)))!=len(anchors+checks):raise ValueError('Registration pads must be unique; held-out checks cannot be anchors')
 points=[pads[k]for k in keys(anchors)];h=homography([p['photoPixel']for p in anchors],points);inverse=homography(points,[p['photoPixel']for p in anchors])
 rows=[]
 for p in anchors+checks:
  target=pads[p['ref'],p['pin']];observed=project(h,p['photoPixel'])
  rows.append(dict(p,pcbModel=target,photoModel=observed,pcbPixel=project(inverse,target),residualMm=math.dist(target,observed),heldOut=p in checks))
 # A direct photo-to-photo comparison isolates the effect of locally fitted
 # rigid PCB packages from the original observations. It is not a new authority.
 top=json.loads((ROOT/'photo-landmarks.json').read_text())
 top_pins={(ref,pin):xy for ref,c in top['components'].items()for group in ['pins','checkPins']for pin,xy in c.get(group,{}).items()}
 top_points=[top_pins[k]for k in keys(anchors)]
 cross_h=homography([p['photoPixel']for p in anchors],top_points)
 metric=homography(top['photoCorners'],top['modelCorners']);cross_checks=[]
 for p in checks:
  observed=top_pins[p['ref'],p['pin']];projected=project(cross_h,p['photoPixel'])
  cross_checks.append(dict(ref=p['ref'],pin=p['pin'],topObservedPixel=observed,bottomProjectedTopPixel=projected,residualPixels=math.dist(observed,projected),nominalResidualMm=math.dist(project(metric,observed),project(metric,projected))))
 cross={'scope':'Direct original-photo correspondence with the same four anchors; top lead/socket surfaces may differ from underside hole centers. Nominal mm uses the top board-envelope calibration, not metrology. No PCB edits or copper assignment.', 'topPhotoSha256':hashlib.sha256((ROOT/top['photo']).read_bytes()).hexdigest(),'bottomToTop':cross_h,'checks':cross_checks,'maxCheckResidualMm':max(p['nominalResidualMm']for p in cross_checks)}
 maximum=max(p['residualMm']for p in rows if p['heldOut'])
 return {'schema':1,'scope':e['scope'],'photoSha256':hashlib.sha256((ROOT/e['photo']).read_bytes()).hexdigest(),'toleranceMm':e['toleranceMm'],'photoToModel':h,'modelToPhoto':inverse,'pins':rows,'maxCheckResidualMm':maximum,'withinPhotoTolerance':maximum<=e['toleranceMm'],'copperAssignmentQualified':False,'crossPhoto':cross}
def svg(report):
 e=json.loads((ROOT/'bottom-landmarks.json').read_text());w,h=e['imageSize'];out=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}">',f'<image href="../{e["photo"]}" width="{w}" height="{h}"/>']
 for p in report['pins']:
  x,y=p['photoPixel'];a,b=p['pcbPixel'];color='lime' if p['heldOut']else 'cyan';label=p['ref']+':'+p['pin']
  out.append(f'<path d="M{x},{y} L{a},{b}" stroke="yellow" stroke-width="3"/><circle cx="{x}" cy="{y}" r="9" fill="none" stroke="{color}" stroke-width="3"/><circle cx="{a}" cy="{b}" r="5" fill="red"/><text x="{x+14}" y="{y}" fill="white" stroke="black" stroke-width=".3" font-size="15">{label}</text>')
 return '\n'.join(out+['</svg>'])+'\n'
