#!/usr/bin/env python3
"""Fit nominal lead rectangles in two owner photos. Requires numpy and scipy.
Run --apply to update only photo-registered placements and visible artwork.
Board envelope contains observed edges; unobserved mounts remain estimates.
"""
import argparse,json
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
root=Path(__file__).resolve().parents[1]
args=argparse.ArgumentParser();args.add_argument('--apply',action='store_true');args=args.parse_args()
obs=json.loads((root/'board-photo-observations.json').read_text())
d=json.loads((root/'board-layout.json').read_text())
def project(v,points):
 x,y=np.array(points).T/1000;q=v[6]*x+v[7]*y+1
 return np.array([(v[0]*x+v[1]*y+v[2])/q,(v[3]*x+v[4]*y+v[5])/q]).T
def fit(view,anchor):
 def residual(v):
  out=[]
  for pack in view['packages']:
   p=project(v,pack['corners']);p-=p.mean(axis=0);w,h=pack['size']
   out.extend((p-np.array([[w/2,-h/2],[-w/2,-h/2],[-w/2,h/2],[w/2,h/2]])).flatten())
  out.extend((project(v,[view['anchorPhoto']])[0]-anchor)*5)
  return out
 v=least_squares(residual,[-220,0,60,0,220,-45,0,0],max_nfev=10000).x
 return v,float(np.sqrt(np.mean(np.array(residual(v))**2)))
h,err=fit(obs['processor'],obs['processor']['anchorModel'])
h2,err2=fit(obs['ram'],project(h,[obs['processor']['sharedCTC']])[0])
report={'version':1,'photoObservations':'board-photo-observations.json','processor':{'normalizedHomography':h.tolist(),'rmsMillimetres':err},'ram':{'normalizedHomography':h2.tolist(),'rmsMillimetres':err2},'holdoutCTCDistanceMm':float(np.linalg.norm(project(h,[obs['processor']['holdoutCTC']])-project(h2,[obs['ram']['holdoutCTC']]))),'observedEdgePoints':project(h2,obs['ram']['edgePoints']).tolist()+project(h,obs['processor']['edgePoints']).tolist(),'limitations':obs['limitations']}
assert err<.6 and err2<.3 and report['holdoutCTCDistanceMm']<2,report
(root/'checks/board-calibration.json').write_text(json.dumps(report,indent=2)+'\n')
if args.apply:
 b=d['boards'][0]
 edges=np.array(report['observedEdgePoints']);lo=np.floor(edges.min(axis=0));hi=np.ceil(edges.max(axis=0))
 b['origin'][:2]=lo.tolist();b['size']=(hi-lo).tolist()
 b['envelopeEvidence']='Rectangular envelope of two-photo edge picks, rounded outward to millimetres; photo estimate, not a dimensional certificate. Mounts remain provisional.'
 def xy(p,h=h):return np.round(project(h,[p])[0],3).tolist()
 for c in b['components']:
  if 'photoCentre' not in c:continue
  ram=c['ref'] in {'A4','A5'} or c['ref'][1:].isdigit() and 65<=int(c['ref'][1:])<=96
  c['position'][:2]=xy(np.array(c['photoCentre'])/1.125,h2) if ram else xy(c['photoCentre'])
  c['status']='Multi-package owner-photo registration; nominal pitches, reference correspondence provisional'
 for c in b['passives']:
  if 'photoCentre' in c:c['position'][:2]=xy(c['photoCentre'])
 # Recover a source pixel for older landmarks exactly once.
 old=np.array(d['processorPinRegistration']['homography']).reshape(3,3)
 def old_pixel(p):
  v=np.linalg.inv(old)@np.array([*p[:2],1]);return (v[:2]/v[2]).tolist()
 for c in b['connectors'][1:]:
  c.setdefault('photoCentre',old_pixel(c['position']));c['position'][:2]=xy(c['photoCentre'])
 j=d['motherboardJumpers'];j.setdefault('photoCentre',old_pixel(j['position']));j['position'][:2]=xy(j['photoCentre'])
 a=d['motherboardArtwork'];a['paths']=[[xy(p) for p in path] for path in a['photoPaths']]
 a['lands']=[xy(p) for p in a.get('photoLands',[])]
 for m in a['markings']:
  m.setdefault('photoCentre',old_pixel(m['position']));m['position']=xy(m['photoCentre'])
 d['multiPhotoCalibration']=report
 (root/'board-layout.json').write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
print(json.dumps(report,indent=2))
