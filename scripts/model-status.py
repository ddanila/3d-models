#!/usr/bin/env python3
"""Validate physical-print evidence and rebuild the model status catalogue."""
from pathlib import Path
import hashlib,json
root=Path(__file__).resolve().parents[1]
path=root/'model-status.json'
data=json.loads(path.read_text()) if path.exists() else {'schemaVersion':1,'models':{}}
entries=sorted(set((root/'models').rglob('model.scad'))|set((root/'models').rglob('part-*.scad')))
for p in entries:
 key=str(p.relative_to(root))
 record=data['models'].setdefault(key,{'physicalVerification':'unverified','evidence':[]})
 assert record['physicalVerification'] in ('unverified','printed-and-verified'),key
 if record['physicalVerification']=='printed-and-verified':
  assert record['evidence'],f'{key}: missing physical print/fit evidence'
  for evidence in record['evidence']:
   assert all(evidence.get(k) for k in ['date','verifiedBy','result','files']),key
   for file,digest in evidence['files'].items():
    assert hashlib.sha256((root/file).read_bytes()).hexdigest()==digest,f'{key}: verified artifact changed: {file}; return to unverified until checked'
path.write_text(json.dumps(data,indent=2)+'\n')
lines=['# Physical print verification','', 'This distinction is independent of visual review, render checks and valid STL geometry.', '', '| Model / part | Physical status |','| --- | --- |']
for key,r in data['models'].items():
 label='**Printed and verified**' if r['physicalVerification']=='printed-and-verified' else 'Not physically verified'
 lines.append(f'| [{key.removeprefix("models/")}]({key}) | {label} |')
lines += ['', '“Not physically verified” means no recorded confirmation for this version; it does not claim nobody has printed it.', '', 'To promote a part, record who printed and checked it, the date, fit/function result, and SHA-256 hashes of the exact tested files in `model-status.json`. A changed verified file must be rechecked or returned to unverified. Sibling parts do not inherit verification.', '', 'Run `python3 scripts/model-status.py` after adding models or recording evidence. CAD remains canonical; downstream museum exports carry this status rather than inventing their own.', '']
(root/'MODEL-STATUS.md').write_text('\n'.join(lines))
print(f'Validated {len(data["models"])} model/part records')
