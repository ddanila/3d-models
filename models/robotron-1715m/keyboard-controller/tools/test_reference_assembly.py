#!/usr/bin/env python3
import copy
import unittest
from unittest.mock import patch
import reference_assembly as assembly

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

if __name__=='__main__':unittest.main()
