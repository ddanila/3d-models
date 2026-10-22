#!/usr/bin/env python3
"""Pad-driven reference assembly; mechanical assumptions never qualify historical geometry."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import struct

ROOT=Path(__file__).resolve().parents[1]
REF=ROOT/'reference'
def read(p): return json.loads(p.read_text())
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rotate(p,a):
    a=math.radians(a);return [p[0]*math.cos(a)-p[1]*math.sin(a),p[0]*math.sin(a)+p[1]*math.cos(a)]
def world(p,origin,a,z):
    q=rotate(p,a);return [round(q[0]+origin[0],6),round(q[1]+origin[1],6),z]
def vertices(path):
    raw=path.read_bytes();n=struct.unpack_from('<I',raw,80)[0]
    assert len(raw)==84+50*n,'Expected binary STL'
    return [struct.unpack_from('<3f',raw,84+50*i+12+12*j) for i in range(n) for j in range(3)]
def bounds(points): return [[min(p[i] for p in points),max(p[i] for p in points)] for i in range(3)]
def overlaps(a,b,margin=0):return all(min(a[i][1],b[i][1])-max(a[i][0],b[i][0])>margin for i in range(3))

def segment_box(a,b,box,radius):
    """Conservative swept-wire intersection with a body envelope."""
    low,high=0.,1.
    for i in range(3):
        delta=b[i]-a[i];minimum,maximum=box[i][0]-radius,box[i][1]+radius
        if abs(delta)<1e-9:
            if not minimum<a[i]<maximum:return False
        else:
            u,v=(minimum-a[i])/delta,(maximum-a[i])/delta
            low=max(low,min(u,v));high=min(high,max(u,v))
            if low>=high:return False
    return True

def build():
    layout=read(REF/'generated/layout.json');spec=read(REF/'assembly.json');evidence=read(ROOT/'evidence.json')
    packages={p['id']:p for p in evidence['packageReferences']}
    expected={c['ref'] for c in layout['components'] if not c['ref'].startswith('H')}
    if set(spec['components'])!=expected:raise ValueError('Assembly population differs from PCB')
    sources=['reference/assembly.json','reference/generated/layout.json','generated/connectivity.json','evidence.json','tools/reference_assembly.py']
    result=[]
    for c in layout['components']:
        ref=c['ref']
        if ref not in expected:continue
        s=spec['components'][ref];kind=s['package'];pads=c['pads'];n=len(pads);angle=c['rotation'];origin=c['position'];z=s['seatMm'];mesh=None;profile=None
        pinmap={p['pin']:p for p in pads}
        if kind=='dip':
            width=15.24 if n in (24,40) else 7.62
            mesh=f'components/kicad/meshes/DIP-{n}_W{width:.2f}mm-body.stl'
            sources.append('../'+mesh)
            points=[[*rotate(v[:2],-90),v[2]] for v in vertices(ROOT.parent/mesh)]
            bb=bounds(points);size=[b[1]-b[0] for b in bb]
            # Keep the original body unchanged. Leads bend from body edges to native pads.
            terminals={}
            for p in pads:
                local=rotate([p['position'][i]-origin[i] for i in range(2)],-angle)
                terminals[p['pin']]=[max(bb[0][0]+.2,min(bb[0][1]-.2,local[0])),math.copysign(size[1]/2,local[1]),z+.9]
        else:
            xs=[p['position'][0] for p in pads];ys=[p['position'][1] for p in pads]
            origin=[(min(xs)+max(xs))/2,(min(ys)+max(ys))/2]
            if n==2:
                a,b=pads;angle=math.degrees(math.atan2(b['position'][1]-a['position'][1],b['position'][0]-a['position'][0]))
            else:angle=0
            size=s.get('sizeMm')
            if kind=='transistor':
                package=packages[s['packageReference']];d=package['bodyDimensionsMm'];size=[d['width'],d['depth'],d['height']]
                w,d=size[:2];r=package['backCornerRadiusMm'];front=-package['flatFaceToLeadPlaneMm'];back=front+d
                profile=[[-w/2,front],[w/2,front]]+[[w/2-r+r*math.cos(math.radians(a)),back-r+r*math.sin(math.radians(a))] for a in range(0,91,10)]+[[-w/2+r+r*math.cos(math.radians(a)),back-r+r*math.sin(math.radians(a))] for a in range(90,181,10)]
                terminals={pin:[(i-1)*package['outerLeadSpanMm']/2,0,z] for i,pin in enumerate(package['terminalOrderInDrawing'])}
            elif kind in ('axial','filter'):
                terminals={p['pin']:[(-1 if i==0 else 1)*size[0]/2,0,z+size[2]/2] for i,p in enumerate(pads)}
            elif kind=='bridge':terminals={p['pin']:[0,0,z] for p in pads}
            elif kind=='capacitor':terminals={p['pin']:[(-1 if i==0 else 1)*1.5,0,z] for i,p in enumerate(pads)}
            else:terminals={p['pin']:[*rotate([p['position'][i]-origin[i] for i in range(2)],-angle),z] for p in pads}
            points=[[x*size[0]/2,y*size[1]/2+(.25 if kind=='transistor' else 0),h] for x in (-1,1) for y in (-1,1) for h in (0,size[2])]
        if set(terminals)!=set(pinmap):raise ValueError('Package terminal mismatch '+ref)
        leads=[]
        for pin,port in terminals.items():
            p=pinmap[pin];tip=[*p['position'],-.5];entry=[*p['position'],2.1];end=world(port[:2],origin,angle,port[2])
            leads.append({'pin':pin,'net':p['net'],'points':[tip,entry,end],'diameterMm':.3})
        bodybounds=bounds([world(p[:2],origin,angle,z+p[2]) for p in points])
        result.append({'ref':ref,'type':c['type'],'package':kind,'basis':s['basis'],'position':[ *origin,z],'rotation':angle,'sizeMm':size,'mesh':mesh,'profile':profile,'boundsMm':bodybounds,'leads':leads,'footprint':{'id':'RobotronReference_'+ref,'terminals':{p['pin']:{'offsetMm':rotate([p['position'][i]-origin[i] for i in range(2)],-angle),'net':p['net']} for p in pads}}})
    collisions=[{'a':a['ref'],'b':b['ref']} for i,a in enumerate(result) for b in result[i+1:] if overlaps(a['boundsMm'],b['boundsMm'],.05)]
    outline=layout['outlinePolygon'];xmin=min(p[0] for p in outline);xmax=max(p[0] for p in outline);ymin=min(p[1] for p in outline);ymax=max(p[1] for p in outline)
    outside=[c['ref'] for c in result if c['boundsMm'][0][0]<xmin or c['boundsMm'][0][1]>xmax or c['boundsMm'][1][0]<ymin or c['boundsMm'][1][1]>ymax]
    drill=[]
    for c in result:
        pcb=next(x for x in layout['components'] if x['ref']==c['ref'])
        for lead in c['leads']:
            pad=next(p for p in pcb['pads'] if p['pin']==lead['pin'])
            if math.dist(lead['points'][0][:2],pad['position'])>1e-6:raise ValueError('Lead misses pad')
            if min(pad['drill'])<lead['diameterMm']+.2:drill.append(c['ref']+':'+lead['pin'])
    lead_body=[]
    for c in result:
        for lead in c['leads']:
            for other in result:
                if c['ref']==other['ref'] or other['package']=='bridge':continue
                if any(segment_box(a,b,other['boundsMm'],lead['diameterMm']/2) for a,b in zip(lead['points'],lead['points'][1:])):
                    lead_body.append({'terminal':c['ref']+':'+lead['pin'],'body':other['ref']})
    report={'leadBodyEnvelopeIntersections':lead_body,'method':'Conservative axis-aligned body envelopes; nominal lead-to-drill allowance. Swept leads checked against foreign body envelopes. Lead-to-lead clearance, installed case and bend radii remain unqualified.','bodyEnvelopeIntersections':collisions,'bodyOverhangs':outside,'insufficientDrillAllowance':drill,'leadPadAlignmentPassed':True,'mechanicallyQualified':False,'historicallyVerified':False,'fabricationReady':False}
    paths=read(REF/'signal-paths.json');connectivity=read(ROOT/'generated/connectivity.json')['components']
    for stage in paths['stages']:
        if stage['ref'] not in expected:raise ValueError('Unknown walkthrough component')
        for terminal in stage['terminals']:
            ref,pin=terminal.split(':')
            if connectivity[ref]['pins'][pin]!=stage['net']:raise ValueError('Walkthrough net mismatch: '+terminal)
    sources.append('reference/signal-paths.json')
    data={'signalPaths':paths,'schema':1,'variant':'proposed-reference','scope':spec['scope'],'components':result,'review':report,'sources':{p:digest(ROOT/p) for p in sorted(set(sources))}}
    scad=['// Generated by tools/reference_assembly.py; all assembly placements are proposed.','module reference_populated_assembly() {']
    for c in result:
        p=c['position'];a=c['rotation'];size=c['sizeMm'];kind=c['package'];color=[.15,.15,.17] if kind in ('dip','transistor') else [.65,.5,.25] if kind in ('capacitor','network') else [.65,.7,.73]
        if kind!='bridge':
            if c['mesh']:shape=f'rotate([0,0,-90]) import("../../../{c["mesh"]}");'
            elif kind=='axial':shape=f'translate([0,0,{size[2]/2}]) rotate([0,90,0]) cylinder(d={size[1]},h={size[0]},center=true,$fn=24);'
            elif kind=='capacitor':shape=f'translate([0,0,{size[2]/2}]) rotate([90,0,0]) cylinder(d={size[0]},h={size[1]},center=true,$fn=32);'
            elif kind=='transistor':shape=f'linear_extrude({size[2]}) polygon({c["profile"]});'
            else:shape=f'translate({[-size[0]/2,-size[1]/2,0]}) cube({size});'
            scad.append(f'// {c["ref"]}: {c["basis"]}\ncolor({color}) translate({p}) rotate([0,0,{a}]) {shape}')
        for lead in c['leads']:
            for x,y in zip(lead['points'],lead['points'][1:]):scad.append(f'color([.75,.75,.78]) hull() {{translate({x}) sphere(d=.3,$fn=8); translate({y}) sphere(d=.3,$fn=8);}}')
    scad.append('}')
    return data,'\n'.join(scad)+'\n'

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');a=parser.parse_args();data,scad=build()
    for name,content in [('assembly.json',json.dumps(data,indent=2)+'\n'),('assembly.scad',scad)]:
        path=REF/'assembly-generated'/name
        if a.check:
            if not path.exists() or path.read_text()!=content:raise SystemExit('Stale reference assembly: '+name)
        else:path.parent.mkdir(exist_ok=True);path.write_text(content)
    print(json.dumps(data['review'],indent=2))
if __name__=='__main__':main()
