"""Compare unnumbered connector lead observations with inherited pad geometry."""
import math
from photo_registration import homography, project


def review(layout, components, sources, landmarks):
    observation = components['X1']['physicalReview']
    source = next(s for s in sources['sources'] if s['id'] == observation['photoSource'])
    if source['path'] != landmarks['photo'] or source['sha256'] != observation['photoSha256']:
        raise ValueError('Connector observation photograph differs from registration')
    rows = observation['leadEndRowsPixels']
    if set(rows) != {'housingNear', 'housingFar'} or len(rows['housingNear']) != len(rows['housingFar']):
        raise ValueError('Unpaired connector observations')
    if len(rows['housingNear']) < 2 or any(len(p) != 2 or not all(map(math.isfinite, p)) for row in rows.values() for p in row):
        raise ValueError('Invalid connector landmarks')
    transform = homography(landmarks['photoCorners'], landmarks['modelCorners'])
    projected = {name: [project(transform, p) for p in row] for name, row in rows.items()}
    separations = [math.dist(a, b) for a, b in zip(projected['housingNear'], projected['housingFar'])]
    connector = next(c for c in layout['components'] if c['ref'] == 'X1')
    pads = {p['pin']: p['position'] for p in connector['pads']}
    native = [math.dist(pos, pads['B' + pin[1:]]) for pin, pos in pads.items()
              if pin.startswith('A') and 'B' + pin[1:] in pads]
    return {'qualifiedForPadPlacement': False, 'photoSource': source['id'], 'photoSha256': source['sha256'],
            'pixelUncertainty': observation['pixelUncertainty'],
            'scope': 'Unnumbered visible lead ends, not qualified hole centres. Projection uses the nominal board envelope; dimensions are estimates. Near/far rows are not assigned to A/B or schematic nets.',
            'projectedLeadEndRowsMm': projected,
            'projectedRowSeparationMm': {'minimum': min(separations), 'maximum': max(separations)},
            'inheritedPadRowSeparationMm': {'minimum': min(native), 'maximum': max(native)},
            'nextEvidence': 'Resolve lead-to-hole positions and numbered terminal order before replacing the inherited native footprint. Both visible lead rows emerge from the same housing side.'}
