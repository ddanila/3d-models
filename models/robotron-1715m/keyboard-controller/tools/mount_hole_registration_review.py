#!/usr/bin/env python3
"""Screen conditional metric fits using independent mounting-hole rim shape."""
import argparse
import hashlib
import json
import math
from pathlib import Path
from distributed_registration_review import solve
from photo_registration import project
ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/'reference/package-reviews/mount-hole-registration/assessment.json'


def circle(points):
    if len(points)<5:raise ValueError('Need a distributed rim')
    # Centre coordinates before solving to avoid the long board offset dominating.
    origin=[sum(p[i] for p in points)/len(points) for i in (0,1)]
    points=[[p[i]-origin[i] for i in (0,1)] for p in points]
    rows=[[x,y,1] for x,y in points];rhs=[-(x*x+y*y) for x,y in points]
    columns=list(zip(*rows))
    a,b,c=solve([[sum(x*y for x,y in zip(u,v)) for v in columns] for u in columns],
                [sum(x*y for x,y in zip(u,rhs)) for u in columns])
    radius_squared=(a*a+b*b)/4-c
    if radius_squared<=0:raise ValueError('Invalid fitted circle')
    return [origin[0]-a/2,origin[1]-b/2],math.sqrt(radius_squared)



def circle_intersects_quad(centre,radius,quad):
    if radius<=0 or len(quad)!=4:raise ValueError('Invalid circle or quadrilateral')
    signs=[];distances=[]
    for a,b in zip(quad,quad[1:]+quad[:1]):
        dx,dy=b[0]-a[0],b[1]-a[1];length=dx*dx+dy*dy
        if length==0:raise ValueError('Degenerate picking box')
        signs.append(dx*(centre[1]-a[1])-dy*(centre[0]-a[0]))
        t=max(0,min(1,((centre[0]-a[0])*dx+(centre[1]-a[1])*dy)/length))
        distances.append(math.dist(centre,[a[0]+t*dx,a[1]+t*dy]))
    inside=all(v>=0 for v in signs) or all(v<=0 for v in signs)
    minimum=0 if inside else min(distances)
    maximum=max(math.dist(centre,p) for p in quad)
    return minimum<=radius<=maximum


def screen(matrix,pixels,uncertainty):
    if not math.isfinite(uncertainty) or uncertainty<=0:raise ValueError('Invalid picking allowance')
    def mapped(p):return project(matrix,[(p[0]-1200)/1000,(p[1]-1900)/1000])
    points=[mapped(p) for p in pixels];centre,radius=circle(points);residuals=[];allowances=[];intersections=[]
    for pixel,point in zip(pixels,points):
        residuals.append(abs(math.dist(point,centre)-radius))
        corners=[[pixel[0]+dx*uncertainty,pixel[1]+dy*uncertainty] for dx,dy in ((-1,-1),(1,-1),(1,1),(-1,1))]
        denominators=[matrix[6]*(p[0]-1200)/1000+matrix[7]*(p[1]-1900)/1000+1 for p in corners]
        if min(denominators)<=0<=max(denominators):raise ValueError('Projective pole crosses picking box')
        # A pole-free homography maps this box to a convex quadrilateral.
        # Maximum displacement from its nominal point occurs at a corner.
        quad=[mapped(p) for p in corners]
        allowances.append(max(math.dist(point,p) for p in quad))
        intersections.append(circle_intersects_quad(centre,radius,quad))
    return {'fittedCentreMm':centre,'fittedRadiusMm':radius,'maximumRadialResidualMm':max(residuals),
            'maximumPickingDisplacementMm':max(allowances),
            'maximumResidualToPickingRatio':max(r/a for r,a in zip(residuals,allowances)),
            'circleIntersectsEveryPickingBox':all(intersections),
            'candidateCircleWithinDisplacementAllowance':all(r<=a for r,a in zip(residuals,allowances)),
            'interpretation':'Circle/convex-quadrilateral intersection supplies a compatible rim-point witness for every picking box when true. False does not exclude another circle. The displacement ratio is diagnostic only.'}


def build():
    names=['reference/mounting-hole-rims.json','reference/package-reviews/distributed-registration/assessment.json',
           'tools/mount_hole_registration_review.py','tools/distributed_registration_review.py','tools/photo_registration.py','sense-review.json']
    observation=json.loads((ROOT/names[0]).read_text());fits=json.loads((ROOT/names[1]).read_text())
    if observation['photoSha256']!=json.loads((ROOT/'sense-review.json').read_text())['sourceSha256']:raise ValueError('Different primary photos')
    candidates=[('nominal',fits['nominal'])]+[(str(t['rowXShiftSigns']),t) for t in fits['systematicPickingTrials']]
    results=[]
    for name,fit in candidates:
        holes=[]
        for hole in observation['holes']:
            x,y=hole['cropPixels'][:2];scale=hole['reviewDisplayScale']
            pixels=[[x+p[0]/scale,y+p[1]/scale] for p in hole['rimPointsInReviewCrop']]
            holes.append({'id':hole['id'],**screen(fit['normalizedPhotoToMetric'],pixels,observation['pixelUncertainty'])})
        results.append({'fit':name,'holes':holes})
    return {'schema':1,'sources':{n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in names},
            'photoSha256':observation['photoSha256'],'pickingAllowancePixels':observation['pixelUncertainty'],
            'candidates':results,'registrationQualified':False,'padPlacementAuthorized':False,
            'scope':'Held-out primary mounting-hole shape; no diameter assumption and no refitting of registration. Approximate rim circularity is a hypothesis, not an established manufacturing tolerance.',
            'allCandidatesHaveCircularRimWitnesses':all(h['circleIntersectsEveryPickingBox'] for c in results for h in c['holes']),
            'nextDecision':'When all competing fits have witnesses, these rims cannot select transverse scale even under exact circularity within the stated picking boxes. A sharper independently bounded observation or a known transverse board-plane distance is needed; do not tighten uncertainty to select a fit.'}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');a=p.parse_args()
    def stable(v):
        if isinstance(v,float):return round(v,6)+0.0
        if isinstance(v,list):return [stable(x) for x in v]
        if isinstance(v,dict):return {k:stable(x) for k,x in v.items()}
        return v
    text=json.dumps(stable(build()),indent=2)+'\n'
    if a.check:
        if TARGET.read_text()!=text:raise SystemExit('Stale mounting-hole shape review')
    else:TARGET.parent.mkdir(parents=True,exist_ok=True);TARGET.write_text(text)
    print(TARGET)
