import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
import efs_registration_review as review


class RegistrationTests(unittest.TestCase):
    def test_known_affine_geometry_and_independent_scale_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for name in ('reference/efs-form-constraints.json','component-evidence.json',
                         'bottom-landmarks.json','sense-review.json','tools/efs_registration_review.py',
                         'tools/photo_registration.py'):
                target=root/name;target.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(review.ROOT/name,target)
            def write(name,value): (root/name).write_text(json.dumps(value))
            components=json.loads((root/'component-evidence.json').read_text())
            obs=components['X1']['physicalReview']['underside'];obs['pixelUncertainty']=0
            obs['jointRowsPixels']={row:[[100+12*x,200+30*i] for i in range(13)]
                                   for row,x in [('housingFar',0),('housingNear',5)]}
            write('component-evidence.json',components)
            bottom=json.loads((root/'bottom-landmarks.json').read_text())
            bottom['checks']=[{'ref':'A5','pin':pin,'photoPixel':point} for pin,point in
                              [('1',[100,800]),('20',[100,1370]),('40',[280,800]),('21',[280,1370])]]
            write('bottom-landmarks.json',bottom)
            with patch.object(review,'ROOT',root):result=review.build()
            self.assertTrue(result['nominalCpuSpanChecksPassed'])
            self.assertAlmostEqual(result['maximumInteriorConnectorResidualMm'],0)
            for row in result['heldOutCpuChecks']:self.assertAlmostEqual(row['projectedSpanMm'],47.5)
            self.assertFalse(result['registrationQualified'])
            bottom['checks'][1]['photoPixel'][1]+=60
            write('bottom-landmarks.json',bottom)
            with patch.object(review,'ROOT',root):result=review.build()
            self.assertFalse(result['nominalCpuSpanChecksPassed'])
            self.assertTrue(result['heldOutCpuChecks'][0]['exceedsExistingPointBudget'])

if __name__=='__main__':unittest.main()
