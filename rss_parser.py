#!/usr/bin/env python3
"""Fetch each station's FCC public-file RSS feed and append new filings to
data/raw/YYYY.jsonl, deduped by RSS entry id.
"""
import concurrent.futures
import csv
import glob
import json
import os

import feedparser
import requests

CSV_FILE = 'urban_radio_stations_with_status.csv'
RAW_DIR = 'data/raw'
REQUEST_TIMEOUT = 30
MAX_WORKERS = 16


def load_existing_ids():
    ids = set()
    for path in glob.glob(os.path.join(RAW_DIR, '*.jsonl')):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line:
                    ids.add(json.loads(line)['id'])
    return ids


def parse_feed(station_url, state, city):
    """Fetch and parse one station's RSS feed into slim raw records."""
    entries = []
    try:
        response = requests.get(station_url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as exc:
        print(f'  fetch failed for {station_url}: {exc}')
        return entries

    feed = feedparser.parse(response.content)
    for entry in feed.entries:
        try:
            title = entry.title
            if 'Issues and Programs Lists' in title:
                continue
            record = {
                'id': entry.id,
                'title': title,
                'url': entry.link,
                'updated': entry.updated,
                'station_url': station_url,
            }
        except AttributeError:
            continue

        if state:
            record['state'] = state
        if city:
            record['city'] = city
        entries.append(record)

    return entries


def fetch_rss_entries(csv_file):
    existing_ids = load_existing_ids()

    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = [row for row in reader if row.get('FCC URL')]

    new_by_year = {}
    failures = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(parse_feed, row['FCC URL'], row.get('State'), row.get('City')): row['FCC URL']
            for row in rows
        }
        for future in concurrent.futures.as_completed(futures):
            try:
                entries = future.result()
            except Exception as exc:
                failures += 1
                print(f'  error processing {futures[future]}: {exc}')
                continue

            for entry in entries:
                if entry['id'] in existing_ids:
                    continue
                existing_ids.add(entry['id'])
                year = entry['updated'][:4] if entry.get('updated') else 'unknown'
                new_by_year.setdefault(year, []).append(entry)

    os.makedirs(RAW_DIR, exist_ok=True)
    total_new = 0
    for year, entries in sorted(new_by_year.items()):
        path = os.path.join(RAW_DIR, f'{year}.jsonl')
        with open(path, 'a') as f:
            for entry in entries:
                f.write(json.dumps(entry, separators=(',', ':')) + '\n')
        total_new += len(entries)
        print(f'  {year}.jsonl: +{len(entries)} records')

    print(f'Added {total_new} new records ({failures} station fetch failures out of {len(rows)})')


if __name__ == '__main__':
    fetch_rss_entries(CSV_FILE)
