"""Require source-bound export receipts for every native controller mesh consumer."""
from copy import deepcopy

PARTS = frozenset('keyboard-controller-' + suffix for suffix in (
    'board', 'chips', 'caps', 'metal', 'ink', 'traces', 'solder', 'ceramic',
    'rom-cover', 'rom-ink', 'leads', 'resistors', 'resistor-bands', 'connectors', 'networks')) | frozenset(
    'keyboard-entry-' + suffix for suffix in ('choke', 'wires', 'black', 'pink', 'blue'))
SOURCES = ('specimen-details.scad', 'keyboard-controller/generated/controller.scad',
           'controller-package-data.scad')


def receipts(previous, parts, selected, source_hashes):
    """Only meshes actually rebuilt in this run receive current source hashes."""
    result = deepcopy(previous)
    rebuilt = PARTS if selected is None else PARTS.intersection(selected)
    by_name = {part['name']: part for part in parts}
    for name in rebuilt:
        result[name] = {'meshSha256': by_name[name]['sha256'],
                        'sources': dict(source_hashes)}
    return result


def validate(manifest, source_hashes):
    by_name = {part['name']: part for part in manifest['parts']}
    recorded = manifest.get('keyboardControllerMeshes', {})
    for name in sorted(PARTS):
        receipt = recorded.get(name, {})
        if receipt.get('sources') != source_hashes:
            raise ValueError('stale controller mesh sources: ' + name)
        if receipt.get('meshSha256') != by_name[name]['sha256']:
            raise ValueError('controller mesh does not match export receipt: ' + name)
