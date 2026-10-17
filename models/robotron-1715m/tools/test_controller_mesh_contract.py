import unittest
from controller_mesh_contract import PARTS, receipts, validate


class ControllerMeshContractTests(unittest.TestCase):
    def setUp(self):
        self.parts = [{'name': name, 'sha256': name + '-old'} for name in PARTS]
        self.old_sources = {'controller.scad': 'old'}
        self.new_sources = {'controller.scad': 'new'}
        self.old = receipts({}, self.parts, None, self.old_sources)

    def test_full_export_qualifies_all_consumers(self):
        manifest = {'parts': self.parts, 'keyboardControllerMeshes':
                    receipts(self.old, self.parts, PARTS, self.new_sources)}
        validate(manifest, self.new_sources)

    def test_partial_export_cannot_bless_stale_leads_or_resistor_meshes(self):
        for omitted in ['leads', 'resistors', 'resistor-bands', 'solder']:
            with self.subTest(omitted=omitted):
                selected = PARTS - {'keyboard-controller-' + omitted}
                manifest = {'parts': self.parts, 'keyboardControllerMeshes':
                            receipts(self.old, self.parts, selected, self.new_sources)}
                with self.assertRaisesRegex(ValueError, 'stale controller mesh sources'):
                    validate(manifest, self.new_sources)
                self.assertEqual(self.old['keyboard-controller-' + omitted]['sources'], self.old_sources)

    def test_mesh_replacement_invalidates_receipt(self):
        changed = [dict(p, sha256='changed') if p['name'].endswith('-leads') else p for p in self.parts]
        with self.assertRaisesRegex(ValueError, 'does not match export receipt'):
            validate({'parts': changed, 'keyboardControllerMeshes': self.old}, self.old_sources)

    def test_missing_receipts_do_not_qualify_legacy_exports(self):
        with self.assertRaisesRegex(ValueError, 'stale controller mesh sources'):
            validate({'parts': self.parts}, self.old_sources)


if __name__ == '__main__':
    unittest.main()
