#!/usr/bin/env python3
"""Nominal solid intersections between reference components and keyboard surroundings."""
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
    cases = [(name, module, 0) for name, module in INTERFACES.items()]
    cases.append(('raised-assembly-control', 'keyboard_pcb', 1))
    with tempfile.TemporaryDirectory() as temp:
        temp = Path(temp)
        for name, module, lift in cases:
            scad, stl, deps = (temp / (name + ext) for ext in ('.scad', '.stl', '.deps'))
            scad.write_text(f'''include <{ROOT}/model.scad>
include <{ROOT}/keyboard-controller/reference/assembly-generated/assembly.scad>
intersection() {{
    keyboard_controller_pose() translate([0,0,{lift}]) reference_populated_assembly();
    {module}();
}}
''')
            result = subprocess.run(['openscad', '--backend', 'Manifold', '--export-format', 'binstl',
                                     '-D', 'part="audit"', '-d', str(deps), '-o', str(stl), str(scad)],
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
            rows.append({'interface': name, 'assemblyLiftMm': lift,
                         'intersectionMm3': round(value, 6), 'intersects': value >= .001})
    report = {
        'schema': 1, 'variant': 'proposed-reference',
        'scope': 'Populated reference bodies and leads at the existing keyboard controller transform. Static nominal solids only; excludes PCB copper, connector engagement, cable and shield braid, bend radii and manufacturing tolerances. Zero volume permits touching. Enclosure dimensions and installed seating remain unmeasured.',
        'engine': subprocess.check_output(['openscad', '--version'], stderr=subprocess.STDOUT, text=True).strip(),
        'intersectionBudgetMm3': .001, 'results': rows[:-1], 'positiveControl': rows[-1],
        'nominalInterfacesClear': not any(row['intersects'] for row in rows[:-1]),
        'mechanicallyQualified': False,
        'sources': {str(p.relative_to(ROOT)): digest(p) for p in sorted(sources)},
    }
    if not rows[-1]['intersects']:
        raise ValueError('Raised-assembly positive control did not intersect the matrix board')
    TARGET.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ('results', 'positiveControl', 'nominalInterfacesClear')}, indent=2))


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
    if {r['interface'] for r in report['results']} != set(INTERFACES):
        raise ValueError('Incomplete enclosure review')
    if not report['positiveControl']['intersects'] or report['mechanicallyQualified']:
        raise ValueError('Invalid enclosure review scope or positive control')
    if report['nominalInterfacesClear'] != (not any(r['intersects'] for r in report['results'])):
        raise ValueError('Inconsistent enclosure result')
    print('Nominal enclosure result matches retained sources; physical fit remains unqualified')


if __name__ == '__main__':
    main()
