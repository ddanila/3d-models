"""Distances between the swept cylindrical lead paths used by the reference model."""
import math


def sub(a,b): return tuple(x-y for x,y in zip(a,b))
def dot(a,b): return sum(x*y for x,y in zip(a,b))
def along(a,u,t): return tuple(x+t*y for x,y in zip(a,u))
def clamp(t): return max(0.,min(1.,t))


def closest_segments(a,b,c,d):
    """Minimum of the convex quadratic on [0,1]^2, including degenerate segments."""
    u,v,w=sub(b,a),sub(d,c),sub(a,c)
    aa,bb,cc,dd,ee=dot(u,u),dot(u,v),dot(v,v),dot(u,w),dot(v,w)
    candidates=[(0.,clamp(ee/cc) if cc else 0.),
                (1.,clamp((ee+bb)/cc) if cc else 0.),
                (clamp(-dd/aa) if aa else 0.,0.),
                (clamp((bb-dd)/aa) if aa else 0.,1.)]
    determinant=aa*cc-bb*bb
    if determinant>1e-14*aa*cc:
        s,t=(bb*ee-cc*dd)/determinant,(aa*ee-bb*dd)/determinant
        if 0<=s<=1 and 0<=t<=1:candidates.append((s,t))
    points=[(along(a,u,s),along(c,v,t)) for s,t in candidates]
    p,q=min(points,key=lambda pair:math.dist(*pair))
    return math.dist(p,q),p,q


def review(components, radial_allowance_mm=0):
    if not math.isfinite(radial_allowance_mm) or radial_allowance_mm<0:
        raise ValueError("Invalid lead radial allowance")
    leads=[]
    for c in components:
        for lead in c['leads']:
            points=lead['points'];radius=lead['diameterMm']/2
            error=lead.get('centerlineApproximationMm',0)
            if len(points)<2 or not math.isfinite(radius) or radius<=0 or not math.isfinite(error) or error<0 or not all(len(p)==3 and all(math.isfinite(x) for x in p) for p in points):
                raise ValueError('Invalid lead geometry: '+c['ref']+':'+lead['pin'])
            lengths=[math.dist(a,b) for a,b in zip(points,points[1:])]
            stations=[0.]
            for length in lengths:stations.append(stations[-1]+length)
            segments=list(zip(points,points[1:]))
            leads.append({'terminal':c['ref']+':'+lead['pin'],'ref':c['ref'],'package':c['package'],
                          'net':lead['net'],'points':points,'radius':radius+error+radial_allowance_mm,'localRadius':radius+error,
                          'stations':stations,'segments':segments,
                          'bounds':[[min(p[k] for p in points),max(p[k] for p in points)] for k in range(3)],
                          'boxes':[[[min(a[k],b[k]),max(a[k],b[k])] for k in range(3)] for a,b in segments]})
    unintended=[];intended=[];closest=None

    def minimum(a,b,self_check=False,winding_join=False):
        best=None
        for i,(p0,p1) in enumerate(a['segments']):
            for j,(q0,q1) in enumerate(b['segments']):
                if self_check and j<=i+1:continue
                if best is not None:
                    lower=sum(max(0,x[0]-y[1],y[0]-x[1])**2 for x,y in zip(a['boxes'][i],b['boxes'][j]))
                    if lower>best[0]**2:continue
                distance,p,q=closest_segments(p0,p1,q0,q1)
                # Adjacent swept capsules intentionally overlap. Exclude only the
                # local tube neighbourhood by distance along the same conductor;
                # distant turns and crossings remain eligible even on the same net.
                if self_check or winding_join:
                    sp=a['stations'][i]+math.dist(p0,p)
                    sq=b['stations'][j]+math.dist(q0,q)
                    separation=(sq-sp if self_check else a['stations'][-1]-sp+b['stations'][-1]-sq)
                    if separation<=math.pi*(a['localRadius']+b['localRadius'])/2+1e-9:continue
                if best is None or distance<best[0]:best=(distance,p,q,i,j)
        return best

    def record_pair(a,b,nearest,join=None):
        nonlocal closest
        if nearest is None:return
        distance,p,q,i,j=nearest;gap=distance-a['radius']-b['radius']
        record={'terminals':[a['terminal'],b['terminal']],'nets':[a['net'],b['net']],
                'surfaceClearanceMm':round(gap,9),'closestCenterlinePointsMm':[[round(x,9) for x in point] for point in (p,q)]}
        if a is b:record['segments']=[i,j]
        if not join and (closest is None or gap<closest[0]):closest=(gap,record)
        if gap<=1e-9:
            if join:intended.append(dict(record,basis=join))
            else:unintended.append(record)

    for i,a in enumerate(leads):
        for b in leads[i+1:]:
            # AABB distance is a lower bound: skip only when this pair can
            # neither touch nor improve the smallest reported clearance.
            lower=sum(max(0,x[0]-y[1],y[0]-x[1])**2 for x,y in zip(a['bounds'],b['bounds']))
            limit=a['radius']+b['radius']+max(0,closest[0] if closest else float('inf'))
            if lower>limit**2:continue
            winding_join=a['ref']==b['ref'] and a['package']=='filter' and math.dist(a['points'][-1],b['points'][-1])<1e-8
            if winding_join:intended.append({'terminals':[a['terminal'],b['terminal']],'basis':'winding-midpoint'})
            join=('reference-bridge' if a['ref']==b['ref'] and a['package']=='bridge' else
                  'same-net' if not winding_join and a['net'] and a['net']==b['net'] else None)
            record_pair(a,b,minimum(a,b,winding_join=winding_join),join)
    for lead in leads:
        if lead['package']=='filter':record_pair(lead,lead,minimum(lead,lead,self_check=True))
    return {'method':'Minimum 3D segment distance minus wire radii and centerline approximation bounds. Touching is reported. Local overlap along a continuous winding is excluded by arc length; distinct turns are checked even on the same net.',
            'unintendedContacts':unintended,'intendedContacts':intended,
            'minimumUnintendedClearance':closest[1] if closest else None,
            'noUnintendedContact':not unintended,
            'radialAllowanceMm':radial_allowance_mm,
            'scope':'Capsule geometry includes tessellation error and the stated radial allowance. Local-neighbour exclusion uses nominal radii. No insulation rating or specimen dimension qualification.'}
