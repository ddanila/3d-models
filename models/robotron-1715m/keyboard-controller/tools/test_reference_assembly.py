#!/usr/bin/env python3
import copy
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

    def test_intended_join_does_not_hide_other_net_contact(self):
        a=self.component('BR1','/A',[[-1,0,0],[0,0,0]],'bridge')
        a['leads'].append({'pin':'2','net':'/B','points':[[1,0,0],[0,0,0]],'diameterMm':.3})
        r=review_leads([a]);self.assertTrue(r['noUnintendedContact']);self.assertEqual(r['intendedContacts'][0]['basis'],'reference-bridge')
        b=self.component('B','/C',[[0,-1,0],[0,1,0]])
        self.assertFalse(review_leads([a,b])['noUnintendedContact'])

if __name__=='__main__':unittest.main()
