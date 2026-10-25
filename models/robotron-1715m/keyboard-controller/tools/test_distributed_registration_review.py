import math
import unittest
from distributed_registration_review import fit
from photo_registration import homography, project


class DistributedFitTests(unittest.TestCase):
    def test_recovers_independent_points_under_perspective(self):
        targets=[[x,2.5*i] for x in (0,5) for i in range(13)]
        # Known projective camera, including unequal axis scales and shear.
        camera=[12,.25,1200,-.2,11.5,1800,.0003,-.00015,1]
        points=[project(camera,p) for p in targets]
        cpu_targets=[[[3,65],[3,112.5]],[[18,65],[18,112.5]]]
        cpu=[[project(camera,p) for p in row] for row in cpu_targets]
        h,status=fit(points,targets,cpu,47.5)
        self.assertTrue(status['converged'])
        for expected in [[-5,-30],[25,150],[10,45]]:
            pixel=project(camera,expected)
            actual=project(h,[(pixel[0]-1200)/1000,(pixel[1]-1900)/1000])
            self.assertLess(math.dist(actual,expected),.001)

    def test_incomplete_geometry_rejected(self):
        with self.assertRaises(ValueError):fit([],[],[],47.5)

if __name__=='__main__':unittest.main()
