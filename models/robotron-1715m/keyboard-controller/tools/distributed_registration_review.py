#!/usr/bin/env python3
"""Conditional distributed metric fit; no native geometry is changed."""
import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path
from photo_registration import homography, project

ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/'reference/package-reviews/distributed-registration/assessment.json'


def solve(matrix, rhs):
    rows=[list(a)+[b] for a,b in zip(matrix,rhs)];n=len(rows)
    for i in range(n):
        pivot=max(range(i,n),key=lambda j:abs(rows[j][i]));rows[i],rows[pivot]=rows[pivot],rows[i]
        if abs(rows[i][i])<1e-15:raise ValueError('Singular fit')
        scale=rows[i][i];rows[i]=[v/scale for v in rows[i]]
        for j in range(n):
            if j!=i:
                scale=rows[j][i];rows[j]=[a-scale*b for a,b in zip(rows[j],rows[i])]
    return [r[-1] for r in rows]


def fit(points,targets,cpu,span):
    if len(points)!=26 or len(targets)!=26 or len(cpu)!=2 or not math.isfinite(span) or span<=0:
        raise ValueError('Expected two complete X1 rows and two CPU spans')
    def normalized(p):return [(p[0]-1200)/1000,(p[1]-1900)/1000]
    points=[normalized(p) for p in points];cpu=[[normalized(p) for p in pair] for pair in cpu]
    corners=[0,12,13,25]
    h=homography([points[i] for i in corners],[targets[i] for i in corners])[:8]
    def residuals(h):
        matrix=h+[1]
        values=[(a-b)/math.sqrt(len(points)) for p,t in zip(points,targets)
                for a,b in zip(project(matrix,p),t)]
        return values+[(math.dist(project(matrix,a),project(matrix,b))-span)/math.sqrt(len(cpu)) for a,b in cpu]
    damping=1e-5;converged=False
    for iteration in range(100):
        r=residuals(h);cost=sum(v*v for v in r);columns=[]
        for i in range(8):
            delta=1e-6*max(1,abs(h[i]));trial=h[:];trial[i]+=delta
            columns.append([(a-b)/delta for a,b in zip(residuals(trial),r)])
        gram=[[sum(a*b for a,b in zip(x,y)) for y in columns] for x in columns]
        gradient=[sum(a*b for a,b in zip(x,r)) for x in columns]
        if max(abs(v) for v in gradient)<1e-7:converged=True;break
        for i in range(8):gram[i][i]+=damping*max(1,gram[i][i])
        step=solve(gram,[-v for v in gradient]);trial=[a+b for a,b in zip(h,step)]
        trial_cost=sum(v*v for v in residuals(trial))
        if trial_cost<cost:
            h=trial;damping=max(1e-12,damping/3)
            if cost-trial_cost<1e-12:converged=True;break
        else:damping*=10
    return h+[1],{'converged':converged,'iterations':iteration+1,'weightedSquaredResidual':sum(v*v for v in residuals(h))}


def build():
    names=['reference/efs-form-constraints.json','component-evidence.json','bottom-landmarks.json',
           'sense-review.json','generated/layout.json','tools/distributed_registration_review.py','tools/photo_registration.py']
    form,component,bottom,sense,layout=[json.loads((ROOT/n).read_text()) for n in names[:5]]
    obs=component['X1']['physicalReview']['underside']
    if obs['photoSha256']!=sense['sourceSha256']:raise ValueError('Different photos')
    pattern=form['commonPcbPattern'];pixels={}
    for region in [bottom]+bottom['pcbRegions']:
        for p in region['anchors']+region['checks']:
            key=p['ref']+':'+p['pin']
            if key in pixels and pixels[key]!=p['photoPixel']:raise ValueError('Conflicting picks')
            pixels[key]=p['photoPixel']
    points=[p for row in ('housingFar','housingNear') for p in obs['jointRowsPixels'][row]]
    targets=[[x,i*pattern['longitudinalPitchMm']] for x in (0,pattern['rowSeparationMm']) for i in range(pattern['contactsPerRow'])]
    pairs=[('A5:1','A5:20'),('A5:40','A5:21')];cpu=[[pixels[a],pixels[b]] for a,b in pairs]
    span=sense['metricReview']['cpuReference']['longitudinalEndSpanMm']
    checks=[]
    for c in layout['components']:
        if c['ref'] not in ('A1','A2.1','A4','A8'):continue
        pads={int(p['pin']):p['position'] for p in c['pads']};half=len(pads)//2
        for row in (range(1,half+1),range(half+1,2*half+1)):
            available=[i for i in row if c['ref']+':'+str(i) in pixels]
            if len(available)<2:continue
            a,b=min(available),max(available);keys=[c['ref']+':'+str(i) for i in (a,b)]
            checks.append((keys,math.dist(pads[a],pads[b])))
    def evaluate(points,cpu):
        h,status=fit(points,targets,cpu,span)
        def mapped(p):return project(h,[(p[0]-1200)/1000,(p[1]-1900)/1000])
        den=[h[6]*(p[0]-1200)/1000+h[7]*(p[1]-1900)/1000+1 for p in sense['envelopeTrial']['photoCorners']]
        result={'optimizer':status,'normalizedPhotoToMetric':h,'poleCrossesBoard':min(den)<=0<=max(den),
                'maximumConnectorResidualMm':max(math.dist(mapped(p),t) for p,t in zip(points,targets)),
                'cpuSpanResidualsMm':[math.dist(mapped(a),mapped(b))-span for a,b in cpu],
                'unconstrainedCpuCrossRowDistancesMm':[math.dist(mapped(cpu[0][i]),mapped(cpu[1][i])) for i in (0,1)],
                'projectedBoardCornersMm':[mapped(p) for p in sense['envelopeTrial']['photoCorners']],
                'heldOutSameRowChecks':[{'terminals':keys,'nominalNativeSpanMm':expected,
                                        'projectedSpanMm':math.dist(mapped(pixels[keys[0]]),mapped(pixels[keys[1]])),
                                        'minimumEndpointResidualMm':abs(math.dist(mapped(pixels[keys[0]]),mapped(pixels[keys[1]]))-expected)/2}
                                       for keys,expected in checks]}
        return result
    baseline=evaluate(points,cpu);trials=[]
    # Correlated row shifts avoid pretending that 26 picks are independent.
    for signs in itertools.product((-1,1),repeat=2):
        shifted=[[p[0]+obs['pixelUncertainty']*signs[i//13],p[1]] for i,p in enumerate(points)]
        result=evaluate(shifted,cpu);trials.append({'rowXShiftSigns':list(signs),**result})
    return {'schema':1,'sources':{n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in names},
            'fitScope':'Equal total squared-residual weights for X1 and CPU. X1 nominal pattern and CPU manufacturer longitudinal span only; no DIP row-spacing constraint. Coordinate normalization: (pixel-[1200,1900])/1000.',
            'nominal':baseline,'systematicPickingTrials':trials,'pointBudgetMm':bottom['toleranceMm'],
            'registrationQualified':False,'padPlacementAuthorized':False,
            'limits':'Held-out spans use nominal native longitudinal dimensions, not independently measured specimens. Span agreement is necessary but cannot validate absolute placement or cross-side registration. Correlated transverse shifts are sensitivity examples, not complete uncertainty bounds. Manufacturing tolerances, other picking modes and lens distortion remain unbounded.'}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');args=p.parse_args()
    def stable(v):
        if isinstance(v,float):return round(v,6)+0.0
        if isinstance(v,list):return [stable(x) for x in v]
        if isinstance(v,dict):return {k:stable(x) for k,x in v.items()}
        return v
    text=json.dumps(stable(build()),indent=2)+'\n'
    if args.check:
        if TARGET.read_text()!=text:raise SystemExit('Stale distributed registration assessment')
    else:TARGET.parent.mkdir(parents=True,exist_ok=True);TARGET.write_text(text)
    print('Distributed registration assessment checked' if args.check else TARGET)
