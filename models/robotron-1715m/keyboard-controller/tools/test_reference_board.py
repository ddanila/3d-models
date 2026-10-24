#!/usr/bin/env python3
"""Reference connectivity must not silently change the historical circuit."""
import copy
import json
from pathlib import Path
import unittest
from reference_board import validate_pins, check, router_deck

ROOT=Path(__file__).resolve().parents[1]
class ReferenceTests(unittest.TestCase):
    def setUp(self):
        layout=json.loads((ROOT/'reference/generated/layout.json').read_text())
        self.components=layout['components']
        self.expected=json.loads((ROOT/'generated/connectivity.json').read_text())['components']
        evidence=json.loads((ROOT/'component-evidence.json').read_text())
        self.unused={ref:e['physicalUnusedPads'] for ref,e in evidence.items() if e.get('physicalUnusedPads')}

    def test_source_contract_and_reference_exports(self):
        validate_pins(self.components,self.expected,self.unused)
        check()
        historical=json.loads((ROOT/'generated/layout.json').read_text())
        with self.assertRaisesRegex(ValueError, 'X1:A8'):
            validate_pins(historical['components']+historical['unplaced'],self.expected,self.unused)
        layout=json.loads((ROOT/'reference/generated/layout.json').read_text())
        validate_pins(layout['components'],self.expected,self.unused)
        self.assertEqual(layout['variant'],'proposed-reference')
        self.assertTrue(all(r['classification'] in ('proposed','inherited-historical-geometry') for r in layout['routes']+layout['vias']))
        q=json.loads((ROOT/'reference/generated/qualification.json').read_text())
        self.assertFalse(q['historicallyVerified'])
        self.assertFalse(q['electricallyQualified'])
        self.assertFalse(q['fabricationReady'])

    def test_router_constraints_preserve_native_rules(self):
        spec=json.loads((ROOT/'reference/implementation.json').read_text())
        deck='(unit um) (boundary (path pcb 0 15000 -27000 285000 -27000 285000 -73000 15000 -73000 15000 -27000)) (width 200) (width 200) (type route)'
        result=router_deck(deck,spec)
        self.assertIn('15350 -27350',result)
        self.assertIn('284650 -72650',result)
        self.assertEqual(result.count('(width 250)'),2)
        self.assertIn('(type normal)',result)
        with self.assertRaises(ValueError):router_deck(deck.replace('(unit um)','(unit inch)'),spec)
        with self.assertRaises(ValueError):router_deck(deck.replace('15000 -27000','16000 -27000',1),spec)

    def test_wrong_net_missing_pad_and_unused_pad_short_are_rejected(self):
        for mutation in ('net','missing','unused'):
            components=copy.deepcopy(self.components)
            c=next(c for c in components if c['ref']==('R1' if mutation=='unused' else 'A5'))
            if mutation=='missing': c['pads'].pop()
            elif mutation=='unused':next(p for p in c['pads'] if p['pin']=='10')['net']='/GND'
            else:c['pads'][0]['net']='/WRONG'
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                validate_pins(components,self.expected,self.unused)

if __name__=='__main__':unittest.main()
