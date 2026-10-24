#!/usr/bin/env python3
"""Compare a conditional published X1 pitch with retained photo projections."""
import argparse
import hashlib
import json
import math
from pathlib import Path

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
    names=['reference/connector-package-candidate.json','generated/connector-review.json','tools/connector_package_review.py']
    candidate=json.loads((ROOT/names[0]).read_text())
    observation=json.loads((ROOT/names[1]).read_text())
    result={name:{row:row_review(points,candidate['candidate']) for row,points in rows.items()}
            for name,rows in [('topLeadEnds',observation['projectedLeadEndRowsMm']),('undersideJoints',observation['underside']['projectedJointRowsMm'])]}
    return {'schema':1,'candidate':candidate['id'],'sources':{name:digest(ROOT/name) for name in names},
            'comparisons':result,'installedIdentityConfirmed':False,'padPlacementAuthorized':False,
            'scope':'Conditional catalogue contact pitch compared with projected visible lead ends and underside joints. Endpoint-based interior residuals test row regularity only. No registration qualification, physical continuity, automatic scaling, package adoption or mating-clearance claim.',
            'nextAction':'Resolve detailed connector form and independently constrain board-plane scale before changing native pads or the reference connector adapter.'}

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    text=json.dumps(build(),indent=2)+'\n'
    if args.check:
        if TARGET.read_text()!=text:raise SystemExit('Stale X1 package comparison')
        print('X1 conditional package comparison matches sources')
    else:
        TARGET.parent.mkdir(parents=True,exist_ok=True);TARGET.write_text(text)
        print(text)

if __name__=='__main__':main()
