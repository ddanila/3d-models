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
    connectivity = read('generated/connectivity.json')['components']
    cross = result['crossSide']
    latch_paths = result.get('latchPaths', [])
    for path in latch_paths:
        if path['nativeCopper'] is not False or path['continuityEstablished'] is not False:
            raise ValueError('Latch candidates cannot assign copper or continuity')
        if path.get('reverseReview', {}).get('continuityEstablished', False) is not False:
            raise ValueError('Latch eye correspondence is not established')
        constraint = path.get('referenceConstraints')
        if constraint:
            constraint['terminals'] = [dict(terminal=t,net=connectivity[t.split(':')[0]]['pins'][t.split(':')[1]]) for t in constraint['terminals']]
            constraint['compatibleWithTarget'] = any(t['net']==path['referenceNet'] for t in constraint['terminals'])
            constraint['physicalIdentityEstablished'] = False
    records = [cross, cross['comparison'], *result['paths'], *latch_paths,
               *[p['reverseReview'] for p in latch_paths if 'reverseReview' in p]]
    records.extend(result.get('eyeReview', {}).get('comparisons', []))
    for trial in result.get('registrationTrials', []):
        if trial['copperAssignmentQualified'] is not False:
            raise ValueError('Registration trials cannot qualify copper')
        records.extend([trial, dict(source=trial['bottomSource'], sourceSha256=trial['bottomSourceSha256'])])
        anchors, checks = trial['anchors'], trial['checks']
        for key in ('id', 'photoPixel', 'bottomPixel'):
            if len({str(p[key]) for p in anchors+checks}) != len(anchors+checks):
                raise ValueError('Registration trial checks must be independent')
        if len(anchors)!=4 or len(checks)<4:
            raise ValueError('Registration trial needs four anchors and independent checks')
        fit = homography([p['photoPixel'] for p in anchors], [p['bottomPixel'] for p in anchors])
        from bottom_registration import inside_hull
        region = next(r for r in read('generated/bottom-registration.json')['pcbRegions'] if r['id']==trial['bottomRegion'])
        for check in checks:
            predicted = project(fit, check['photoPixel'])
            check.update(projectedBottomPixel=[round(v,9) for v in predicted],
                         residualPixels=round(math.dist(predicted,check['bottomPixel']),9),
                         insideBottomFitHull=inside_hull(check['bottomPixel'],region['anchorHull']))
        trial['maxCheckResidualPixels'] = max(c['residualPixels'] for c in checks)
        trial['anchorsInsideBottomFitHull'] = all(inside_hull(a['bottomPixel'],region['anchorHull']) for a in anchors)
    for path in latch_paths:
        for comparison in path.get('comparisons', []):
            records.append(comparison)
            comparison['electricalIdentityTransferred'] = False
        terminal = path.get('terminalReview')
        if terminal:
            if (terminal['nativeCopper'] is not False or terminal['continuityEstablished'] is not False
                    or terminal['terminal'] not in path['terminals']):
                raise ValueError('Terminal review cannot establish latch continuity')
            records.extend([terminal, terminal['topReview']])
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
        reverse['positionCheck'] = {'residualMm': round(residual, 9), 'toleranceMm': min(limits),
                                    'withinFitBudget': residual <= min(limits), 'continuityEstablished': False}
        bottom_region = next(r for r in read('generated/bottom-registration.json')['pcbRegions']
                             if r['id'] == reverse['registrationRegions']['bottom'])
        alternatives = reverse.get('alternatives', [])
        if len({a['id'] for a in alternatives}) != len(alternatives):
            raise ValueError('Duplicate alternative eye identifier')
        for alternative in alternatives:
            if alternative['kind'] not in ('eye', 'pad') or not inside_hull(alternative['point'], bottom_region['anchorHull']):
                raise ValueError('Alternative feature exceeds local fit hull or has invalid kind')
            distance = math.dist(projections['top'], project(bottom_region['photoToModel'], alternative['point']))
            alternative['positionCheck'] = {'residualMm': round(distance, 9), 'toleranceMm': min(limits),
                                           'withinFitBudget': distance <= min(limits), 'continuityEstablished': False}
        reverse['alternatives'] = sorted(alternatives, key=lambda a: (a['positionCheck']['residualMm'], a['id']))
        continuation = reverse.get('continuationProjection')
        if continuation:
            region = next(r for r in read('generated/top-registration.json')['pcbRegions'] if r['id'] == continuation['region'])
            point = project(region['bottomToTop'],reverse['unassignedEnd'])
            continuation.update(point=[round(v,9) for v in point],
                                insideFitHull=inside_hull(reverse['unassignedEnd'],region['bottomHull']),
                                continuityEstablished=False)
    eye_review = result.get('eyeReview')
    if eye_review:
        from bottom_registration import inside_hull
        region = next(r for r in read('generated/top-registration.json')['pcbRegions'] if r['id'] == eye_review['region'])
        bottom_region = next(r for r in read('generated/bottom-registration.json')['pcbRegions'] if r['id'] == region['bottomRegion'])
        if not region['copperAssignmentQualified']:
            raise ValueError('Bus eye review requires a qualified eye fit')
        eye_review['maxCheckResidualMm'] = region['maxCheckResidualMm']
        eye_review['toleranceMm'] = region['toleranceMm']
        for target in eye_review['targets']:
            if any(target['top']==a['photoPixel'] or target['bottom']==a['bottomPixel'] for a in region['anchors']):
                raise ValueError('Bus target must not be its own eye fit anchor')
            residual = math.dist(project(region['photoToModel'],target['top']),project(bottom_region['photoToModel'],target['bottom']))
            target.update(residualMm=round(residual,9),
                          insideFitHull=inside_hull(target['top'],region['anchorHull']) and inside_hull(target['bottom'],region['bottomHull']),
                          withinFitBudget=residual<=region['toleranceMm'],continuityEstablished=False)
        for comparison in eye_review['comparisons']:
            comparison['electricalIdentityTransferred'] = False
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
    for path in latch_paths:
        terminal = path.get('terminalReview')
        if not terminal or 'projectionRegion' not in terminal:
            continue
        recorded = terminal['point']==bottom_pins.get(terminal['terminal'])
        if not recorded and terminal.get('landmarkRouteGroup'):
            layout = read('generated/layout.json')
            ref,pin = terminal['terminal'].split(':')
            pad = next(p['position'] for c in layout['components'] if c['ref']==ref for p in c['pads'] if p['pin']==pin)
            for route in layout['routes']:
                if route['side']!='bottom' or route['evidence'].get('group')!=terminal['landmarkRouteGroup']:
                    continue
                for photo in route['evidence']['sources']:
                    if photo['id']!='photo-bottom':continue
                    recorded |= any(pixel==terminal['point'] and math.dist(model,pad)<=.000002
                                    for pixel,model in zip(photo['locator']['pixelSegment'],route['points']))
        if terminal['source']!='photo-bottom' or not recorded:
            raise ValueError('Terminal search must use the recorded underside pin landmark')
        region = next(r for r in read('generated/top-registration.json')['pcbRegions'] if r['id']==terminal['projectionRegion'])
        if not region['copperAssignmentQualified']:
            raise ValueError('Terminal search needs a qualified local fit')
        point = project(region['bottomToTop'],terminal['point'])
        endpoint = path['segments'][-1]['points'][-1]
        bounded = inside_hull(terminal['point'],region['bottomHull']) and inside_hull(endpoint,region['anchorHull'])
        separation = math.dist(project(region['photoToModel'],point),project(region['photoToModel'],endpoint)) if bounded else None
        terminal['topProjection'] = dict(point=[round(v,9) for v in point],insideFitHull=bounded,
                                         endpointSeparationMm=round(separation,9) if separation is not None else None,
                                         continuityEstablished=False)
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
