#!/usr/bin/env python3
"""Test whether outline perspective independently constrains board aspect ratio."""
import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path
from photo_registration import homography

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT/'reference/package-reviews/outline-metric/assessment.json'


def estimate(corners, principal):
    h = homography([[0,0],[1,0],[1,1],[0,1]], corners)
    cx,cy = principal
    a = [h[0]-cx*h[6], h[3]-cy*h[6]]
    b = [h[1]-cx*h[7], h[4]-cy*h[7]]
    denominator = h[6]*h[7]
    if abs(denominator) < 1e-18:
        raise ValueError('Outline does not identify focal length')
    focal_squared = -sum(x*y for x,y in zip(a,b))/denominator
    if not math.isfinite(focal_squared) or focal_squared <= 0:
        raise ValueError('No positive focal length under these assumptions')
    lengths = [sum(v*v/focal_squared for v in xy)+z*z for xy,z in ((a,h[6]),(b,h[7]))]
    return {'focalPixels': math.sqrt(focal_squared),
            'longToShortAspect': math.sqrt(lengths[1]/lengths[0])}


def sweep(corners, size, displacement):
    results = []; invalid = 0
    # A sensitivity experiment, not measured uncertainty or a confidence interval.
    for dx,dy in itertools.product((-.01,0,.01), repeat=2):
        center = [size[0]*(.5+dx), size[1]*(.5+dy)]
        for signs in itertools.product((-1,1), repeat=8):
            trial = [[p[axis]+displacement*signs[2*i+axis] for axis in range(2)]
                     for i,p in enumerate(corners)]
            try:
                results.append(estimate(trial,center))
            except ValueError:
                invalid += 1
    return {'cornerCoordinatePerturbationPixels': displacement,
            'principalPointOffsetsFractionOfImage': [-.01,0,.01],
            'validSamples': len(results), 'incompatibleOrUnidentifiedSamples': invalid,
            'sampledRanges': {key:[round(min(r[key] for r in results),6), round(max(r[key] for r in results),6)]
                              for key in ('focalPixels','longToShortAspect')} if results else None}


def build():
    names = ('photo-landmarks.json','bottom-landmarks.json','sense-review.json',
             'tools/photo_registration.py','tools/outline_metric_review.py')
    top = json.loads((ROOT/names[0]).read_text())
    bottom = json.loads((ROOT/names[1]).read_text())
    sense = json.loads((ROOT/names[2]).read_text())
    cases = []
    for name,points,size in [('primary-top',top['photoCorners'],top['imageSize']),
                            ('primary-bottom',sense['envelopeTrial']['photoCorners'],bottom['imageSize'])]:
        result = estimate(points,[v/2 for v in size])
        cases.append({'photo': name, 'corners': points, 'imageSize':size,
                      'centeredCameraEstimate':{k:round(v,6) for k,v in result.items()},
                      'sensitivity':[sweep(points,size,d) for d in (1,8)]})
    return {'schema':1, 'sources':{n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in names},
            'cases':cases, 'registrationQualified':False, 'dimensionsAdopted':False,
            'assumptions':['Planar rectangular board outline.', 'Undistorted pinhole image with square pixels and zero skew.',
                           'Principal point at image center for the nominal calculation; no independent camera calibration is available.'],
            'scope':'Orthogonal vanishing-direction calculation from existing outline corners, independent of DIP row spacing. It estimates aspect ratio only, not absolute scale. Corner perturbations and principal-point offsets are illustrative sensitivity samples, not measured bounds, probabilities or confidence intervals. Lens correction, crop and corner-picking errors are not identified by this calculation. No failed sample is discarded from the reported count, and no geometry is promoted.',
            'nextAction':'Use independent camera/outline constraints or board-plane metrology before treating outline perspective as a replacement for package calibration.'}


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    text=json.dumps(build(),indent=2)+'\n'
    if args.check:
        if TARGET.read_text()!=text:raise SystemExit('Stale outline metric diagnostic')
        print('Outline metric diagnostic matches sources')
    else:
        TARGET.parent.mkdir(parents=True,exist_ok=True);TARGET.write_text(text)
        for c in json.loads(text)['cases']:print(c['photo'],c['centeredCameraEstimate'],c['sensitivity'])
