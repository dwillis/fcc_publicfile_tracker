#!/usr/bin/env python3
"""
Create optimized JSON for heatmap with only necessary fields.
This reduces file size for GitHub Pages deployment.
"""
import json

def create_minimal_json():
    print('Loading radio_ads_standardized.json...')
    with open('radio_ads_standardized.json', 'r') as f:
        data = json.load(f)

    print(f'Loaded {len(data):,} records')

    # Fields actually used by heatmap.html:
    # - record_type (filter for political_ad/political_matters)
    # - station (Y-axis labels, filtering)
    # - sponsor_normalized (X-axis labels, filtering, grouping)
    # - office (filter dropdown)
    # - year (filter dropdown)
    # - state (filter dropdown, location display)
    # - city (location display)
    # - updated (date range statistics)

    minimal_data = []
    for record in data:
        minimal = {
            'record_type': record.get('record_type'),
            'station': record.get('station'),
            'sponsor_normalized': record.get('sponsor_normalized'),
            'office': record.get('office'),
            'year': record.get('year'),
            'state': record.get('state'),
            'city': record.get('city'),
            'updated': record.get('updated')
        }
        minimal_data.append(minimal)

    print('Saving optimized version...')
    with open('radio_ads_heatmap.json', 'w') as f:
        json.dump(minimal_data, f, separators=(',', ':'))  # Compact JSON (no spaces)

    # Get file sizes
    import os
    original_size = os.path.getsize('radio_ads_standardized.json')
    minimal_size = os.path.getsize('radio_ads_heatmap.json')

    print()
    print('=' * 80)
    print('OPTIMIZATION COMPLETE')
    print('=' * 80)
    print()
    print(f'Original file:  {original_size:,} bytes ({original_size / 1024 / 1024:.2f} MB)')
    print(f'Optimized file: {minimal_size:,} bytes ({minimal_size / 1024 / 1024:.2f} MB)')
    print(f'Reduction:      {original_size - minimal_size:,} bytes ({(1 - minimal_size/original_size)*100:.1f}%)')
    print()
    print('Removed fields:')
    print('  - id (not used by heatmap)')
    print('  - title (not used by heatmap)')
    print('  - url (PDF links - not currently used)')
    print('  - facility_id (not used by heatmap)')
    print('  - sponsor (original - heatmap uses sponsor_normalized)')
    print('  - file_path (not used by heatmap)')
    print('  - station_url (not used by heatmap)')
    print()
    print('Kept fields (all used by heatmap):')
    print('  - record_type (filtering)')
    print('  - station (display, filtering)')
    print('  - sponsor_normalized (display, filtering, grouping)')
    print('  - office (filtering)')
    print('  - year (filtering)')
    print('  - state (filtering, location display)')
    print('  - city (location display)')
    print('  - updated (date range stats)')
    print()
    print('Output: radio_ads_heatmap.json')
    print('=' * 80)

if __name__ == '__main__':
    create_minimal_json()
