"""Join photo-only sense-lane observations to live reference tracing targets."""
import copy
import hashlib
import json
import math
from bottom_registration import inside_hull
from photo_registration import homography, project


def envelope_trial(root, trial, paths):
    """Check an enclosing mechanical fit without changing pad or copper authority."""
    read = lambda name: json.loads((root/name).read_text())
    if trial['copperAssignmentQualified'] is not False:
        raise ValueError('Envelope trial cannot qualify copper')
    hull = trial['photoCorners']
    if len(hull)!=4 or trial['modelCornerIndices']!=[1,0,3,2]:
        raise ValueError('Envelope trial requires mirrored underside corners')
    model = read('photo-landmarks.json')['modelCorners']
    h = homography(hull,[model[i] for i in trial['modelCornerIndices']])
    pads = {(c['ref'],p['pin']):p['position'] for c in read('generated/layout.json')['components'] for p in c['pads']}
    landmarks = read('bottom-landmarks.json')
    checks = {}
    for region in landmarks['pcbRegions']:
        for p in region['anchors']+region['checks']:
            key = p['ref'],p['pin']
            if key in checks:continue
            predicted = project(h,p['photoPixel'])
            checks[key] = dict(p,photoModel=predicted,pcbModel=pads[key],
                               residualMm=round(math.dist(predicted,pads[key]),9),
                               insideAnchorHull=inside_hull(p['photoPixel'],hull))
    maximum = max(p['residualMm'] for p in checks.values())
    return dict(trial,photoToModel=h,anchorHull=hull,checks=list(checks.values()),
                toleranceMm=landmarks['toleranceMm'],maxCheckResidualMm=maximum,
                withinPhotoTolerance=maximum<=landmarks['toleranceMm'],
                boundedPaths=[p['id'] for p in paths if all(inside_hull(q,hull) for s in p['segments'] for q in s['points'])])


def build(root):
    read = lambda name: json.loads((root/name).read_text())
    result = copy.deepcopy(read('sense-review.json'))
    sources = {s['id']:s for s in read('evidence.json')['sources']}
    for record in [result,*result['photos']]:
        source = sources[record['source']]
        if record['sourceSha256']!=source['sha256'] or hashlib.sha256((root/source['path']).read_bytes()).hexdigest()!=source['sha256']:
            raise ValueError('Sense review source hash mismatch')
    components = read('generated/connectivity.json')['components']
    rows = result['paths']
    if len(rows)!=8 or {p['latchTerminal'] for p in rows}!={'A4:'+str(i) for i in range(1,9)}:
        raise ValueError('Sense review must cover eight distinct latch inputs')
    if len({p['bankObservationIndex'] for p in rows})!=8:
        raise ValueError('Sense lanes must not share a bank observation')
    ends = result['bankEndReview']
    if ends['status']!='inferred' or ends['commonGroundAttachmentEstablished'] or ends['primaryMarkingIdentified']:
        raise ValueError('Bank end review cannot establish primary identity or ground attachment')
    if {ends['primaryCommonObservationIndex'],ends['primaryUnusedObservationIndex']}!={0,9} or len(ends['comparisonJoints'])!=len(result['bankJointCandidates']):
        raise ValueError('Bank end review requires both end observations and matching joint counts')
    if any(p['bankObservationIndex'] in (0,9) for p in rows):
        raise ValueError('Sense branch cannot use a bank end observation')
    photo_ids = {p['source'] for p in result['photos']}
    if not {ends['comparisonMarkSource'],ends['comparisonUndersideSource']}<=photo_ids:
        raise ValueError('Bank end review requires hashed comparison photos')
    result['envelopeTrial'] = envelope_trial(root,result['envelopeTrial'],rows)
    regions = [r for r in read('generated/bottom-registration.json')['pcbRegions'] if r['copperAssignmentQualified']]
    latch = {r['terminal']:r for r in read('bus-review.json')['latchAttachmentReview']['rows']}
    if not {'A4:'+str(i) for i in range(1,21)}<=set(latch):
        raise ValueError('Attachment review must cover every package pin once')
    for path in rows:
        if path['nativeCopper'] is not False or path['continuityEstablished'] is not False:
            raise ValueError('Sense review cannot assign native copper or continuity')
        pin = path['latchTerminal'].split(':')[1]
        net = components['A4']['pins'][pin]
        banks = ['R1:'+p for p,n in components['R1']['pins'].items() if n==net]
        collectors = [ref+':C' for ref,c in components.items() if ref.startswith('V4.') and c['pins'].get('C')==net]
        if len(banks)!=1 or len(collectors)!=1:
            raise ValueError('Sense target needs one bank branch and one collector')
        transistor = collectors[0].split(':')[0]
        base = components[transistor]['pins']['B']
        row_inputs = [dict(ref=ref,nets=list(c['pins'].values())) for ref,c in components.items() if ref.startswith('R9.') and base in c['pins'].values()]
        if len(row_inputs)!=1:raise ValueError('Sense target needs one matrix input resistor')
        segments = path['segments']
        if (segments[0]['points'][0]!=result['bankJointCandidates'][path['bankObservationIndex']]
                or segments[-1]['points'][-1]!=latch[path['latchTerminal']]['bottomJoint']):
            raise ValueError('Sense lane endpoints disagree with recorded observations')
        if segments[0]['status']!='inferred' or segments[-1]['status']!='inferred':
            raise ValueError('Sense solder attachments must remain inferred')
        for a,b in zip(segments,segments[1:]):
            if a['points'][-1]!=b['points'][0]:raise ValueError('Discontinuous sense review polyline')
        qualified = [r['id'] for r in regions if all(inside_hull(p,r['anchorHull']) for s in segments for p in s['points'])]
        path.update(referenceNet=net,terminals=[path['latchTerminal'],banks[0]],collectorTarget=collectors[0],
                    matrixInput=row_inputs[0],source=result['source'],sourceSha256=result['sourceSha256'],
                    bankPinCandidate=dict(terminal=banks[0],observationIndex=path['bankObservationIndex'],status='inferred'),
                    qualifiedWholePathRegions=qualified,collectorAttachmentEstablished=False,
                    reason='Underside lane-order candidate. R1 branch and solder attachments remain inferred; the collector branch is unresolved. No qualified local fit covers this whole corridor, and R1 has no native placement.')
    result['commonReferenceNet'] = components['R1']['pins']['1']
    result['electricalScope'] = 'Reference digital sensing drives the latch high for an active row; R1 loads collectors toward ground. HDL agreement does not identify specimen terminals or qualify SC308 devices.'
    return result
