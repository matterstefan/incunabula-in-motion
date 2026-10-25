#!/usr/bin/env python3
"""Checkpointed Swisscollections SRU harvest; no biographical enrichment."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

ENDPOINT = 'https://sru.swisscollections.ch/swisscollections'
NS = {'s': 'http://www.loc.gov/zing/srw/', 'm': 'http://www.loc.gov/MARC21/slim'}
CODES = {f'Z{i:02d}' for i in range(1, 7)}
ROOT = Path(__file__).resolve().parents[1]

def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_bytes(data)
    tmp.replace(path)

def save(path, value):
    write(path, (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode())

def query_for(start, end):
    scope = ' OR '.join(f'sc.possessingInstitution = {c}' for c in sorted(CODES))
    return f'({scope}) AND dc.date >= {start} AND dc.date <= {end}'

def parse_page(raw):
    tree = ET.fromstring(raw)
    diagnostics = tree.findall('.//{http://www.loc.gov/zing/srw/diagnostic/}diagnostic')
    if diagnostics:
        raise ValueError('SRU diagnostic: ' + ' '.join(diagnostics[0].itertext()))
    total = tree.find('s:numberOfRecords', NS)
    if total is None:
        raise ValueError('Response lacks SRU numberOfRecords')
    records = tree.findall('s:records/s:record/s:recordData/m:record', NS)
    wrappers = tree.findall('s:records/s:record', NS)
    if len(wrappers) != len(records):
        raise ValueError('Response contains non-MARC records')
    return int(total.text), records

def rid(record):
    value = record.findtext("m:controlfield[@tag='001']", namespaces=NS)
    if not value:
        raise ValueError('MARC record without 001')
    return value

def vals(field, code):
    return [s.text or '' for s in field if s.get('code') == code]

def profile(records, start, end):
    counts = Counter(); rows = []
    for record in records:
        fs = record.findall('m:datafield', NS)
        refs = sorted({(b, j) for f in fs if f.get('tag') == '852'
                       for b in vals(f, 'b') if b in CODES for j in vals(f, 'j') if j.strip()})
        public = [f for f in fs if not (f.get('tag') in {'361', '541', '561'} and f.get('ind1') == '0')]
        owners = [f for f in public if f.get('tag') in {'700', '710', '711'} and
                  ('fmo' in vals(f, '4') or any(re.search(r'vorbesitzer|former owner|eigentümer', x, re.I) for x in vals(f, 'e')))]
        evidence = [f for f in public if f.get('tag') in {'361', '561'} or f in owners]
        date = record.findtext("m:controlfield[@tag='008']", default='', namespaces=NS)
        leader = record.findtext('m:leader', default='', namespaces=NS)
        flags = []
        if any((f.text or '').startswith('h') for f in record.findall("m:controlfield[@tag='007']", NS)) or date[23:24] in {'a', 'b', 'c'}:
            flags.append('microform_encoding')
        if date[6:7] == 'r':
            flags.append('reproduction_date_type')
        if not (date[7:11].isdigit() and start <= int(date[7:11]) <= end):
            flags.append('008_first_date_outside_or_uncertain')
        if leader[6:7] != 'a':
            flags.append('not_coded_language_material')
        if not refs:
            flags.append('no_ZB_852_shelfmark')
        tagged = {f.get('tag') for f in public}
        counts['records'] += 1
        counts['catalogue_references'] += len(refs)
        counts['records_with_core_provenance'] += bool(evidence)
        counts['references_in_records_with_core_provenance'] += len(refs) if evidence else 0
        counts['records_with_former_owner'] += bool(owners)
        counts['records_with_owner_authority'] += any(vals(f, '0') or vals(f, '1') for f in owners)
        for tag in ['361', '541', '561', '563', '590']:
            counts['records_with_' + tag] += tag in tagged
        for flag in flags:
            counts['records_flagged_' + flag] += 1
        # Keep all relevant fields with scope indicators for a subsequent copy-level audit.
        fields = [f for f in public if f.get('tag') in {'260', '264', '500', '541', '561', '361', '563', '590', '596', '852', '949'} or f in owners]
        rows.append({'record_id': rid(record), 'title': [v for f in fs if f.get('tag') == '245' for v in vals(f, 'a')],
                     'references': [{'institution_code': b, 'shelfmark': j} for b, j in refs],
                     'review_flags': flags, 'date_008': date[6:15],
                     'fields': [{'tag': f.get('tag'), 'ind1': f.get('ind1'), 'ind2': f.get('ind2'),
                                 'subfields': [(s.get('code'), s.text or '') for s in f]} for f in fields]})
    return dict(counts), rows

def harvest(out, query, fetch):
    records = {}; pages = []; position = 1; expected = None
    while expected is None or position <= expected:
        path = out / 'pages' / f'{position:07d}.xml'
        url = ENDPOINT + '?' + urlencode(dict(version='1.2', operation='searchRetrieve', query=query,
                    recordSchema='marc21-xml', maximumRecords=100, startRecord=position))
        cached = path.exists()
        raw = path.read_bytes() if cached else fetch(url)
        total, batch = parse_page(raw)
        if total > 50000:
            raise ValueError('More than 50,000 results: run a shorter date interval.')
        if expected is not None and expected != total:
            raise ValueError('SRU hit count changed; start a new snapshot label to avoid mixing results.')
        expected = total
        if not batch and position <= total:
            raise ValueError(f'Empty page at {position}/{total}')
        for record in batch:
            key = rid(record)
            if key in records:
                raise ValueError('Duplicate MARC 001 across pages: ' + key + '; restart with new snapshot label.')
            records[key] = record
        if len(records) > total:
            raise ValueError('Returned more records than reported')
        if not cached:
            write(path, raw)
        pages.append({'start_record': position, 'count': len(batch), 'reported_total': total,
                      'url': url, 'sha256': hashlib.sha256(raw).hexdigest()})
        save(out / 'progress.json', {'complete': False, 'records_read': len(records), 'reported_total': total, 'pages': pages})
        print(f'{len(records)}/{total} records', flush=True)
        position += len(batch)
        if total == 0:
            break
    if len(records) != expected:
        raise ValueError('Final count mismatch')
    return list(records.values()), pages

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--start', type=int, default=1526)
    p.add_argument('--end', type=int, default=1550)
    p.add_argument('--snapshot', default='20261025')
    p.add_argument('--output', type=Path)
    a = p.parse_args()
    if not (1450 <= a.start <= a.end <= 1900) or not re.fullmatch(r'[A-Za-z0-9_-]{1,40}', a.snapshot):
        p.error('Use years 1450–1900 and a simple snapshot label (letters, numbers, hyphen, underscore).')
    out = a.output or ROOT / f'data/research/zurich-tranches/{a.start}-{a.end}-{a.snapshot}'
    out.mkdir(parents=True, exist_ok=True)
    query = query_for(a.start, a.end)
    config = {'query': query, 'endpoint': ENDPOINT, 'schema': 'marc21-xml', 'page_size': 100, 'version': 1}
    manifest = out / 'request.json'
    if manifest.exists() and json.loads(manifest.read_text()) != config:
        raise ValueError('Checkpoint configuration mismatch')
    save(manifest, config)
    # One request at a time, including retries; minimum two seconds between starts.
    last = [0.0]
    def fetch(url):
        for attempt in range(4):
            time.sleep(max(0, 2 - (time.monotonic() - last[0])))
            last[0] = time.monotonic()
            try:
                with urlopen(Request(url, headers={'User-Agent': 'Incunabula-in-Motion research harvest', 'Accept': 'application/xml'}), timeout=90) as response:
                    raw = response.read()
                parse_page(raw)
                return raw
            except Exception:
                if attempt == 3:
                    raise
                time.sleep(5 * (attempt + 1))
    try:
        records, pages = harvest(out, query, fetch)
        counts, rows = profile(records, a.start, a.end)
        save(out / 'record-profile.json', rows)
        save(out / 'summary.json', {'complete': True, 'compiled_at': datetime.now(timezone.utc).isoformat(),
            'query': query, 'counts': counts, 'pages': pages, 'limitations': [
                'Index-selected records, not a verified census of original printed copies.',
                'References are MARC 001 + institution + shelfmark, not verified physical volumes.',
                'Provenance counts concern records; fields are not yet assigned to individual references.',
                'No owner biographies, manual collection rules or inferred historical locations applied.',
                'Flags are retained for review, not automatic exclusions. Adjacent tranches may overlap.',
                'Cached SRU pages are not an atomic catalogue snapshot; changes with stable totals may be undetected.',
                'Public endpoint raw pages retained; private-indicator 361/541/561 excluded from derived profile.'
            ]})
        save(out / 'progress.json', {'complete': True, 'records_read': len(records), 'pages': pages})
        print(json.dumps(counts, indent=2))
    except Exception as exc:
        save(out / 'failure.json', {'error': str(exc), 'complete': False})
        raise
    else:
        (out / 'failure.json').unlink(missing_ok=True)

if __name__ == '__main__':
    main()
