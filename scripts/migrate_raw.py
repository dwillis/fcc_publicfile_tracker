#!/usr/bin/env python3
"""One-time migration: radio_ads.json -> data/raw/YYYY.jsonl.

Splits the old monolithic (and pretty-printed) raw archive into compact,
append-friendly JSONL shards by filing year, dropping the office/sponsor/
facility_id fields that build_site.py re-derives from the title anyway.
Run once, then delete radio_ads.json.
"""
import json
import os
from collections import defaultdict

SOURCE = 'radio_ads.json'
RAW_DIR = 'data/raw'
KEEP_FIELDS = ('id', 'title', 'url', 'updated', 'station', 'station_url', 'state', 'city')


def slim(record):
    return {k: record[k] for k in KEEP_FIELDS if record.get(k)}


def migrate():
    with open(SOURCE) as f:
        data = json.load(f)

    by_year = defaultdict(list)
    for record in data:
        updated = record.get('updated')
        year = updated[:4] if updated else 'unknown'
        by_year[year].append(slim(record))

    os.makedirs(RAW_DIR, exist_ok=True)
    total = 0
    for year, records in sorted(by_year.items()):
        records.sort(key=lambda r: r.get('updated', ''))
        path = os.path.join(RAW_DIR, f'{year}.jsonl')
        with open(path, 'w') as f:
            for record in records:
                f.write(json.dumps(record, separators=(',', ':')) + '\n')
        total += len(records)
        print(f'  {year}.jsonl: {len(records):,} records')

    print(f'Migrated {total:,} of {len(data):,} source records')
    assert total == len(data), 'record count mismatch during migration'


if __name__ == '__main__':
    migrate()
