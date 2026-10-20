"""Project visual output assembly observations without creating electrical pads."""
import math
from photo_registration import homography, project


def build(observation, evidence, landmarks):
    source = next(s for s in evidence['sources'] if s['id'] == observation['photoSource'])
    if source.get('specimenId') or source['path'] != landmarks['photo']:
        raise ValueError('Output assembly requires the primary registered photograph')
    if observation['status'] != 'visual-observations-only':
        raise ValueError('Output assembly cannot assign electrical terminals')
    transform = homography(landmarks['photoCorners'], landmarks['modelCorners'])
    def points(items):
        if len(items) < 2 or any(len(p) != 2 or not all(math.isfinite(v) for v in p) for p in items):
            raise ValueError('Invalid output assembly observations')
        return [[round(v, 6) for v in project(transform, p)] for p in items]
    f, c = observation['filter'], observation['cable']
    for obj, keys in [(f, ['bodyBaseHeightMm', 'bodyHeightMm', 'wireHeightMm', 'wireRadiusMm']),
                      (c, ['wireHeightMm', 'wireRadiusMm'])]:
        if any(not math.isfinite(obj[k]) or obj[k] <= 0 for k in keys):
            raise ValueError('Invalid output assembly dimensions')
        if obj['wireHeightMm'] - obj['wireRadiusMm'] <= 1.6:
            raise ValueError('Observed raised wires must remain above the board')
    return {
        'status': observation['status'], 'refs': observation['refs'], 'scope': observation['scope'],
        'photoSource': source['id'], 'photoSha256': source['sha256'],
        'filter': {'bodyPolygon': points(f['bodyPolygonPixels']),
                   'baseHeight': f['bodyBaseHeightMm'], 'height': f['bodyHeightMm'],
                   'jointRows': {name: points(row) for name, row in f['jointRowsPixels'].items()},
                   'raisedWireArcs': [points(arc) for arc in f['raisedWireArcsPixels']],
                   'wireHeight': f['wireHeightMm'], 'wireRadius': f['wireRadiusMm'], 'scope': f['scope']},
        'cable': {'raisedWireArcs': [{'colour': arc['colour'], 'points': points(arc['points'])}
                                   for arc in c['raisedWireArcs']],
                  'wireHeight': c['wireHeightMm'], 'wireRadius': c['wireRadiusMm'], 'scope': c['scope']},
        'unresolved': observation['unresolved']}
