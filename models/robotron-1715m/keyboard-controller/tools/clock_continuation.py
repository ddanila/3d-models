"""Review a candidate clock continuation without joining hidden copper."""
import math
from photo_registration import homography, project
from bottom_registration import inside_hull


def fit(pairs, anchor_names, check_names):
    if set(anchor_names) & set(check_names) or len(anchor_names) != 4 or len(check_names) < 2:
        raise ValueError('Clock continuation needs independent fit checks')
    anchors = [dict(terminal=n, **pairs[n]) for n in anchor_names]
    hull = [a['bottomPixel'] for a in anchors]
    if not all(inside_hull(p, hull) for p in hull):
        raise ValueError('Clock anchors must form a convex boundary')
    h = homography(hull, [a['topPixel'] for a in anchors])
    checks = [dict(terminal=n, **pairs[n], residualPixels=math.dist(project(h, pairs[n]['bottomPixel']), pairs[n]['topPixel'])) for n in check_names]
    return dict(anchors=anchors, checks=checks, bottomToTop=h, bottomAnchorHull=hull,
                maxCheckResidualPixels=max(c['residualPixels'] for c in checks), copperAssignmentQualified=False)


def build(data, source):
    raw = data['clock-continuation.json']
    components = data['component-evidence.json']
    def top(name):
        ref, pin = name.split(':')
        return components[ref]['photoPins'][pin]
    bank = raw['bankRegistration']
    pairs = {n: dict(bottomPixel=p, topPixel=top(n)) for n, p in bank['bottomPins'].items()}
    registration = fit(pairs, bank['anchors'], bank['checks'])
    registration['scope'] = bank['scope']
    def prediction(reg, p):
        return dict(bottomPixel=p, projectedTopPixel=project(reg['bottomToTop'], p),
                    insideAnchorHull=inside_hull(p, reg['bottomAnchorHull']))
    start = components['R10.1']['signalBranchObservation']['pixelPolyline'][-1]
    clock_stop = prediction(registration, start)
    eye = raw['eyes']['bankReturn']
    matched = dict(eye, **prediction(registration, eye['bottomPixel']))
    matched['residualPixels'] = math.dist(matched['topPixel'], matched['projectedTopPixel'])
    allowance = bank['observationAllowancePixels']
    registration['observationAllowancePixels'] = allowance
    registration['photoAlignmentAccepted'] = registration['maxCheckResidualPixels'] <= allowance
    matched['geometricCorrespondenceAccepted'] = registration['photoAlignmentAccepted'] and matched['insideAnchorHull'] and matched['residualPixels'] <= allowance
    # Reuse canonical upper-bank observations rather than inventing a global fit.
    upper_def = next(f for f in data['supply-review.json']['fits'] if f['id']=='upper-resistors')
    upper_pairs = {p['terminal']: dict(bottomPixel=p['bottomPixel'], topPixel=top(p['terminal'])) for p in data['cable-copper.json']['registration']['checks']}
    upper = fit(upper_pairs, upper_def['anchors'], upper_def['checks'])
    upper_stop = prediction(upper, raw['eyes']['upperStop']['bottomPixel'])
    upper_stop['scope'] = raw['eyes']['upperStop']['scope']
    if raw['bottomReturn']['points'][0] != eye['bottomPixel'] or raw['bottomReturn']['points'][-1] != upper_stop['bottomPixel']:
        raise ValueError('Return lane endpoints must match the recorded eyes')
    corridor = raw['upperCorridor']
    corridor_pairs = dict(upper_pairs)
    rows = data['output-assembly.json']['filter']['jointRowsPixels']
    graph = data['cable-copper.json']
    for prefix, row in [('CF', 'cableFacing'), ('LF', 'logicFacing')]:
        for i, pixel in enumerate(rows[row]):
            name = prefix + str(i+1)
            corridor_pairs[name] = dict(bottomPixel=graph['nodes'][name]['pixel'], topPixel=pixel)
    trial = fit(corridor_pairs, corridor['anchors'], corridor['checks'])
    trial['scope'] = corridor['registrationScope']
    for check in trial['checks']:
        check['insideAnchorHull'] = inside_hull(check['bottomPixel'], trial['bottomAnchorHull'])
        check['allowancePixels'] = (components[check['terminal'].split(':')[0]]['pixelUncertainty']
                                    if ':' in check['terminal'] else data['output-assembly.json']['filter']['jointPixelUncertainty'])
    trial['extrapolationChecks'] = [c for c in trial['checks'] if not c['insideAnchorHull']]
    trial['checks'] = [c for c in trial['checks'] if c['insideAnchorHull']]
    trial['maxCheckResidualPixels'] = max(c['residualPixels'] for c in trial['checks'])
    trial['photoAlignmentAccepted'] = len(trial['checks']) >= 4 and all(c['residualPixels'] <= c['allowancePixels'] for c in trial['checks'])
    corridor_review = dict(scope=corridor['scope'], registration=trial,
                           unmatchedTopFeatures=corridor['unmatchedTopFeatures'],
                           comparisonScope=corridor['comparisonScope'], assignedFilterTerminals={})
    figures = []
    def figure(sid, segments, markers):
        photo = source(sid)
        if photo.get('specimenId'):
            raise ValueError('Clock continuation geometry must use the primary specimen')
        for segment in segments:
            if segment['status'] != 'observed' or any(len(p)!=2 or not all(math.isfinite(v) for v in p) for p in segment['points']):
                raise ValueError('Hidden joins cannot enter observed clock spans')
        return dict(source=photo, segments=[dict(s, group='unassigned-clock-continuation', net=None, imageSize=[3072,4080], detail=s.get('scope', raw['scope'])) for s in segments], markers=markers)
    figures.append(figure('photo-top', raw['topSpans'], [
        dict(point=clock_stop['projectedTopPixel'], radius=allowance, kind='search', label='R10.1 stop projected beneath R9.5; hidden top entry'),
        dict(point=eye['topPixel'], label='Anonymous bank return eye; geometric correspondence, no net assignment')]))
    figures.append(figure('photo-bottom', [raw['bottomReturn']], [
        dict(point=eye['bottomPixel'], label='Bank return eye; unassigned outer lane begins here'),
        dict(point=upper_stop['bottomPixel'], label='Upper eye; top continuation to filter unresolved')]))
    figures.append(figure('photo-top', corridor['spans'], [
        dict(point=upper_stop['projectedTopPixel'], radius=math.ceil(upper['maxCheckResidualPixels']+allowance), kind='search', label='Upper-eye search near R4.1; no observed join to the corridor'),
        dict(point=corridor['spans'][0]['points'][-1], label='Recorded corridor stop before capacitor-side copper; not a capacitor pin or LF assignment')]))
    return dict(scope=raw['scope'], bankRegistration=registration, clockStop=clock_stop,
                bankReturn=matched, upperRegistration=upper, upperStop=upper_stop,
                figures=figures, upperCorridor=corridor_review, openJoins=raw['openJoins'], assignedReferenceTerminals={},
                electricalPathComplete=False, newNativeRoutes=[],
                comparisonScope=raw['comparisonScope'], comparisonSources=[source(sid) for sid in raw['comparisonSources']])
