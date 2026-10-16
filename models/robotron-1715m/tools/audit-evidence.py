#!/usr/bin/env python3
"""Report source-rule coverage, including ordered overlaps; never infer evidence."""
import json,re
from pathlib import Path
root=Path(__file__).resolve().parents[1]
data=json.loads((root/'browser/model.json').read_text())
rules=json.loads((root/'evidence-map.json').read_text())['rules']
rows=[]
for part in data['parts']:
 matches=[i for i,r in enumerate(rules) if re.search(r['pattern'],part['name'])]
 rows.append(dict(part=part['name'],rule=matches[0] if matches else None,overriddenRules=matches[1:],category=rules[matches[0]]['category'] if matches else 'unknown'))
report=dict(scope='Canonical exported part names only. First matching rule wins; overlaps are listed for review. Runtime-generated packages, labels and helpers are audited separately in DAC. Coverage is not proof of dimensions or physical print verification.',parts=rows,unmapped=[r['part'] for r in rows if r['rule'] is None])
(root/'checks/evidence-coverage.json').write_text(json.dumps(report,indent=2)+'\n')
print(f"{len(rows)} canonical parts; {len(report['unmapped'])} unmapped")
