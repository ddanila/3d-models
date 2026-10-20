#!/usr/bin/env python3
"""Generate a photo-backed review sheet without changing native connectivity."""
import argparse
import hashlib
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUTS = ['connection-review.json', 'evidence.json', 'component-evidence.json',
          'route-evidence.json', 'generated/connectivity.json', 'generated/layout.json',
          'generated/connector-terminals.json', 'generated/top-registration.json',
          'generated/bottom-registration.json']


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
            if route['group'] not in groups:
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
                figure(sid)['markers'].append({'point': point, 'label': 'X1:' + contact + ' — unclassified; top marker is a lead observation, not a hole centre'})
        result['figures'] = list(figures.values())
        result['supportingPhotos'] = [source(sid) for sid in case['supportingSources']]
        cases.append(result)
    return {'schema': 1, 'scope': data['connection-review.json']['scope'],
            'inputSha256': {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in INPUTS + ['tools/connection_review.py']},
            'cases': cases}


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
            overlays.append(f'<circle cx="{px}" cy="{py}" r="9"/><text x="{px+13}" y="{py-12}">{i}</text>')
            labels.append(f'<li>{esc(marker["label"])} · original pixel {esc(marker["point"])}</li>')
        return f'''<figure><a href="{esc(source['href'])}">Open original: {esc(source['id'])}</a>
<svg role="img" aria-label="Annotated {esc(source['id'])}" viewBox="{x} {y} {w} {h}">
<image href="{esc(source['href'])}" width="3072" height="4080"/>
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
        rows = ''
        if case.get('terminalOrder'):
            rows = '<p>' + ' · '.join(f'{esc(row)}: {esc(" → ".join(pins))}' for row,pins in case['terminalOrder']['resolvedRows'].items()) + '</p>'
        cards.append(f'''<section id="{esc(case['id'])}"><h2>{esc(case['title'])}</h2>
<p>{esc(case['finding'])}</p><h3>Reference endpoints — not measured continuity</h3>
<ul>{nets or '<li>No reference net assigned.</li>'}</ul>{series}{rows}
<div class="photos">{''.join(photo(f) for f in case['figures'])}</div>
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
<p>Markers locate existing observations; they do not identify hidden vias. Photos remain in their own original orientation. Comparison photos belong to another specimen.</p>
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
