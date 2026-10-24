#!/usr/bin/env python3
import math
import unittest
from lead_bends import fillet


class LeadBendTests(unittest.TestCase):
    def test_right_angle_radius_and_sagitta(self):
        points, bends = fillet([[0, 0, 0], [2, 0, 0], [2, 2, 0]], .5, .005)
        self.assertEqual(points[0], [0, 0, 0])
        self.assertEqual(points[-1], [2, 2, 0])
        center = [1.5, .5, 0]
        for p in points[1:-1]:
            self.assertAlmostEqual(math.dist(p, center), .5)
        for a, b in zip(points[1:-2], points[2:-1]):
            midpoint = [(x+y)/2 for x, y in zip(a, b)]
            self.assertLessEqual(.5-math.dist(midpoint, center), .005+1e-12)
        self.assertAlmostEqual(bends[0]['tangentOffsetMm'], .5)

    def test_rotation_preserves_geometry(self):
        source = [[0, 0, 0], [2, 0, 0], [2, 2, 0]]
        def rotate(p):
            x, y, z = p
            return [(x-y)/math.sqrt(2)+3, (x+y)/2+4, (x+y)/2+z+5]
        a, _ = fillet(source, .5, .005)
        b, _ = fillet([rotate(p) for p in source], .5, .005)
        for p, q in zip(a, b):
            self.assertLess(math.dist(rotate(p), q), 1e-12)

    def test_adjacent_bends_cannot_overlap(self):
        with self.assertRaisesRegex(ValueError, 'segment 1'):
            fillet([[0, 0, 0], [2, 0, 0], [2, .8, 0], [4, .8, 0]], .5, .005)

    def test_no_silent_radius_reduction(self):
        with self.assertRaisesRegex(ValueError, 'segment 0'):
            fillet([[0, 0, 0], [.2, 0, 0], [.2, 2, 0]], .5, .005)

    def test_straight_and_duplicate_points(self):
        points, bends = fillet([[0, 0, 0], [0, 0, 0], [1, 0, 0], [2, 0, 0]], .5, .005)
        self.assertEqual(points, [[0, 0, 0], [1, 0, 0], [2, 0, 0]])
        self.assertEqual(bends, [])

    def test_invalid_geometry(self):
        for points in ([[0, 0, 0]], [[0, 0, 0], [float('nan'), 0, 0]],
                       [[0, 0, 0], [1, 0, 0], [0, 0, 0]]):
            with self.assertRaises(ValueError):
                fillet(points, .5, .005)
        for radius, error in ((0, .01), (.5, 0), (.5, .5), (float('inf'), .01)):
            with self.assertRaises(ValueError):
                fillet([[0, 0, 0], [1, 0, 0]], radius, error)


if __name__ == '__main__':
    unittest.main()
