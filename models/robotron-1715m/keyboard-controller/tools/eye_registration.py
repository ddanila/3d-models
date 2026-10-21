"""Compose a checked eye-to-eye photo fit with bounded underside placement."""
import hashlib
import math
from bottom_registration import inside_hull
from photo_registration import homography, project


def intersection(subject, clip):
    """Convex polygon intersection; preserve the source boundary order."""
    orientation = sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(clip, clip[1:]+clip[:1]))
    for a,b in zip(clip, clip[1:]+clip[:1]):
        def distance(p):
            return ((b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])) * (1 if orientation > 0 else -1)
        output = []
        for p,q in zip(subject, subject[1:]+subject[:1]):
            dp,dq = distance(p),distance(q)
            if dp >= 0: output.append(p)
            if (dp >= 0) != (dq >= 0):
                t = dp/(dp-dq)
                output.append([p[i]+t*(q[i]-p[i]) for i in range(2)])
        subject = output
        if not subject: break
    return subject


def compose(a,b):
    # Python 3.12 changed float sum(); pin accumulation across supported runtimes.
    result = [math.fsum(a[3*r+k]*b[3*k+c] for k in range(3)) for r in range(3) for c in range(3)]
    return [v/result[8] for v in result]


def review(evidence, bottom, root):
    source = evidence['eyeRegistration']
    if source['bottomLandmarksSha256'] != hashlib.sha256((root/'bottom-landmarks.json').read_bytes()).hexdigest():
        raise ValueError('Stale eye registration underside landmarks')
    if source['bottomPhotoSha256'] != bottom['photoSha256']:
        raise ValueError('Eye registration underside photograph mismatch')
    region = next(r for r in bottom['pcbRegions'] if r['id'] == source['bottomRegion'])
    if not region['copperAssignmentQualified']:
        raise ValueError('Eye registration needs qualified underside placement')
    anchors,checks = source['anchors'],source['checks']
    if len(anchors) != 4 or len(checks) < 4:
        raise ValueError('Eye registration requires four anchors and four held-out checks')
    for key in ('id','photoPixel','bottomPixel'):
        values = [str(p[key]) for p in anchors+checks]
        if len(set(values)) != len(values):
            raise ValueError('Eye registration anchors and checks must be independent')
    top_hull = [p['photoPixel'] for p in anchors]
    bottom_hull = [p['bottomPixel'] for p in anchors]
    for hull in (top_hull,bottom_hull):
        turns = [(hull[(i+1)%4][0]-hull[i][0])*(hull[(i+2)%4][1]-hull[(i+1)%4][1])
                 -(hull[(i+1)%4][1]-hull[i][1])*(hull[(i+2)%4][0]-hull[(i+1)%4][0]) for i in range(4)]
        if not (all(v>0 for v in turns) or all(v<0 for v in turns)):
            raise ValueError('Eye anchors must form a convex boundary')
    forward = homography(top_hull,bottom_hull)
    inverse = homography(bottom_hull,top_hull)
    bounded_bottom = intersection(bottom_hull,region['anchorHull'])
    bounded_top = [project(inverse,p) for p in bounded_bottom]
    if len(bounded_top) < 3:
        raise ValueError('Eye and underside registration hulls do not overlap')
    matrix = compose(region['photoToModel'],forward)
    rows = []
    for p in checks:
        predicted = project(forward,p['photoPixel'])
        if not (inside_hull(p['photoPixel'],bounded_top) and inside_hull(p['bottomPixel'],bounded_bottom)):
            raise ValueError('Held-out eye exceeds bounded registration hull')
        residual = math.dist(project(region['photoToModel'],predicted),project(region['photoToModel'],p['bottomPixel']))
        rows.append(dict(p,projectedBottomPixel=[round(v,9) for v in predicted],
                         residualMm=round(residual,9),withinTolerance=residual<=min(evidence['toleranceMm'],region['toleranceMm'])))
    return dict(id=source['id'],scope=source['scope'],anchors=anchors,checks=rows,
                photoToModel=matrix,topToBottom=forward,bottomToTop=inverse,
                eyeAnchorHull=top_hull,anchorHull=bounded_top,bottomHull=bounded_bottom,
                bottomRegion=region['id'],maxCheckResidualMm=max(p['residualMm'] for p in rows),
                toleranceMm=min(evidence['toleranceMm'],region['toleranceMm']),
                copperAssignmentQualified=source['reviewedForCopper'] and all(p['withinTolerance'] for p in rows))
