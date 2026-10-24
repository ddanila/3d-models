import unittest
from row_spacing_review import trial

class RowSpacingTests(unittest.TestCase):
 def pose(self):
  return {'anchors':['1','2'],'checks':[
   {'terminal':n,'heldOut':n not in ('1','2'),'residualAcrossRowMm':a,'residualAlongRowMm':v}
   for n,a,v in [('1',0,0),('2',0,0),('3',-1,0),('4',-1,2),('5',-1.5,0)]]}
 def test_one_row_offset_preserves_independent_errors(self):
  result=trial(self.pose(),'3',['3','4','5'])
  self.assertEqual(result['signedOppositeRowOffsetMm'],-1)
  checks={p['terminal']:p for p in result['checks']}
  self.assertFalse(checks['3']['heldOut'])
  self.assertTrue(checks['4']['heldOut'])
  self.assertEqual(checks['4']['residualMm'],2)
  self.assertEqual(checks['5']['residualMm'],.5)
  self.assertEqual(result['maximumHeldOutResidualMm'],2)
 def test_anchor_cannot_calibrate_opposite_row(self):
  with self.assertRaises(ValueError):trial(self.pose(),'1',['1','4','5'])
 def test_two_independent_opposite_points_required(self):
  with self.assertRaises(ValueError):trial(self.pose(),'3',['3','4'])

if __name__=='__main__':unittest.main()
