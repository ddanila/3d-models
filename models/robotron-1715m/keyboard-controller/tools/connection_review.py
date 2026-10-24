#!/usr/bin/env python3
"""Generate a photo-backed review sheet without changing native connectivity."""
import argparse
import hashlib
import html
import json
import math
from pathlib import Path
from photo_registration import homography, project
from bottom_registration import inside_hull
from clock_continuation import build as clock_continuation
from path_tracing import build as path_tracing

ROOT = Path(__file__).resolve().parents[1]
INPUTS = ['connection-review.json', 'evidence.json', 'component-evidence.json',
          'route-evidence.json', 'generated/connectivity.json', 'generated/layout.json',
          'generated/connector-terminals.json', 'generated/top-registration.json',
          'generated/bottom-registration.json', 'photo-landmarks.json',
          'bottom-landmarks.json', 'clock-continuation.json', 'cable-copper.json', 'supply-review.json', 'output-assembly.json', 'path-tracing.json']
CODE_INPUTS = ['tools/connection_review.py', 'tools/photo_registration.py',
               'tools/bottom_registration.py', 'tools/clock_continuation.py', 'tools/path_tracing.py']


def stable_numbers(value):
    """Discard sub-pixel numerical noise in portable review artifacts."""
    if isinstance(value, float):
        return float(format(value, '.10g'))
    if isinstance(value, dict):
        return {key: stable_numbers(item) for key, item in value.items()}
    if isinstance(value, list):
        return [stable_numbers(item) for item in value]
    return value


def cross_side_search(data, stop):
    """Localize an occluded stop; never qualify a track or layer transition."""
    config = data['connection-review.json']['crossSideSearch']
    region = next(r for r in data['bottom-landmarks.json']['pcbRegions']
                  if r['id'] == config['region'])
    components = data['component-evidence.json']
    top = data['photo-landmarks.json']['components']
    pairs = {}
    for item in region['anchors'] + region['checks']:
        ref, pin = item['ref'], item['pin']
        if 'photoPins' in components[ref]:
            pixel = components[ref]['photoPins'].get(pin)
        else:
            pixel = top[ref]['pins'].get(pin, top[ref].get('checkPins', {}).get(pin))
        if pixel:
            pairs[ref + ':' + pin] = {'bottomPixel': item['photoPixel'], 'topPixel': pixel}
    fits = []
    for names in config['fits']:
        if len(names) != 4 or len(set(names)) != 4:
            raise ValueError('Cross-side search requires four distinct anchors')
        anchors = [dict(terminal=n, **pairs[n]) for n in names]
        hull = [p['bottomPixel'] for p in anchors]
        # Sort into convex boundary order for a genuine hull test.
        center = [sum(p[i] for p in hull)/4 for i in range(2)]
        hull.sort(key=lambda p: math.atan2(p[1]-center[1], p[0]-center[0]))
        if any(inside_hull(p, hull[:i]+hull[i+1:]) for i, p in enumerate(hull)):
            raise ValueError('Cross-side anchors must form a convex quadrilateral')
        h = homography([p['bottomPixel'] for p in anchors], [p['topPixel'] for p in anchors])
        checks = [dict(terminal=n, **p, residualPixels=math.dist(project(h, p['bottomPixel']), p['topPixel']))
                  for n, p in pairs.items() if n not in names]
        if len(checks) < 4:
            raise ValueError('Cross-side search requires held-out checks')
        fits.append({'anchors': anchors, 'checks': checks, 'bottomToTop': h,
                     'projectedTopPixel': project(h, stop['bottomPixel']),
                     'insideAnchorHull': inside_hull(stop['bottomPixel'], hull),
                     'maxCheckResidualPixels': max(p['residualPixels'] for p in checks)})
    locations = [f['projectedTopPixel'] for f in fits]
    center = [sum(p[i] for p in locations)/len(locations) for i in range(2)]
    spread = max(math.dist(a, b) for a in locations for b in locations)
    radius = math.ceil(max(f['maxCheckResidualPixels'] for f in fits) + spread + stop['searchPaddingPixels'])
    return {'scope': config['scope'], 'fits': fits, 'centerTopPixel': center,
            'fitSpreadPixels': spread, 'searchRadiusPixels': radius,
            'radiusBasis': 'Maximum held-out residual + fit spread + explicit search padding; heuristic search margin, not a confidence bound.',
            'copperAssignmentQualified': False}


def build(root=ROOT):
    data = {name: json.loads((root / name).read_text()) for name in INPUTS}
    components = data['generated/connectivity.json']['components']
    sources = {s['id']: s for s in data['evidence.json']['sources']}
    routes = data['route-evidence.json']['items']
    native = {r['id']: r for r in data['generated/layout.json']['routes']}
    reviews = {r['id']: r for r in data['evidence.json']['routeReviews']}
    x1 = data['component-evidence.json']['X1']['physicalReview']
    terminals = data['generated/connector-terminals.json']

    def endpoint(name):
        ref, pin = name.split(':')
        return {'terminal': name, 'net': components[ref]['pins'][pin]}

    def source(source_id):
        item = sources[source_id]
        path = root / item['path']
        if hashlib.sha256(path.read_bytes()).hexdigest() != item['sha256']:
            raise ValueError('Photo hash mismatch: ' + source_id)
        return {**item, 'href': '../' + item['path'],
                'specimen': item.get('specimenId', 'primary museum specimen')}

    traces = path_tracing(data, source)
    cases = []
    for case in data['connection-review.json']['cases']:
        result = dict(case)
        result['referenceNets'] = []
        for names in case['sameNetSets']:
            ends = [endpoint(name) for name in names]
            if not ends or ends[0]['net'] is None or len({e['net'] for e in ends}) != 1:
                raise ValueError('Reference endpoint net mismatch: ' + case['id'])
            result['referenceNets'].append({'net': ends[0]['net'], 'terminals': names})
        result['candidateEndpoints'] = [endpoint(n) for n in case.get('candidateEndpoints', [])]
        result['series'] = {ref: components[ref] for ref in case['seriesComponents']}
        result['reviews'] = [{key: reviews[i].get(key) for key in ('id', 'status', 'summary', 'nextEvidence')} for i in case['reviews']]
        figures = {}

        def figure(sid):
            if sid not in figures:
                figures[sid] = {'source': source(sid), 'segments': [], 'markers': []}
            return figures[sid]

        groups = set(case['routeGroups'])
        found = set()
        for uuid, route in routes.items():
            if route.get('group') not in groups:
                continue
            if uuid not in native or native[uuid]['evidence'] != route:
                raise ValueError('Native route review mismatch: ' + uuid)
            found.add(route['group'])
            for observation in route['sources']:
                sid = observation['id']
                if observation['sha256'] != sources[sid]['sha256']:
                    raise ValueError('Stale route photograph: ' + uuid)
                figure(sid)['segments'].append({
                    'uuid': uuid, 'group': route['group'], 'status': route['status'],
                    'points': observation['locator']['pixelSegment'],
                    'imageSize': observation['locator']['imageSize'], 'detail': route['detail']})
        if found != groups:
            raise ValueError('Missing route groups: ' + str(groups - found))
        for sid, fig in list(figures.items()):
            # Degree-one endpoints mark stops in recorded geometry, not electrical pins.
            by_group = {}
            for segment in fig['segments']:
                counts = by_group.setdefault(segment['group'], {})
                a, b = map(tuple, segment['points'])
                if a == b:
                    continue
                for point in (a, b):
                    counts[point] = counts.get(point, 0) + 1
            for group, counts in by_group.items():
                for point, count in counts.items():
                    if count == 1:
                        fig['markers'].append({'point': list(point), 'label': 'Recorded span end: ' + group})
        if case.get('connectorConstraints'):
            for constraint in x1['terminalConstraints']:
                figure(constraint['photoSource'])['segments'].append({
                    'group': constraint['id'], 'status': 'constraint',
                    'points': constraint['pixelPolyline'], 'imageSize': [3072, 4080],
                    'detail': constraint['basis']})
            result['terminalOrder'] = terminals
        if case.get('connectorContact'):
            contact = case['connectorContact']
            if contact not in terminals['referenceAbsentPins'] or contact in components['X1']['pins']:
                raise ValueError('Contact is no longer absent from the reference: ' + contact)
            row, index = next((row, pins.index(contact)) for row, pins in terminals['resolvedRows'].items() if contact in pins)
            for sid, point in [(x1['photoSource'], x1['leadEndRowsPixels'][row][index]),
                               (x1['underside']['photoSource'], x1['underside']['jointRowsPixels'][row][index])]:
                classification = 'owner-observed present, soldered and unrouted' if case.get('ownerObservation') else 'unclassified'
                location = 'raised lead observation, not a hole centre' if sid == x1['photoSource'] else 'registered solder-joint observation; dimensions estimated'
                figure(sid)['markers'].append({'point': point, 'label': 'X1:' + contact + ' — ' + classification + '; ' + location})
        if case.get('crossSideStop'):
            stop = case['crossSideStop']
            if not any(stop['bottomPixel'] == marker['point'] for marker in figure('photo-bottom')['markers']):
                raise ValueError('Cross-side stop is not a recorded route endpoint')
            search = cross_side_search(data, stop)
            result['crossSideSearch'] = search
            figure('photo-top')['markers'].append({
                'point': search['centerTopPixel'], 'radius': search['searchRadiusPixels'],
                'kind': 'search', 'label': 'Projected search region beneath ' + stop['occludingBody'] + '; not an observed joint'})
        if case['id'] == 'host-clock':
            result['continuation'] = clock_continuation(data, source)
        if case['id'] in traces:
            result['traceReview'] = traces[case['id']]
        result['figures'] = list(figures.values())
        result['supportingPhotos'] = [source(sid) for sid in case['supportingSources']]
        cases.append(result)
    return stable_numbers({'schema': 1, 'scope': data['connection-review.json']['scope'],
            'inputSha256': {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in INPUTS + CODE_INPUTS},
            'cases': cases})


def render(report):
    esc = lambda value: html.escape(str(value), quote=True)
    def photo(fig):
        source = fig['source']
        points = [p for seg in fig['segments'] for p in seg['points']] + [m['point'] for m in fig['markers']]
        xs, ys = zip(*points)
        x, y = max(0, min(xs)-90), max(0, min(ys)-90)
        w, h = max(xs)-x+90, max(ys)-y+90
        # Give narrow traces enough context to recognize neighbouring copper lanes.
        if w < h*.65:
            extra = h*.65-w
            x = max(0, x-extra/2)
            w += extra
        overlays = []
        for seg in fig['segments']:
            coords = ' '.join(','.join(map(str, p)) for p in seg['points'])
            overlays.append(f'<polyline class="{esc(seg["status"])}" points="{coords}"><title>{esc(seg["detail"])}</title></polyline>')
        labels = []
        for i, marker in enumerate(fig['markers'], 1):
            px, py = marker['point']
            overlays.append(f'<circle class="{esc(marker.get("kind", "endpoint"))}" cx="{px}" cy="{py}" r="{marker.get("radius", 9)}"/><text x="{px+13}" y="{py-12}">{i}</text>')
            labels.append(f'<li>{esc(marker["label"])} · original pixel {esc([round(v, 1) for v in marker["point"]])}</li>')
        return f'''<figure><a href="{esc(source['href'])}">Open original: {esc(source['id'])}</a>
<svg role="img" aria-label="Annotated {esc(source['id'])}" viewBox="{x} {y} {w} {h}">
<image href="{esc(source['href'])}" width="{fig.get('imageSize', [3072, 4080])[0]}" height="{fig.get('imageSize', [3072, 4080])[1]}"/>
<g class="overlay">{''.join(overlays)}</g></svg>
<figcaption>{esc(source['specimen'])}; original photo coordinates, no cross-side warp.</figcaption>
<ol>{''.join(labels)}</ol></figure>'''

    cards = []
    for case in report['cases']:
        nets = ''.join(f'<li><code>{esc(n["net"])}</code>: {esc(" ↔ ".join(n["terminals"]))}</li>' for n in case['referenceNets'])
        if case['candidateEndpoints']:
            nets += ''.join(f'<li>Alternative to distinguish: {esc(e["terminal"])} <code>{esc(e["net"])}</code></li>' for e in case['candidateEndpoints'])
        series = ''.join(f'<p>{esc(ref)} separates the two reference nets through a winding; this is not a copper short. Physical winding identity remains unresolved.</p>' for ref in case['series'])
        alternatives = ''.join(f'<li>{esc(text)}</li>' for text in case['alternatives'])
        photos = ''.join(f'<li><a href="{esc(s["href"])}">{esc(s["id"])}</a> — {esc(s["specimen"])}</li>' for s in case['supportingPhotos'])
        trace = case.get('traceReview')
        trace_html = ''
        if trace:
            fits = ' '.join(r['id'] + ': ' + str(round(r['maxCheckResidualPixels'], 1)) + ' px; alignment accepted: ' + str(r['photoAlignmentAccepted']) + '.' for r in trace['registrations'])
            trace_html = '<details><summary>Local path tracing — unresolved joins</summary><p>' + esc(trace['scope']) + '</p><p>' + esc(fits) + '</p><div class="photos">' + ''.join(photo(f) for f in trace['figures']) + '</div><ul>' + ''.join('<li>' + esc(g['scope']) + '</li>' for g in trace['openJoins']) + '</ul><p>' + esc(trace['comparisonScope']) + '</p></details>'
        if trace and trace.get('cpuReverse'):
            reverse = trace['cpuReverse']
            trace_html += '<details><summary>Reverse trace: CPU RD and WR</summary><p>' + esc(reverse['scope']) + '</p><div class="photos">' + ''.join(photo(f) for f in reverse['figures']) + '</div><p>' + esc(reverse['excludedShortcut']) + '</p><p>' + esc(reverse['nextEvidence']) + '</p></details>'
        continuation = ''
        if case.get('continuation'):
            c = case['continuation']
            gaps = ''.join('<li>' + esc(g['scope']) + '</li>' for g in c['openJoins'])
            continuation = '<details><summary>Candidate clock continuation — unassigned copper</summary><p>' + esc(c['scope']) + '</p><p>' + esc(c['upperCorridor']['scope']) + ' Wider fit maximum held-out residual: ' + str(round(c['upperCorridor']['registration']['maxCheckResidualPixels'], 1)) + ' px; accepted: ' + str(c['upperCorridor']['registration']['photoAlignmentAccepted']) + '.</p><div class="photos">' + ''.join(photo(f) for f in c['figures']) + '</div><ul>' + gaps + '</ul></details>'
        rows = ''
        search_text = ''
        if case.get('crossSideSearch'):
            search = case['crossSideSearch']
            diagnostics = '; '.join(f'fit {i}: maximum held-out residual {f["maxCheckResidualPixels"]:.1f}px, stop {"inside" if f["insideAnchorHull"] else "outside"} anchor hull' for i, f in enumerate(search['fits'], 1))
            search_text = f'<p>{esc(search["scope"])}</p><p>{esc(diagnostics)}. Fit spread {search["fitSpreadPixels"]:.1f}px; search radius {search["searchRadiusPixels"]}px. {esc(search["radiusBasis"])}</p>'
        if case.get('terminalOrder'):
            rows = '<p>' + ' · '.join(f'{esc(row)}: {esc(" → ".join(pins))}' for row,pins in case['terminalOrder']['resolvedRows'].items()) + '</p>'
        cards.append(f'''<section id="{esc(case['id'])}"><h2>{esc(case['title'])}</h2>
<p>{esc(case['finding'])}</p><h3>Reference endpoints — not measured continuity</h3>
<ul>{nets or '<li>No reference net assigned.</li>'}</ul>{series}{rows}
<div class="photos">{''.join(photo(f) for f in case['figures'])}</div>
{search_text}{continuation}{trace_html}
<h3>Alternatives to distinguish</h3><ul>{alternatives}</ul>
<dl><dt>Next desk work</dt><dd>{esc(case['nextDeskWork'])}</dd>
<dt>Evidence that closes the span</dt><dd>{esc(case['decisiveObservation'])}</dd>
<dt>Interpretation limit</dt><dd>{esc(case['doNotInfer'])}</dd></dl>
<details><summary>Supporting photographs</summary><ul>{photos}</ul></details></section>''')
    navigation = ''.join(f'<a href="#{esc(c["id"])}">{esc(c["id"])}</a>' for c in report['cases'])
    hashes = ''.join(f'<li>{esc(name)}: <code>{sha}</code></li>' for name,sha in report['inputSha256'].items())
    return '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>Keyboard controller connection review</title><style>
*{box-sizing:border-box}body{font:16px/1.5 system-ui,sans-serif;color:#16283a;background:#edf1f4;margin:0}main{max-width:1100px;margin:auto;padding:28px}h1{line-height:1.15}h2{margin-top:0}h3{font-size:1rem}section,header{background:white;padding:26px;margin:20px 0;border:1px solid #cbd4dd;border-radius:8px}nav{display:flex;gap:16px;flex-wrap:wrap}a{color:#075ca8}code{overflow-wrap:anywhere}.photos{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:20px}figure{margin:0;min-width:0}svg{display:block;width:100%;height:480px;background:#202a30;margin-top:10px}svg polyline{fill:none;stroke:#37f3d4;stroke-width:3;vector-effect:non-scaling-stroke}svg .inferred{stroke:#ffcf5b;stroke-dasharray:7 5}svg .constraint{stroke:#91c9ff}svg circle{fill:#d32967;stroke:white;stroke-width:1;vector-effect:non-scaling-stroke}svg text{font:bold 24px sans-serif;fill:white;paint-order:stroke;stroke:#182a3b;stroke-width:3}figcaption,figure ol{font-size:13px}dt{font-weight:700;margin-top:12px}dd{margin:0}details{margin-top:18px}#toggle{padding:8px 12px}body.hide-overlays .overlay{visibility:hidden}.legend span{padding:3px 8px;background:#19333f;color:white;display:inline-block}footer{font-size:13px}@media(max-width:600px){main{padding:10px}section,header{padding:16px}}@media print{body{background:white}main{padding:0}nav,#toggle{display:none}section{break-before:page;border:0;padding:0}svg{height:320px}details{display:block}details ul{display:block}footer{break-before:page}}
</style><main><header><h1>Keyboard controller<br>Connection review</h1>
<p>''' + esc(report['scope']) + '''</p><p class="legend"><span>Teal: observed segment</span> <span>Dashed amber: inferred attachment</span> <span>Blue: connector constraint</span> <span>Pink: recorded span end or unclassified contact</span></p>
<style>svg circle.search{fill:none;stroke:#ffcf5b;stroke-width:2;stroke-dasharray:5 4}</style>
<p>Dashed amber circles are projected search regions, not observed joints. Other markers locate existing observations; they do not identify hidden vias. Photos remain in their own original orientation. Comparison photos belong to another specimen.</p>
<button id="toggle" type="button" aria-pressed="false">Hide overlays</button><nav>''' + navigation + '''</nav></header>''' + ''.join(cards) + '''<footer><p>Generated from canonical CAD evidence. No pad, net or track is changed by this review. If resistance observations are later needed, use a disconnected, unpowered board and record readings and probe locations; a buzzer alone does not establish copper continuity.</p><details><summary>Input hashes</summary><ul>''' + hashes + '''</ul></details></footer></main><script>
document.querySelector('#toggle').onclick=function(){const hidden=document.body.classList.toggle('hide-overlays');this.textContent=hidden?'Show overlays':'Hide overlays';this.setAttribute('aria-pressed',String(hidden));};
</script></html>
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    report = build()
    outputs = {'connection-review.json': json.dumps(report, indent=2, ensure_ascii=False) + '\n',
               'connection-review.html': render(report)}
    for name, text in outputs.items():
        path = ROOT / 'review' / name
        path.parent.mkdir(exist_ok=True)
        if args.check:
            if not path.exists() or path.read_text() != text:
                raise SystemExit('Stale connection review: ' + str(path))
        else:
            path.write_text(text)
    print('Connection review verified' if args.check else 'Connection review generated')


if __name__ == '__main__':
    main()
