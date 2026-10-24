"""Proposed rectangular shared-core geometry; no magnetic or specimen calibration."""
import math


def build(spec, components):
    members=spec['members'];byref={c['ref']:c for c in components}
    if len(members)!=4 or len(set(members))!=4 or any(byref[r]['package']!='filter' for r in members):
        raise ValueError('Shared filter requires four distinct winding components')
    x,y,z=spec['positionMm'];w,d,h=spec['outerSizeMm'];iw,id_=spec['windowSizeMm']
    gap=spec['wireToCoreCenterlineMm'];diameter=spec['wireDiameterMm'];turns=spec['turns'];pitch=spec['turnPitchMm']
    if not (0<iw<w and 0<id_<d and h>0 and diameter>0 and gap>diameter/2 and turns>=1 and int(turns)==turns and pitch>diameter):
        raise ValueError('Invalid shared-core dimensions or winding clearance')
    boxes=[[[x-w/2,x-iw/2],[y-d/2,y+d/2],[z,z+h]],
           [[x+iw/2,x+w/2],[y-d/2,y+d/2],[z,z+h]],
           [[x-iw/2,x+iw/2],[y-d/2,y-id_/2],[z,z+h]],
           [[x-iw/2,x+iw/2],[y+id_/2,y+d/2],[z,z+h]]]
    for ref in members:
        c=byref[ref];a,b=sorted(c['leads'],key=lambda lead:lead['pin'])
        px=(a['points'][0][0]+b['points'][0][0])/2;py=(a['points'][0][1]+b['points'][0][1])/2
        sign=1 if py>y else -1
        if abs(px-x)+turns*pitch/2+diameter/2>=iw/2:
            raise ValueError('Winding crosses the core corner: '+ref)
        # Helical rectangular centerline, deliberately independent of electrical parameters.
        inner=y+sign*(id_/2-gap);outer=y+sign*(d/2+gap)
        corners=[(outer,z-gap),(inner,z-gap),(inner,z+h+gap),(outer,z+h+gap)]
        points=[]
        for step in range(4*turns+1):
            yy,zz=corners[step%4]
            points.append([round(px-turns*pitch/2+step*pitch/4,6),yy,zz])
        mid=len(points)//2
        a['points']=a['points'][:2]+points[:mid+1]
        b['points']=b['points'][:2]+list(reversed(points[mid:]))
        for lead in (a,b):lead['diameterMm']=diameter
        c['sharedBody']=spec['id']
        c['boundsMm']=[[min(p[i] for p in points)-diameter/2,max(p[i] for p in points)+diameter/2] for i in range(3)]
        c['basis']='Proposed winding on shared core; turn count and dimensions are mechanical assumptions, not measured inductance, coupling or specimen routing.'
    return {'id':spec['id'],'members':members,'shape':'rectangular-ring','positionMm':[x,y,z],
            'outerSizeMm':[w,d,h],'windowSizeMm':[iw,id_],
            'boundsMm':[[x-w/2,x+w/2],[y-d/2,y+d/2],[z,z+h]],'solidBoxesMm':boxes,
            'scope':spec['scope']}
