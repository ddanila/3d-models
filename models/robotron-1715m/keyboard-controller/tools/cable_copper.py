#!/usr/bin/env python3
"""Build an anonymous physical graph; photo projection never assigns nets."""
import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path
from photo_registration import homography, project
from bottom_registration import inside_hull

ROOT = Path(__file__).resolve().parents[1]
INPUTS = ['cable-copper.json', 'evidence.json', 'component-evidence.json',
          'photo-landmarks.json', 'generated/connectivity.json',
          'tools/cable_copper.py', 'tools/photo_registration.py', 'tools/bottom_registration.py',
          'supply-review.json', 'route-evidence.json']


def stable(value):
    if isinstance(value, float):
        return float(format(value, '.10g'))
    if isinstance(value, dict):
        return {k: stable(v) for k, v in value.items()}
    if isinstance(value, list):
        return [stable(v) for v in value]
    return value


def partition(nodes, edges):
    adjacent = {name: set() for name in nodes}
    for edge in edges:
        a, b = edge['ends']
        if a not in nodes or b not in nodes or a == b:
            raise ValueError('Invalid graph edge endpoints: ' + edge['id'])
        if edge['status'] != 'observed':
            raise ValueError('Uncertain joins belong in unresolved, not graph edges')
        adjacent[a].add(b)
        adjacent[b].add(a)
    groups, remaining = [], set(nodes)
    while remaining:
        pending, group = [min(remaining)], set()
        while pending:
            name = pending.pop()
            if name in group:
                continue
            group.add(name)
            pending.extend(adjacent[name] - group)
        groups.append(sorted(group))
        remaining -= group
    return sorted(groups)


def supply_review(data, graph, components, connectivity, routes, source):
    def net(terminal):
        ref, pin = terminal.split(':')
        return connectivity['components'][ref]['pins'][pin]
    bottom = {p['terminal']: p['bottomPixel'] for p in graph['registration']['checks']}
    for ref, component in components.items():
        for pin, pixel in component.get('bottomPhotoPins', {}).items():
            bottom[ref + ':' + pin] = pixel
    def terminal(name):
        ref, pin = name.split(':')
        return dict(terminal=name, topPixel=components[ref]['photoPins'][pin], bottomPixel=bottom[name], net=net(name))
    fits = []
    for definition in data['fits']:
        anchors = [terminal(t) for t in definition['anchors']]
        hull = [t['bottomPixel'] for t in anchors]
        h = homography(hull, [t['topPixel'] for t in anchors])
        def check(name):
            t = terminal(name)
            prediction = project(h, t['bottomPixel'])
            return dict(t, projectedTopPixel=prediction, residualPixels=math.dist(prediction, t['topPixel']),
                        insideAnchorHull=inside_hull(t['bottomPixel'], hull))
        if set(definition['anchors']) & set(definition['checks'] + definition['extrapolationChecks']):
            raise ValueError('Supply fit checks must be held out')
        predictions = {name: dict(topPixel=project(h, n['pixel']), insideAnchorHull=inside_hull(n['pixel'], hull))
                       for name, n in graph['nodes'].items() if name.startswith(('CF', 'LF'))}
        fits.append(dict(id=definition['id'], anchors=anchors, checks=[check(t) for t in definition['checks']],
                         extrapolationChecks=[check(t) for t in definition['extrapolationChecks']],
                         bottomToTop=h, filterPredictions=predictions, copperAssignmentQualified=False))
    spans = []
    found = set()
    for uid, route in routes['items'].items():
        if route['group'] not in data['supplyRouteGroups']:
            continue
        found.add(route['group'])
        photo = next(s for s in route['sources'] if s['id'] == data['topPhotoSource'])
        if photo['sha256'] != source(data['topPhotoSource'])['sha256']:
            raise ValueError('Stale supply route photograph')
        spans.append(dict(routeId=uid, status=route['status'], photoPixels=photo['locator']['pixelSegment']))
    if found != set(data['supplyRouteGroups']):
        raise ValueError('Missing supply route group')
    ground = [terminal(t) for t in data['groundTerminals']]
    if {t['net'] for t in ground} != {'/GND'}:
        raise ValueError('Ground review contradicts reference nets')
    return dict(scope=data['scope'], topSource=source(data['topPhotoSource']), fits=fits,
                supplySpans=spans, groundTerminals=ground, gaps=data['gaps'],
                maxFilterFitDisagreementPixels=max(math.dist(fits[0]['filterPredictions'][n]['topPixel'],
                                                            fits[1]['filterPredictions'][n]['topPixel'])
                                                  for n in fits[0]['filterPredictions']),
                assignedFilterTerminals={}, rejectedWindingPairings=[],
                conclusion='Neither supply continuity nor cross-side registration identifies a filter terminal. Winding alternatives remain unconstrained.')


def build(root=ROOT):
    read = lambda name: json.loads((root / name).read_text())
    data, evidence, components, landmarks, connectivity = [read(name) for name in INPUTS[:5]]
    sources = {s['id']: s for s in evidence['sources']}
    def source(sid):
        s = sources[sid]
        if hashlib.sha256((root / s['path']).read_bytes()).hexdigest() != s['sha256']:
            raise ValueError('Stale copper photo: ' + sid)
        return s
    primary = source(data['photoSource'])
    comparison = source(data['comparison']['photoSource'])
    if primary.get('specimenId') or not comparison.get('specimenId'):
        raise ValueError('Keep primary and comparison specimens separate')
    def top(item):
        if 'topPixel' in item:
            return item['topPixel']
        ref, pin = item['terminal'].split(':')
        return components[ref]['photoPins'][pin] if 'photoPins' in components[ref] else landmarks['components'][ref]['pins'][pin]
    reg = data['registration']
    anchors = [dict(p, topPixel=top(p)) for p in reg['anchors']]
    hull = [p['bottomPixel'] for p in anchors]
    if len(anchors) != 4 or not all(inside_hull(p, hull) for p in hull):
        raise ValueError('Invalid registration anchors')
    h = homography(hull, [p['topPixel'] for p in anchors])
    board = homography(landmarks['photoCorners'], landmarks['modelCorners'])
    checks = [dict(p, topPixel=top(p), projectedTopPixel=project(h, p['bottomPixel']),
                   residualPixels=math.dist(top(p), project(h, p['bottomPixel']))) for p in reg['checks']]
    if set(data['nodes']) & set(connectivity['components']):
        raise ValueError('Anonymous node IDs must not shadow reference component names')
    nodes = {}
    for name, n in data['nodes'].items():
        if len(n['pixel']) != 2 or not all(math.isfinite(v) for v in n['pixel']):
            raise ValueError('Invalid node pixels')
        nodes[name] = dict(n, net=None, modelPosition=project(board, project(h, n['pixel'])),
                          insideAnchorHull=inside_hull(n['pixel'], hull))
    if len({e['id'] for e in data['edges']}) != len(data['edges']):
        raise ValueError('Duplicate graph edge ID')
    groups = partition(nodes, data['edges'])
    edges = []
    for edge in data['edges']:
        a, b = edge['ends']
        pixels = [nodes[a]['pixel'], *edge['via'], nodes[b]['pixel']]
        if any(len(p) != 2 or not all(math.isfinite(v) for v in p) for p in pixels):
            raise ValueError('Invalid edge pixels')
        edges.append(dict(edge, net=None, photoPixels=pixels,
                          modelPoints=[project(board, project(h, p)) for p in pixels]))
    cmp = data['comparison']
    ca = cmp['anchors']
    ch = homography([a['pixel'] for a in ca], [nodes[a['node']]['pixel'] for a in ca])
    cmp_checks = [dict(p, projectedPrimaryPixel=project(ch, p['pixel']),
                       residualPixels=math.dist(project(ch, p['pixel']), nodes[p['node']]['pixel'])) for p in cmp['checks']]
    roles = {ref: connectivity['components'][ref]['pins'] for ref in ['L1.1', 'L1.2', 'L1.3', 'L1.4', 'XT1']}
    return stable({
        'schema': 1, 'scope': data['scope'], 'regionPixels': data['regionPixels'], 'source': primary, 'nodes': nodes, 'edges': edges,
        'connectedGroups': groups, 'unresolved': data['unresolved'],
        'referenceRoles': roles, 'assignedReferenceTerminals': {},
        'supplyReview': supply_review(read('supply-review.json'), data, components, connectivity, read('route-evidence.json'), source),
        'windingPairingCandidates': [dict(zip(['CF1', 'CF2', 'CF3', 'CF4'], order))
                                     for order in itertools.permutations(['LF1', 'LF2', 'LF3', 'LF4'])],
        'projection': {'scope': reg['scope'], 'anchors': anchors, 'checks': checks,
                       'bottomToTop': h, 'topToModel': board,
                       'maxCheckResidualPixels': max(p['residualPixels'] for p in checks),
                       'copperAssignmentQualified': False},
        'comparison': {'source': comparison, 'scope': cmp['scope'], 'anchors': ca,
                       'checks': cmp_checks, 'comparisonToPrimary': ch,
                       'maxCheckResidualPixels': max(p['residualPixels'] for p in cmp_checks),
                       'electricalIdentityTransferred': False},
        'inputSha256': {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in INPUTS}})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    output = json.dumps(build(), indent=2, sort_keys=True) + '\n'
    path = ROOT / 'generated/cable-copper.json'
    if args.check:
        if path.read_text() != output:
            raise SystemExit('Stale cable copper graph')
    else:
        path.write_text(output)
    print('Cable copper graph verified' if args.check else 'Cable copper graph generated')


if __name__ == '__main__':
    main()
