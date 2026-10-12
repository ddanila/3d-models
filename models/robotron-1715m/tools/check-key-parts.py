#!/usr/bin/env python3
"""Audit exported key STL topology and measured spring envelope without dependencies."""
from pathlib import Path
from collections import Counter, defaultdict
import json,struct
root=Path(__file__).resolve().parents[1]
reports={}
for rel in ['keycap/keycap.stl']+[f'key-switch/{p}.stl' for p in ['spring','guide','mount','carrier','rubber','contacts']]:
    data=(root/rel).read_bytes();count=struct.unpack_from('<I',data,80)[0]
    assert len(data)==84+50*count,rel
    edges=Counter();adj=defaultdict(set);vertices=set();volume=0
    for i in range(count):
        tri=[tuple(round(v,5) for v in struct.unpack_from('<3f',data,84+50*i+12+12*j)) for j in range(3)]
        vertices.update(tri)
        for j in range(3):
            a,b=tri[j],tri[(j+1)%3];edges[tuple(sorted((a,b)))]+=1;adj[a].add(b);adj[b].add(a)
        a,b,c=tri;volume+=(a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6
    assert all(n==2 for n in edges.values()),f'Non-closed edge: {rel}'
    left=set(vertices);components=0
    while left:
        todo=[left.pop()];components+=1
        while todo:
            v=todo.pop();new=adj[v]&left;left-=new;todo.extend(new)
    assert components==(2 if rel.endswith('contacts.stl') else 1),(rel,components)
    assert volume>0,(rel,volume)
    bounds=[[min(v[j] for v in vertices) for j in range(3)],[max(v[j] for v in vertices) for j in range(3)]]
    extents=[round(bounds[1][j]-bounds[0][j],5) for j in range(3)]
    if rel.endswith('spring.stl'):
        assert all(abs(a-b)<.001 for a,b in zip(extents,[13,13,23])),extents
        # Wire cross-section at the first meridian: radial diameter is 0.4 mm.
        first=[struct.unpack_from('<3f',data,84+50*i+12+12*j) for i in range(count) for j in range(3)]
        section=[v for v in first if abs(v[1])<.00001 and v[0]>0 and v[2]<.41]
        assert abs(max(v[0] for v in section)-min(v[0] for v in section)-.4)<.001
    reports[rel]={'triangles':count,'closedTwoManifold':True,'components':components,'boundsMm':bounds,'extentsMm':extents,'volumeMm3':round(volume,3)}
(root/'key-switch/mesh-check.json').write_text(json.dumps(reports,indent=2)+'\n')
(root/'keycap/mesh-check.json').write_text(json.dumps(reports['keycap/keycap.stl'],indent=2)+'\n')
print(json.dumps(reports,indent=2))
