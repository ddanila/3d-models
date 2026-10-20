"""Report native same-net copper islands using KiCad's connectivity engine."""
from collections import defaultdict


def build(board, components, layout, drc):
    connectivity = board.GetConnectivity()
    connectivity.Build(board)
    items = list(board.GetTracks()) + [p for f in board.GetFootprints() for p in f.Pads()]
    uid = lambda item: item.m_Uuid.AsString()
    by_id = {uid(item): item for item in items}
    parent = {key: key for key in by_id}

    def root(key):
        while parent[key] != key:
            parent[key] = parent[parent[key]]
            key = parent[key]
        return key

    for item in items:
        for other in connectivity.GetConnectedItems(item):
            if uid(other) in parent and item.GetNetCode() == other.GetNetCode():
                parent[root(uid(other))] = root(uid(item))
    pad_names = {uid(p): f.GetReference()+':'+p.GetNumber() for f in board.GetFootprints() for p in f.Pads()}
    placed = {c['ref'] for c in layout['components']}
    route_evidence = {r['id']: r['evidence'] for r in layout['routes']+layout['vias']}
    nets = defaultdict(list)
    for ref, component in components.items():
        for pin, net in component['pins'].items():
            if net:
                nets[net].append(ref+':'+pin)
    result = []
    uuid_net = {uid(i): i.GetNetname() for i in items}
    gaps = defaultdict(int)
    for gap in drc['unconnected_items']:
        names = {uuid_net.get(i['uuid']) for i in gap['items']}
        names.discard(None)
        if len(names) != 1:
            raise ValueError('DRC gap must identify one native net')
        gaps[names.pop()] += 1
    # KiCad can choose different equivalent airwire endpoints on each run.
    # Keep per-net DRC counts; deterministic islands define the actual gaps.
    for net, terminals in sorted(nets.items()):
        groups = defaultdict(list)
        for item in items:
            if item.GetNetname() == net:
                groups[root(uid(item))].append(uid(item))
        for item in layout['routes']+layout['vias']:
            if item['net'] == net and not set(item['evidence'].get('terminals', [])) <= set(terminals):
                raise ValueError('Route evidence endpoints differ from their schematic net')
        islands = []
        for ids in groups.values():
            pins = sorted(pad_names[i] for i in ids if i in pad_names)
            copper = sorted(i for i in ids if i not in pad_names)
            islands.append(dict(terminals=pins, copperIds=copper,
                unplacedTerminals=[p for p in pins if p.split(':')[0] not in placed],
                evidenceGroups=sorted({route_evidence[i].get('group', 'ungrouped') for i in copper}),
                evidenceStatuses=sorted({route_evidence[i]['status'] for i in copper})))
        islands.sort(key=lambda g:(g['terminals'],g['copperIds']))
        pad_groups = sum(bool(g['terminals']) for g in islands)
        result.append(dict(net=net, terminals=sorted(terminals), minimumLinks=max(0,len(terminals)-1),
             islands=islands, padGroups=pad_groups, floatingCopperGroups=len(islands)-pad_groups,
             remainingPadGroupLinks=max(0,pad_groups-1),
             nativePadsConnected=pad_groups==1, multiTerminal=len(terminals)>1,
             drcUnconnectedItems=gaps.get(net, 0)))
    return dict(schema=1, scope='Native KiCad same-net connectivity, including off-board placeholder pads. Connected does not mean historically verified or fabrication-ready. DRC gaps may include floating copper; pad-group links count only disconnected terminal groups. Cross-net clearance/short findings remain in qualification.json.',
        summary=dict(assignedPins=sum(len(n) for n in nets.values()), nets=len(nets),
            multiTerminalNets=sum(r['multiTerminal'] for r in result),
            fullyConnectedMultiTerminalNets=sum(r['multiTerminal'] and r['nativePadsConnected'] for r in result),
            minimumLinks=sum(r['minimumLinks'] for r in result),
            remainingPadGroupLinks=sum(r['remainingPadGroupLinks'] for r in result),
            floatingCopperGroups=sum(r['floatingCopperGroups'] for r in result),
            drcUnconnectedItems=len(drc['unconnected_items'])), nets=result)
