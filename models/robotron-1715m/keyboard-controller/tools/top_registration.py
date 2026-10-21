"""Bounded board-plane top registration, separate from raised lead observations."""
import hashlib,json,math
from pathlib import Path
from bottom_registration import pcb_regions,inside_hull
from photo_registration import project
ROOT=Path(__file__).resolve().parents[1]
def review(layout,bottom=None):
 evidence=json.loads((ROOT/'top-copper-landmarks.json').read_text())
 actual=hashlib.sha256((ROOT/evidence['photo']).read_bytes()).hexdigest()
 if actual!=evidence['photoSha256']:raise ValueError('Stale top copper photograph')
 pads={(c['ref'],p['pin']):p['position']for c in layout['components']for p in c['pads']}
 regions=pcb_regions(evidence,pads)
 for source,region in zip(evidence['pcbRegions'],regions):
  region['extrapolationChecks']=[]
  for row in source.get('extrapolationChecks',[]):
   projected=project(region['photoToModel'],row['photoPixel']);target=pads[row['ref'],row['pin']]
   region['extrapolationChecks'].append(dict(row,photoModel=projected,pcbModel=target,residualMm=math.dist(projected,target),insideAnchorHull=inside_hull(row['photoPixel'],region['anchorHull'])))
 if 'eyeRegistration' in evidence:
  from eye_registration import review as eye_review
  if bottom is None:
   from bottom_registration import review as bottom_review
   bottom=bottom_review(layout)
  regions.append(eye_review(evidence,bottom,ROOT))
 return dict(schema=1,scope=evidence['scope'],photoSha256=actual,pcbRegions=regions,copperAssignmentQualified=False)
