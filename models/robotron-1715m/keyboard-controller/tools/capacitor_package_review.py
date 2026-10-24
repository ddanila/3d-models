#!/usr/bin/env python3
"""Check a published replacement can envelope without changing historical geometry."""
import argparse
import json
import math
from pathlib import Path
import subprocess
import tempfile
from unittest.mock import patch

import reference_assembly as assembly
from reference_enclosure import INTERFACES, volume

ROOT = assembly.ROOT
CANDIDATE = ROOT/'reference/capacitor-package-candidate.json'


def not_any(rows):
    return not any(row['intersects'] for row in rows)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--check', action='store_true', help='Check retained scope and source identities without rendering')
    args=parser.parse_args()
    if args.check:
        report=assembly.read(args.out/'assessment.json')
        if report['candidate']!=assembly.read(CANDIDATE):raise ValueError('Candidate changed')
        if report['adopted'] or report['mechanicallyQualified']:raise ValueError('Invalid qualification claim')
        if not math.isfinite(report['candidateVolumeMm3']) or report['candidateVolumeMm3']<=0:raise ValueError('Missing nonempty control')
        rows=report['interfaces']
        if len(rows)!=len(INTERFACES) or {row['interface'] for row in rows}!=set(INTERFACES):raise ValueError('Incomplete interfaces')
        for row in rows:
            value=row['intersectionMm3']
            if not math.isfinite(value) or value<0 or row['intersects']!=(value>=.001):raise ValueError('Invalid intersection')
        if report['nominalEnclosureClear']!=not_any(rows):raise ValueError('Invalid enclosure conclusion')
        for name,expected in report['sources'].items():
            if assembly.digest(ROOT.parent/name)!=expected:raise ValueError('Stale candidate review: '+name)
        print('Candidate receipt matches sources; not adopted or mechanically qualified')
        return
    candidate=assembly.read(CANDIDATE)
    spec=assembly.read(assembly.REF/'assembly.json')
    original_read=assembly.read
    for ref in candidate['components']:
        record=spec['components'][ref]
        record.update(sizeMm=candidate['bodyEnvelopeMm'],leadPitchMm=candidate['leadPitchNominalMm'],
                      bendRadiusMm=candidate['proposedBendRadiusMm'])
        # Existing circumscribed lead-section interface: zero second axis models
        # the stated round nominal diameter, not an asserted maximum tolerance.
        record['leadSectionMaximumMm']=[candidate['leadDiameterNominalMm'],0]
    with patch.object(assembly,'read',side_effect=lambda path:spec if path==assembly.REF/'assembly.json' else original_read(path)):
        data,scad=assembly.build()
    report={'candidate':candidate,'adopted':False,'mechanicallyQualified':False,
            'assemblyReview':data['review'],'sources':{'keyboard-controller/'+name:digest for name,digest in data['sources'].items()}, 'interfaces':[],
            'scope':'Proposed replacement envelope at existing seats and pads. Nominal pitch and lead diameter only; no polarity mapping, tolerance-extreme fit, installed identity or electrical substitution qualification.'}
    report['sources']['keyboard-controller/reference/capacitor-package-candidate.json']=assembly.digest(CANDIDATE)
    report['sources']['keyboard-controller/tools/capacitor_package_review.py']=assembly.digest(Path(__file__))
    report['sources']['keyboard-controller/tools/reference_enclosure.py']=assembly.digest(ROOT/'tools/reference_enclosure.py')
    args.out.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory() as directory:
        temp=Path(directory)
        # Isolate candidate modules from the accepted reference assembly.
        scad=scad.replace('reference_populated_assembly','candidate_populated_assembly')
        scad=scad.replace('reference_assembly_allowance_envelope','candidate_allowance_envelope')
        scad=scad.replace('reference_leads','candidate_leads').replace('reference_lead_allowance_envelope','candidate_lead_allowance_envelope')
        scad=scad.replace('"../../../', '"'+str(ROOT.parent.resolve())+'/')
        generated=temp/'candidate.scad';generated.write_text(scad)
        for name,module in INTERFACES.items():
            path=temp/(name+'.scad');stl=temp/(name+'.stl');deps=temp/(name+'.deps')
            path.write_text(f'include <{ROOT.parent}/model.scad>\ninclude <{ROOT}/reference/review.scad>\ninclude <{generated}>\nintersection() {{keyboard_controller_pose() candidate_populated_assembly(); {module}();}}\n')
            result=subprocess.run(['openscad','--backend','Manifold','--export-format','binstl','-D','part="audit"','-D','show_reference=false','-d',str(deps),'-o',str(stl),str(path)],capture_output=True,text=True,timeout=60)
            empty='Current top level object is empty' in result.stderr
            if 'WARNING:' in result.stderr or 'ERROR:' in result.stderr or (result.returncode and not empty):
                raise ValueError(result.stderr)
            if not empty and not stl.exists():raise ValueError('Missing intersection output')
            for line in deps.read_text().splitlines()[1:]:
                dependency=Path(line.strip().removesuffix('\\').rstrip()).resolve()
                if dependency in (path.resolve(),generated.resolve()):continue
                report['sources'][str(dependency.relative_to(ROOT.parent))]=assembly.digest(dependency)
            size=volume(stl) if stl.exists() else 0
            report['interfaces'].append({'interface':name,'intersectionMm3':size,'intersects':size>=.001})
        # Nonempty candidate STL guards against a missing/empty assembly.
        control=temp/'control.scad';control.write_text(f'include <{generated}>\ncandidate_populated_assembly();\n')
        subprocess.run(['openscad','--backend','Manifold','--export-format','binstl','-o',str(temp/'control.stl'),str(control)],check=True,capture_output=True,timeout=60)
        report['candidateVolumeMm3']=volume(temp/'control.stl')
        if report['candidateVolumeMm3']<=0:raise ValueError('Empty candidate')
    for name,expected in report['sources'].items():
        if assembly.digest(ROOT.parent/name)!=expected:raise ValueError('Source changed during review: '+name)
    report['nominalEnclosureClear']=not any(row['intersects'] for row in report['interfaces'])
    report['engine']=subprocess.check_output(['openscad','--version'],stderr=subprocess.STDOUT,text=True).strip()
    (args.out/'assessment.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'nominalEnclosureClear':report['nominalEnclosureClear'],'interfaces':report['interfaces']},indent=2))


if __name__=='__main__':main()
