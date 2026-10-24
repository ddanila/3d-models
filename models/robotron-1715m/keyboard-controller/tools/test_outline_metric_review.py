import math
import unittest
from outline_metric_review import estimate

class OutlineMetricTests(unittest.TestCase):
    def test_tilted_rectangle_recovers_camera_and_aspect(self):
        x,y=math.radians(15),math.radians(20)
        a=[math.cos(y),0,-math.sin(y)]
        b=[math.sin(y)*math.sin(x),math.cos(x),math.cos(y)*math.sin(x)]
        corners=[]
        for u,v in ((0,0),(1,0),(1,1),(0,1)):
            p=[2*u*a[i]+6*v*b[i]+(15 if i==2 else 0) for i in range(3)]
            corners.append([800+1000*p[0]/p[2],600+1000*p[1]/p[2]])
        r=estimate(corners,[800,600])
        self.assertAlmostEqual(r['focalPixels'],1000,places=7)
        self.assertAlmostEqual(r['longToShortAspect'],3,places=9)
    def test_affine_outline_does_not_identify_focal_length(self):
        with self.assertRaises(ValueError):estimate([[0,0],[2,0],[2,6],[0,6]],[1,3])
    def test_degenerate_outline_rejected(self):
        with self.assertRaises(ValueError):estimate([[0,0]]*4,[1,3])

if __name__=='__main__':unittest.main()
