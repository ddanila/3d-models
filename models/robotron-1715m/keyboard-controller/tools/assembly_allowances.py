"""Conservative reference-design envelopes; not measured manufacturing tolerances."""
import math
from lead_clearance import review as lead_review


def expand(box, allowance):
    return [[low-allowance, high+allowance] for low, high in box]


def review(components, cores, layout, spec, segment_box, overlaps):
    keys=('bodyEnvelopeMm','leadRadialEnvelopeMm','coreEnvelopeMm','holeRadialLossMm')
    if any(not math.isfinite(spec[k]) or spec[k]<0 for k in keys):
        raise ValueError('Assembly allowances must be finite and nonnegative')
    body,wire,core,hole=(spec[k] for k in keys)
    bodies=[{'ref':c['ref'],'box':expand(c['boundsMm'],body)} for c in components if c['package'] not in ('bridge','filter','cable-termination')]
    core_boxes=[{'ref':c['id'],'box':expand(box,core)} for c in cores for box in c['solidBoxesMm']]
    collisions=[{'a':a['ref'],'b':b['ref']} for i,a in enumerate(bodies) for b in bodies[i+1:] if overlaps(a['box'],b['box'])]
    core_contacts=[{'component':a['ref'],'core':b['ref'],'kind':'body'} for a in bodies for b in core_boxes if overlaps(a['box'],b['box'])]
    lead_body=[];drills=[]
    pcb={c['ref']:c for c in layout['components']}
    for c in components:
        for lead in c['leads']:
            terminal=c['ref']+':'+lead['pin']
            radius=lead['diameterMm']/2+wire+lead.get('centerlineApproximationMm',0)
            segments=list(zip(lead['points'],lead['points'][1:]))
            for b in bodies:
                if c['ref']!=b['ref'] and any(segment_box(a,z,b['box'],radius) for a,z in segments):
                    lead_body.append({'terminal':terminal,'body':b['ref']})
            for b in core_boxes:
                if any(segment_box(a,z,b['box'],radius) for a,z in segments):
                    entry={'component':terminal,'core':b['ref'],'kind':'wire'}
                    if entry not in core_contacts:core_contacts.append(entry)
            pad=next(p for p in pcb[c['ref']]['pads'] if p['pin']==lead['pin'])
            # Hole fit uses a straight pin, so curved-path tessellation is irrelevant.
            clearance=min(pad['drill'])/2-hole-lead['diameterMm']/2-wire
            if clearance<=0:drills.append({'terminal':terminal,'radialClearanceMm':round(clearance,9)})
    lead_clearance=lead_review(components,radial_allowance_mm=wire)
    outline=layout['outlinePolygon'];board=[[min(p[k] for p in outline),max(p[k] for p in outline)] for k in range(2)]
    overhangs=sorted({b['ref'] for b in bodies+core_boxes if any(b['box'][k][0]<board[k][0] or b['box'][k][1]>board[k][1] for k in range(2))})
    return {'assumptions':spec,'bodyEnvelopeIntersections':collisions,'leadBodyEnvelopeIntersections':lead_body,
            'sharedCoreIntersections':core_contacts,'bodyOverhangs':overhangs,'insufficientHoleClearance':drills,
            'leadClearance':lead_clearance,
            'envelopesClear':not any((collisions,lead_body,core_contacts,overhangs,drills,lead_clearance['unintendedContacts'])),
            'mechanicallyQualified':False,
            'scope':'Independent isotropic envelopes for body dimensions/placement, lead forming and core dimensions/placement; hole radius loss is separate. Conservative boxes may overreport clashes. Excludes connector engagement, insulation, magnetic properties and measured specimen fit.'}


def scad_envelope(components,cores,spec):
    lines=['module reference_assembly_allowance_envelope() {']
    def box_shape(box):
        lines.append(f'translate({[p[0] for p in box]}) cube({[p[1]-p[0] for p in box]});')
    for c in components:
        if c['package'] not in ('bridge','filter','cable-termination'):box_shape(expand(c['boundsMm'],spec['bodyEnvelopeMm']))
        for lead in c['leads']:
            radius=lead['diameterMm']/2+spec['leadRadialEnvelopeMm']+lead.get('centerlineApproximationMm',0)
            # Circumscribe a polyhedron rather than inscribing one inside the
            # radius budget. The extra mesh conservatism cannot hide collisions.
            radius=round(radius/math.cos(math.pi/12)**2,9)+1e-9
            for a,b in zip(lead['points'],lead['points'][1:]):
                lines.append(f'hull() {{translate({a}) sphere(r={radius},$fn=12);translate({b}) sphere(r={radius},$fn=12);}}')
    for c in cores:
        for box in c['solidBoxesMm']:box_shape(expand(box,spec['coreEnvelopeMm']))
    return '\n'.join(lines+['}'])


def scad_leads(components, allowance, name):
    lines=['module '+name+'() {']
    for c in components:
        for lead in c['leads']:
            radius=(lead['diameterMm']/2+allowance+lead.get('centerlineApproximationMm',0))/math.cos(math.pi/12)**2
            radius=round(radius,9)+1e-9
            for a,b in zip(lead['points'],lead['points'][1:]):
                lines.append(f'hull() {{translate({a}) sphere(r={radius},$fn=12);translate({b}) sphere(r={radius},$fn=12);}}')
    return '\n'.join(lines+['}'])
