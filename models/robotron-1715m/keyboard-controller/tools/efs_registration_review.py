#!/usr/bin/env python3
"""Test conditional X1 calibration against independent CPU row spans.

Corner perturbations are sensitivity witnesses, not interval bounds or a random
error model. Neither fitted connector residuals nor overlapping ranges qualify
whole-board registration.
"""
import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path
from photo_registration import homography, project

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / 'reference/package-reviews/efs-registration/assessment.json'


def build():
    names = ['reference/efs-form-constraints.json', 'component-evidence.json',
             'bottom-landmarks.json', 'sense-review.json',
             'tools/efs_registration_review.py', 'tools/photo_registration.py']
    source = {n: hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in names}
    form, components, bottom, sense = [json.loads((ROOT/n).read_text()) for n in names[:4]]
    obs = components['X1']['physicalReview']['underside']
    if obs['photoSha256'] != sense['sourceSha256']:
        raise ValueError('Different photographs')
    pattern = form['commonPcbPattern']
    rows = obs['jointRowsPixels']; count = pattern['contactsPerRow']
    if any(len(row) != count for row in rows.values()):
        raise ValueError('Unexpected row population')
    pixels = [rows[row][i] for row in ('housingFar', 'housingNear') for i in (0, count-1)]
    targets = [[x, y] for x in (0, pattern['rowSeparationMm'])
               for y in (0, pattern['contactSpanMm'])]
    nominal = homography(pixels, targets)
    cpu = {v['pin']: v['photoPixel'] for v in bottom['checks'] if v['ref'] == 'A5'}
    pairs = [('1', '20'), ('40', '21')]
    expected = sense['metricReview']['cpuReference']['longitudinalEndSpanMm']
    tolerance = bottom['toleranceMm']
    def spans(h):
        return [math.dist(project(h, cpu[a]), project(h, cpu[b])) for a,b in pairs]
    baseline = spans(nominal)
    residuals = [math.dist(project(nominal, p), [x, i*pattern['longitudinalPitchMm']])
                 for x,row in zip((0,pattern['rowSeparationMm']), ('housingFar','housingNear'))
                 for i,p in enumerate(rows[row]) if 0 < i < count-1]
    uncertainty = obs['pixelUncertainty']
    extrema = [[v,v] for v in baseline]; poles = 0; witnesses = []
    # All coordinate-box vertices of the four fitting picks. Denominator sign
    # is checked across the entire observed board outline, not only the fit.
    outline = sense['envelopeTrial']['photoCorners']
    for signs in itertools.product((-1,1), repeat=8):
        perturbed = [[p[k]+uncertainty*signs[2*i+k] for k in range(2)] for i,p in enumerate(pixels)]
        h = homography(perturbed, targets)
        den = [h[6]*p[0]+h[7]*p[1]+h[8] for p in outline]
        if min(den) <= 0 <= max(den):
            poles += 1
            if not witnesses: witnesses.append({'anchorCoordinateSigns':list(signs),'reason':'projection pole crosses board outline'})
            continue
        for v, limits in zip(spans(h), extrema):
            limits[0] = min(limits[0], v); limits[1] = max(limits[1], v)
    return {
        'schema':1, 'sources':source, 'photoSha256':obs['photoSha256'],
        'condition':form['condition'], 'fit':'Four outer X1 solder-joint centres to the shared nominal rectangular hole pattern; no CPU calibration.',
        'anchorPixels':pixels, 'targetMm':targets,
        'maximumInteriorConnectorResidualMm':max(residuals),
        'heldOutCpuChecks':[{'pins':list(pair),'expectedSpanMm':expected,'projectedSpanMm':v,
                            'minimumPossibleMaximumEndpointResidualMm':abs(v-expected)/2,
                            'exceedsExistingPointBudget':abs(v-expected)>2*tolerance,
                            'sampledAnchorPerturbationSpanRangeMm':limits}
                           for pair,v,limits in zip(pairs,baseline,extrema)],
        'registrationPointBudgetMm':tolerance,
        'sensitivity':{'anchorPixelUncertainty':uncertainty,'coordinateBoxVertices':256,
                       'boardPoleCases':poles,'poleWitness':witnesses,
                       'scope':'Deterministic corner witnesses only, not certified extrema, confidence intervals or a probability model. Excludes held-out picking error and manufacturing tolerance.'},
        'registrationQualified':False,'padPlacementAuthorized':False,
        'nominalCpuSpanChecksPassed':all(abs(v-expected)<=2*tolerance for v in baseline),
        'finding':'Independent CPU spans test the exact nominal endpoint fit only. Anchor-picking witnesses describe extrapolation sensitivity; fitted X1 regularity cannot qualify the global board.',
        'nextAction':'Test a distributed joint fit using common X1 geometry and independent longitudinal package pitches, retaining held-out board-plane checks and systematic picking uncertainty. Obtain PCB tolerance constraints before physical admission.'}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');a=p.parse_args()
    def stable(v):
        if isinstance(v,float):return round(v,8)+0.0
        if isinstance(v,list):return [stable(x) for x in v]
        if isinstance(v,dict):return {k:stable(x) for k,x in v.items()}
        return v
    text=json.dumps(stable(build()),indent=2)+'\n'
    if a.check:
        if TARGET.read_text()!=text:raise SystemExit('Stale conditional X1 registration review')
    else:
        TARGET.parent.mkdir(parents=True,exist_ok=True);TARGET.write_text(text)
    print('Conditional X1 registration review matches sources' if a.check else str(TARGET))

if __name__=='__main__':main()
