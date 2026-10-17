"""Independent underside registration audit. Does not assign or move copper."""
import hashlib,json,math
from pathlib import Path
from photo_registration import homography,project
ROOT=Path(__file__).resolve().parents[1]
def local_reviews(e,top_pins,metric):
 regions=[]
 for region in e.get('localRegions',[]):
  anchors,checks=region['anchors'],region['checks']
  keys=[(p['ref'],p['pin'])for p in anchors+checks]
  if len(anchors)!=4 or not checks or len(set(keys))!=len(keys):
   raise ValueError('Local registration needs four unique anchors and independent checks')
  h=homography([p['photoPixel']for p in anchors],[top_pins[p['ref'],p['pin']]for p in anchors])
  def comparison(bottom,top):
   predicted=project(h,bottom)
   return {'bottomPixel':bottom,'topPixel':top,'projectedTopPixel':predicted,'residualPixels':math.dist(top,predicted),'nominalResidualMm':math.dist(project(metric,top),project(metric,predicted))}
  checked=[dict(ref=p['ref'],pin=p['pin'],**comparison(p['photoPixel'],top_pins[p['ref'],p['pin']]))for p in checks]
  # Explicitly retain extrapolation: a good DIP-local fit is not a board-wide fit.
  xs=[p['photoPixel'][0]for p in anchors];ys=[p['photoPixel'][1]for p in anchors]
  def candidate(p):
   x,y=p['bottomPixel'];outside=not(min(xs)<=x<=max(xs)and min(ys)<=y<=max(ys))
   return dict(p,**{k:v for k,v in comparison(p['bottomPixel'],p['topPixel']).items()if k not in p},outsideAnchorBounds=outside)
  maximum=max(p['nominalResidualMm']for p in checked)
  regions.append({'id':region['id'],'scope':region['scope'],'bottomToTop':h,'anchors':anchors,'checks':checked,'maxCheckResidualMm':maximum,'withinPhotoTolerance':maximum<=e['toleranceMm'],'copperAssignmentQualified':False,'candidates':[candidate(p)for p in region['candidates']],'extrapolationChecks':[candidate(p)for p in region.get('extrapolationChecks',[])]})
 return regions

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
 return {'schema':1,'scope':e['scope'],'photoSha256':hashlib.sha256((ROOT/e['photo']).read_bytes()).hexdigest(),'toleranceMm':e['toleranceMm'],'photoToModel':h,'modelToPhoto':inverse,'pins':rows,'maxCheckResidualMm':maximum,'withinPhotoTolerance':maximum<=e['toleranceMm'],'copperAssignmentQualified':False,'crossPhoto':cross,'localRegions':local_reviews(e,top_pins,metric)}
def svg(report):
 e=json.loads((ROOT/'bottom-landmarks.json').read_text());w,h=e['imageSize'];out=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}">',f'<image href="../{e["photo"]}" width="{w}" height="{h}"/>']
 for p in report['pins']:
  x,y=p['photoPixel'];a,b=p['pcbPixel'];color='lime' if p['heldOut']else 'cyan';label=p['ref']+':'+p['pin']
  out.append(f'<path d="M{x},{y} L{a},{b}" stroke="yellow" stroke-width="3"/><circle cx="{x}" cy="{y}" r="9" fill="none" stroke="{color}" stroke-width="3"/><circle cx="{a}" cy="{b}" r="5" fill="red"/><text x="{x+14}" y="{y}" fill="white" stroke="black" stroke-width=".3" font-size="15">{label}</text>')
 for region in report.get('localRegions',[]):
  for p in region['checks']:
   x,y=p['bottomPixel'];out.append(f'<circle cx="{x}" cy="{y}" r="8" fill="none" stroke="orange" stroke-width="3"/><text x="{x+12}" y="{y}" fill="white" font-size="14">Local {p["ref"]}:{p["pin"]}</text>')
  for p in region['candidates']:
   x,y=p['bottomPixel'];out.append(f'<circle cx="{x}" cy="{y}" r="10" fill="none" stroke="magenta" stroke-width="3"/><text x="{x+12}" y="{y}" fill="white" font-size="14">{p["id"]}?</text>')
 return '\n'.join(out+['</svg>'])+'\n'
