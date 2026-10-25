import math
import unittest
from mount_hole_registration_review import circle, circle_intersects_quad, screen
from photo_registration import homography, project

class MountHoleTests(unittest.TestCase):
    def test_known_circle_under_perspective(self):
        camera=[12,.5,1200,-.3,11,1900,.0004,-.0002,1]
        ground=[[0,0],[10,0],[10,10],[0,10]]
        photo=[project(camera,p) for p in ground]
        matrix=homography([[(p[0]-1200)/1000,(p[1]-1900)/1000] for p in photo],ground)
        ring=[[4+2*math.cos(i*math.pi/4),5+2*math.sin(i*math.pi/4)] for i in range(8)]
        pixels=[project(camera,p) for p in ring]
        result=screen(matrix,pixels,.1)
        self.assertAlmostEqual(result['fittedRadiusMm'],2,places=8)
        self.assertLess(result['maximumRadialResidualMm'],1e-8)
        self.assertTrue(result['circleIntersectsEveryPickingBox'])
        distorted=[v*(2 if i in (0,1,2) else 1) for i,v in enumerate(matrix)]
        self.assertFalse(screen(distorted,pixels,.1)['circleIntersectsEveryPickingBox'])

    def test_intersection_is_not_bounding_disk(self):
        square=[[1,1],[2,1],[2,2],[1,2]]
        self.assertFalse(circle_intersects_quad([0,0],1,square))
        self.assertTrue(circle_intersects_quad([0,0],2,square))
        self.assertTrue(circle_intersects_quad([0,0],2,list(reversed(square))))
        self.assertFalse(circle_intersects_quad([0,0],3,square))
        self.assertFalse(circle_intersects_quad([1.5,1.5],2,square))
        self.assertTrue(circle_intersects_quad([1.5,1.5],.1,square))

    def test_degenerate_geometry_rejected(self):
        with self.assertRaises(ValueError):circle([[0,0]]*8)
        with self.assertRaises(ValueError):screen([1,0,0,0,1,0,0,0,1],[],0)

if __name__=='__main__':unittest.main()
