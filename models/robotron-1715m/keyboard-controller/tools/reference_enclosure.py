#!/usr/bin/env python3
"""Nominal solid intersections between reference PCB, components and keyboard surroundings."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / 'keyboard-controller/reference/enclosure-review.json'
INTERFACES = {
    'shell': 'keyboard_shell',
    'bottom': 'keyboard_bottom',
    'supports': 'keyboard_pcb_supports',
    'mounts': 'keyboard_controller_mounts',
    'matrix-board': 'keyboard_pcb',
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def volume(path):
    raw = path.read_bytes()
    count = struct.unpack_from('<I', raw, 80)[0]
    if len(raw) != 84 + 50 * count:
        raise ValueError('Expected binary STL')
    total = 0.
    for i in range(count):
        a, b, c = [struct.unpack_from('<3f', raw, 84 + i * 50 + 12 + j * 12) for j in range(3)]
        total += (a[0] * (b[1]*c[2]-b[2]*c[1]) +
                  a[1] * (b[2]*c[0]-b[0]*c[2]) +
                  a[2] * (b[0]*c[1]-b[1]*c[0]))
    return abs(total / 6)


def run():
    sources = {Path(__file__).resolve()}
    rows = []
    # A deliberately raised assembly must collide with the matrix board. This
    # guards against empty geometry or a disabled intersection masquerading as fit.
    cases = [(name, module, 'reference_populated_assembly', [0, 0, 0]) for name, module in INTERFACES.items()]
    cases += [('substrate-' + name, module, 'reference_substrate', [0, 0, 0]) for name, module in INTERFACES.items()]
    cases.append(('own-substrate', 'reference_substrate', 'reference_leads', [0, 0, 0]))
    nominal_count=len(cases)
    cases += [('allowance-' + name, module, 'reference_assembly_allowance_envelope', [0, 0, 0]) for name, module in INTERFACES.items()]
    cases.append(('allowance-own-substrate', 'reference_substrate', 'reference_lead_allowance_envelope', [0, 0, 0]))
    cases.append(('raised-assembly-control', 'keyboard_pcb', 'reference_populated_assembly', [0, 0, 1]))
    cases.append(('misaligned-mounting-control', 'keyboard_controller_mounts', 'reference_substrate', [.5, 0, 0]))
    cases.append(('raised-allowance-control', 'keyboard_pcb', 'reference_assembly_allowance_envelope', [0, 0, 1]))
    with tempfile.TemporaryDirectory() as temp:
        temp = Path(temp)
        for name, module, subject, offset in cases:
            scad, stl, deps = (temp / (name + ext) for ext in ('.scad', '.stl', '.deps'))
            scad.write_text(f'''include <{ROOT}/model.scad>
include <{ROOT}/keyboard-controller/reference/review.scad>
intersection() {{
    keyboard_controller_pose() translate({offset}) {subject}();
    {'keyboard_controller_pose() ' if module=='reference_substrate' else ''}{module}();
}}
''')
            result = subprocess.run(['openscad', '--backend', 'Manifold', '--export-format', 'binstl',
                                     '-D', 'part="audit"', '-D', 'show_reference=false', '-d', str(deps), '-o', str(stl), str(scad)],
                                    capture_output=True, text=True, timeout=60)
            empty = 'Current top level object is empty' in result.stderr
            if 'WARNING:' in result.stderr or 'ERROR:' in result.stderr or (result.returncode and not empty):
                raise RuntimeError(result.stderr)
            if not empty and not stl.exists():
                raise ValueError('OpenSCAD did not produce a solid or an explicit empty result')
            for line in deps.read_text().splitlines()[1:]:
                path = Path(line.strip().removesuffix('\\').rstrip()).resolve()
                if path == scad.resolve():
                    continue
                path.relative_to(ROOT)  # Reject dependencies outside the retained model.
                sources.add(path)
            value = volume(stl) if stl.exists() else 0.
            rows.append({'interface': name, 'subject': subject, 'offsetMm': offset,
                         'intersectionMm3': round(value, 6), 'intersects': value >= .001})
    report = {
        'schema': 3, 'variant': 'proposed-reference',
        'scope': 'Reference PCB substrate, drilled holes, populated bodies and leads at the existing keyboard controller transform. Nominal solids and conservative assembly allowance envelopes are reported separately. Allowance envelopes include curve approximation error; substrate mounting and hole solids remain nominal; analytical hole-loss checks are in the assembly report. Nominal and allowance lead envelopes are also intersected with their own drilled substrate; intentional body seating is excluded from that interface. Excludes PCB copper, connector engagement, cable and shield braid. Proposed circular lead bends are included. Zero volume permits touching. Enclosure dimensions and installed seating remain unmeasured.',
        'engine': subprocess.check_output(['openscad', '--version'], stderr=subprocess.STDOUT, text=True).strip(),
        'intersectionBudgetMm3': .001, 'results': rows[:nominal_count], 'allowanceResults': rows[nominal_count:-3],
        'allowanceInterfacesClear': not any(row['intersects'] for row in rows[nominal_count:-3]), 'positiveControl': rows[-3], 'mountingControl': rows[-2], 'allowanceControl': rows[-1],
        'nominalInterfacesClear': not any(row['intersects'] for row in rows[:nominal_count]),
        'mechanicallyQualified': False,
        'sources': {str(p.relative_to(ROOT)): digest(p) for p in sorted(sources)},
    }
    if not all(row['intersects'] for row in rows[-3:]):
        raise ValueError('Deliberately colliding assembly or mounting control did not intersect')
    TARGET.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ('results', 'positiveControl', 'mountingControl', 'nominalInterfacesClear')}, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true', help='Check retained result and exact source identities without rendering')
    args = parser.parse_args()
    if not args.check:
        run()
        return
    report = json.loads(TARGET.read_text())
    for name, expected in report['sources'].items():
        if digest(ROOT / name) != expected:
            raise ValueError('Stale enclosure review: ' + name)
    if {r['interface'] for r in report['results']} != set(INTERFACES) | {'substrate-' + name for name in INTERFACES} | {'own-substrate'}:
        raise ValueError('Incomplete enclosure review')
    if {r['interface'] for r in report['allowanceResults']} != {'allowance-' + name for name in INTERFACES} | {'allowance-own-substrate'}:
        raise ValueError('Incomplete allowance enclosure review')
    if report['allowanceInterfacesClear'] != (not any(r['intersects'] for r in report['allowanceResults'])):
        raise ValueError('Inconsistent allowance enclosure result')
    if not all(report[key]['intersects'] for key in ('positiveControl', 'mountingControl', 'allowanceControl')) or report['mechanicallyQualified']:
        raise ValueError('Invalid enclosure review scope or positive control')
    if report['nominalInterfacesClear'] != (not any(r['intersects'] for r in report['results'])):
        raise ValueError('Inconsistent enclosure result')
    print('Nominal enclosure result matches retained sources; physical fit remains unqualified')


if __name__ == '__main__':
    main()
