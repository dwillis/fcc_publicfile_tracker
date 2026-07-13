#!/usr/bin/env python3
"""Build docs/data/*.json for the exploratory frontend from data/raw/*.jsonl.

Replaces the old tag_and_clean_data.py -> standardize_sponsors.py ->
create_minimal_json.py chain with a single pass: read every raw filing,
classify it by its FCC public-file folder path, normalize the sponsor name,
and write one compact JSON shard per filing year plus a manifest.
"""
import glob
import json
import os
import re
from collections import defaultdict
from datetime import datetime, timezone

from sponsors import standardize_sponsor_advanced, standardize_sponsor_basic

RAW_DIR = 'data/raw'
OUT_DIR = 'docs/data'
COLS = ['date', 'station', 'state', 'city', 'office', 'sponsor', 'type', 'path', 'service']

# The office categories categorize_record() actually recognizes. Filed paths that
# don't match one of the known shapes still get *some* office value (the fallback
# guesses a folder name), but those are noise, not real categories -- so the
# office filter offered to users is capped to this known set.
OFFICE_CATEGORIES = {
    'US House', 'US Senate', 'President', 'Federal', 'State', 'Local',
    'Non-Candidate Issue Ads', 'Political Matters',
}


def extract_station_and_service(record):
    """Pull the AM/FM service and call sign out of the record's profile URLs.

    The service ('am' or 'fm') is what lets the frontend link to the station's
    public file on the FCC site (/{service}-profile/{call sign}/...), since the
    FCC blocks direct links to individual PDFs.
    """
    for value in (record.get('id'), record.get('station_url'), record.get('url')):
        if not value:
            continue
        match = re.search(r'/(am|fm)-profile/([A-Z0-9-]+)/', value)
        if match:
            return match.group(2), match.group(1)
    return None, None


def categorize_record(title):
    """Classify a filing from the FCC public-file folder path embedded in its RSS title."""
    if ' in ' not in title:
        return 'unknown', None, None, None

    path = title.split(' in ')[1].split(' on ')[0]

    if path.startswith('Political Matters and Controversial Issues Disclosures'):
        segments = [s for s in path.replace(
            'Political Matters and Controversial Issues Disclosures/', ''
        ).split('/') if s]
        if segments and segments[0].isdigit() and len(segments[0]) == 4:
            segments = segments[1:]
        sponsor = segments[-1] if segments else None
        return 'political_matters', path, 'Political Matters', sponsor

    if path.startswith('Political Files/'):
        segments = path.replace('Political Files/', '').split('/')
        if segments and segments[0].isdigit() and len(segments[0]) == 4:
            segments = segments[1:]

        federal_offices = ['US House', 'US Senate', 'President']
        category_values = ['Federal', 'State', 'Local', 'Non-Candidate Issue Ads']
        office = sponsor = None

        if len(segments) == 1:
            office = segments[0]
        elif len(segments) == 2:
            if segments[0] in category_values:
                if segments[1] in federal_offices or segments[1] in category_values:
                    office = segments[1]
                else:
                    office, sponsor = segments[0], segments[1]
            else:
                office, sponsor = segments[0], segments[1]
        elif len(segments) >= 3:
            if segments[0] in category_values:
                office, sponsor = segments[1], segments[2]
            else:
                office, sponsor = segments[-2], segments[-1]

        return 'political_ad', path, office, sponsor

    return 'non_political', path, None, None


def normalize_sponsor(sponsor, record_type):
    if not sponsor:
        return None
    if record_type in ('political_ad', 'political_matters'):
        return standardize_sponsor_advanced(sponsor)
    return standardize_sponsor_basic(sponsor) or sponsor


def load_raw_records():
    for path in sorted(glob.glob(os.path.join(RAW_DIR, '*.jsonl'))):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line:
                    yield json.loads(line)


def build():
    by_year = defaultdict(list)
    states = set()
    offices = set()

    for record in load_raw_records():
        title = record.get('title', '')
        updated = record.get('updated')
        if not updated:
            continue

        record_type, path, office, sponsor = categorize_record(title)
        extracted_station, service = extract_station_and_service(record)
        station = record.get('station') or extracted_station
        sponsor_normalized = normalize_sponsor(sponsor, record_type)
        state = record.get('state')
        city = record.get('city')

        if office in OFFICE_CATEGORIES:
            offices.add(office)
        if state:
            states.add(state)

        row = [
            updated[:10],
            station,
            state,
            city,
            office,
            sponsor_normalized,
            record_type,
            path,
            service,
        ]
        by_year[updated[:4]].append(row)

    os.makedirs(OUT_DIR, exist_ok=True)

    years_summary = []
    for year, rows in sorted(by_year.items()):
        rows.sort(key=lambda r: r[0])
        with open(os.path.join(OUT_DIR, f'filings-{year}.json'), 'w') as f:
            json.dump({'cols': COLS, 'rows': rows}, f, separators=(',', ':'))
        years_summary.append({'year': year, 'rows': len(rows)})
        print(f'  filings-{year}.json: {len(rows):,} rows')

    manifest = {
        'generated': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'total': sum(y['rows'] for y in years_summary),
        'years': years_summary,
        'states': sorted(states),
        'offices': sorted(offices),
    }
    with open(os.path.join(OUT_DIR, 'manifest.json'), 'w') as f:
        json.dump(manifest, f, indent=2)

    print(f"Total: {manifest['total']:,} records across {len(years_summary)} years")


if __name__ == '__main__':
    build()
