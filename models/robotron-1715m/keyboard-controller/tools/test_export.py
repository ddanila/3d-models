#!/usr/bin/env python3
"""Fast consistency and handedness checks; no KiCad install required."""
import importlib.util,json,subprocess,sys,tempfile,unittest,shutil
from pathlib import Path
from geometry import arc_points,outline_polygon
from photo_registration import homography,project,rigid_fit,selected_fits,review
R=Path(__file__).resolve().parents[1]
class ControllerExportTests(unittest.TestCase):
 def test_unused_package_lead_requires_catalog_and_no_schematic_pin(self):
  import copy
  from export import unused_package_pads
  records=json.loads((R/'component-evidence.json').read_text());evidence=json.loads((R/'evidence.json').read_text());components=json.loads((R/'generated/connectivity.json').read_text())['components']
  self.assertEqual(unused_package_pads(records,evidence,components),{'R1':{'10'}})
  bad=copy.deepcopy(records);bad['R1']['physicalUnusedPads']=['1']
  with self.assertRaisesRegex(ValueError,'catalog support'):unused_package_pads(bad,evidence,components)
  bad=copy.deepcopy(evidence);next(p for p in bad['packageReferences'] if p['id']=='kwh-3894')['unusedTerminals']=[]
  with self.assertRaisesRegex(ValueError,'catalog support'):unused_package_pads(records,bad,components)
  layout=json.loads((R/'generated/layout.json').read_text());r1=next(c for c in layout['unplaced'] if c['ref']=='R1');pads={p['pin']:p for p in r1['pads']}
  self.assertEqual(set(pads),{str(i) for i in range(1,11)})
  self.assertIsNone(pads['10']['net']);self.assertEqual(pads['10']['classification'],'no-internal-connection')
  for i in range(1,10):self.assertAlmostEqual(__import__('math').dist(pads[str(i)]['position'],pads[str(i+1)]['position']),2.5)
  self.assertNotIn('10',components['R1']['pins'])

 def test_eye_fit_checks_are_independent_and_domain_is_bounded(self):
  import copy
  from eye_registration import review
  from bottom_registration import inside_hull
  evidence=json.loads((R/'top-copper-landmarks.json').read_text())
  bottom=json.loads((R/'generated/bottom-registration.json').read_text())
  actual=review(evidence,bottom,R)
  self.assertTrue(actual['copperAssignmentQualified'])
  self.assertLess(actual['maxCheckResidualMm'],.5)
  self.assertEqual(actual,next(r for r in json.loads((R/'generated/top-registration.json').read_text())['pcbRegions']if r['id']=='latch-eyes'))
  underlying=next(r for r in bottom['pcbRegions']if r['id']==actual['bottomRegion'])
  for p in actual['anchorHull']:
   self.assertTrue(inside_hull(p,actual['eyeAnchorHull']))
   self.assertTrue(inside_hull(project(actual['topToBottom'],p),underlying['anchorHull']))
  self.assertFalse(inside_hull([1408,2923],actual['bottomHull']))
  bad=copy.deepcopy(evidence);bad['eyeRegistration']['checks'][0]=bad['eyeRegistration']['anchors'][0]
  with self.assertRaisesRegex(ValueError,'must be independent'):review(bad,bottom,R)
  bad=copy.deepcopy(evidence);bad['eyeRegistration']['bottomLandmarksSha256']='0'*64
  with self.assertRaisesRegex(ValueError,'Stale eye registration'):review(bad,bottom,R)
  bad=copy.deepcopy(evidence);bad['eyeRegistration']['checks'][0]['bottomPixel']=[0,0]
  with self.assertRaisesRegex(ValueError,'exceeds bounded'):review(bad,bottom,R)
  bad=copy.deepcopy(evidence);bad['eyeRegistration']['checks'][1]['bottomPixel'][0]+=25
  self.assertFalse(review(bad,bottom,R)['copperAssignmentQualified'])

 def test_sense_review_keeps_physical_candidates_separate_from_reference(self):
  from sense_review import build
  report=build(R)
  self.assertEqual(report['commonReferenceNet'],'/GND')
  trial=report['envelopeTrial']
  self.assertEqual(set(trial['boundedPaths']),{p['id'] for p in report['paths']})
  self.assertFalse(trial['copperAssignmentQualified']);self.assertFalse(trial['withinPhotoTolerance'])
  self.assertGreater(trial['maxCheckResidualMm'],trial['toleranceMm'])
  self.assertTrue(all(c['insideAnchorHull'] for c in trial['checks']))
  self.assertEqual(len(trial['checks']),len({(c['ref'],c['pin']) for c in trial['checks']}))
  self.assertEqual(trial['maxCheckResidualMm'],max(c['residualMm'] for c in trial['checks']))
  self.assertFalse(report['bankEndReview']['commonGroundAttachmentEstablished'])
  self.assertTrue(any(p[0]<1500 for p in report['paths'][0]['segments'][1]['points']))
  metric=report['metricReview']
  self.assertFalse(metric['copperAssignmentQualified'])
  self.assertAlmostEqual(metric['nativeCpuPitchMm'],2.54,places=6)
  self.assertEqual(metric['cpuReference']['longitudinalPitchMm'],2.5)
  for v in metric['variants']:
   self.assertEqual(v['independentCheckComponents'],['A2.1','A4','A8'])
   self.assertLess(v['maxHeldOutResidualMm'],v['maxNominalHeldOutResidualMm'])
   self.assertTrue(all(p['heldOut'] for p in v['pairs'] if p['terminals'][0].startswith(('A2.1:','A4:','A8:'))))
  for i,p in enumerate(report['paths']):
   self.assertEqual(p['referenceNet'],'/SENSE'+str(i))
   self.assertEqual(p['terminals'],['A4:'+str(i+1),'R1:'+str(9-i)])
   self.assertFalse(p['nativeCopper']);self.assertFalse(p['continuityEstablished'])
   self.assertFalse(p['qualifiedWholePathRegions']);self.assertFalse(p['collectorAttachmentEstablished'])
   self.assertEqual(p['bankPinCandidate']['status'],'inferred')
   self.assertIn('/ROW'+str(i),p['matrixInput']['nets'])

 def test_latch_attachment_audit_preserves_numbering_and_inference(self):
  from bus_review import build
  report=build()['latchAttachmentReview']
  self.assertEqual({r['terminal'] for r in report['rows']},{'A4:'+str(i) for i in range(1,21)})
  self.assertEqual(sum(r['comparisonLead'] is not None for r in report['rows']),10)
  self.assertFalse(report['continuityEstablished'])
  joins=[g for r in report['rows'] for g in r['nativeJoins']]
  self.assertEqual({g['group'] for g in joins},{'cpu-latch-d'+str(i) for i in [0,2,3,5,6,7]})
  self.assertTrue(all(a['status']=='inferred' for g in joins for a in g['attachmentRoutes']))
  for r in report['rows']:
   self.assertFalse(r['boardEntrySearch']['continuityEstablished'])
   if r['referenceNet'] in ['/D1','/D4']:
    self.assertFalse(r['nativeJoins']);self.assertTrue(r['unresolvedCandidates'])

 def test_cross_side_via_rejects_stale_or_displaced_evidence(self):
  import copy,hashlib
  from bottom_registration import review_registered_vias
  layout=json.loads((R/'generated/layout.json').read_text())
  reports={s:json.loads((R/('generated/'+s+'-registration.json')).read_text())for s in ('top','bottom')}
  hashes={s:hashlib.sha256((R/f).read_bytes()).hexdigest()for s,f in [('top','top-copper-landmarks.json'),('bottom','bottom-landmarks.json')]}
  self.assertEqual(review_registered_vias(layout['vias'],reports,hashes),layout['viaRegistration'])
  via=next(v for v in layout['vias']if v['evidence'].get('group')=='cpu-latch-d0')
  self.assertEqual(via['evidence']['status'],'inferred')
  bad=copy.deepcopy(via);bad['position'][0]+=.01
  with self.assertRaisesRegex(ValueError,'differs from cross-side'):review_registered_vias([bad],reports,hashes)
  bad=copy.deepcopy(via);bad['evidence']['crossSideRegistration']['top']['landmarksSha256']='0'*64
  with self.assertRaisesRegex(ValueError,'Stale via registration'):review_registered_vias([bad],reports,hashes)
  bad=copy.deepcopy(via);bad['evidence']['sources']=[s for s in bad['evidence']['sources']if s['id']!='photo-top']
  with self.assertRaisesRegex(ValueError,'both sides'):review_registered_vias([bad],reports,hashes)

 def test_native_hull_rounding_does_not_allow_photo_extrapolation(self):
  from bottom_registration import inside_hull
  for size in [1,100]:
   hull=[[0,0],[size,0],[size,size],[0,size]]
   self.assertFalse(inside_hull([-0.000001,size/2],hull))
   self.assertTrue(inside_hull([-0.000001,size/2],hull,0.000002))
   self.assertFalse(inside_hull([-0.001,size/2],hull,0.000002))

 def test_bus_search_preserves_occlusion_without_assigning_continuity(self):
  from bus_review import build
  report=build()
  self.assertEqual(report,json.loads((R/'generated/bus-review.json').read_text()))
  candidates={}
  for p in report['latchPaths']:candidates.setdefault(p['referenceNet'],p)
  self.assertTrue(candidates['/D1']['reverseReview']['positionCheck']['withinFitBudget'])
  self.assertNotIn('/D2',candidates)
  alternatives=candidates['/D1']['reverseReview']['alternatives']
  self.assertEqual(alternatives[0]['id'],'middle-eye')
  self.assertTrue(all(not a['positionCheck']['continuityEstablished'] for a in alternatives))
  self.assertFalse(candidates['/D1']['reverseReview']['continuationProjection']['insideFitHull'])
  d2=next(t for t in report['eyeReview']['targets']if t['referenceNet']=='/D2')
  self.assertTrue(d2['insideFitHull']);self.assertTrue(d2['withinFitBudget'])
  self.assertFalse(d2['continuityEstablished'])
  terminal=candidates['/D1']['terminalReview']
  self.assertEqual(terminal['terminal'],'A5:15')
  self.assertNotEqual(terminal['point'],candidates['/D1']['reverseReview']['unassignedEnd'])
  self.assertFalse(terminal['nativeCopper'])
  self.assertFalse(terminal['topProjection']['insideFitHull'])
  self.assertIsNone(terminal['topProjection']['endpointSeparationMm'])
  constraint=candidates['/D1']['referenceConstraints']
  self.assertFalse(constraint['compatibleWithTarget'])
  self.assertFalse(constraint['physicalIdentityEstablished'])
  self.assertEqual(next(t['net']for t in constraint['terminals']if t['terminal']=='R6.4:2'),'/CPU_PULLUP')
  alternate=next(p for p in report['latchPaths']if p['id']=='latch-review-d1-inner-eye')
  self.assertTrue(alternate['reverseReview']['positionCheck']['withinFitBudget'])
  self.assertEqual(alternate['reverseReview']['endKind'],'candidate-pad')
  self.assertEqual(alternate['referenceConstraints']['terminals'],[{'terminal':'A2.2:2','net':'/A7'}])
  self.assertFalse(alternate['referenceConstraints']['compatibleWithTarget'])
  trial=report['registrationTrials'][0]
  self.assertFalse(trial['copperAssignmentQualified'])
  self.assertFalse(trial['anchorsInsideBottomFitHull'])
  self.assertGreater(trial['maxCheckResidualPixels'],10)
  self.assertFalse(candidates['/D4']['comparisons'][0]['electricalIdentityTransferred'])
  self.assertFalse(alternate['continuityEstablished'])
  d4=candidates['/D4']['terminalReview']['topProjection']
  self.assertTrue(d4['insideFitHull']);self.assertGreater(d4['endpointSeparationMm'],4)
  self.assertFalse(d4['continuityEstablished'])
  self.assertFalse(candidates['/D1']['continuityEstablished'])
  self.assertFalse(report['crossSide']['copperAssignmentQualified'])
  self.assertFalse(report['crossSide']['comparison']['electricalIdentityTransferred'])
  for path in report['paths']:
   self.assertTrue(path['crossSideSearch']['insideCpuBodyWithSearchMargin'])
   self.assertFalse(path['crossSideSearch']['continuityEstablished'])
   self.assertFalse(path['nativeCopper'])
  with tempfile.TemporaryDirectory() as tmp:
   r=Path(tmp)/'board';shutil.copytree(R,r,ignore=shutil.ignore_patterns('__pycache__'))
   for source in json.loads((R/'evidence.json').read_text())['sources']:
    if source.get('path'):
     p=r/source['path'];p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/source['path'],p)
   original=json.loads((r/'bus-review.json').read_text())
   sense_original=json.loads((r/'sense-review.json').read_text())
   import copy
   from sense_review import build as sense_build
   for mutate,message in [(lambda d:d['paths'][0].update(nativeCopper=True),'cannot assign'),(lambda d:d['paths'][1].update(bankObservationIndex=d['paths'][0]['bankObservationIndex']),'must not share'),(lambda d:d.update(sourceSha256='0'*64),'source hash mismatch'),(lambda d:d['paths'][0]['segments'][0].update(status='observed'),'must remain inferred')]:
    bad=copy.deepcopy(sense_original);mutate(bad);(r/'sense-review.json').write_text(json.dumps(bad))
    with self.assertRaisesRegex(ValueError,message):sense_build(r)
   (r/'sense-review.json').write_text(json.dumps(sense_original))

   for mutate,message in [(lambda d:d['metricReview'].update(copperAssignmentQualified=True),'cannot qualify copper'),(lambda d:d['metricReview']['calibrationPairs'].__setitem__(1,d['metricReview']['calibrationPairs'][0]),'distinct distance'),(lambda d:d['metricReview']['calibrationPairs'].__setitem__(0,['A5:1','A1:1']),'within-package'),(lambda d:d['metricReview']['cpuReference'].update(longitudinalPitchMm=2.54),'pitch and end span')]:
    bad=copy.deepcopy(sense_original);mutate(bad);(r/'sense-review.json').write_text(json.dumps(bad))
    with self.assertRaisesRegex(ValueError,message):sense_build(r)
   (r/'sense-review.json').write_text(json.dumps(sense_original))

   for mutate,message in [(lambda d:d['envelopeTrial'].update(copperAssignmentQualified=True),'cannot qualify copper'),(lambda d:d['envelopeTrial'].update(modelCornerIndices=[0,1,2,3]),'mirrored underside'),(lambda d:d['bankEndReview'].update(commonGroundAttachmentEstablished=True),'cannot establish primary'),(lambda d:d['bankEndReview'].update(comparisonMarkSource='missing'),'hashed comparison')]:
    bad=copy.deepcopy(sense_original);mutate(bad);(r/'sense-review.json').write_text(json.dumps(bad))
    with self.assertRaisesRegex(ValueError,message):sense_build(r)
   (r/'sense-review.json').write_text(json.dumps(sense_original))

   import copy
   bad=copy.deepcopy(original);bad['crossSide']['sourceSha256']='0'*64
   (r/'bus-review.json').write_text(json.dumps(bad))
   with self.assertRaisesRegex(ValueError,'source hash mismatch'):build(r)
   bad=copy.deepcopy(original);bad['registrationTrials'][0]['copperAssignmentQualified']=True
   (r/'bus-review.json').write_text(json.dumps(bad))
   with self.assertRaisesRegex(ValueError,'cannot qualify copper'):build(r)
   bad=copy.deepcopy(original);bad['registrationTrials'][0]['checks'][0]=bad['registrationTrials'][0]['anchors'][0]
   (r/'bus-review.json').write_text(json.dumps(bad))
   with self.assertRaisesRegex(ValueError,'must be independent'):build(r)
   bad=copy.deepcopy(original);bad['latchPaths'][2]['comparisons'][0]['sourceSha256']='0'*64
   (r/'bus-review.json').write_text(json.dumps(bad))
   with self.assertRaisesRegex(ValueError,'source hash mismatch'):build(r)
   bad=copy.deepcopy(original);bad['latchAttachmentReview']['rows'][1]=bad['latchAttachmentReview']['rows'][0]
   (r/'bus-review.json').write_text(json.dumps(bad))
   with self.assertRaisesRegex(ValueError,'every package pin once'):build(r)
   bad=copy.deepcopy(original);bad['latchAttachmentReview']['rows'][0]['attachmentStatus']='observed'
   (r/'bus-review.json').write_text(json.dumps(bad))
   with self.assertRaisesRegex(ValueError,'cannot upgrade hidden'):build(r)
   bad=copy.deepcopy(original);bad['latchAttachmentReview']['photos'][2]['sourceSha256']='0'*64
   (r/'bus-review.json').write_text(json.dumps(bad))
   with self.assertRaisesRegex(ValueError,'source hash mismatch'):build(r)
   bad=copy.deepcopy(original);bad['crossSide']['checkTerminals']=['A5:1']
   (r/'bus-review.json').write_text(json.dumps(bad))
   with self.assertRaisesRegex(ValueError,'independent checks'):build(r)
   bad=copy.deepcopy(original);bad['latchPaths'][0]['reverseReview']['continuityEstablished']=True
   (r/'bus-review.json').write_text(json.dumps(bad))
   with self.assertRaisesRegex(ValueError,'correspondence is not established'):build(r)
   bad=copy.deepcopy(original);bad['latchPaths'][0]['terminalReview']['continuityEstablished']=True
   (r/'bus-review.json').write_text(json.dumps(bad))
   with self.assertRaisesRegex(ValueError,'cannot establish latch continuity'):build(r)
   bad=copy.deepcopy(original);bad['latchPaths'][0]['terminalReview']['point']=[1307,2706]
   (r/'bus-review.json').write_text(json.dumps(bad))
   with self.assertRaisesRegex(ValueError,'recorded underside pin landmark'):build(r)
   bad=copy.deepcopy(original);bad['latchPaths'][0]['reverseReview']['alternatives'][0]['point']=[0,0]
   (r/'bus-review.json').write_text(json.dumps(bad))
   with self.assertRaisesRegex(ValueError,'exceeds local fit hull'):build(r)
   bad=copy.deepcopy(original);bad['latchPaths'][0]['terminalReview']['topReview']['sourceSha256']='0'*64
   (r/'bus-review.json').write_text(json.dumps(bad))
   with self.assertRaisesRegex(ValueError,'source hash mismatch'):build(r)
   bad=copy.deepcopy(original);bad['eyeReview']['targets'][0]['top']=[1501,2847]
   (r/'bus-review.json').write_text(json.dumps(bad))
   with self.assertRaisesRegex(ValueError,'own eye fit anchor'):build(r)
   bad=copy.deepcopy(original);bad['paths'][0]['observedEnds'][0]['point']=[1400,2700]
   (r/'bus-review.json').write_text(json.dumps(bad))
   self.assertFalse(build(r)['paths'][0]['crossSideSearch']['insideCpuBodyWithSearchMargin'])

 def test_cable_graph_does_not_join_windings_or_assign_terminals(self):
  import copy
  from cable_copper import build,partition
  report=build()
  self.assertEqual(report,json.loads((R/'generated/cable-copper.json').read_text()))
  group=next(g for g in report['connectedGroups'] if 'CF2' in g)
  self.assertEqual(group,['CF2','CL1','E2'])
  self.assertFalse(any(n.startswith('LF') for n in group))
  self.assertIn(['LF3'],report['connectedGroups'])
  self.assertFalse(report['projection']['copperAssignmentQualified'])
  self.assertFalse(report['comparison']['electricalIdentityTransferred'])
  self.assertEqual(report['assignedReferenceTerminals'],{})
  self.assertTrue(all(n['net'] is None for n in report['nodes'].values()))
  # Reversing the winding row must survive as a hypothesis, not a copper edge.
  self.assertIn({'CF1':'LF4','CF2':'LF3','CF3':'LF2','CF4':'LF1'},report['windingPairingCandidates'])
  edges=copy.deepcopy(report['edges']);edges[0]['status']='inferred'
  with self.assertRaisesRegex(ValueError,'Uncertain joins'):partition(report['nodes'],edges)
  edges=copy.deepcopy(report['edges']);edges[0]['ends'][0]='missing'
  with self.assertRaisesRegex(ValueError,'Invalid graph edge'):partition(report['nodes'],edges)

 def test_supply_fit_does_not_promote_extrapolation_to_identity(self):
  from cable_copper import build
  report=build();review=report['supplyReview']
  upper,extended=review['fits']
  self.assertLess(max(c['residualPixels'] for c in upper['checks']),5)
  self.assertGreater(max(c['residualPixels'] for c in upper['extrapolationChecks']),90)
  self.assertGreater(review['maxFilterFitDisagreementPixels'],30)
  for fit in review['fits']:
   self.assertFalse(fit['copperAssignmentQualified'])
   self.assertTrue(all(not p['insideAnchorHull'] for p in fit['filterPredictions'].values()))
   self.assertFalse({a['terminal'] for a in fit['anchors']} & {c['terminal'] for c in fit['checks']})
  self.assertEqual(review['assignedFilterTerminals'],{})
  self.assertEqual(review['rejectedWindingPairings'],[])
  self.assertEqual(len(report['windingPairingCandidates']),24)
  self.assertEqual({t['net'] for t in review['groundTerminals']},{'/GND'})
  routes=json.loads((R/'route-evidence.json').read_text())['items']
  for span in review['supplySpans']:
   route=routes[span['routeId']]
   self.assertEqual(span['photoPixels'],route['sources'][0]['locator']['pixelSegment'])
   self.assertEqual(span['status'],route['status'])

 def test_filter_correspondence_is_bounded_and_cannot_assign_nets(self):
  from copy import deepcopy
  from cable_copper import build,filter_registration
  report=build();fit=report['filterRegistration']
  self.assertTrue(fit['photoAlignmentAccepted'])
  self.assertLessEqual(fit['maxCheckResidualPixels'],fit['tolerancePixels'])
  self.assertTrue(all(c['insideAnchorHull'] for c in fit['checks']))
  self.assertTrue(all(not c['insideAnchorHull'] for c in fit['extrapolationChecks']))
  self.assertFalse(fit['copperAssignmentQualified'])
  self.assertEqual(fit['assignedReferenceTerminals'],{})
  self.assertEqual({s['id'] for s in fit['boundedUndersideSpans']},{'cf1-stub','cf2-stub','cf3-stub','cf4-stub'})
  self.assertTrue(all(s['net'] is None and s['status']=='projected-underside-observation' for s in fit['boundedUndersideSpans']))
  read=lambda name:json.loads((R/name).read_text())
  config,graph,assembly,components=[read(name)for name in ['filter-registration.json','cable-copper.json','output-assembly.json','component-evidence.json']]
  source=lambda sid:next(s for s in read('evidence.json')['sources']if s['id']==sid)
  bad=deepcopy(assembly);bad['filter']['jointRowsPixels']['cableFacing'][1][1]+=30
  rejected=filter_registration(config,graph,bad,components,source)
  self.assertFalse(rejected['photoAlignmentAccepted'])
  self.assertEqual(rejected['boundedUndersideSpans'],[])
  self.assertTrue(any(s['reason']=='fit-rejected'for s in rejected['excludedSpans']))
  bad=deepcopy(config);bad['checks'][0]=bad['anchors'][0]
  with self.assertRaisesRegex(ValueError,'held out'):filter_registration(bad,graph,assembly,components,source)
  bad=deepcopy(config);bad['anchors'][2],bad['anchors'][3]=bad['anchors'][3],bad['anchors'][2]
  with self.assertRaisesRegex(ValueError,'convex boundary'):filter_registration(bad,graph,assembly,components,source)
  bad=deepcopy(config);bad['topPhotoSource']='comparison-photo-080406304'
  with self.assertRaisesRegex(ValueError,'primary top'):filter_registration(bad,graph,assembly,components,source)

 def test_clock_continuation_does_not_bridge_occluded_spans(self):
  from connection_review import build
  c=next(c for c in build()['cases']if c['id']=='host-clock')['continuation']
  self.assertTrue(c['bankRegistration']['photoAlignmentAccepted'])
  self.assertLess(c['bankRegistration']['maxCheckResidualPixels'],3)
  self.assertTrue(c['bankReturn']['geometricCorrespondenceAccepted'])
  self.assertLess(c['bankReturn']['residualPixels'],3)
  self.assertTrue(c['clockStop']['insideAnchorHull'])
  self.assertTrue(c['upperStop']['insideAnchorHull'])
  self.assertFalse(c['electricalPathComplete'])
  self.assertEqual(c['assignedReferenceTerminals'],{})
  self.assertEqual(c['newNativeRoutes'],[])
  spans=[s for f in c['figures']for s in f['segments']]
  self.assertTrue(all(s['net'] is None for s in spans))
  self.assertEqual(len([s for s in spans if s['id']=='outer-lane-to-upper-eye']),1)
  self.assertEqual({g['id']for g in c['openJoins']},{'clock-stop-to-bank-lane','under-r96','under-r97','return-eye-transition','upper-eye-to-filter','upper-eye-to-corridor','under-capacitor'})
  self.assertTrue(all(s['specimenId'] for s in c['comparisonSources']))
  trial=c['upperCorridor']['registration']
  self.assertFalse(trial['photoAlignmentAccepted'])
  self.assertGreater(trial['maxCheckResidualPixels'],18)
  self.assertTrue(any(p['residualPixels']>p['allowancePixels'] for p in trial['checks']))
  self.assertEqual(c['upperCorridor']['assignedFilterTerminals'],{})
  self.assertTrue(all('bottomPixel' not in p for p in c['upperCorridor']['unmatchedTopFeatures']))
  self.assertEqual(next(s for s in spans if s['id']=='upper-corridor-middle')['points'][-1],[1440,810])

 def test_data_and_strobe_tracing_preserves_unresolved_joins(self):
  from connection_review import build
  cases={c['id']:c for c in build()['cases']}
  data,strobe=[cases[name]['traceReview'] for name in ['host-data','clock-strobe']]
  self.assertTrue(data['stop']['insideAnchorHull'])
  self.assertLess(data['registrations'][0]['maxCheckResidualPixels'],3)
  self.assertTrue(data['registrations'][1]['photoAlignmentAccepted'])
  self.assertTrue(data['figures'][1]['source']['specimenId'])
  self.assertFalse(strobe['a6Candidate']['insideAnchorHull'])
  self.assertFalse(strobe['a6Candidate']['layerTransitionQualified'])
  self.assertLess(strobe['a6Candidate']['residualPixels'],8)
  self.assertTrue(strobe['a4Candidate']['outsideAnchorBounds'])
  for review in [data,strobe]:
   self.assertFalse(review['electricalPathComplete'])
   self.assertEqual(review['newNativeRoutes'],[])
   self.assertEqual(review['assignedReferenceTerminals'],{})
   self.assertTrue(all(s['net'] is None for f in review['figures'] for s in f['segments']))

 def test_cpu_reverse_keeps_both_candidates_and_neighbour_lane_unassigned(self):
  from connection_review import build,render
  report=build()
  reverse=next(c for c in report['cases'] if c['id']=='clock-strobe')['traceReview']['cpuReverse']
  self.assertEqual({c['terminal'] for c in reverse['candidates']},{'A5:21','A5:22'})
  self.assertTrue(all(not c['excluded'] and not c['observedPathToA6'] for c in reverse['candidates']))
  self.assertFalse(reverse['electricalPathComplete'])
  self.assertEqual(reverse['newNativeRoutes'],[])
  self.assertEqual(reverse['assignedReferenceTerminals'],{})
  self.assertTrue(all(s['net'] is None for f in reverse['figures'] for s in f['segments']))
  self.assertEqual(reverse['figures'][-1]['imageSize'],[4080,3072])
  self.assertIn('width="4080" height="3072"',render(report))
  self.assertNotIn(reverse['primary']['neighbourLand'],[c['bottomPixel'] for c in reverse['candidates']])

 def test_path_tracing_rejects_broken_endpoint_and_reused_check(self):
  from copy import deepcopy
  from connection_review import INPUTS
  from path_tracing import build
  data={name:json.loads((R/name).read_text()) for name in INPUTS}
  source=lambda sid:next(s for s in data['evidence.json']['sources'] if s['id']==sid)
  bad=deepcopy(data);bad['path-tracing.json']['clock-strobe']['bottomSpan']['points'][-1]=[1620,3110]
  with self.assertRaisesRegex(ValueError,'canonical terminal'):build(bad,source)
  bad=deepcopy(data);bad['path-tracing.json']['host-data']['registration']['checks'][0]='R8:1'
  with self.assertRaisesRegex(ValueError,'independent fit checks'):build(bad,source)
  bad=deepcopy(data);bad['path-tracing.json']['host-data']['comparison']['source']='photo-top'
  with self.assertRaisesRegex(ValueError,'specimen identity'):build(bad,source)
  bad=deepcopy(data);bad['path-tracing.json']['clock-strobe']['cpuReverse']['candidates'][0]['excluded']=True
  with self.assertRaisesRegex(ValueError,'cannot resolve or exclude'):build(bad,source)
  bad=deepcopy(data);bad['path-tracing.json']['clock-strobe']['cpuReverse']['candidates'][0]['bottomPixel']=[1125,3148]
  with self.assertRaisesRegex(ValueError,'canonical pin observations'):build(bad,source)


 def test_output_assembly_is_visual_and_preserves_reference_pads(self):
  import copy
  from output_assembly import build
  observation=json.loads((R/'output-assembly.json').read_text())
  evidence=json.loads((R/'evidence.json').read_text())
  landmarks=json.loads((R/'photo-landmarks.json').read_text())
  layout=json.loads((R/'generated/layout.json').read_text())
  result=build(observation,evidence,landmarks)
  self.assertEqual(result,layout['visualOutputAssembly'])
  self.assertNotIn('pads',result);self.assertNotIn('net',result)
  self.assertTrue(all(ref in {c['ref'] for c in layout['unplaced']} for ref in observation['refs'] if ref!='XT1'))
  for p in result['filter']['bodyPolygon']:
   self.assertTrue(-135<p[0]<135 and -23<p[1]<23)
  wrong=copy.deepcopy(observation);wrong['photoSource']='comparison-photo-080406304'
  with self.assertRaisesRegex(ValueError,'primary registered'):build(wrong,evidence,landmarks)
  wrong=copy.deepcopy(observation);wrong['filter']['wireHeightMm']=1.6
  with self.assertRaisesRegex(ValueError,'above the board'):build(wrong,evidence,landmarks)

 def test_connection_review_uses_reference_nets_and_separate_connectors(self):
  from connection_review import build,render
  report=build();cases={c['id']:c for c in report['cases']}
  self.assertEqual(cases['host-clock']['referenceNets'][1]['terminals'],['L1.1:2','XT1:B2'])
  self.assertEqual(cases['host-data']['referenceNets'][1]['terminals'],['L1.4:2','XT1:A1'])
  self.assertEqual(cases['clock-strobe']['candidateEndpoints'],[{'terminal':'A5:21','net':'/RD_N'}])
  self.assertEqual(cases['x1-a8']['referenceNets'],[])
  self.assertEqual({f['source']['id']for f in cases['x1-a8']['figures']},{'photo-top','photo-bottom'})
  self.assertTrue(cases['x1-order']['terminalOrder']['completeTerminalOrderResolved'])
  self.assertIn('not measured continuity',render(report))

 def test_connection_review_rejects_changed_net_and_route_evidence(self):
  from connection_review import build,INPUTS,CODE_INPUTS
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp)/'board';root.mkdir()
   (root.parent/'reference').symlink_to(R.parent/'reference',target_is_directory=True)
   for name in INPUTS+CODE_INPUTS:
    target=root/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/name,target)
   p=root/'generated/connectivity.json';original=p.read_text();data=json.loads(original)
   data['components']['XT1']['pins']['B2']='/CABLE_DATEN';p.write_text(json.dumps(data))
   with self.assertRaisesRegex(ValueError,'Reference endpoint net mismatch'):build(root)
   p.write_text(original)
   p=root/'route-evidence.json';data=json.loads(p.read_text())
   item=next(v for v in data['items'].values()if v['group']=='r101-output-top-local')
   item['status']='observed' if item['status']!='observed' else 'inferred';p.write_text(json.dumps(data))
   with self.assertRaisesRegex(ValueError,'Native route review mismatch'):build(root)

 def test_cross_side_search_retains_occlusion_and_extrapolation(self):
  from connection_review import build,cross_side_search,INPUTS
  report=build()
  for case in report['cases'][:2]:
   search=case['crossSideSearch']
   self.assertFalse(search['copperAssignmentQualified'])
   self.assertLess(search['fitSpreadPixels'],4)
   for fit in search['fits']:
    self.assertTrue(fit['insideAnchorHull'])
    self.assertTrue(set(a['terminal'] for a in fit['anchors']).isdisjoint(c['terminal'] for c in fit['checks']))
   marker=next(m for f in case['figures'] for m in f['markers'] if m.get('kind')=='search')
   self.assertIn(case['crossSideStop']['occludingBody'],marker['label'])
  data={name:json.loads((R/name).read_text()) for name in INPUTS}
  stop=dict(data['connection-review.json']['cases'][0]['crossSideStop'],bottomPixel=[0,0])
  search=cross_side_search(data,stop)
  self.assertTrue(all(not f['insideAnchorHull'] for f in search['fits']))
  self.assertFalse(search['copperAssignmentQualified'])
  data['connection-review.json']['crossSideSearch']['fits'][0]=['R4.2:1']*4
  with self.assertRaisesRegex(ValueError,'distinct anchors'):cross_side_search(data,stop)

 def test_visual_networks_do_not_create_electrical_pads(self):
  import copy
  from export import visual_networks
  components=json.loads((R/'component-evidence.json').read_text())
  evidence=json.loads((R/'evidence.json').read_text())
  landmarks=json.loads((R/'photo-landmarks.json').read_text())
  layout=json.loads((R/'generated/layout.json').read_text())
  result=visual_networks(components,evidence,landmarks,layout['unplaced'])
  self.assert_report_equal(result,layout['visualNetworks'])
  self.assertEqual({n['ref']for n in result},{'R1','R2'})
  for n in result:
   self.assertNotIn('pads',n);self.assertNotIn('net',n)
   self.assertEqual(len(n['observedLeads']),10)
   self.assertTrue(20<n['length']<30)
   self.assertFalse(any(c['ref']==n['ref']for c in layout['components']))
  self.assertEqual(visual_networks(components,evidence,landmarks,[]),[])
  wrong=copy.deepcopy(components)
  wrong['R1']['visualNetworkCandidate']['photoSource']='comparison-photo-080450163'
  with self.assertRaisesRegex(ValueError,'primary registered photo'):visual_networks(wrong,evidence,landmarks,layout['unplaced'])
  wrong=copy.deepcopy(components)
  wrong['R1']['visualNetworkCandidate']['photoBodyAxis']=[[1,1],[1,1]]
  with self.assertRaisesRegex(ValueError,'Degenerate'):visual_networks(wrong,evidence,landmarks,layout['unplaced'])

 def test_visual_axials_keep_photo_bodies_separate_from_holes(self):
  import copy
  from export import visual_axials
  components=json.loads((R/'component-evidence.json').read_text())
  evidence=json.loads((R/'evidence.json').read_text())
  landmarks=json.loads((R/'photo-landmarks.json').read_text())
  layout=json.loads((R/'generated/layout.json').read_text())
  result=visual_axials(components,evidence,landmarks,layout['unplaced'])
  self.assert_report_equal(result,layout['visualAxials'])
  self.assertEqual({n['ref']for n in result},{'R6.4','R6.5'})
  for n in result:
   self.assertNotIn('pads',n);self.assertNotIn('net',n)
   self.assertEqual(len(n['observedLeads']),2)
   self.assertFalse(any(c['ref']==n['ref']for c in layout['components']))
  self.assertEqual(visual_axials(components,evidence,landmarks,[]),[])
  wrong=copy.deepcopy(components)
  wrong['R6.4']['placementCandidate']['photoSource']='comparison-photo-080434345'
  with self.assertRaisesRegex(ValueError,'primary registered photo'):visual_axials(wrong,evidence,landmarks,layout['unplaced'])
  wrong=copy.deepcopy(components)
  wrong['R6.5']['visualAxialCandidate']['bodyCentreHeightMm']=1
  with self.assertRaisesRegex(ValueError,'above the board'):visual_axials(wrong,evidence,landmarks,layout['unplaced'])

 def assert_report_equal(self,actual,expected,path='report'):
  # Python/libm versions can differ by an ULP in distance calculations.
  # Preserve exact structure and labels; this tolerance is far below native nanometre rounding.
  if isinstance(actual,dict):
   self.assertEqual(set(actual),set(expected),path)
   for key in actual:self.assert_report_equal(actual[key],expected[key],path+'/'+key)
  elif isinstance(actual,list):
   self.assertEqual(len(actual),len(expected),path)
   for i,(a,b) in enumerate(zip(actual,expected)):self.assert_report_equal(a,b,path+'/'+str(i))
  elif isinstance(actual,float):self.assertAlmostEqual(actual,expected,delta=1e-12,msg=path)
  else:self.assertEqual(actual,expected,path)

 def test_connector_terminal_constraints_do_not_assume_matching_row_direction(self):
  import copy
  from connector_terminals import review as terminal_review
  component=json.loads((R/'component-evidence.json').read_text())['X1']
  connectivity=json.loads((R/'generated/connectivity.json').read_text())
  result=terminal_review(component,connectivity)
  self.assertEqual(result,json.loads((R/'generated/connector-terminals.json').read_text()))
  self.assertEqual(result['resolvedRows']['housingFar'],['A'+str(i) for i in range(1,14)])
  self.assertEqual(result['resolvedRows']['housingNear'],['B'+str(i) for i in range(1,14)])
  self.assertEqual(result['unresolvedRows'],[])
  self.assertTrue(result['completeTerminalOrderResolved'])
  incomplete=copy.deepcopy(component)
  incomplete['physicalReview']['terminalConstraints']=[c for c in incomplete['physicalReview']['terminalConstraints'] if c['photoSource']=='photo-top']
  unresolved=terminal_review(incomplete,connectivity)
  self.assertEqual(unresolved['unresolvedRows'],['housingNear'])
  self.assertFalse(unresolved['completeTerminalOrderResolved'])
  comparison=copy.deepcopy(component)
  comparison['physicalReview']['terminalConstraints'][-1]['photoSource']='comparison-photo-080347973'
  with self.assertRaisesRegex(ValueError,'primary photograph'):terminal_review(comparison,connectivity)
  self.assertEqual(result['referenceAbsentPins'],['A8'])
  wrong=copy.deepcopy(component)
  wrong['physicalReview']['terminalConstraints'][1]['indexFromCable']=4
  rejected=terminal_review(wrong,connectivity)
  self.assertEqual(rejected['resolvedRows'],{})
  self.assertFalse(any(c['consistent'] for c in rejected['candidates']))
 def test_connector_review_keeps_observations_unnumbered(self):
  import copy
  from connector_review import review as connector_review, placement_review
  layout=json.loads((R/'generated/layout.json').read_text())
  components=json.loads((R/'component-evidence.json').read_text())
  sources=json.loads((R/'evidence.json').read_text())
  landmarks=json.loads((R/'photo-landmarks.json').read_text())
  before=copy.deepcopy(layout)
  bottom=json.loads((R/'generated/bottom-registration.json').read_text())
  result=connector_review(layout,components,sources,landmarks,bottom)
  terminals=json.loads((R/'generated/connector-terminals.json').read_text())
  result['nativePlacement']=placement_review(layout,result,terminals)
  self.assert_report_equal(result,json.loads((R/'generated/connector-review.json').read_text()))
  self.assertEqual(result['nativePlacement']['unclassifiedContacts'],['A8'])
  shifted=copy.deepcopy(layout)
  next(c for c in shifted['components'] if c['ref']=='X1')['pads'][0]['position'][0]+=.2
  with self.assertRaisesRegex(ValueError,'native pads differ'):placement_review(shifted,result,terminals)
  self.assertFalse(result['qualifiedForPadPlacement'])
  visual=next(c for c in layout['visualConnectors'] if c['ref']=='X1')
  self.assertEqual(visual['rows'],result['underside']['projectedJointRowsMm'])
  self.assertEqual(visual['status'],'photo-placed-reference-terminal-order')
  self.assertNotIn('nets',visual)
  self.assertNotIn('pins',visual)
  self.assertTrue(result['underside']['allJointsInsideAnchorHull'])
  self.assertTrue(result['underside']['registrationWithinTolerance'])
  self.assertFalse(result['underside']['terminalMappingQualified'])
  badbottom=copy.deepcopy(bottom);badbottom['photoSha256']='changed'
  with self.assertRaisesRegex(ValueError,'photograph differs'):
   connector_review(layout,components,sources,landmarks,badbottom)
  self.assertEqual(set(result['projectedLeadEndRowsMm']),{'housingNear','housingFar'})
  self.assertEqual(layout,before)
  bad=copy.deepcopy(components);bad['X1']['physicalReview']['photoSha256']='changed'
  with self.assertRaisesRegex(ValueError,'photograph differs'):
   connector_review(layout,bad,sources,landmarks)
  bad=copy.deepcopy(components);bad['X1']['physicalReview']['leadEndRowsPixels']['housingNear'].pop()
  with self.assertRaisesRegex(ValueError,'Unpaired'):
   connector_review(layout,bad,sources,landmarks)
 def test_visual_bridge_does_not_assign_pads_or_duplicate_native_placement(self):
  from export import visual_bridges
  import copy
  evidence=json.loads((R/'evidence.json').read_text())
  landmarks=json.loads((R/'photo-landmarks.json').read_text())
  layout=json.loads((R/'generated/layout.json').read_text())
  bridges=visual_bridges(evidence,landmarks,layout['unplaced'])
  self.assertEqual(bridges,layout['visualBridges'])
  self.assertEqual([b['ref'] for b in bridges],['BR2'])
  self.assertFalse(any(p['ref']=='BR2' for c in layout['components'] for p in c['pads']))
  self.assertNotIn('net',bridges[0]);self.assertNotIn('pads',bridges[0])
  self.assertEqual(visual_bridges(evidence,landmarks,[]),[])
  changed=copy.deepcopy(evidence)
  br=next(b for b in changed['serviceInterfaces']['bridges']if b['ref']=='BR2')
  br['physicalEvidence']['photoEndpoints'][1]=br['physicalEvidence']['photoEndpoints'][0]
  with self.assertRaisesRegex(ValueError,'Degenerate'):visual_bridges(changed,landmarks,layout['unplaced'])
  changed=copy.deepcopy(landmarks);changed['photo']='another-specimen.jpg'
  with self.assertRaisesRegex(ValueError,'differs'):visual_bridges(evidence,changed,layout['unplaced'])
 def test_ceramic_body_and_bent_lead_endpoints_remain_distinct(self):
  layout=json.loads((R/'generated/layout.json').read_text())
  c=next(c for c in layout['components']if c['ref']=='C5.1')
  self.assertEqual({p['pin']:p['net']for p in c['pads']},{'1':'/+5V','2':'/GND'})
  self.assertNotIn('C5.1',[c['ref']for c in layout['unplaced']])
  # The photographed disc is offset from the lead-entry line; centering it on
  # the pads would erase the bent-lead geometry this migration must preserve.
  midpoint=[sum(p['position'][i]for p in c['pads'])/2 for i in range(2)]
  self.assertGreater(c['position'][1]-midpoint[1],2.5)
  scad=(R/'generated/controller.scad').read_text()
  ceramics=json.loads(scad.split('controller_pcb_ceramics=')[1].split(';')[0])
  self.assertEqual(next(x for x in ceramics if x[3]=='C5.1'),[c['position'],c['pads'][0]['position'],c['pads'][1]['position'],'C5.1'])
  self.assertEqual({x[3]for x in ceramics},{'C5.1','C5.2','C5.3','C5.4'})
  for row in ceramics:
   native=next(x for x in layout['components']if x['ref']==row[3])
   self.assertEqual(row[:3],[native['position'],*[p['position']for p in native['pads']]])
 def test_curves_and_outline_errors(self):
  points=arc_points([10,0],[0,10],[-10,0])
  self.assertEqual(points[0],[10,0]);self.assertEqual(points[-1],[-10,0])
  self.assertGreater(max(y for x,y in points),9.9)
  for x,y in points:self.assertAlmostEqual(x*x+y*y,100,places=4)
  reverse=arc_points([-10,0],[0,10],[10,0]);self.assertGreater(max(y for x,y in reverse),9.9)
  with self.assertRaises(ValueError):outline_polygon([[[0,0],[1,0]],[[1,0],[1,1]]])
  with self.assertRaises(ValueError):arc_points([0,0],[1,0],[2,0])
 def test_photo_registration(self):
  h=homography([[0,0],[2,0],[2,1],[0,1]],[[4,3],[4,7],[2,7],[2,3]])
  self.assertEqual(project(h,[1,.5]),[3,5])
  angle,transform=rigid_fit([[0,0],[1,0],[0,1]],[[4,3],[4,4],[3,3]])
  self.assertAlmostEqual(angle,1.57079632679)
  self.assertAlmostEqual(transform([1,1])[0],3);self.assertAlmostEqual(transform([1,1])[1],4)
  report=json.loads((R/'generated/photo-registration.json').read_text())
  for c in report['components']:
   self.assertLessEqual(c['maxResidualMm'],report['toleranceMm'],c['ref'])
  self.assertTrue(report['withinPhotoTolerance'])
  self.assertEqual(len(next(c for c in report['components']if c['ref']=='A4')['checkPins']),4)
 def test_underside_registration_uses_independent_pads(self):
  from bottom_registration import review as bottom_review
  from unittest.mock import patch
  layout=json.loads((R/'generated/layout.json').read_text());report=bottom_review(layout)
  self.assertEqual(sum(p['heldOut']for p in report['pins']),6)
  self.assertFalse(report['withinPhotoTolerance']);self.assertFalse(report['copperAssignmentQualified'])
  self.assertGreater(report['maxCheckResidualMm'],report['toleranceMm'])
  self.assertEqual(len(report['crossPhoto']['checks']),6)
  cross={p['ref']+':'+p['pin']:p for p in report['crossPhoto']['checks']}
  self.assertLess(cross['A1:7']['nominalResidualMm'],.5)
  self.assertGreater(report['crossPhoto']['maxCheckResidualMm'],report['toleranceMm'])
  e=json.loads((R/'bottom-landmarks.json').read_text());e['checks'][0]=e['anchors'][0]
  with patch('bottom_registration.Path.read_text',return_value=json.dumps(e)):
   with self.assertRaisesRegex(ValueError,'unique'):bottom_review(layout)
 def test_fit_rejects_held_out_error_and_unknown_refs(self):
  from unittest.mock import patch
  evidence={'photoCorners':[[0,0],[2,0],[2,2],[0,2]],'modelCorners':[[0,0],[2,0],[2,2],[0,2]],'scope':'test','photo':'unused','maxResidualMm':1.25,'components':{'A1':{'pins':{'1':[0,0],'2':[1,0],'3':[0,1]},'checkPins':{'4':[1,4]}}}}
  layout={'components':[{'ref':'A1','position':[0,0],'pads':[{'pin':str(i+1),'position':p} for i,p in enumerate([[0,0],[1,0],[0,1],[1,1]])]}]}
  with patch('photo_registration.Path.read_text',return_value=json.dumps(evidence)),patch('photo_registration.Path.read_bytes',return_value=b'photo'):
   r=review(layout)
  self.assertEqual(r['components'][0]['fitMaxResidualMm'],3)
  with self.assertRaisesRegex(ValueError,'inconsistent'):selected_fits(r,['A1'])
  with self.assertRaisesRegex(ValueError,'Unknown'):selected_fits(r,['TYPO'])
 def test_reset_and_service_bridge_topology(self):
  c=json.loads((R/'generated/connectivity.json').read_text())['components']
  n=lambda ref,pin:c[ref]['pins'][pin]
  self.assertEqual(n('BR1','1'),n('A7','8'));self.assertEqual(n('BR1','2'),n('A5','6'));self.assertNotEqual(n('BR1','1'),n('BR1','2'))
  self.assertEqual(n('BR2','1'),n('V4.9','C'));self.assertEqual(n('BR2','2'),n('A5','26'));self.assertNotEqual(n('BR2','1'),n('BR2','2'))
  self.assertEqual(n('C1','2'),n('V4.9','C'));self.assertNotEqual(n('C1','2'),n('C4','1'))
  self.assertEqual(n('V3.1','C'),'/+5V');self.assertEqual(n('V3.2','C'),n('V4.9','B'))
  self.assertEqual(n('R5','2'),n('V3.2','B'));self.assertEqual(n('V1.2','A'),n('C2','1'))
  self.assertEqual(n('X1','A9'),n('A5','25'));self.assertEqual(n('R6.5','2'),n('A5','25'));self.assertNotEqual(n('A5','25'),n('A5','24'))
 def test_cable_filter_pin_mapping(self):
  c=json.loads((R/'generated/connectivity.json').read_text())['components']
  for choke,signal,cable,pin in [('L1.1','/TA_TAKT','/CABLE_TAKT','B2'),('L1.2','/GND','/CABLE_GND','A3'),('L1.3','/+5V','/CABLE_5V','B4'),('L1.4','/TA_DATEN','/CABLE_DATEN','A1')]:
   self.assertEqual(c[choke]['pins'],{'1':signal,'2':cable});self.assertEqual(c['XT1']['pins'][pin],cable)
 def test_local_registration_does_not_qualify_extrapolated_copper(self):
  from bottom_registration import review as bottom_review,local_reviews
  report=bottom_review(json.loads((R/'generated/layout.json').read_text()))
  region=report['localRegions'][0]
  self.assertEqual(len(region['checks']),4);self.assertLess(region['maxCheckResidualMm'],.4)
  self.assertTrue(region['withinPhotoTolerance']);self.assertFalse(region['copperAssignmentQualified'])
  self.assertTrue(all(p['outsideAnchorBounds']for p in region['candidates']))
  self.assertLess(region['candidates'][0]['nominalResidualMm'],.3)
  self.assertGreater(region['extrapolationChecks'][0]['nominalResidualMm'],2)
  bad={'localRegions':[{'anchors':[{'ref':'A4','pin':'1'}]*4,'checks':[{'ref':'A4','pin':'1'}]}]}
  with self.assertRaisesRegex(ValueError,'unique'):local_reviews(bad,{},[])
 def test_cpu_region_limits_and_withdrawn_clock_assignment(self):
  from bottom_registration import review as bottom_review,validate_registered_routes,pcb_regions,inside_hull
  from copy import deepcopy
  import hashlib
  layout=json.loads((R/'generated/layout.json').read_text());report=bottom_review(layout);region=report['pcbRegions'][0]
  self.assertTrue(region['copperAssignmentQualified']);self.assertFalse(report['copperAssignmentQualified'])
  self.assertEqual(len(region['checks']),6);self.assertLess(region['maxCheckResidualMm'],.67)
  self.assertTrue(any(p['ref']=='A5'and p['pin']=='6'for p in region['checks']))
  self.assertFalse(any(r['evidence']['group']=='cpu-clock-bottom-partial'for r in layout['routes']))
  self.assertEqual(len([r for r in layout['routes']if r['net']=='/CLK']),1)
  conflict=json.loads((R/'evidence.json').read_text())['routeReviews'][0]
  self.assertEqual(conflict['status'],'assignment-withdrawn')
  self.assertFalse(set(conflict['withdrawnNativeTrackIds'])&{r['id']for r in layout['routes']})
  # Synthetic geometry exercises the registration guard without asserting a net.
  pixels=[[1328,2678],[1360,2706]]
  route={'side':'bottom','points':[project(region['photoToModel'],p)for p in pixels],
   'evidence':{'status':'observed','registration':{'region':'cpu-a4','landmarksSha256':''},
    'sources':[{'id':'photo-bottom','locator':{'pixelSegment':pixels}}]}}
  routes=[deepcopy(route),deepcopy(route)]
  digest=hashlib.sha256((R/'bottom-landmarks.json').read_bytes()).hexdigest()
  for route in routes:route['evidence']['registration']['landmarksSha256']=digest
  validate_registered_routes(routes,report,digest)
  with self.assertRaisesRegex(ValueError,'Stale'):validate_registered_routes(routes,report,'changed')
  bad=deepcopy(routes);bad[1]['evidence']['sources'][0]['locator']['pixelSegment'][0]=[1600,3700]
  with self.assertRaisesRegex(ValueError,'hull'):validate_registered_routes(bad,report,digest)
  bad=deepcopy(routes);bad[1]['points'][0][0]+=1
  with self.assertRaisesRegex(ValueError,'projection'):validate_registered_routes(bad,report,digest)
  bad=deepcopy(routes);bad[1]['evidence']['status']='inferred';bad[1]['points'][0]=[1000,1000]
  with self.assertRaisesRegex(ValueError,'hull'):validate_registered_routes(bad,report,digest)
  bad=deepcopy(routes);bad[1]['evidence']['status']='inferred';bad[1]['points'][0][0]+=2
  with self.assertRaisesRegex(ValueError,'tolerance'):validate_registered_routes(bad,report,digest)
  bad=deepcopy(report);bad['pcbRegions'][0]['copperAssignmentQualified']=False
  with self.assertRaisesRegex(ValueError,'not locally'):validate_registered_routes(routes,bad,digest)
  evidence=json.loads((R/'bottom-landmarks.json').read_text());pads={(c['ref'],p['pin']):p['position']for c in layout['components']for p in c['pads']}
  evidence['pcbRegions'][0]['checks'][-1]['photoPixel'][0]+=100
  self.assertFalse(pcb_regions(evidence,pads)[0]['copperAssignmentQualified'])
  self.assertFalse(inside_hull([0,0],region['anchorHull']))
 def test_col11_route_connects_reference_pads_with_bounded_registration(self):
  from bottom_registration import review as bottom_review,validate_registered_routes
  import hashlib,collections
  layout=json.loads((R/'generated/layout.json').read_text());report=bottom_review(layout)
  regions={r['id']:r for r in report['pcbRegions']}
  self.assertTrue(regions['matrix-col11']['copperAssignmentQualified'])
  rejected=regions['matrix-upper-expanded']
  self.assertFalse(rejected['copperAssignmentQualified'])
  self.assertGreater(rejected['maxCheckResidualMm'],rejected['toleranceMm'])
  routes=[r for r in layout['routes'] if r['evidence'].get('group')=='x1-b8-col11-bottom']
  self.assertTrue(routes);self.assertEqual({r['net'] for r in routes},{'/COL11'})
  self.assertEqual({r['side'] for r in routes},{'bottom'})
  validate_registered_routes(routes,report,hashlib.sha256((R/'bottom-landmarks.json').read_bytes()).hexdigest())
  pads={(c['ref'],p['pin']):tuple(p['position']) for c in layout['components'] for p in c['pads']}
  adjacency=collections.defaultdict(list)
  for r in routes:
   a,b=map(tuple,r['points']);adjacency[a].append(b);adjacency[b].append(a)
  endpoints={pads['X1','B8'],pads['A2.1','6']}
  self.assertEqual({p for p,neighbors in adjacency.items() if len(neighbors)==1},endpoints)
  self.assertTrue(all(len(neighbors) in (1,2) for neighbors in adjacency.values()))
  pending=[pads['X1','B8']];seen=set()
  while pending:
   point=pending.pop()
   if point not in seen:seen.add(point);pending.extend(adjacency[point])
  self.assertEqual(seen,set(adjacency))
  for r in routes:
   touches=any(tuple(p) in endpoints for p in r['points'])
   self.assertEqual(r['evidence']['status'],'inferred' if touches else 'observed')
 def test_output_branches_remain_partial_and_have_no_invented_vias(self):
  self.assertEqual(json.loads((R/'generated/qualification.json').read_text())['drc']['violations'],{'track_dangling':4,'clearance':1})
  from bottom_registration import review as bottom_review,validate_registered_routes
  import hashlib,collections
  layout=json.loads((R/'generated/layout.json').read_text());report=bottom_review(layout)
  self.assertTrue(next(r for r in report['pcbRegions'] if r['id']=='output-pullups')['copperAssignmentQualified'])
  pads={(c['ref'],p['pin']):tuple(p['position'])for c in layout['components']for p in c['pads']}
  for ref,net,cpu in [('R10.1','/TA_TAKT','2'),('R10.2','/TA_DATEN','4')]:
   routes=[r for r in layout['routes'] if r['evidence']['group']==ref.lower().replace('.','')+'-output-bottom-partial'];self.assertTrue(routes)
   self.assertTrue(all(r['net']==net for r in routes))
   self.assertTrue(all(r['side']=='bottom' for r in routes))
   validate_registered_routes(routes,report,hashlib.sha256((R/'bottom-landmarks.json').read_bytes()).hexdigest())
   degree=collections.Counter(tuple(p)for r in routes for p in r['points'])
   ends={p for p,n in degree.items() if n==1}
   self.assertEqual(len(ends),2);self.assertIn(pads[ref,'2'],ends)
   self.assertNotIn(pads['A1',cpu],degree)
   self.assertEqual(sum(r['evidence']['status']=='inferred'for r in routes),1)
   self.assertFalse(any(v['net']==net for v in layout['vias']))
 def test_a2_factory_identity_and_placement(self):
  components=json.loads((R/'generated/connectivity.json').read_text())['components']
  review=json.loads((R/'evidence.json').read_text())['referenceVariants'][0]
  self.assertEqual(review['status'],'reconstruction-placement-error-corrected')
  self.assertEqual(sum(len(g)for g in review['schematicGateReview'].values()),12)
  for ref,gates in review['schematicGateReview'].items():
   for gate in gates:
    for pin in gate['inputs']:self.assertEqual(components[ref]['pins'][pin],gate['inputNet'])
    self.assertEqual(components[ref]['pins'][gate['output']],gate['outputNet'])
  placed={c['ref']:c for c in json.loads((R/'generated/layout.json').read_text())['components']}
  self.assertLess(placed['A2.1']['position'][0],0)
  self.assertGreater(placed['A2.1']['position'][1],0)
  self.assertGreater(placed['A2.2']['position'][0],0)
  self.assertLess(placed['A2.2']['position'][1],0)
  self.assertGreater(placed['A2.3']['position'][0],0)
  self.assertGreater(placed['A2.3']['position'][1],0)
 def test_native_output_pullups_replace_unplaced_estimates(self):
  layout=json.loads((R/'generated/layout.json').read_text());placed={c['ref']:c for c in layout['components']}
  for ref,signal in [('R10.1','/TA_TAKT'),('R10.2','/TA_DATEN')]:
   pads={p['pin']:p for p in placed[ref]['pads']}
   self.assertEqual(pads['1']['net'],'/+5V');self.assertEqual(pads['2']['net'],signal)
   self.assertGreater(pads['1']['position'][0],pads['2']['position'][0])
   self.assertNotIn(ref,[c['ref']for c in layout['unplaced']])
  report=json.loads((R/'generated/photo-registration.json').read_text())
  self.assertTrue({'R10.1','R10.2'} <= {r['ref']for r in report['discretes']})
  for row in report['discretes']:
   self.assertFalse(row['independentValidation'])
   if row['ref'] not in ['R9.3','R9.4']:self.assertLess(row['maxResidualMm'],.00001)
  self.assertIn('controller_pcb_resistors=',(R/'generated/controller.scad').read_text())
 def test_sensing_bank_native_order_and_photo_finish(self):
  layout=json.loads((R/'generated/layout.json').read_text());placed={c['ref']:c for c in layout['components']}
  refs=['R9.'+str(i)for i in range(1,9)];rows=[7,6,0,5,1,2,3,4]
  self.assertEqual([placed[r]['position'][1]for r in refs],sorted(placed[r]['position'][1]for r in refs))
  for ref,row in zip(refs,rows):
   pads={p['pin']:p for p in placed[ref]['pads']}
   self.assertEqual(pads['1']['net'],'/ROW'+str(row));self.assertEqual(pads['2']['net'],'/BASE'+str(row))
   self.assertGreater(pads['1']['position'][0],pads['2']['position'][0])
  evidence=json.loads((R/'component-evidence.json').read_text())
  self.assertEqual([evidence[r]['blueCollarPin']for r in refs],['2']*6+['1','2'])
  text=(R/'generated/controller.scad').read_text();line=next(s for s in text.splitlines()if s.startswith('controller_pcb_resistors='))
  exported=json.loads(line.split('=',1)[1].rstrip(';'));self.assertEqual(len(exported),24)
  self.assertEqual(next(r[5]for r in exported if r[4]=='R9.7'),-1)
  self.assertEqual(next(r[5]for r in exported if r[4]=='R9.8'),1)
 def test_top_route_registration_is_local_and_side_specific(self):
  from copy import deepcopy
  from top_registration import review
  from bottom_registration import validate_registered_routes
  import hashlib
  layout=json.loads((R/'generated/layout.json').read_text());report=review(layout)
  self.assert_report_equal(report,json.loads((R/'generated/top-registration.json').read_text()))
  region=report['pcbRegions'][0]
  self.assertTrue(region['copperAssignmentQualified'])
  self.assertGreater(max(p['residualMm']for p in region['extrapolationChecks']),region['toleranceMm'])
  routes=[r for r in layout['routes']if r['evidence']['group']=='r101-output-top-local']
  self.assertEqual(len(routes),3)
  self.assertTrue(all(r['net']=='/TA_TAKT' and r['side']=='top'for r in routes))
  sha=hashlib.sha256((R/'top-copper-landmarks.json').read_bytes()).hexdigest()
  validate_registered_routes(routes,report,sha,side='top')
  for failure in ['outside','wrong-side','stale','moved','unknown-side']:
   bad=deepcopy(routes)
   if failure=='outside':bad[-1]['evidence']['sources'][0]['locator']['pixelSegment'][-1]=[1285,1495]
   elif failure=='wrong-side':bad[0]['side']='bottom'
   elif failure=='stale':bad[0]['evidence']['registration']['landmarksSha256']='stale'
   elif failure=='moved':bad[-1]['points'][-1][0]+=.01
   else:bad[0]['evidence']['registration']['side']='inner'
   with self.assertRaises(ValueError):validate_registered_routes(bad,report,sha,side='top')
 def test_underside_resistor_pads_require_supported_registration(self):
  import copy
  from bottom_registration import validate_pad_placements
  layout=json.loads((R/'generated/layout.json').read_text());report=json.loads((R/'generated/bottom-registration.json').read_text());evidence=json.loads((R/'component-evidence.json').read_text())
  rows=validate_pad_placements(layout,report,evidence)
  self.assertEqual({(r['ref'],r['pin'])for r in rows},{('R9.3','1'),('R9.4','1')})
  for kind in ['outside','moved','unqualified']:
   l,r,e=copy.deepcopy(layout),copy.deepcopy(report),copy.deepcopy(evidence)
   if kind=='outside':e['R9.3']['bottomPadPlacement']['pins']['1']=[0,0]
   elif kind=='moved':next(c for c in l['components']if c['ref']=='R9.3')['pads'][0]['position'][0]+=1
   else:next(x for x in r['pcbRegions']if x['id']=='output-pullups')['copperAssignmentQualified']=False
   with self.assertRaises(ValueError):validate_pad_placements(l,r,e)
 def test_reset_resistor_common_strip_terminal_order(self):
  layout=json.loads((R/'generated/layout.json').read_text());placed={c['ref']:c for c in layout['components']}
  evidence=json.loads((R/'component-evidence.json').read_text());nets=[]
  for ref,signal in [('R4.2','RESET_OUT'),('R7','RESET_EMITTERS'),('R8','RESET_RC')]:
   pads={p['pin']:p for p in placed[ref]['pads']}
   self.assertEqual({n:p['net']for n,p in pads.items()},{'1':'/'+signal,'2':'/GND'})
   self.assertLess(pads['2']['position'][1],pads['1']['position'][1])
   self.assertLess(evidence[ref]['photoPins']['2'][0],evidence[ref]['photoPins']['1'][0])
   self.assertNotIn('placementCandidate',evidence[ref]);nets.append({p['net']for p in pads.values()})
  self.assertEqual(set.intersection(*nets),{'/GND'})
 def test_led_resistor_inner_leads_face_adjacent_connector_rows(self):
  layout=json.loads((R/'generated/layout.json').read_text());placed={c['ref']:c for c in layout['components']}
  a,b=[{p['pin']:p for p in placed[r]['pads']}for r in ['R11.1','R11.2']]
  self.assertLess(a['1']['position'][0],a['2']['position'][0])
  self.assertLess(a['2']['position'][0],b['2']['position'][0])
  self.assertLess(b['2']['position'][0],b['1']['position'][0])
  for pads,name in [(a,'SISO'),(b,'CAPS')]:
   self.assertEqual(pads['1']['net'],'/LED_'+name+'_N');self.assertEqual(pads['2']['net'],'/LED_'+name)
 def test_partial_a1_route_keeps_endpoint_unresolved(self):
  from route_evidence import annotate
  layout=json.loads((R/'generated/layout.json').read_text())
  routes=layout['routes'];self.assertEqual({r['id'] for r in routes+layout['vias']},set(json.loads((R/'route-evidence.json').read_text())['items']))
  annotate(routes,layout['vias'],json.loads((R/'route-evidence.json').read_text()),json.loads((R/'evidence.json').read_text()))
  routes=[r for r in routes if r['net']=='/WR_N'];self.assertEqual(len(routes),8)
  self.assertEqual({r['net']for r in routes},{'/WR_N'})
  self.assertEqual(sum(r['evidence']['status']=='observed'for r in routes),7)
  self.assertEqual(sum(r['evidence']['status']=='inferred'for r in routes),1)
  self.assertFalse(any(v['net']=='/WR_N'for v in layout['vias']))
  self.assertIn('magenta',(R/'generated/photo-registration.svg').read_text())
 def test_reset_pair_supply_route_connects_only_reviewed_pads(self):
  layout=json.loads((R/'generated/layout.json').read_text())
  routes=[r for r in layout['routes']if r['evidence'].get('group')=='reset-pair-supply-top']
  self.assertEqual(len(routes),5);self.assertEqual({r['net']for r in routes},{'/+5V'})
  self.assertEqual({r['side']for r in routes},{'top'})
  self.assertEqual(sum(r['evidence']['status']=='observed'for r in routes),3)
  self.assertEqual(sum(r['evidence']['status']=='inferred'for r in routes),2)
  # Check actual exported copper reaches both numbered supply pads, with no branches.
  from collections import Counter
  ends=Counter(tuple(p)for r in routes for p in r['points'])
  pads=[tuple(p['position'])for c in layout['components']if c['ref']in ['R3','R4.1']for p in c['pads']if p['pin']=='1']
  self.assertEqual(set(p for p,n in ends.items()if n==1),set(pads))
  self.assertTrue(all(n in [1,2]for n in ends.values()))
 def test_reset_supply_tree_reaches_four_resistors(self):
  layout=json.loads((R/'generated/layout.json').read_text())
  routes=[r for r in layout['routes']if r['evidence']['group'].startswith('reset-')]
  self.assertEqual(len(routes),13)
  from collections import Counter,defaultdict
  ends=Counter();edges=defaultdict(set)
  for r in routes:
   a,b=map(tuple,r['points']);ends.update([a,b]);edges[a].add(b);edges[b].add(a)
  pads=[tuple(p['position'])for c in layout['components']if c['ref']in ['R3','R4.1','R5','R6.1']for p in c['pads']if p['pin']=='1']
  self.assertEqual(set(p for p,n in ends.items()if n==1),set(pads))
  seen=set();pending=[pads[0]]
  while pending:
   point=pending.pop()
   if point in seen:continue
   seen.add(point);pending.extend(edges[point]-seen)
  self.assertEqual(seen,set(ends));self.assertEqual(sum(n==3 for n in ends.values()),2)
  r5=next(c for c in layout['components']if c['ref']=='R5');pads={p['pin']:p for p in r5['pads']}
  self.assertEqual(pads['2']['net'],'/RESET_BIAS')
  self.assertGreater(pads['1']['position'][1],pads['2']['position'][1])
 def test_a4_pullup_supply_link_preserves_separate_island(self):
  layout=json.loads((R/'generated/layout.json').read_text())
  routes=[r for r in layout['routes']if r['evidence']['group']=='a4-pullup-supply-top']
  self.assertEqual(len(routes),3);self.assertEqual({r['net']for r in routes},{'/+5V'})
  self.assertEqual(sum(r['evidence']['status']=='observed'for r in routes),1)
  from collections import Counter
  ends=Counter(tuple(p)for r in routes for p in r['points'])
  pads=[tuple(p['position'])for c in layout['components']if c['ref']in ['R6.3','R9.9']for p in c['pads']if p['pin']=='1']
  self.assertEqual(set(p for p,n in ends.items()if n==1),set(pads))
  reset_points={tuple(p)for r in layout['routes']if r['evidence']['group'].startswith('reset-')for p in r['points']}
  self.assertFalse(set(ends)&reset_points)
 def test_br1_reference_sides_and_inferred_local_clock_route(self):
  layout=json.loads((R/'generated/layout.json').read_text());parts={c['ref']:c for c in layout['components']}
  bridge={p['pin']:p for p in parts['BR1']['pads']};pullup={p['pin']:p for p in parts['R10.3']['pads']}
  self.assertEqual(bridge['1']['net'],'/OSC_OUT');self.assertEqual(bridge['2']['net'],'/CLK')
  self.assertEqual(pullup['2']['net'],'/CLK');self.assertEqual(pullup['1']['net'],'/+5V')
  routes=[r for r in layout['routes']if r['evidence']['group']=='br1-r103-local-clock'];self.assertEqual(len(routes),1)
  route=routes[0];self.assertEqual(route['side'],'bottom');self.assertEqual(route['evidence']['status'],'inferred')
  self.assertEqual({tuple(p)for p in route['points']},{tuple(bridge['2']['position']),tuple(pullup['2']['position'])})
  self.assertFalse(json.loads((R/'generated/bottom-registration.json').read_text())['copperAssignmentQualified'])
  text=(R/'generated/controller.scad').read_text();line=next(s for s in text.splitlines()if s.startswith('controller_pcb_bridges='))
  exported=json.loads(line.split('=',1)[1].rstrip(';'));self.assertEqual(exported,[[bridge['1']['position'],bridge['2']['position'],'BR1']])
 def test_route_evidence_rejects_stale_or_unsupported_claims(self):
  from route_evidence import annotate,geometry_sha
  from copy import deepcopy
  route={'id':'track-1','points':[[0,0],[1,0]],'width':.3,'side':'top','net':'/TA_TAKT'}
  sources={'sources':[{'id':'photo-top','sha256':'abc'},{'id':'schematic','sha256':'def'}]}
  record={'status':'observed','geometrySha256':geometry_sha(route),'detail':'Visible section, hidden continuation unresolved.','sources':[{'id':'photo-top','sha256':'abc','locator':'original pixels: (10,20) to (30,40)'}]}
  ledger={'schema':1,'items':{'track-1':record}}
  routes=[deepcopy(route)];annotate(routes,[],ledger,sources)
  self.assertEqual(routes[0]['evidence'],record)
  for field,value in [('net','/D0'),('side','bottom'),('width',.4),('points',[[0,0],[2,0]])]:
   changed=dict(route,**{field:value})
   with self.assertRaisesRegex(ValueError,'geometry changed'):annotate([changed],[],ledger,sources)
  with self.assertRaisesRegex(ValueError,'exactly'):annotate([],[],ledger,sources)
  for change,message in [({'status':'verified'},'status'),({'detail':''},'explanation'),({'sources':[]},'source references'),({'sources':[{'id':'photo-top','sha256':'old','locator':'p1'}]},'stale'),({'sources':[{'id':'schematic','sha256':'def','locator':'p1'}]},'photographs')]:
   bad=deepcopy(ledger);bad['items']['track-1'].update(change)
   with self.assertRaisesRegex(ValueError,message):annotate([deepcopy(route)],[],bad,sources)
  via={'id':'via-1','position':[0,0],'diameter':1,'drill':.5,'net':'/TA_TAKT'}
  vrecord=dict(record,geometrySha256=geometry_sha(via))
  with self.assertRaisesRegex(ValueError,'board sides'):annotate([],[via],{'schema':1,'items':{'via-1':vrecord}},sources)
 def test_pinned_sources(self):subprocess.run([sys.executable,R/'tools/export.py','--check'],check=True)
 def test_asymmetric_landmarks(self):
  layout=json.loads((R/'generated/layout.json').read_text());cs={c['ref']:c for c in layout['components']}
  # CPU and ROM are deliberately not interchangeable; pad 1 fixes handedness.
  self.assertLess(cs['A5']['position'][0],cs['A8']['position'][0]);self.assertGreater(cs['A5']['position'][1],0)
  pads={p['pin']:p for p in cs['A5']['pads']}
  self.assertLess(pads['1']['position'][0],pads['20']['position'][0]);self.assertLess(pads['1']['position'][1],pads['40']['position'][1])
  self.assertEqual(pads['1']['net'],'/A11');self.assertEqual(pads['40']['net'],'/A10')
  polygon=layout['outlinePolygon'];self.assertEqual(len(polygon),4)
  area=abs(sum(x*polygon[(i+1)%4][1]-y*polygon[(i+1)%4][0] for i,(x,y) in enumerate(polygon)))/2
  self.assertEqual(area,270*46)
 def test_unresolved_artwork_is_not_copper(self):
  l=json.loads((R/'generated/layout.json').read_text());self.assertTrue(l['unresolvedArtwork'])
  self.assertTrue(all(x['net'] is None for x in l['unresolvedArtwork']))
  self.assertTrue(all(c['evidence']=='unplaced' for c in l['unplaced']))
 def test_stale_source_and_output_rejected(self):
  with tempfile.TemporaryDirectory() as tmp:
   d=Path(tmp)/'board';shutil.copytree(R,d,ignore=shutil.ignore_patterns('__pycache__'))
   photos=[source['path'] for source in json.loads((R/'evidence.json').read_text())['sources'] if source.get('path')]
   for photo in photos:
    (d/photo).parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/photo,d/photo)
   subprocess.run([sys.executable,d/'tools/export.py','--check'],check=True)
   for name in ['controller.kicad_sch','controller.kicad_pcb','generated/controller.scad']+photos:
    p=d/name;before=p.read_bytes();p.write_bytes(before+b'\n')
    r=subprocess.run([sys.executable,d/'tools/export.py','--check'],capture_output=True)
    self.assertNotEqual(r.returncode,0,name);p.write_bytes(before)
if __name__=='__main__':unittest.main()
