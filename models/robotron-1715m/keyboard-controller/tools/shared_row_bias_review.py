#!/usr/bin/env python3
"""Cross-check a shared row-spacing bias without fitting the target package."""
import argparse
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / 'reference/package-reviews/shared-row-bias/assessment.json'
TRAINING = ('A2.1', 'A4')
HELD_OUT = ('A5', 'A8')


def spacing(component):
    pads = {int(p['pin']): p['position'] for p in component['pads']}
    half = len(pads) // 2
    axis = [b-a for a, b in zip(pads[1], pads[half])]
    length = math.hypot(*axis)
    normal = [-axis[1]/length, axis[0]/length]
    width = sum((pads[2*half][i]-pads[1][i])*normal[i] for i in range(2))
    if width <= 0:
        raise ValueError('Expected positive numbered DIP row separation')
    return round(width, 9), half


def fit(training):
    if len(training) < 2 or len({p['ref'] for p in training}) != len(training):
        raise ValueError('Two distinct training packages required')
    numerator = denominator = 0.
    for package in training:
        width = package['widthMm']
        values = package['oppositeResidualsMm']
        if not math.isfinite(width) or width <= 0 or len(values) < 2 or not all(map(math.isfinite, values)):
            raise ValueError('Invalid independent row observations')
        # Give packages equal weight, regardless of how many joints were picked.
        numerator += width * sum(values)/len(values)
        denominator += width*width
    return numerator/denominator


def build():
    files = ('generated/bus-review.json', 'generated/layout.json', 'tools/shared_row_bias_review.py')
    review = json.loads((ROOT/files[0]).read_text())['senseReview']['metricReview']
    components = {c['ref']: c for c in json.loads((ROOT/files[1]).read_text())['components']}
    variants = []
    for variant in review['variants']:
        poses = {p['ref']: p for p in variant['packagePoses']}
        training = []
        for ref in TRAINING:
            width, half = spacing(components[ref])
            values = [p['residualAcrossRowMm'] for p in poses[ref]['checks']
                      if int(p['terminal'].split(':')[1]) > half]
            training.append({'ref': ref, 'widthMm': width, 'oppositeResidualsMm': values})
        fraction = fit(training)
        checks = []
        for ref in HELD_OUT:
            width, half = spacing(components[ref])
            pose = poses[ref]
            points = []
            for point in pose['checks']:
                if not point['heldOut']:
                    continue
                opposite = int(point['terminal'].split(':')[1]) > half
                across = point['residualAcrossRowMm'] - (fraction*width if opposite else 0)
                points.append({'terminal': point['terminal'], 'oppositeRow': opposite,
                    'originalResidualMm': point['fittedResidualMm'],
                    'predictedAcrossCorrectionMm': round(fraction*width if opposite else 0, 9),
                    'remainingAcrossMm': round(across, 9),
                    'unchangedAlongMm': point['residualAlongRowMm'],
                    'remainingResidualMm': round(math.hypot(across, point['residualAlongRowMm']), 9)})
            checks.append({'ref': ref, 'originalMaximumMm': pose['maxHeldOutResidualMm'],
                           'unchangedToleranceMm': pose['toleranceMm'], 'points': points,
                           'maximumHeldOutResidualMm': max(p['remainingResidualMm'] for p in points)})
        variants.append({'calibrationVariant': variant['id'], 'training': training,
                         'fractionalRowOffset': round(fraction, 12), 'heldOutPackages': checks})
    return {'schema': 1, 'sources': {n: hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in files},
            'variants': variants, 'registrationQualified': False, 'padPlacementAuthorized': False,
            'scope': 'Diagnostic shared fractional opposite-row offset fitted only to A2.1 and A4, with equal package weights. A5 and A8 do not enter that fit; their existing same-row pose anchors remain unchanged and other joints remain held out. Both retained calibration variants are reported. This is not a global projective registration or a measured package dimension. Shared photo picking, nominal footprint spacing, local lead forming and calibration bias remain confounded; original rigid fits and acceptance budgets are unchanged.',
            'nextAction': 'Use independent board-plane hole observations to distinguish shared registration/picking bias from installed row spacing. Do not change A8 alone on the basis of its conditional row-offset trial.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    text = json.dumps(build(), indent=2) + '\n'
    if args.check:
        if TARGET.read_text() != text:
            raise SystemExit('Stale shared row-bias diagnostic')
        print('Shared row-bias diagnostic matches sources')
    else:
        TARGET.parent.mkdir(parents=True, exist_ok=True)
        TARGET.write_text(text)
        for variant in json.loads(text)['variants']:
            print(variant['calibrationVariant'], variant['fractionalRowOffset'],
                  [(p['ref'], p['maximumHeldOutResidualMm']) for p in variant['heldOutPackages']])
