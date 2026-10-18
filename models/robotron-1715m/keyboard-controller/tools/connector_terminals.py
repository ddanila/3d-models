"""Constrain connector numbering using photo-supported reference-net attachments."""
import itertools


def review(component, connectivity):
    physical = component['physicalReview']
    rows = physical['leadEndRowsPixels']
    names = ['housingFar', 'housingNear']
    counts = {len(rows[name]) for name in names}
    if len(counts) != 1:
        raise ValueError('Connector rows differ in length')
    count = counts.pop()
    constraints = physical['terminalConstraints']
    if not constraints:
        raise ValueError('No independent terminal constraints')
    for item in constraints:
        if item['row'] not in names or not 0 <= item['indexFromCable'] < count:
            raise ValueError('Connector contact outside observed row')
        if item['photoSource'] != physical['photoSource']:
            raise ValueError('Terminal attachment requires primary photograph')
    candidates = []
    for letters in [('A', 'B'), ('B', 'A')]:
        for directions in itertools.product([1, -1], repeat=2):
            mapping = {name: [letter + str(i+1 if direction == 1 else count-i) for i in range(count)]
                       for name, letter, direction in zip(names, letters, directions)}
            checks = []
            for item in constraints:
                endpoint = item['referenceEndpoint']
                net = connectivity['components'][endpoint['ref']]['pins'][endpoint['pin']]
                pin = mapping[item['row']][item['indexFromCable']]
                assigned = connectivity['components']['X1']['pins'].get(pin)
                checks.append({'observation': item['id'], 'candidatePin': pin,
                               'referenceNet': net, 'matches': net is not None and net == assigned})
            candidates.append({'rows': mapping, 'checks': checks,
                               'consistent': all(c['matches'] for c in checks)})
    survivors = [c for c in candidates if c['consistent']]
    resolved = {name: survivors[0]['rows'][name] for name in names
                if survivors and all(c['rows'][name] == survivors[0]['rows'][name] for c in survivors)}
    return {'scope': 'Conditional on photographed attachments and the reference schematic. Logical elimination is not a continuity measurement. Row directions are independent hypotheses.',
            'candidates': candidates, 'resolvedRows': resolved,
            'unresolvedRows': [name for name in names if name not in resolved],
            'completeTerminalOrderResolved': bool(survivors) and len(resolved) == len(names),
            'referenceAbsentPins': sorted({pin for c in survivors for row in c['rows'].values() for pin in row}
                                          - set(connectivity['components']['X1']['pins']))}
