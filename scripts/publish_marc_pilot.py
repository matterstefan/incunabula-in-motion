#!/usr/bin/env python3
"""Copy the prepared MARC pilot into the static map data directories (offline)."""
from pathlib import Path
import json, shutil
root=Path(__file__).resolve().parents[1]
source=root/'data/research/zurich-postincunabula-export-20261023/route-pilot-geocoded.json'
routes=json.loads(source.read_text(encoding='utf-8'))
ids=[r['reference_id'] for r in routes]
assert len(set(ids))==len(ids), 'Duplicate MARC reference IDs'
assert all(i.startswith('marc:') for i in ids)
for route in routes:
    assert len(route['stations'])==3
    for station in route['stations']:
        assert -90<=station['coordinates']['latitude']<=90
        assert -180<=station['coordinates']['longitude']<=180
for folder in [root/'data/map',root/'dist/data/map']:
    folder.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(source,folder/'marc-pilot.json')
print(f'Published {len(routes)} prepared MARC references. No catalogue requests made.')
