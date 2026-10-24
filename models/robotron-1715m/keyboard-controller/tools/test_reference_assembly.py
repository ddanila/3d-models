#!/usr/bin/env python3
import copy
import random
from lead_bends import fillet
from assembly_allowances import review as allowance_review
import unittest
from unittest.mock import patch
import reference_assembly as assembly
from lead_clearance import closest_segments, review as review_leads

class AssemblyTests(unittest.TestCase):
    def test_population_pin_identity_and_mechanical_scope(self):
        data,_=assembly.build()
        layout=assembly.read(assembly.REF/'generated/layout.json')
        byref={c['ref']:c for c in layout['components']}
        for c in data['components']:
            self.assertEqual({l['pin'] for l in c['leads']},{p['pin'] for p in byref[c['ref']]['pads']})
            for lead in c['leads']:
                pad=next(p for p in byref[c['ref']]['pads'] if p['pin']==lead['pin'])
                self.assertEqual(lead['points'][0][:2],pad['position'])
                self.assertEqual(lead['net'],pad['net'])
        self.assertFalse(data['review']['mechanicallyQualified'])
        self.assertFalse(data['review']['fabricationReady'])
        self.assertEqual(data['review']['bodyEnvelopeIntersections'],[])
        self.assertEqual(data['review']['bodyOverhangs'],[])
        self.assertEqual(data['review']['insufficientDrillAllowance'],[])
        self.assertEqual(data['review']['leadBodyEnvelopeIntersections'],[])
        self.assertTrue(data['review']['leadClearance']['noUnintendedContact'])
        self.assertGreater(data['review']['leadClearance']['minimumUnintendedClearance']['surfaceClearanceMm'],0)

    def test_shared_core_windings_keep_terminal_identity_and_clearance(self):
        data,scad=assembly.build();core,=data['sharedBodies']
        self.assertEqual(set(core['members']),{'L1.1','L1.2','L1.3','L1.4'})
        self.assertEqual(data['review']['sharedCoreIntersections'],[])
        self.assertIn('difference()',scad)
        for c in data['components']:
            if c['ref'] not in core['members']:continue
            self.assertEqual(c['sharedBody'],core['id'])
            self.assertEqual(c['leads'][0]['points'][-1],c['leads'][1]['points'][-1])
            self.assertTrue(all(len(lead['points'])>3 for lead in c['leads']))
        original=assembly.read
        def altered(path):
            data=original(path)
            if path==assembly.REF/'assembly.json':
                data['sharedFilter']['outerSizeMm'][0]=40
                data['sharedFilter']['positionMm'][2]=1.6
            return data
        with patch.object(assembly,'read',side_effect=altered):bad,_=assembly.build()
        self.assertTrue(bad['review']['sharedCoreIntersections'])
        self.assertEqual(bad['review']['sharedCoreOverhangs'],['L1'])

    def test_r1_catalog_envelope_and_formed_adapter(self):
        data,_=assembly.build()
        r1=next(c for c in data['components'] if c['ref']=='R1')
        self.assertEqual(r1['sizeMm'],[27.5,3,11])
        self.assertEqual(r1['position'][2],2.2)
        for lead in r1['leads']:
            self.assertAlmostEqual(lead['diameterMm'],(.65**2+.5**2)**.5)
            self.assertAlmostEqual(lead['points'][-1][1]-lead['points'][0][1],2.1)
            self.assertTrue(lead['bends'])
        self.assertTrue(data['review']['assemblyAllowances']['envelopesClear'])

    def test_r2_spare_branch_and_equal_resistor_mapping(self):
        data,_=assembly.build();r2=next(c for c in data['components'] if c['ref']=='R2')
        self.assertEqual(r2['sizeMm'],[27.5,3,9])
        self.assertEqual(r2['externallyOpenPackagePins'],['10'])
        leads={p['pin']:p for p in r2['leads']}
        self.assertEqual(leads['1']['packagePin'],'1');self.assertEqual(leads['1']['net'],'/+5V')
        self.assertEqual({p['packagePin'] for p in leads.values()},{str(i) for i in range(1,11)})
        self.assertIsNone(leads['10']['net'])
        self.assertEqual({p['net'] for k,p in leads.items() if k not in ('1','10')},{'/BASE'+str(i) for i in range(8)})
        self.assertTrue(data['review']['assemblyAllowances']['envelopesClear'])
        original=assembly.read
        def altered(path):
            result=original(path)
            if path==assembly.REF/'assembly.json':
                result['components']['R2']['terminalToPackagePin']['1']='2'
                result['components']['R2']['terminalToPackagePin']['6']='1'
            return result
        with patch.object(assembly,'read',side_effect=altered),self.assertRaisesRegex(ValueError,'common terminal'):
            assembly.build()

    def test_radial_capacitor_bodies_use_bottom_lead_entries(self):
        data,scad=assembly.build();cans=[c for c in data['components'] if c['package']=='radial-capacitor']
        self.assertEqual({c['ref'] for c in cans},{'C2','C3.1','C3.2','C4'})
        for c in cans:
            self.assertEqual(c['sizeMm'],[6.8,6.8,6])
            self.assertEqual(c['capacitorPackage']['positivePin'],'1')
            self.assertEqual(c['capacitorPackage']['negativePin'],'2')
            self.assertTrue(all(l['diameterMm']==.5 for l in c['leads']))
            self.assertEqual(len(c['leads']),2)
            for lead in c['leads']:self.assertEqual(lead['points'][-1][2],c['position'][2])
        self.assertIn('cylinder(d=6.8,h=6',scad)
        self.assertTrue(data['review']['assemblyAllowances']['envelopesClear'])

    def test_ceramics_preserve_maximum_coating_and_wire_envelopes(self):
        data,_=assembly.build();parts=[c for c in data['components'] if c['package']=='radial-ceramic']
        self.assertEqual({c['ref'] for c in parts},{'C1','C6',*(f'C5.{i}' for i in range(1,6))})
        for c in parts:
            self.assertEqual(c['sizeMm'],[3.81,2.54,4.66])
            self.assertFalse(c['capacitorPackage']['polarized'])
            self.assertEqual(c['capacitorPackage']['dielectric'],'C0G')
            self.assertNotIn('positivePin',c['capacitorPackage'])
            for lead in c['leads']:
                self.assertEqual(lead['diameterMm'],.61)
                self.assertEqual(lead['points'][-1][2],c['position'][2])
        self.assertTrue(data['review']['assemblyAllowances']['envelopesClear'])

    def test_straight_body_entries_and_rounded_paths(self):
        data,_=assembly.build()
        for c in data['components']:
            for lead in c['leads']:
                if c['ref'] in ('X1','XT1'):
                    self.assertEqual(len(lead['points']),2)
                    self.assertGreater(lead['points'][-1][2],lead['points'][0][2])
                for bend in lead.get('bends',[]):
                    self.assertGreater(bend['radiusMm'],lead['diameterMm']/2)
                    self.assertLessEqual(bend['maximumChordErrorMm'],data['leadForming']['chordErrorMm'])
        self.assertTrue(any(lead.get('bends') for c in data['components'] for lead in c['leads']))

    def test_oversized_body_is_reported_not_blessed(self):
        original=assembly.read
        def altered(path):
            data=original(path)
            if path==assembly.REF/'assembly.json':
                data=copy.deepcopy(data);data['components']['R1']['sizeMm']=[400,100,50]
            return data
        with patch.object(assembly,'read',side_effect=altered):data,_=assembly.build()
        self.assertIn('R1',data['review']['bodyOverhangs'])
        self.assertTrue(data['review']['leadBodyEnvelopeIntersections'])
        self.assertTrue(any('R1' in (c['a'],c['b']) for c in data['review']['bodyEnvelopeIntersections']))
        self.assertFalse(data['review']['mechanicallyQualified'])

    def test_walkthrough_rejects_wrong_net(self):
        original=assembly.read
        def altered(path):
            data=original(path)
            if path==assembly.REF/'signal-paths.json':data['stages'][0]['net']='/GND'
            return data
        with patch.object(assembly,'read',side_effect=altered), self.assertRaisesRegex(ValueError,'Walkthrough net mismatch'):
            assembly.build()

    def test_missing_package_terminal_rejected(self):
        original=assembly.read
        def altered(path):
            data=original(path)
            if path==assembly.ROOT/'evidence.json':
                data['packageReferences'][0]['terminalOrderInDrawing']=['B','E','X']
            return data
        with patch.object(assembly,'read',side_effect=altered), self.assertRaisesRegex(ValueError,'terminal mismatch'):
            assembly.build()

    def test_reversed_supply_capacitor_polarity_rejected(self):
        original=assembly.read
        def altered(path):
            data=original(path)
            if path.name=='capacitor-polarity.json':
                c=data['components']['C3.1'];c['positivePin'],c['negativePin']='2','1'
            return data
        with patch.object(assembly,'read',side_effect=altered),self.assertRaisesRegex(ValueError,'supply polarity'):
            assembly.build()

    def test_package_value_must_match_reference(self):
        original=assembly.read
        def altered(path):
            data=original(path)
            if path.name=='capacitor-package-low-profile.json':data['components']['C4']['microfarads']=100
            return data
        with patch.object(assembly,'read',side_effect=altered),self.assertRaisesRegex(ValueError,'reference value'):
            assembly.build()

class LeadClearanceTests(unittest.TestCase):
    def test_segment_interiors_skew_parallel_and_degenerate(self):
        for a,b,c,d,expected in [
            ((-1,0,0),(1,0,0),(0,-1,0),(0,1,0),0),
            ((-1,0,0),(1,0,0),(0,-1,2),(0,1,2),2),
            ((0,0,0),(2,0,0),(3,1,0),(-1,1,0),1),
            ((0,0,0),(0,0,0),(1,-1,0),(1,1,0),1),
            ((0,0,0),(1,0,0),(2,1,0),(2,2,0),2**.5),
        ]:
            distance,p,q=closest_segments(a,b,c,d)
            self.assertAlmostEqual(distance,expected)
            self.assertAlmostEqual(closest_segments(c,d,a,b)[0],expected)

    def component(self,ref,net,points,package='axial'):
        return {'ref':ref,'package':package,'leads':[{'pin':'1','net':net,'points':points,'diameterMm':.3}]}

    def test_actual_wire_radii_crossing_and_unassigned_nets(self):
        a=self.component('A',None,[[-1,0,0],[1,0,0]])
        b=self.component('B',None,[[0,-1,.2],[0,1,.2]])
        r=review_leads([a,b])
        self.assertFalse(r['noUnintendedContact'])
        self.assertAlmostEqual(r['unintendedContacts'][0]['surfaceClearanceMm'],-.1)
        b['leads'][0]['points']=[[0,-1,.31],[0,1,.31]]
        self.assertTrue(review_leads([a,b])['noUnintendedContact'])

    def test_winding_join_does_not_hide_turn_crossings(self):
        a=self.component('L1.1','/A',[[0,0,0],[2,0,0],[2,2,0],[0,2,0],[0,0,0]],'filter')
        self.assertFalse(review_leads([a])['noUnintendedContact'])
        a['leads'].append({'pin':'2','net':'/B','diameterMm':.3,'points':[[1,-1,0],[1,1,0],[0,0,0]]})
        result=review_leads([a])
        self.assertTrue(any(c['basis']=='winding-midpoint' for c in result['intendedContacts']))
        self.assertTrue(result['unintendedContacts'])

    def test_rounded_winding_is_not_a_self_contact(self):
        path,_=fillet([[0,0,0],[3,0,0],[3,3,0],[0,3,0]],.4,.005)
        a=self.component('L1','/A',path,'filter')
        self.assertTrue(review_leads([a])['noUnintendedContact'])
        # Split inside a bend: joining the two halves must not change the result.
        mid=len(path)//2
        a['leads'][0]['points']=path[:mid+1]
        a['leads'].append({'pin':'2','net':'/B','diameterMm':.3,'points':list(reversed(path[mid:]))})
        self.assertTrue(review_leads([a])['noUnintendedContact'])
        # A foreign conductor crossing that bend is still a short.
        p=path[mid]
        b=self.component('B','/C',[[p[0],p[1],-1],[p[0],p[1],1]])
        self.assertFalse(review_leads([a,b])['noUnintendedContact'])

    def test_chord_error_is_included_in_clearance(self):
        a=self.component('A','/A',[[0,0,0],[2,0,0]])
        b=self.component('B','/B',[[0,.31,0],[2,.31,0]])
        self.assertTrue(review_leads([a,b])['noUnintendedContact'])
        a['leads'][0]['centerlineApproximationMm']=.02
        self.assertFalse(review_leads([a,b])['noUnintendedContact'])

    def test_broad_phase_matches_exhaustive_segment_distances(self):
        rng=random.Random(1715)
        components=[self.component(str(i),str(i),[[rng.uniform(-5,5) for _ in range(3)] for _ in range(3)]) for i in range(16)]
        expected=[]
        for i,a in enumerate(components):
            for b in components[i+1:]:
                p=a['leads'][0]['points'];q=b['leads'][0]['points']
                gap=min(closest_segments(x,y,u,v)[0] for x,y in zip(p,p[1:]) for u,v in zip(q,q[1:]))-.3
                expected.append((gap,[a['ref']+':1',b['ref']+':1']))
        result=review_leads(components)
        self.assertAlmostEqual(result['minimumUnintendedClearance']['surfaceClearanceMm'],min(expected)[0],places=8)
        self.assertEqual({tuple(r['terminals']) for r in result['unintendedContacts']},{tuple(pair) for gap,pair in expected if gap<=1e-9})

    def test_allowances_expose_contacts_and_validate_budget(self):
        a=self.component('A','/A',[[0,0,0],[2,0,0]])
        b=self.component('B','/B',[[0,.4,0],[2,.4,0]])
        self.assertTrue(review_leads([a,b])['noUnintendedContact'])
        self.assertFalse(review_leads([a,b],radial_allowance_mm=.06)['noUnintendedContact'])
        with self.assertRaises(ValueError):review_leads([a,b],radial_allowance_mm=-.1)

    def test_body_and_hole_allowances_report_nominally_clear_fixture(self):
        a=self.component('A','/A',[[0,0,0],[0,0,2]])
        b=self.component('B','/B',[[3,0,0],[3,0,2]])
        a['boundsMm']=[[0,1],[0,1],[2,3]]
        b['boundsMm']=[[1.1,2.1],[0,1],[2,3]]
        layout={'outlinePolygon':[[-5,-5],[5,-5],[5,5],[-5,5]],'components':[
            {'ref':ref,'pads':[{'pin':'1','drill':[.4,.4]}]} for ref in ('A','B')]}
        spec=dict(bodyEnvelopeMm=0,leadRadialEnvelopeMm=0,coreEnvelopeMm=0,holeRadialLossMm=0)
        nominal=allowance_review([a,b],[],layout,spec,assembly.segment_box,assembly.overlaps)
        self.assertEqual(nominal['bodyEnvelopeIntersections'],[])
        self.assertEqual(nominal['insufficientHoleClearance'],[])
        spec.update(bodyEnvelopeMm=.1,holeRadialLossMm=.06)
        expanded=allowance_review([a,b],[],layout,spec,assembly.segment_box,assembly.overlaps)
        self.assertEqual(expanded['bodyEnvelopeIntersections'],[{'a':'A','b':'B'}])
        self.assertEqual(len(expanded['insufficientHoleClearance']),2)
        self.assertFalse(expanded['envelopesClear'])
        self.assertFalse(expanded['mechanicallyQualified'])

    def test_intended_join_does_not_hide_other_net_contact(self):
        a=self.component('BR1','/A',[[-1,0,0],[0,0,0]],'bridge')
        a['leads'].append({'pin':'2','net':'/B','points':[[1,0,0],[0,0,0]],'diameterMm':.3})
        r=review_leads([a]);self.assertTrue(r['noUnintendedContact']);self.assertEqual(r['intendedContacts'][0]['basis'],'reference-bridge')
        b=self.component('B','/C',[[0,-1,0],[0,1,0]])
        self.assertFalse(review_leads([a,b])['noUnintendedContact'])

if __name__=='__main__':unittest.main()
