"""Bind reviewed routing claims to exact native geometry and pinned sources."""
import hashlib
import json


def geometry_sha(item):
    # Exclude annotations; moving, resizing, flipping or renetting invalidates review.
    fields = ('id', 'points', 'width', 'side', 'position', 'diameter', 'drill', 'net')
    def normalized(value):
        if isinstance(value, (int, float)):
            return float(value) if value else 0.0
        if isinstance(value, list):
            return [normalized(v) for v in value]
        return value
    geometry = {key: normalized(item[key]) for key in fields if key in item}
    return hashlib.sha256(json.dumps(geometry, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def annotate(routes, vias, ledger, evidence):
    if ledger.get('schema') != 1:
        raise ValueError('Unsupported route evidence schema')
    sources = {source['id']: source for source in evidence['sources']}
    records = ledger['items']
    items = routes + vias
    ids = [item['id'] for item in items]
    if len(set(ids)) != len(ids):
        raise ValueError('Duplicate copper UUID')
    if set(records) != set(ids):
        raise ValueError('Route evidence must cover exactly the native copper UUIDs')
    for item in items:
        record = records[item['id']]
        if record.get('status') not in ('observed', 'inferred', 'unresolved'):
            raise ValueError('Invalid route evidence status')
        if record.get('geometrySha256') != geometry_sha(item):
            raise ValueError('Route geometry changed since evidence review: ' + item['id'])
        if not isinstance(record.get('detail'), str) or not record['detail'].strip():
            raise ValueError('Route evidence requires a review explanation')
        citations = record.get('sources', [])
        if not citations:
            raise ValueError('Route evidence requires source references')
        photo_sides = set()
        for citation in citations:
            source = sources.get(citation.get('id'))
            if source is None or citation.get('sha256') != source['sha256']:
                raise ValueError('Unknown or stale route evidence source')
            if not citation.get('locator'):
                raise ValueError('Route evidence requires a source locator')
            if source['id'] in ('photo-top', 'photo-bottom'):
                photo_sides.add(source['id'][6:])
        required = {item['side']} if 'side' in item else {'top', 'bottom'}
        if record['status'] == 'observed' and not required <= photo_sides:
            raise ValueError('Observed copper requires photographs of its board sides')
        item['evidence'] = record
