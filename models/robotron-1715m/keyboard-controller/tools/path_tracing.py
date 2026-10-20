"""Bounded photo searches for data and strobe; never infer hidden joins."""
import math
from clock_continuation import fit
from photo_registration import project
from bottom_registration import inside_hull


def build(data, source):
    raw = data['path-tracing.json']
    components = data['component-evidence.json']
    chips = data['photo-landmarks.json']['components']

    def top(name):
        ref, pin = name.split(':')
        if 'photoPins' in components[ref]:
            return components[ref]['photoPins'][pin]
        return chips[ref]['pins'].get(pin, chips[ref].get('checkPins', {}).get(pin))

    def registration(pairs, config):
        result = fit(pairs, config['anchors'], config['checks'])
        result['observationAllowancePixels'] = config['allowancePixels']
        for check in result['checks']:
            check['insideAnchorHull'] = inside_hull(check['bottomPixel'], result['bottomAnchorHull'])
        result['photoAlignmentAccepted'] = all(c['residualPixels'] <= config['allowancePixels'] for c in result['checks'])
        return result

    def candidate(reg, bottom, observed=None):
        predicted = project(reg['bottomToTop'], bottom)
        result = dict(bottomPixel=bottom, projectedTopPixel=predicted,
                      insideAnchorHull=inside_hull(bottom, reg['bottomAnchorHull']),
                      layerTransitionQualified=False)
        if observed is not None:
            result.update(topPixel=observed, residualPixels=math.dist(predicted, observed))
        return result

    def figure(sid, spans, markers, image_size=(3072, 4080)):
        photo = source(sid)
        for span in spans:
            if span['status'] != 'observed' or len(span['points']) < 2 or any(
                    len(p) != 2 or not all(math.isfinite(v) and 0 <= v <= image_size[i]
                                          for i, v in enumerate(p)) for p in span['points']):
                raise ValueError('Invalid observed path span')
        return dict(source=photo, imageSize=list(image_size), segments=[dict(s, group=s['id'], net=None,
                    imageSize=list(image_size), detail=s['scope']) for s in spans], markers=markers)

    result = {}
    d = raw['host-data']
    pairs = {ref+':'+pin: dict(bottomPixel=p, topPixel=top(ref+':'+pin))
             for ref in ['R4.2', 'R7', 'R8'] for pin, p in components[ref]['bottomPhotoPins'].items()}
    reg = registration(pairs, d['registration'])
    stop = components['R10.2']['signalBranchObservation']['pixelPolyline'][-1]
    search = candidate(reg, stop)
    compare = d['comparison']
    if not source(compare['source']).get('specimenId'):
        raise ValueError('Comparison observations must retain their specimen identity')
    compare_pairs = {name: dict(bottomPixel=top(name), topPixel=p) for name, p in compare['pins'].items()}
    compare_reg = registration(compare_pairs, dict(d['registration'], allowancePixels=compare['allowancePixels']))
    compare_reg['coordinateScope'] = 'bottomPixel denotes primary TOP coordinates; topPixel denotes comparison TOP coordinates. No layer transition.'
    compare_search = project(compare_reg['bottomToTop'], search['projectedTopPixel'])
    figures = [figure('photo-top', d['topSpans'], [dict(point=search['projectedTopPixel'],
               radius=math.ceil(reg['maxCheckResidualPixels']+d['registration']['allowancePixels']),
               kind='search', label='R10.2 stop projected beneath R7; no identified top joint')]),
               figure(compare['source'], compare['spans'], [dict(point=compare_search, radius=compare['allowancePixels'],
                      kind='search', label='Comparison location of primary search; not a matched hole')], compare['imageSize'])]
    result['host-data'] = dict(scope=d['scope'], registrations=[dict(id='r7-local', **reg), dict(id='comparison-r7', **compare_reg)],
                             stop=search, figures=figures, comparisonScope=compare['scope'], openJoins=d['openJoins'])

    d = raw['clock-strobe']
    config = d['a6Registration']
    pairs = {name: dict(bottomPixel=p, topPixel=config['additionalTopPins'].get(name, top(name)))
             for name, p in config['bottomPins'].items()}
    reg = registration(pairs, config)
    reg['scope'] = config['scope']
    a4 = next(r for r in data['generated/bottom-registration.json']['localRegions'] if r['id']=='a4')
    a4_candidate = next(c for c in a4['candidates'] if c['id']=='a1-track-terminal')
    a6_eye = next(c for c in a4['extrapolationChecks'] if c['id']=='a6-nearby-terminal')
    if d['bottomSpan']['points'][0] != a4_candidate['bottomPixel'] or d['bottomSpan']['points'][-1] != a6_eye['bottomPixel'] or d['topSpan']['points'][0] != a6_eye['topPixel']:
        raise ValueError('Strobe lane endpoints must match canonical terminal candidates')
    match = candidate(reg, a6_eye['bottomPixel'], a6_eye['topPixel'])
    figures = [figure('photo-bottom', [d['bottomSpan']], [dict(point=p, label=label) for p, label in [
               (a4_candidate['bottomPixel'], 'A4-side terminal candidate; unresolved layer transition'),
               (a6_eye['bottomPixel'], 'A6-side terminal candidate; unresolved layer transition')]]),
               figure('photo-top', [d['topSpan']], [dict(point=match['projectedTopPixel'], radius=8,
                      kind='search', label='A6 local extrapolation; candidate eye outside anchor hull'),
                      dict(point=d['topSpan']['points'][-1], label='Stop before A6 body; not a pin assignment')]),
               ]
    reverse = d['cpuReverse']
    if {c['terminal'] for c in reverse['candidates']} != {'A5:21', 'A5:22'}:
        raise ValueError('Reverse tracing must retain both CPU candidates')
    for c in reverse['candidates']:
        pin = c['terminal'].split(':')[1]
        if data['generated/connectivity.json']['components']['A5']['pins'][pin] != '/'+c['signal']+'_N':
            raise ValueError('CPU signal differs from the reference pin map')
        recorded = next(m['point'] for m in d['cpuCandidates'] if m['label'].startswith(c['terminal']+' '))
        if c['bottomPixel'] != recorded or (pin == '21' and c['topPixel'] != top('A5:21')):
            raise ValueError('Reverse CPU markers differ from canonical pin observations')
        if c['observedPathToA6'] or c['excluded']:
            raise ValueError('Occluded CPU review cannot resolve or exclude a candidate')
    reverse_figures = []
    for specimen in ['primary', 'comparison']:
        config = reverse[specimen]
        for side in ['bottom', 'top']:
            sid = config[side+'Source']
            if bool(source(sid).get('specimenId')) != (specimen == 'comparison'):
                raise ValueError('Reverse CPU photo specimen mismatch')
            key = (('comparison'+side.title()) if specimen == 'comparison' else side)+'Pixel'
            markers = [dict(point=c[key], label=c['terminal']+' '+c['signal']+'; covered exit, not a complete route') for c in reverse['candidates']]
            spans = []
            if side == 'bottom':
                if config['span']['points'][0] != config['neighbourLand'] or any(c[key] == config['neighbourLand'] for c in reverse['candidates']):
                    raise ValueError('Separate CPU-end land must not become a CPU pin')
                markers.append(dict(point=config['neighbourLand'], label='Separate round land beyond the CPU row; not RD or WR pin'))
                spans = [config['span']]
            size = config.get(side+'ImageSize', config.get('imageSize'))
            reverse_figures.append(figure(sid, spans, markers, size))
    cpu_reverse = dict(reverse, figures=reverse_figures, assignedReferenceTerminals={},
                       newNativeRoutes=[], electricalPathComplete=False)
    result['clock-strobe'] = dict(scope=d['scope'], registrations=[dict(id='a6-local', **reg)],
           a4Candidate=a4_candidate, a6Candidate=match, figures=figures, cpuReverse=cpu_reverse,
           comparisonSources=[source(s) for s in d['comparisonSources']],
           comparisonScope=d['comparisonScope'], openJoins=d['openJoins'])
    for review in result.values():
        review.update(assignedReferenceTerminals={}, electricalPathComplete=False, newNativeRoutes=[])
    return result
