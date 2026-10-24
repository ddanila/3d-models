import unittest
from shared_row_bias_review import fit, spacing

class SharedBiasTests(unittest.TestCase):
    def test_known_fraction_and_equal_package_weight(self):
        a = {'ref': 'a', 'widthMm': 10, 'oppositeResidualsMm': [-1, -1]}
        b = {'ref': 'b', 'widthMm': 20, 'oppositeResidualsMm': [-2, -2]}
        self.assertAlmostEqual(fit([a, b]), -.1)
        b['oppositeResidualsMm'] *= 5
        self.assertAlmostEqual(fit([a, b]), -.1)
        a['oppositeResidualsMm'] = [-2, -2]
        expected = fit([a, b])
        a['oppositeResidualsMm'] *= 4
        self.assertEqual(fit([a, b]), expected)
    def test_duplicate_or_insufficient_training_rejected(self):
        a = {'ref': 'a', 'widthMm': 10, 'oppositeResidualsMm': [-1, -1]}
        for data in ([a], [a, a], [a, {**a, 'ref': 'b', 'oppositeResidualsMm': [0]}]):
            with self.assertRaises(ValueError):
                fit(data)
    def test_numbered_row_spacing(self):
        c = {'pads': [{'pin': str(i), 'position': p} for i, p in
                     [(1, [0, 0]), (2, [10, 0]), (3, [10, 5]), (4, [0, 5])]]}
        self.assertEqual(spacing(c), (5, 2))
        for pad in c['pads']:
            x, y = pad['position']; pad['position'] = [-y+30, x-20]
        self.assertEqual(spacing(c), (5, 2))

if __name__ == '__main__':
    unittest.main()
