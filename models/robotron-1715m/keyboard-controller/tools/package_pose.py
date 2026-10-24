"""Conditional rigid package fits: no scale, shear, reflection or copper admission."""
import math


def fit(reference, observed, anchors):
    if set(reference)!=set(observed) or len(anchors)!=2 or len(set(anchors))!=2 or not set(anchors)<=set(reference):
        raise ValueError('Package pose requires matching points and two distinct anchors')
    if len(reference)<4:
        raise ValueError('Package pose requires independent check points')
    if not all(len(p)==2 and all(math.isfinite(v) for v in p) for points in (reference,observed) for p in points.values()):
        raise ValueError('Invalid package pose points')
    a,b=anchors
    u=[reference[b][k]-reference[a][k] for k in range(2)]
    v=[observed[b][k]-observed[a][k] for k in range(2)]
    if min(math.hypot(*u),math.hypot(*v))<=1e-9:raise ValueError('Coincident package pose anchors')
    angle=math.atan2(v[1],v[0])-math.atan2(u[1],u[0])
    cosine,sine=math.cos(angle),math.sin(angle)
    center=lambda points:[sum(points[key][k] for key in anchors)/2 for k in range(2)]
    rc,oc=center(reference),center(observed)
    def transform(p):
        x,y=p[0]-rc[0],p[1]-rc[1]
        return [oc[0]+cosine*x-sine*y,oc[1]+sine*x+cosine*y]
    axis=[x/math.hypot(*v) for x in v]
    normal=[-axis[1],axis[0]]
    checks=[]
    for key in sorted(reference):
        q=transform(reference[key])
        error=[observed[key][i]-q[i] for i in range(2)]
        checks.append({'terminal':key,'heldOut':key not in anchors,
                       'originalResidualMm':round(math.dist(reference[key],observed[key]),9),
                       'fittedResidualMm':round(math.dist(q,observed[key]),9),
                       'residualAlongRowMm':round(sum(error[i]*axis[i] for i in range(2)),9)+0.0,
                       'residualAcrossRowMm':round(sum(error[i]*normal[i] for i in range(2)),9)+0.0})
    center_before=[sum(p[k] for p in reference.values())/len(reference) for k in range(2)]
    center_after=transform(center_before)
    return {'residualFrame':'Observed minus rigid-fit position; along points from first anchor to second, across is its left normal. Signed components diagnose the mismatch without changing the fit or acceptance budget.',
            'anchors':anchors,'rotationDegrees':round(math.degrees(math.atan2(sine,cosine)),9),
            'centerShiftMm':[round(a-b,9) for a,b in zip(center_after,center_before)],
            'anchorSpanMismatchMm':round(abs(math.hypot(*v)-math.hypot(*u)),9),
            'maxHeldOutResidualMm':max(p['fittedResidualMm'] for p in checks if p['heldOut']),
            'maxOriginalHeldOutResidualMm':max(p['originalResidualMm'] for p in checks if p['heldOut']),
            'checks':checks,'copperAssignmentQualified':False}
