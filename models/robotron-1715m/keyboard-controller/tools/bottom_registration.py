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

def inside_hull(point,hull):
 # Anchors must be supplied in convex boundary order; no bounding-box extrapolation.
 crosses=[(b[0]-a[0])*(point[1]-a[1])-(b[1]-a[1])*(point[0]-a[0])for a,b in zip(hull,hull[1:]+hull[:1])]
 return all(v>=-1e-8 for v in crosses)or all(v<=1e-8 for v in crosses)

def pcb_regions(e,pads):
 regions=[]
 for region in e.get('pcbRegions',[]):
  anchors,checks=region['anchors'],region['checks'];keys=[(p['ref'],p['pin'])for p in anchors+checks]
  if len(anchors)!=4 or len(checks)<4 or len(keys)!=len(set(keys)):
   raise ValueError('PCB region requires four unique anchors and at least four independent checks')
  hull=[p['photoPixel']for p in anchors]
  # Each corner must be on the same side of all non-adjacent edges.
  turns=[(hull[(i+1)%4][0]-hull[i][0])*(hull[(i+2)%4][1]-hull[(i+1)%4][1])-(hull[(i+1)%4][1]-hull[i][1])*(hull[(i+2)%4][0]-hull[(i+1)%4][0])for i in range(4)]
  if not(all(v>0 for v in turns)or all(v<0 for v in turns)):raise ValueError('PCB region anchors must form a convex boundary')
  h=homography(hull,[pads[p['ref'],p['pin']]for p in anchors]);rows=[]
  for p in checks:
   predicted=project(h,p['photoPixel']);target=pads[p['ref'],p['pin']]
   rows.append(dict(p,photoModel=predicted,pcbModel=target,residualMm=math.dist(predicted,target),insideAnchorHull=inside_hull(p['photoPixel'],hull)))
  maximum=max(p['residualMm']for p in rows)
  # Check pads just outside the hull remain useful validation, never extend its scope.
  regions.append(dict(id=region['id'],scope=region['scope'],anchors=anchors,checks=rows,anchorHull=hull,photoToModel=h,maxCheckResidualMm=maximum,toleranceMm=e['toleranceMm'],copperAssignmentQualified=region.get('reviewedForCopper',False)and maximum<=e['toleranceMm']))
 return regions

def validate_registered_routes(routes,report,landmark_sha):
 regions={r['id']:r for r in report.get('pcbRegions',[])}
 for route in routes:
  record=route['evidence'];registration=record.get('registration')
  if not registration:continue
  region=regions.get(registration['region'])
  if registration['landmarksSha256']!=landmark_sha:raise ValueError('Stale route registration evidence')
  if not region or not region['copperAssignmentQualified']:raise ValueError('Route registration is not locally qualified')
  photo=next((s for s in record['sources']if s['id']=='photo-bottom'),None)
  points=photo['locator'].get('pixelSegment',[])if photo else []
  if route['side']!='bottom' or len(points)!=len(route['points']):raise ValueError('Registered route needs underside pixel correspondence')
  if not all(inside_hull(p,region['anchorHull'])for p in points):raise ValueError('Route exceeds local registration hull')
  model_hull=[project(region['photoToModel'],p)for p in region['anchorHull']]
  if not all(inside_hull(p,model_hull)for p in route['points']):raise ValueError('Native route exceeds local registration hull')
  if record['status']=='inferred' and any(math.dist(project(region['photoToModel'],p),q)>region['toleranceMm']for p,q in zip(points,route['points'])):
   raise ValueError('Inferred attachment exceeds local registration tolerance')
  if record['status']=='observed' and any(math.dist(project(region['photoToModel'],p),q)>0.000002 for p,q in zip(points,route['points'])):
   raise ValueError('Observed route geometry differs from local photo projection')

def validate_pad_placements(layout,report,evidence):
 regions={r['id']:r for r in report['pcbRegions']}
 pads={(c['ref'],p['pin']):p['position']for c in layout['components']for p in c['pads']}
 rows=[]
 for ref,record in evidence.items():
  placement=record.get('bottomPadPlacement')
  if not placement:continue
  region=regions.get(placement['region'])
  if placement['photoSource']!='photo-bottom' or not region or not region['copperAssignmentQualified']:
   raise ValueError('Unqualified underside pad registration')
  for pin,pixel in placement['pins'].items():
   if not inside_hull(pixel,region['anchorHull']):raise ValueError('Pad exceeds local registration hull')
   target=project(region['photoToModel'],pixel);actual=pads[ref,pin];error=math.dist(target,actual)
   if error>0.000002:raise ValueError('Native pad differs from registered underside joint')
   rows.append(dict(ref=ref,pin=pin,photoPixel=pixel,photoModel=target,pcbModel=actual,residualMm=error,region=region['id']))
 return rows

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
 return {'schema':1,'scope':e['scope'],'photoSha256':hashlib.sha256((ROOT/e['photo']).read_bytes()).hexdigest(),'toleranceMm':e['toleranceMm'],'photoToModel':h,'modelToPhoto':inverse,'pins':rows,'maxCheckResidualMm':maximum,'withinPhotoTolerance':maximum<=e['toleranceMm'],'copperAssignmentQualified':False,'crossPhoto':cross,'localRegions':local_reviews(e,top_pins,metric),'pcbRegions':pcb_regions(e,pads)}
def svg(report,layout=None):
 e=json.loads((ROOT/'bottom-landmarks.json').read_text());w,h=e['imageSize'];out=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}">',f'<image href="../{e["photo"]}" width="{w}" height="{h}"/>']
 for p in report['pins']:
  x,y=p['photoPixel'];a,b=p['pcbPixel'];color='lime' if p['heldOut']else 'cyan';label=p['ref']+':'+p['pin']
  out.append(f'<path d="M{x},{y} L{a},{b}" stroke="yellow" stroke-width="3"/><circle cx="{x}" cy="{y}" r="9" fill="none" stroke="{color}" stroke-width="3"/><circle cx="{a}" cy="{b}" r="5" fill="red"/><text x="{x+14}" y="{y}" fill="white" stroke="black" stroke-width=".3" font-size="15">{label}</text>')
 for region in report.get('localRegions',[]):
  for p in region['checks']:
   x,y=p['bottomPixel'];out.append(f'<circle cx="{x}" cy="{y}" r="8" fill="none" stroke="orange" stroke-width="3"/><text x="{x+12}" y="{y}" fill="white" font-size="14">Local {p["ref"]}:{p["pin"]}</text>')
  for p in region['candidates']:
   x,y=p['bottomPixel'];out.append(f'<circle cx="{x}" cy="{y}" r="10" fill="none" stroke="magenta" stroke-width="3"/><text x="{x+12}" y="{y}" fill="white" font-size="14">{p["id"]}?</text>')
 for region in report.get('pcbRegions',[]):
  points=' '.join(f'{x},{y}'for x,y in region['anchorHull'])
  out.append(f'<polygon points="{points}" fill="none" stroke="cyan" stroke-width="3" stroke-dasharray="12 8"/>')
  for p in region['checks']:
   x,y=p['photoPixel'];out.append(f'<circle cx="{x}" cy="{y}" r="8" fill="none" stroke="orange" stroke-width="3"/>')
 if layout:
  for route in layout['routes']:
   if not route['evidence'].get('registration'):continue
   photo=next(s for s in route['evidence']['sources']if s['id']=='photo-bottom')
   points=' '.join(f'{x},{y}'for x,y in photo['locator']['pixelSegment'])
   out.append(f'<polyline points="{points}" fill="none" stroke="magenta" stroke-width="2"/>')
 return '\n'.join(out+['</svg>'])+'\n'
