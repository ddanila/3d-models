#!/usr/bin/env python3
"""Test an opposite-row offset while preserving the original rigid-fit failure."""
import argparse
import hashlib
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/'reference/package-reviews/a8-row-spacing/assessment.json'


def trial(pose, calibration, opposite):
    checks={p['terminal']:p for p in pose['checks']}
    if calibration not in opposite or not set(opposite)<=set(checks):
        raise ValueError('Calibration must identify an observed opposite-row terminal')
    if set(opposite)&set(pose['anchors']) or len(opposite)<3:
        raise ValueError('Require an independent opposite row with two held-out checks')
    offset=checks[calibration]['residualAcrossRowMm']
    result=[]
    for terminal,p in checks.items():
        across=p['residualAcrossRowMm']-(offset if terminal in opposite else 0)
        result.append({'terminal':terminal,'heldOut':p['heldOut'] and terminal!=calibration,
                       'residualAlongRowMm':p['residualAlongRowMm'],
                       'residualAcrossRowMm':round(across,9)+0.0,
                       'residualMm':round(math.hypot(p['residualAlongRowMm'],across),9)})
    return {'calibrationTerminal':calibration,'signedOppositeRowOffsetMm':offset,
            'checks':result,'maximumHeldOutResidualMm':max(p['residualMm'] for p in result if p['heldOut'])}


def build():
    paths=['generated/bus-review.json','generated/layout.json','tools/row_spacing_review.py']
    review=json.loads((ROOT/paths[0]).read_text())['senseReview']['metricReview']
    package=next(c for c in json.loads((ROOT/paths[1]).read_text())['components'] if c['ref']=='A8')
    pads={p['pin']:p['position'] for p in package['pads']}
    axis=[b-a for a,b in zip(pads['1'],pads['12'])];length=math.hypot(*axis)
    normal=[-axis[1]/length,axis[0]/length]
    native=sum((pads['24'][i]-pads['1'][i])*normal[i] for i in range(2))
    trials=[]
    for variant in review['variants']:
        pose=next(p for p in variant['packagePoses'] if p['ref']=='A8')
        assert pose['anchors']==['A8:1','A8:12']
        opposite=[p['terminal'] for p in pose['checks'] if int(p['terminal'].split(':')[1])>12]
        result=trial(pose,'A8:24',opposite)
        result.update(calibrationVariant=variant['id'],originalRigidFitMaximumMm=pose['maxHeldOutResidualMm'],
                      originalRigidFitWithinTolerance=pose['withinPhotoTolerance'],
                      unchangedToleranceMm=pose['toleranceMm'],
                      conditionalRowSpacingMm=round(abs(native+result['signedOppositeRowOffsetMm']),9))
        trials.append(result)
    return {'schema':1,'component':'A8','sources':{n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in paths},
            'nativeRowSpacingMm':round(abs(native),9),'trials':trials,
            'padPlacementAuthorized':False,'registrationQualified':False,
            'scope':'Counterfactual package-row translation only. Preserve the two same-row pose anchors and fit one normal offset using the opposite terminal adjacent to the first anchor (A8:24); A8:13 and A8:19 remain held out. No scale, row rotation or along-row correction is fitted. Original rigid-fit failures remain authoritative. The inferred spacing is conditional on photo registration and native calibration packages, not a measured package specification or proof of hole centres.',
            'nextAction':'Distinguish actual board-hole row spacing from solder-joint picking and projection bias using independent row observations before changing the A8 footprint or promoting copper.'}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');args=p.parse_args()
    text=json.dumps(build(),indent=2)+'\n'
    if args.check:
        if TARGET.read_text()!=text:raise SystemExit('Stale A8 row-spacing diagnostic')
        print('A8 row-spacing diagnostic matches sources')
    else:
        TARGET.parent.mkdir(parents=True,exist_ok=True);TARGET.write_text(text)
        for t in json.loads(text)['trials']:print(t['calibrationVariant'],t['conditionalRowSpacingMm'],t['maximumHeldOutResidualMm'])
