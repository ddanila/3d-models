"""Locate hidden bus eyes across photographs without assigning native copper."""
import copy, hashlib, json, math
from pathlib import Path
from photo_registration import homography, project

ROOT = Path(__file__).resolve().parents[1]

def build(root=ROOT):
    read = lambda name: json.loads((root / name).read_text())
    result = copy.deepcopy(read('bus-review.json'))
    sources = {s['id']: s for s in read('evidence.json')['sources']}
    top, bottom = read('photo-landmarks.json'), read('bottom-landmarks.json')
    cross = result['crossSide']
    latch_paths = result.get('latchPaths', [])
    for path in latch_paths:
        if path['nativeCopper'] is not False or path['continuityEstablished'] is not False:
            raise ValueError('Latch candidates cannot assign copper or continuity')
        if path.get('reverseReview', {}).get('continuityEstablished', False) is not False:
            raise ValueError('Latch eye correspondence is not established')
    records = [cross, cross['comparison'], *result['paths'], *latch_paths,
               *[p['reverseReview'] for p in latch_paths if 'reverseReview' in p]]
    for record in records:
        source = sources[record['source']]
        if (record['sourceSha256'] != source['sha256'] or
                hashlib.sha256((root / source['path']).read_bytes()).hexdigest() != source['sha256']):
            raise ValueError('Bus review source hash mismatch: ' + source['id'])
    for path in latch_paths:
        reverse = path.get('reverseReview')
        if not reverse or 'registrationRegions' not in reverse:
            continue
        projections = {}
        limits = []
        for side, region_id in reverse['registrationRegions'].items():
            region = next(r for r in read('generated/' + side + '-registration.json')['pcbRegions'] if r['id'] == region_id)
            if not region['copperAssignmentQualified']:
                raise ValueError('Latch search requires reviewed local fits')
            point = path['segments'][-1]['points'][-1] if side == 'top' else reverse['point']
            from bottom_registration import inside_hull
            if not inside_hull(point, region['anchorHull']):
                raise ValueError('Latch search exceeds local fit hull')
            projections[side] = project(region['photoToModel'], point)
            limits.append(region['toleranceMm'])
        residual = math.dist(projections['top'], projections['bottom'])
        reverse['positionCheck'] = {'residualMm': residual, 'toleranceMm': min(limits),
                                    'withinFitBudget': residual <= min(limits), 'continuityEstablished': False}
    if sources[cross['source']]['path'] != top['photo']:
        raise ValueError('Bus review top landmarks use a different photograph')
    bottom_pins = {}
    for region in [bottom, *bottom['pcbRegions']]:
        for pin in region['anchors'] + region['checks']:
            key = pin['ref'] + ':' + pin['pin']
            if key in bottom_pins and bottom_pins[key] != pin['photoPixel']:
                raise ValueError('Conflicting underside landmark: ' + key)
            bottom_pins[key] = pin['photoPixel']
    top_pins = {ref + ':' + pin: point for ref, c in top['components'].items()
                for pin, point in {**c['pins'], **c.get('checkPins', {})}.items()}
    anchors, checks = cross['anchorTerminals'], cross['checkTerminals']
    if len(set(anchors)) != 4 or not checks or set(anchors) & set(checks):
        raise ValueError('Bus search needs four unique anchors and independent checks')
    fit = homography([bottom_pins[t] for t in anchors], [top_pins[t] for t in anchors])
    cross['checks'] = [{'terminal': t, 'residualPixels': round(math.dist(project(fit, bottom_pins[t]), top_pins[t]), 3)} for t in checks]
    cross['copperAssignmentQualified'] = False
    cross['comparison']['electricalIdentityTransferred'] = False
    # A search margin, not a statistical uncertainty or fabrication tolerance.
    radius = max(16, math.ceil(max(c['residualPixels'] for c in cross['checks'])
                              + top['pixelUncertainty'] + bottom['pixelUncertainty']))
    polygon = cross['occluder']['polygon']
    def margin(point):
        edges = list(zip(polygon, polygon[1:] + polygon[:1]))
        signs = [(b[0]-a[0])*(point[1]-a[1])-(b[1]-a[1])*(point[0]-a[0]) for a,b in edges]
        inside = all(v >= 0 for v in signs) or all(v <= 0 for v in signs)
        distance = min(abs(v)/math.dist(a,b) for v,(a,b) in zip(signs,edges))
        return distance if inside else -distance
    for path in result['paths']:
        if path['nativeCopper'] is not False or sources[path['source']]['path'] != bottom['photo']:
            raise ValueError('Bus search must remain an underside review, not native copper')
        eye = next(p['point'] for p in path['observedEnds'] if p.get('kind') == 'unassigned-eye')
        point = [round(v, 3) for v in project(fit, eye)]
        path['crossSideSearch'] = {
            'point': point, 'radiusPixels': radius,
            'insideCpuBodyWithSearchMargin': margin(point) > radius,
            'status': 'projected-search-only', 'continuityEstablished': False,
        }
    return result
