"""Compare unnumbered connector lead observations with inherited pad geometry."""
import math
from photo_registration import homography, project


def review(layout, components, sources, landmarks, bottom=None):
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
    result = {'qualifiedForPadPlacement': False, 'photoSource': source['id'], 'photoSha256': source['sha256'],
            'pixelUncertainty': observation['pixelUncertainty'],
            'scope': 'Unnumbered visible lead ends, not qualified hole centres. Projection uses the nominal board envelope; dimensions are estimates. Near/far rows are not assigned to A/B or schematic nets.',
            'projectedLeadEndRowsMm': projected,
            'projectedRowSeparationMm': {'minimum': min(separations), 'maximum': max(separations)},
            'nativePadRowSeparationMm': {'minimum': min(native), 'maximum': max(native)},
            'nextEvidence': 'Reconcile native pad geometry against the independent underside observations and terminal constraints. Actual dimensions and continuity remain unmeasured.'}

    if bottom is not None and observation.get('underside'):
        from bottom_registration import inside_hull
        underside = observation['underside']
        source = next(s for s in sources['sources'] if s['id'] == underside['photoSource'])
        if source['sha256'] != underside['photoSha256'] or source['sha256'] != bottom['photoSha256']:
            raise ValueError('Underside connector photograph differs from registration')
        region = next(r for r in bottom['pcbRegions'] if r['id'] == underside['registrationRegion'])
        rows = underside['jointRowsPixels']
        if set(rows) != set(projected) or any(len(rows[name]) != len(projected[name]) for name in rows):
            raise ValueError('Unpaired underside connector observations')
        if any(len(p) != 2 or not all(map(math.isfinite, p)) for row in rows.values() for p in row):
            raise ValueError('Invalid underside connector landmarks')
        inside = all(inside_hull(p, region['anchorHull']) for row in rows.values() for p in row)
        joints = {name: [project(region['photoToModel'], p) for p in row] for name, row in rows.items()}
        distances = [math.dist(a,b) for a,b in zip(joints['housingNear'],joints['housingFar'])]
        residuals = {name: [math.dist(a,b) for a,b in zip(joints[name],projected[name])] for name in rows}
        result['underside'] = {'photoSource': source['id'], 'photoSha256': source['sha256'],
            'pixelUncertainty': underside['pixelUncertainty'], 'registrationRegion': region['id'],
            'allJointsInsideAnchorHull': inside, 'registrationCheckResidualMm': region['maxCheckResidualMm'],
            'registrationWithinTolerance': region['maxCheckResidualMm'] <= region['toleranceMm'],
            'projectedJointRowsMm': joints, 'topLeadEndToJointResidualsMm': residuals,
            'projectedRowSeparationMm': {'minimum': min(distances), 'maximum': max(distances)},
            'terminalMappingQualified': False,
            'scope': 'Solder-joint geometry from local nominal registration, not metrology. Top lead ends can be raised bends; cross-side residuals do not prove electrical identity.'}
    return result


def placement_review(layout, observation, terminals):
    """Check native positions without deriving or moving them during export."""
    joints = observation['underside']
    if not terminals['completeTerminalOrderResolved'] or not joints['allJointsInsideAnchorHull'] or not joints['registrationWithinTolerance']:
        raise ValueError('Connector placement requires bounded registration and terminal order')
    expected = {pin: point for row, pins in terminals['resolvedRows'].items()
                for pin, point in zip(pins, joints['projectedJointRowsMm'][row])}
    native = next(c for c in layout['components'] if c['ref'] == 'X1')
    errors = {p['pin']: math.dist(p['position'], expected[p['pin']]) for p in native['pads']}
    missing = sorted(set(expected) - set(errors))
    isolated = sorted(p['pin'] for p in native['pads'] if p.get('classification') == 'owner-observed-unrouted' and p['net'] is None)
    if sorted(missing + isolated) != terminals['referenceAbsentPins']:
        raise ValueError('Connector native pad inventory differs from supported terminals')
    # Native coordinates are integer nanometres; this checks transcription, not photo accuracy.
    if max(errors.values()) > .000002:
        raise ValueError('Connector native pads differ from registered joint positions')
    return {'status': 'photo-placed-reference-terminal-order', 'padResidualsMm': errors,
            'unclassifiedContacts': missing, 'isolatedContacts': isolated,
            'scope': 'Native reference pads match locally registered joints. Numbering is reference-derived; dimensions, hole diameters and continuity are not measured. Owner-observed unrouted contacts have isolated native pads; missing contacts remain visual geometry only.'}
