#!/usr/bin/env python3
"""Pad-driven reference assembly; mechanical assumptions never qualify historical geometry."""
import argparse
import difflib
import hashlib
import json
import math
from pathlib import Path
import struct
from lead_clearance import review as lead_clearance_review
from shared_filter import build as shared_filter_build
from lead_bends import fillet
from assembly_allowances import review as allowance_review, scad_envelope, scad_leads

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
    sources=['reference/assembly.json','reference/generated/layout.json','generated/connectivity.json','evidence.json','tools/reference_assembly.py','tools/lead_clearance.py','tools/lead_bends.py','tools/assembly_allowances.py']
    capacitor_packages={}
    for ref,component in spec['components'].items():
        if 'packageCandidate' not in component:continue
        name=component['packageCandidate']
        if component['package']!='radial-capacitor' or name!='reference/capacitor-package-low-profile.json':raise ValueError('Unsupported capacitor package source')
        candidate=read(ROOT/name);part=candidate['components'][ref]
        polarity_name='reference/capacitor-polarity.json';polarity=read(ROOT/polarity_name)
        terminal=polarity['components'][ref]
        connectivity=read(ROOT/'generated/connectivity.json')['components'][ref]
        if terminal['pins']!=connectivity['pins'] or {terminal['positivePin'],terminal['negativePin']}!=set(connectivity['pins']):raise ValueError('Capacitor polarity pin mapping changed')
        if connectivity['type']!=str(part['microfarads'])+'u':raise ValueError('Capacitor reference value changed')
        if ref.startswith('C3.') and (terminal['pins'][terminal['positivePin']]!='/+5V' or terminal['pins'][terminal['negativePin']]!='/GND'):raise ValueError('Capacitor supply polarity changed')
        component.update(sizeMm=candidate['bodyEnvelopeMm'],leadPitchMm=candidate['leadPitchNominalMm'],
            leadSectionMaximumMm=[candidate['leadDiameterMaximumMm'],0],bendRadiusMm=candidate['proposedBendRadiusMm'],bodyOffsetMm=part.get('proposedBodyOffsetMm',[0,0]))
        capacitor_packages[ref]={'partNumber':part['partNumber'],'ratedVoltageVolts':part['volts'],
            'source':candidate['source'],'bodyBasis':candidate['bodyBasis'],
            'positivePin':terminal['positivePin'],'negativePin':terminal['negativePin'],'polarityBasis':terminal['basis'],
            'polarityScope':polarity['scope'],'polaritySource':polarity['resetDiagnostic'] if terminal['basis']=='isolated-reset-diagnostic' else None}
        sources.extend([name,polarity_name])
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
            origin=[origin[i]+s.get('bodyOffsetMm',[0,0])[i] for i in range(2)]
            size=s.get('sizeMm')
            if kind=='transistor':
                package=packages[s['packageReference']];d=package['bodyDimensionsMm'];size=[d['width'],d['depth'],d['height']]
                w,d=size[:2];r=package['backCornerRadiusMm'];front=-package['flatFaceToLeadPlaneMm'];back=front+d
                profile=[[-w/2,front],[w/2,front]]+[[w/2-r+r*math.cos(math.radians(a)),back-r+r*math.sin(math.radians(a))] for a in range(0,91,10)]+[[-w/2+r+r*math.cos(math.radians(a)),back-r+r*math.sin(math.radians(a))] for a in range(90,181,10)]
                terminals={pin:[(i-1)*package['outerLeadSpanMm']/2,0,z] for i,pin in enumerate(package['terminalOrderInDrawing'])}
            elif kind=='network' and 'packageReference' in s:
                package=packages[s['packageReference']]
                mapping=s.get('terminalToPackagePin',{pin:pin for pin in pinmap});direction=s.get('packagePinDirection',1)
                if set(mapping)!=set(pinmap) or set(mapping.values())!={str(i) for i in range(1,package['leadCount']+1)} or direction not in (-1,1):raise ValueError('Incomplete network package mapping '+ref)
                if mapping[package['commonTerminal']]!=package['commonTerminal']:raise ValueError('Network common terminal changed '+ref)
                for pin in s.get('externallyOpenPackagePins',[]):
                    logical=next(k for k,v in mapping.items() if v==pin)
                    if pin not in package['resistorTerminals'] or pinmap[logical]['net'] is not None:raise ValueError('Connected spare resistor branch '+ref)
                terminals={pin:[direction*(int(mapping[pin])-(package['leadCount']+1)/2)*package['leadPitchMm'],0,z] for pin in pinmap}
            elif kind in ('axial','filter'):
                terminals={p['pin']:[(-1 if i==0 else 1)*size[0]/2,0,z+size[2]/2] for i,p in enumerate(pads)}
            elif kind=='bridge':terminals={p['pin']:[0,0,z] for p in pads}
            elif kind=='radial-capacitor':
                pitch=s['leadPitchMm']
                if n!=2 or not 0<pitch<size[0] or size[0]!=size[1]:raise ValueError('Invalid radial capacitor adapter '+ref)
                terminals={p['pin']:[(-1 if i==0 else 1)*pitch/2,0,z] for i,p in enumerate(pads)}
            elif kind=='capacitor':terminals={p['pin']:[(-1 if i==0 else 1)*1.5,0,z+1] for i,p in enumerate(pads)}
            else:terminals={p['pin']:[*rotate([p['position'][i]-origin[i] for i in range(2)],-angle),z] for p in pads}
            points=[[x*size[0]/2,y*size[1]/2+(.25 if kind=='transistor' else 0),h] for x in (-1,1) for y in (-1,1) for h in (0,size[2])]
        if set(terminals)!=set(pinmap):raise ValueError('Package terminal mismatch '+ref)
        leads=[]
        for pin,port in terminals.items():
            p=pinmap[pin];tip=[*p['position'],-.5];entry=[*p['position'],s.get('leadEntryHeightMm',2.1)];end=world(port[:2],origin,angle,port[2])
            path=[tip,end] if math.dist(tip[:2],end[:2])<1e-9 else [tip,entry,end]
            leads.append({'pin':pin,'net':p['net'],'points':path,'diameterMm':math.ceil(math.hypot(*s['leadSectionMaximumMm'])*1e9)/1e9 if 'leadSectionMaximumMm' in s else math.hypot(*package['leadSectionMm']) if kind=='transistor' else .3})
        if kind=='network' and 'packageReference' in s:
            for lead in leads:lead['packagePin']=mapping[lead['pin']]
        bodybounds=bounds([world(p[:2],origin,angle,z+p[2]) for p in points])
        result.append({'ref':ref,'type':c['type'],'package':kind,'basis':s['basis'],'position':[ *origin,z],'rotation':round(angle,9),'sizeMm':size,'mesh':mesh,'profile':profile,'boundsMm':bodybounds,'leads':leads,'footprint':{'id':'RobotronReference_'+ref,'terminals':{p['pin']:{'offsetMm':[round(v,9)+0.0 for v in rotate([p['position'][i]-origin[i] for i in range(2)],-angle)],'net':p['net']} for p in pads}}})
    for c in result:
        s=spec['components'][c['ref']]
        if c['ref'] in capacitor_packages:c['capacitorPackage']=capacitor_packages[c['ref']]
        if c['package']=='network' and 'packageReference' in s:
            c['packageReference']=s['packageReference'];c['externallyOpenPackagePins']=s.get('externallyOpenPackagePins',[])
    shared_bodies=[shared_filter_build(spec['sharedFilter'],result)]
    sources.append('tools/shared_filter.py')
    forming=spec['leadForming']
    for c in result:
        bend_radius=spec['components'][c['ref']].get('bendRadiusMm',forming['radiusMm'])
        if c['package']=='filter':
            a,b=c['leads']
            points,bends=fillet(a['points']+list(reversed(b['points'][:-1])),bend_radius,forming['chordErrorMm'])
            mid=len(points)//2
            a['points']=points[:mid+1];b['points']=list(reversed(points[mid:]))
            c['leadBends']=bends
        else:
            for lead in c['leads']:
                lead['points'],lead['bends']=fillet(lead['points'],bend_radius,forming['chordErrorMm'])
        for lead in c['leads']:
            if (lead.get('bends') or c.get('leadBends')) and bend_radius<=lead['diameterMm']/2:raise ValueError('Bend radius must exceed wire radius')
            lead['centerlineApproximationMm']=forming['chordErrorMm']+1e-9

    core_contacts=[]
    for core in shared_bodies:
        for c in result:
            if c['ref'] not in core['members'] and any(overlaps(c['boundsMm'],box) for box in core['solidBoxesMm']):
                core_contacts.append({'component':c['ref'],'core':core['id'],'kind':'body'})
            for lead in c['leads']:
                if any(segment_box(a,b,box,lead['diameterMm']/2+lead['centerlineApproximationMm']) for a,b in zip(lead['points'],lead['points'][1:]) for box in core['solidBoxesMm']):
                    core_contacts.append({'component':c['ref']+':'+lead['pin'],'core':core['id'],'kind':'wire'})
    collisions=[{'a':a['ref'],'b':b['ref']} for i,a in enumerate(result) for b in result[i+1:] if overlaps(a['boundsMm'],b['boundsMm'],.05)]
    outline=layout['outlinePolygon'];xmin=min(p[0] for p in outline);xmax=max(p[0] for p in outline);ymin=min(p[1] for p in outline);ymax=max(p[1] for p in outline)
    outside=[c['ref'] for c in result if c['boundsMm'][0][0]<xmin or c['boundsMm'][0][1]>xmax or c['boundsMm'][1][0]<ymin or c['boundsMm'][1][1]>ymax]
    core_overhangs=[c['id'] for c in shared_bodies if c['boundsMm'][0][0]<xmin or c['boundsMm'][0][1]>xmax or c['boundsMm'][1][0]<ymin or c['boundsMm'][1][1]>ymax]
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
                if any(segment_box(a,b,other['boundsMm'],lead['diameterMm']/2+lead['centerlineApproximationMm']) for a,b in zip(lead['points'],lead['points'][1:])):
                    lead_body.append({'terminal':c['ref']+':'+lead['pin'],'body':other['ref']})
    report={'sharedCoreIntersections':core_contacts,'sharedCoreOverhangs':core_overhangs,'leadClearance':lead_clearance_review(result),'leadBodyEnvelopeIntersections':lead_body,'method':'Conservative axis-aligned body envelopes; nominal lead-to-drill allowance. Swept leads checked against foreign body envelopes; transistor wires use the circumscribed diameter of the manufacturer lead section. Nominal lead-to-lead capsule clearances include centerline approximation bounds. Proposed circular bend radii are explicit; installed forming tolerances remain unqualified.','bodyEnvelopeIntersections':collisions,'bodyOverhangs':outside,'insufficientDrillAllowance':drill,'leadPadAlignmentPassed':True,'mechanicallyQualified':False,'historicallyVerified':False,'fabricationReady':False}
    report['assemblyAllowances']=allowance_review(result,shared_bodies,layout,spec['assemblyAllowances'],segment_box,overlaps)
    paths=read(REF/'signal-paths.json');connectivity=read(ROOT/'generated/connectivity.json')['components']
    for stage in paths['stages']:
        if stage['ref'] not in expected:raise ValueError('Unknown walkthrough component')
        for terminal in stage['terminals']:
            ref,pin=terminal.split(':')
            if connectivity[ref]['pins'][pin]!=stage['net']:raise ValueError('Walkthrough net mismatch: '+terminal)
    sources.append('reference/signal-paths.json')
    data={'signalPaths':paths,'schema':1,'variant':'proposed-reference','scope':spec['scope'],'leadForming':forming,'components':result,'sharedBodies':shared_bodies,'review':report,'sources':{p:digest(ROOT/p) for p in sorted(set(sources))}}
    scad=['// Generated by tools/reference_assembly.py; all assembly placements are proposed.','module reference_populated_assembly() {']
    for core in shared_bodies:
        w,d,h=core['outerSizeMm'];iw,ih=core['windowSizeMm']
        scad.append(f'color([.18,.19,.18]) translate({core["positionMm"]}) difference() {{translate({[-w/2,-d/2,0]}) cube({[w,d,h]});translate({[-iw/2,-ih/2,-.01]}) cube({[iw,ih,h+.02]});}}')
    for c in result:
        p=c['position'];a=c['rotation'];size=c['sizeMm'];kind=c['package'];color=[.15,.15,.17] if kind in ('dip','transistor','radial-capacitor') else [.65,.5,.25] if kind in ('capacitor','network') else [.65,.7,.73]
        if kind not in ('bridge','filter'):
            if c['mesh']:shape=f'rotate([0,0,-90]) import("../../../{c["mesh"]}");'
            elif kind=='axial':shape=f'translate([0,0,{size[2]/2}]) rotate([0,90,0]) cylinder(d={size[1]},h={size[0]},center=true,$fn=24);'
            elif kind=='radial-capacitor':shape=f'cylinder(d={size[0]},h={size[2]},$fn=32); color([.7,.7,.72]) translate([0,0,{size[2]-.15}]) cylinder(d={size[0]*.9},h=.15,$fn=32);'
            elif kind=='capacitor':shape=f'translate([0,0,{size[2]/2}]) rotate([90,0,0]) cylinder(d={size[0]},h={size[1]},center=true,$fn=32);'
            elif kind=='transistor':shape=f'linear_extrude({size[2]}) polygon({c["profile"]});'
            else:shape=f'translate({[-size[0]/2,-size[1]/2,0]}) cube({size});'
            scad.append(f'// {c["ref"]}: {c["basis"]}\ncolor({color}) translate({p}) rotate([0,0,{a}]) {{{shape}}}')
        for lead in c['leads']:
            for x,y in zip(lead['points'],lead['points'][1:]):scad.append(f'color([.75,.75,.78]) hull() {{translate({x}) sphere(d={lead["diameterMm"]},$fn=8); translate({y}) sphere(d={lead["diameterMm"]},$fn=8);}}')
    scad.append('}')
    scad.append(scad_envelope(result,shared_bodies,spec['assemblyAllowances']))
    scad.append(scad_leads(result,0,'reference_leads'))
    scad.append(scad_leads(result,spec['assemblyAllowances']['leadRadialEnvelopeMm'],'reference_lead_allowance_envelope'))
    return data,'\n'.join(scad)+'\n'

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');a=parser.parse_args();data,scad=build()
    for name,content in [('assembly.json',json.dumps(data,indent=2)+'\n'),('assembly.scad',scad)]:
        path=REF/'assembly-generated'/name
        if a.check:
            if not path.exists():raise SystemExit('Missing reference assembly: '+name)
            if path.read_text()!=content:
                diff=list(difflib.unified_diff(path.read_text().splitlines(),content.splitlines(),fromfile='retained/'+name,tofile='generated/'+name))
                raise SystemExit('Stale reference assembly: '+name+'\n'+'\n'.join(diff[:40]))
        else:path.parent.mkdir(exist_ok=True);path.write_text(content)
    print(json.dumps(data['review'],indent=2))
if __name__=='__main__':main()
