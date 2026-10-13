#!/usr/bin/env python3
"""Refresh keyboard review PNGs only: no full-machine export, museum sync or CI."""
from pathlib import Path
import argparse
import json
import subprocess
import time

root = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--view', choices=['assembled', 'exploded', 'boards', 'all'], default='all')
args = parser.parse_args()
keys = json.loads((root.parent / 'keyboard-layout.json').read_text())
(root / 'legends.scad').write_text(
    '// Generated from ../keyboard-layout.json; same order as ../keyboard-layout.scad.\n'
    + 'key_legends=' + json.dumps([k.get('legend', [k['label']]) for k in keys], ensure_ascii=False) + ';\n')
for view in (['assembled', 'exploded', 'boards'] if args.view == 'all' else [args.view]):
    filename = 'preview.png' if view == 'assembled' else view + '.png'
    camera = '0,0,0,65,0,25,850' if view == 'exploded' else '0,0,0,35,0,0,850'
    started = time.monotonic()
    result = subprocess.run([
        'openscad', '--backend', 'Manifold', '--preview', '--imgsize=1400,900',
        '--viewall', '--autocenter', '--camera=' + camera,
        '-D', 'view=' + json.dumps(view), '-D', 'show_springs=' + str(view == 'exploded').lower(),
        '-o', str(root / filename), str(root / 'model.scad'),
    ], capture_output=True, text=True)
    if result.returncode or 'ERROR:' in result.stderr or 'WARNING:' in result.stderr:
        raise RuntimeError(result.stderr)
    print(f'{filename}: {time.monotonic() - started:.2f}s')
