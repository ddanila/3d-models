#!/usr/bin/env python3
"""Compare a conditional published X1 pitch with retained photo projections."""
import argparse
import difflib
import hashlib
import json
import math
from pathlib import Path
from photo_registration import homography, project

ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/'reference/package-reviews/efs-x1/assessment.json'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def row_review(points, candidate):
    if len(points)!=candidate['contactsPerRow'] or any(len(p)!=2 or not all(map(math.isfinite,p)) for p in points):
        raise ValueError('Invalid projected contact row')
    start,end=points[0],points[-1]
    span=math.dist(start,end)
    if span<=0:raise ValueError('Degenerate contact row')
    intervals=len(points)-1
    pitch=candidate['contactPitchNominalMm']
    if abs(pitch*intervals-candidate['contactSpanNominalMm'])>1e-9:raise ValueError('Inconsistent catalogue span')
    # Endpoints set the direction and observed scale. Interior points are withheld
    # from that fit; their residual checks straightness, not absolute metrology.
    residuals=[math.dist(p,[start[k]+(end[k]-start[k])*i/intervals for k in range(2)]) for i,p in enumerate(points) if 0<i<intervals]
    return {'projectedEndpointSpanMm':span,'projectedPitchMm':span/intervals,
            'catalogueMinusProjectedSpanMm':pitch*intervals-span,
            'conditionalScaleMultiplier':pitch*intervals/span,
            'interiorResidualToEndpointFitMm':residuals,
            'maximumInteriorResidualMm':max(residuals)}

def build():
    names=['reference/connector-package-candidate.json','generated/connector-review.json','generated/bus-review.json','component-evidence.json','sense-review.json','tools/connector_package_review.py','tools/photo_registration.py']
    candidate=json.loads((ROOT/names[0]).read_text())
    observation=json.loads((ROOT/names[1]).read_text())
    result={name:{row:row_review(points,candidate['candidate']) for row,points in rows.items()}
            for name,rows in [('topLeadEnds',observation['projectedLeadEndRowsMm']),('undersideJoints',observation['underside']['projectedJointRowsMm'])]}
    sense=json.loads((ROOT/'sense-review.json').read_text())
    metric=json.loads((ROOT/'generated/bus-review.json').read_text())['senseReview']['metricReview']
    observed=json.loads((ROOT/'component-evidence.json').read_text())['X1']['physicalReview']['underside']
    if observed['photoSha256']!=sense['sourceSha256']:
        raise ValueError('Metric and connector observations must use the same photograph')
    if any(pin.startswith('X1:') for pair in metric['calibrationPairs'] for pin in pair):
        raise ValueError('X1 cannot calibrate its own independent check')
    h=homography(sense['envelopeTrial']['photoCorners'],[[-.5,.5],[-.5,-.5],[.5,-.5],[.5,.5]])
    calibrations=[{'id':'nominal-board-envelope','estimatedEnvelopeMm':metric['nominalEnvelopeMm']}]+metric['variants']
    trials=[]
    uncertainty=observed['pixelUncertainty']
    if not math.isfinite(uncertainty) or uncertainty<0:raise ValueError('Invalid pixel uncertainty')
    catalogue=candidate['candidate']['contactSpanL3Mm']
    catalogue_interval=[catalogue['nominal']-catalogue['tolerance'],catalogue['nominal']+catalogue['tolerance']]
    for trial in calibrations:
        size=trial['estimatedEnvelopeMm']
        def mapped(point):return [v*scale for v,scale in zip(project(h,point),size)]
        rows={}
        for row,pixels in observed['jointRowsPixels'].items():
            points=[mapped(p) for p in pixels]
            record=row_review(points,candidate['candidate'])
            radii=[]
            for pixel,point in [(pixels[0],points[0]),(pixels[-1],points[-1])]:
                # A projective rectangle stays convex when its denominator keeps
                # one sign. Its farthest mapped point is then a corner.
                corners=[[pixel[0]+dx*uncertainty,pixel[1]+dy*uncertainty] for dx in (-1,1) for dy in (-1,1)]
                denominators=[h[6]*p[0]+h[7]*p[1]+h[8] for p in corners]
                if min(denominators)<=0<=max(denominators):raise ValueError('Uncertainty crosses projection pole')
                radii.append(max(math.dist(mapped(p),point) for p in corners))
            radius=sum(radii);span=record['projectedEndpointSpanMm']
            interval=[max(0,span-radius),span+radius]
            record.update(endpointPickingSpanIntervalMm=interval,
                catalogueSpanIntervalMm=catalogue_interval,
                pickingIntervalOverlapsCatalogue=max(interval[0],catalogue_interval[0])<=min(interval[1],catalogue_interval[1]))
            rows[row]=record
        trials.append({'id':trial['id'],'estimatedEnvelopeMm':size,'connectorExcludedFromCalibration':True,
                      'packagePoseChecksEvaluated':'packagePoses' in trial,
                      'failedPackagePoseChecks':[p['ref'] for p in trial.get('packagePoses',[]) if not p['withinPhotoTolerance']],
                      'rows':rows})
    return {'schema':1,'candidate':candidate['id'],'sources':{name:digest(ROOT/name) for name in names},
            'comparisons':result,'independentPackageScaleChecks':trials,
            'bodyWidthAlternativesBMm':candidate['candidate']['bodyWidthAlternativesBMm'],
            'bodyWidthSelection':candidate['candidate']['bodyWidthSelection'],
            'bodyWidthScope':'Both catalogue rows include 26-contact configurations and share longitudinal dimensions. Contact-span agreement cannot select a width; mating-face and form evidence are still required.',
            'uncertaintyScope':'Endpoint picking only: plus/minus the recorded pixel uncertainty on both image axes, propagated through each fixed homography. Excludes board-corner, package-pitch, cross-row-spacing and calibration uncertainty; overlap is not package identification or a registration pass.',
            'installedIdentityConfirmed':False,'padPlacementAuthorized':False,
            'allPickingIntervalsOverlapCatalogue':all(row['pickingIntervalOverlapsCatalogue'] for trial in trials for row in trial['rows'].values()),
            'scope':'Conditional catalogue contact pitch compared with projected visible lead ends and underside joints. Endpoint-based interior residuals test row regularity only. No registration qualification, physical continuity, automatic scaling, package adoption or mating-clearance claim.',
            'nextAction':'Use the manufacturer CPU-pitch calibration as a conditional cross-check, retaining its failed package-pose checks. Do not select the legacy CPU pitch because it fits X1 better. Resolve board-plane registration and detailed connector form before changing native pads or the reference adapter.'}

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    # Retain nanometre precision in mm; libm's last bits vary across hosts.
    def stable(value):
        if isinstance(value,float):return round(value,9)+0.0
        if isinstance(value,list):return [stable(v) for v in value]
        if isinstance(value,dict):return {k:stable(v) for k,v in value.items()}
        return value
    text=json.dumps(stable(build()),indent=2)+'\n'
    if args.check:
        if TARGET.read_text()!=text:
            diff=list(difflib.unified_diff(TARGET.read_text().splitlines(),text.splitlines(),fromfile='retained',tofile='computed'))
            raise SystemExit('Stale X1 package comparison\n'+'\n'.join(diff[:40]))
        print('X1 conditional package comparison matches sources')
    else:
        TARGET.parent.mkdir(parents=True,exist_ok=True);TARGET.write_text(text)
        print(text)

if __name__=='__main__':main()
