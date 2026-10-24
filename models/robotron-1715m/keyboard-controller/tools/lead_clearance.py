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


def review(components):
    leads=[]
    for c in components:
        for lead in c['leads']:
            points=lead['points'];radius=lead['diameterMm']/2
            if len(points)<2 or not math.isfinite(radius) or radius<=0 or not all(len(p)==3 and all(math.isfinite(x) for x in p) for p in points):
                raise ValueError('Invalid lead geometry: '+c['ref']+':'+lead['pin'])
            leads.append({'terminal':c['ref']+':'+lead['pin'],'ref':c['ref'],'package':c['package'],
                          'net':lead['net'],'points':points,'radius':radius})
    unintended=[];intended=[];closest=None
    for i,a in enumerate(leads):
        for b in leads[i+1:]:
            pairs=[(i,j,closest_segments(p0,p1,q0,q1))
                for i,(p0,p1) in enumerate(zip(a['points'],a['points'][1:]))
                for j,(q0,q1) in enumerate(zip(b['points'],b['points'][1:]))]
            winding_join=a['ref']==b['ref'] and a['package']=='filter' and math.dist(a['points'][-1],b['points'][-1])<1e-8
            if winding_join:
                intended.append({'terminals':[a['terminal'],b['terminal']],'basis':'winding-midpoint'})
                pairs=[pair for pair in pairs if pair[:2]!=(len(a['points'])-2,len(b['points'])-2)]
            if not pairs:continue
            distance,p,q=min((pair[2] for pair in pairs),key=lambda item:item[0])
            gap=distance-a['radius']-b['radius']
            join=('reference-bridge' if a['ref']==b['ref'] and a['package']=='bridge' else
                  'same-net' if a['net'] and a['net']==b['net'] else None)
            record={'terminals':[a['terminal'],b['terminal']],'nets':[a['net'],b['net']],
                    'surfaceClearanceMm':round(gap,9),'closestCenterlinePointsMm':[[round(x,9) for x in point] for point in (p,q)]}
            if not join and (closest is None or gap<closest[0]):closest=(gap,record)
            if gap<=1e-9:
                if join:intended.append(dict(record,basis=join))
                else:unintended.append(record)
    for lead in leads:
        if lead['package']!='filter':continue
        segments=list(zip(lead['points'],lead['points'][1:]))
        for i,(a,b) in enumerate(segments):
            for j in range(i+2,len(segments)):
                distance,p,q=closest_segments(a,b,*segments[j]);gap=distance-2*lead['radius']
                record={'terminals':[lead['terminal']]*2,'nets':[lead['net']]*2,'segments':[i,j],
                        'surfaceClearanceMm':round(gap,9),'closestCenterlinePointsMm':[list(p),list(q)]}
                if closest is None or gap<closest[0]:closest=(gap,record)
                if gap<=1e-9:unintended.append(record)
    return {'method':'Minimum 3D segment distance minus the two modeled wire radii. Includes bent segments, endpoints and zero-length segments; touching is reported. Same-net contacts and explicit bridge joins remain separate.',
            'unintendedContacts':unintended,'intendedContacts':intended,
            'minimumUnintendedClearance':closest[1] if closest else None,
            'noUnintendedContact':not unintended,
            'scope':'Nominal capsule geometry only. No manufacturing allowance, insulation rating, lead-forming radius or specimen dimension qualification.'}
