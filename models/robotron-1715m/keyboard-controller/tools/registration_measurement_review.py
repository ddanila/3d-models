#!/usr/bin/env python3
"""Identify independent measurements that discriminate retained metric fits."""
import argparse
import hashlib
import json
import math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/'reference/package-reviews/registration-measurements/assessment.json'


def build():
    names=['reference/package-reviews/distributed-registration/assessment.json',
           'bottom-landmarks.json','sense-review.json','tools/registration_measurement_review.py']
    fits,bottom,sense=[json.loads((ROOT/n).read_text()) for n in names[:3]]
    pixels={}
    for region in [bottom]+bottom['pcbRegions']:
        for item in region['anchors']+region['checks']:
            key=item['ref']+':'+item['pin']
            if key in pixels and pixels[key]!=item['photoPixel']:raise ValueError('Conflicting hole observations')
            pixels[key]=item['photoPixel']
    candidates=[('nominal',fits['nominal'])]+[(str(c['rowXShiftSigns']),c) for c in fits['systematicPickingTrials']]
    requests=[]
    for index,pair in enumerate((('A5:1','A5:40'),('A5:20','A5:21'))):
        predictions=[{'fit':name,'distanceMm':fit['unconstrainedCpuCrossRowDistancesMm'][index]} for name,fit in candidates]
        requests.append({'holePair':pair,'photoPixels':[pixels[p] for p in pair],
                         'measurement':'Centre-to-centre distance between opposing PCB holes, measured on the primary board underside; not body width or loose lead-tip spacing.',
                         'candidatePredictions':predictions,
                         'predictionSpanMm':max(p['distanceMm'] for p in predictions)-min(p['distanceMm'] for p in predictions)})
    corners=sense['envelopeTrial']['photoCorners']
    widths=[]
    for indices in ((0,1),(3,2)):
        widths.append({'photoPixels':[corners[i] for i in indices],
                       'candidatePredictions':[{'fit':name,'distanceMm':math.dist(*(fit['projectedBoardCornersMm'][i] for i in indices))} for name,fit in candidates]})
    return {'schema':1,'sources':{n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in names},
            'photoSha256':sense['sourceSha256'],'specimen':'primary',
            'preferredMeasurements':requests,'alternativeEndWidths':widths,
            'recordWithMeasurement':['Which hole pair or board edge was measured','Measured distance in mm','Instrument resolution and estimated total error, including locating hole centres'],
            'interpretation':'Measure both CPU ends if accessible: one transverse distance constrains scale locally; the second can expose a perspective inconsistency. End widths are a coarser fallback whose photographed corner picks need separate uncertainty.',
            'acceptance':'Use an independent measurement to constrain a new fit and keep other observations held out. Propagate measurement, picking and manufacturing uncertainties before the existing placement and cross-side gates. Do not select the closest tabulated candidate and move pads.',
            'limits':'These predictions cover retained sensitivity examples, not a complete uncertainty envelope. Their separation is not a guaranteed measurement-accuracy requirement. Common row shifts remain almost indistinguishable by widths; absolute placement and terminal identity still need their own evidence.',
            'registrationQualified':False,'padPlacementAuthorized':False}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');a=p.parse_args()
    def stable(value):
        if isinstance(value,float):return round(value,6)+0.0
        if isinstance(value,list):return [stable(v) for v in value]
        if isinstance(value,dict):return {k:stable(v) for k,v in value.items()}
        return value
    text=json.dumps(stable(build()),indent=2)+'\n'
    if a.check:
        if TARGET.read_text()!=text:raise SystemExit('Stale registration measurement review')
    else:TARGET.parent.mkdir(parents=True,exist_ok=True);TARGET.write_text(text)
    print(TARGET)
