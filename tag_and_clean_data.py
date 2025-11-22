#!/usr/bin/env python3
"""
Tag and clean radio_ads.json data:
- Add record_type field (political_ad, political_matters, non_political)
- Extract station call signs from URLs
- Add year field
- Fix parsing issues
"""
import json
import re
from urllib.parse import urlparse

def extract_station_from_url(url, entry_id):
    """Extract station call sign from URL or ID"""
    # Try from ID first (more reliable)
    if entry_id:
        match = re.search(r'/(am|fm)-profile/([A-Z0-9-]+)/', entry_id)
        if match:
            return match.group(2)

    # Try from URL
    if url:
        match = re.search(r'/(am|fm)-profile/([A-Z0-9-]+)/', url)
        if match:
            return match.group(2)

    return None

def extract_year_from_path(path):
    """Extract year from file path"""
    # Look for 4-digit year
    match = re.search(r'\b(20[12][0-9])\b', path)
    if match:
        return int(match.group(1))
    return None

def categorize_record(item):
    """Categorize record as political_ad, political_matters, or non_political"""
    title = item.get('title', '')

    if ' in ' not in title:
        return 'unknown', None, None, None

    path = title.split(' in ')[1].split(' on ')[0]

    # Check if it's Political Matters
    if path.startswith('Political Matters and Controversial Issues Disclosures'):
        # Try to extract sponsor/issue from subdirectories
        segments = path.replace('Political Matters and Controversial Issues Disclosures/', '').split('/')
        # Remove empty segments
        segments = [s for s in segments if s]

        office = 'Political Matters'
        sponsor = None

        # Remove year if first segment is a year
        if segments and segments[0].isdigit() and len(segments[0]) == 4:
            segments = segments[1:]

        # Now extract sponsor from remaining segments
        if len(segments) > 0:
            # Last segment is the sponsor/issue organization
            sponsor = segments[-1]

        return 'political_matters', path, office, sponsor

    # Check if it's Political Files
    if path.startswith('Political Files/'):
        # Parse Political Files structure
        segments = path.replace('Political Files/', '').split('/')

        year = None
        office = None
        sponsor = None

        # Try to extract year (usually first segment)
        if segments and segments[0].isdigit() and len(segments[0]) == 4:
            year = int(segments[0])
            segments = segments[1:]

        # Known category/office values
        federal_offices = ['US House', 'US Senate', 'President']
        category_values = ['Federal', 'State', 'Local', 'Non-Candidate Issue Ads']

        # Determine office and sponsor based on remaining segments
        if len(segments) == 0:
            # Just "Political Files/2024"
            office = None
            sponsor = None
        elif len(segments) == 1:
            # "Political Files/2024/Non-Candidate Issue Ads"
            # or "Political Files/Federal"
            # This is the office/category only, no sponsor
            office = segments[0]
            sponsor = None
        elif len(segments) == 2:
            # "Political Files/2024/Federal/US House" -> office=US House, sponsor=None
            # or "Political Files/2024/Local/Candidate Name" -> office=Local, sponsor=Candidate Name
            if segments[0] in category_values:
                # First segment is Federal/State/Local
                if segments[1] in federal_offices or segments[1] in category_values:
                    # Second segment is also a category (US House, US Senate, etc)
                    office = segments[1]
                    sponsor = None
                else:
                    # Second segment is the sponsor
                    office = segments[0]
                    sponsor = segments[1]
            else:
                # First segment is the office, second is sponsor
                office = segments[0]
                sponsor = segments[1]
        elif len(segments) >= 3:
            # "Political Files/2024/Federal/US Senate/Candidate Name"
            if segments[0] in category_values:
                office = segments[1]
                sponsor = segments[2]
            else:
                # Fallback: office is second-to-last, sponsor is last
                office = segments[-2]
                sponsor = segments[-1]

        return 'political_ad', path, office, sponsor

    # Everything else is non-political
    return 'non_political', path, None, None

def clean_data():
    """Clean and tag all records"""
    with open('radio_ads.json', 'r') as f:
        data = json.load(f)

    print(f'Processing {len(data)} records...')

    stats = {
        'political_ad': 0,
        'political_matters': 0,
        'non_political': 0,
        'unknown': 0,
        'station_extracted': 0,
        'year_extracted': 0
    }

    cleaned_data = []

    for item in data:
        # Categorize the record
        record_type, path, office, sponsor = categorize_record(item)
        stats[record_type] += 1

        # Extract station call sign
        station = item.get('station')
        if not station:
            station = extract_station_from_url(item.get('url'), item.get('id'))
            if station:
                stats['station_extracted'] += 1

        # Extract year from path
        year = None
        if path:
            year = extract_year_from_path(path)
            if year:
                stats['year_extracted'] += 1

        # Create cleaned record
        # For political_ad records, use the newly parsed office/sponsor
        # For other types, keep the original values
        if record_type == 'political_ad':
            final_office = office
            final_sponsor = sponsor
        else:
            final_office = office if office is not None else item.get('office')
            final_sponsor = sponsor if sponsor is not None else item.get('sponsor')

        cleaned_record = {
            'id': item.get('id'),
            'title': item.get('title'),
            'url': item.get('url'),
            'updated': item.get('updated'),
            'record_type': record_type,
            'facility_id': item.get('facility_id'),
            'station': station,
            'year': year,
            'office': final_office,
            'sponsor': final_sponsor,
            'file_path': path,
        }

        # Add optional fields if they exist
        if item.get('state'):
            cleaned_record['state'] = item.get('state')
        if item.get('city'):
            cleaned_record['city'] = item.get('city')
        if item.get('station_url'):
            cleaned_record['station_url'] = item.get('station_url')

        cleaned_data.append(cleaned_record)

    # Save cleaned data
    with open('radio_ads_tagged.json', 'w') as f:
        json.dump(cleaned_data, f, indent=2)

    # Print statistics
    print('\n' + '=' * 80)
    print('DATA CLEANING COMPLETE')
    print('=' * 80)
    print(f'\nTotal records: {len(data):,}')
    print(f'\nRecord Types:')
    print(f'  Political Ads (Political Files):              {stats["political_ad"]:6,} ({stats["political_ad"]/len(data)*100:5.1f}%)')
    print(f'  Political Matters & Controversial Issues:     {stats["political_matters"]:6,} ({stats["political_matters"]/len(data)*100:5.1f}%)')
    print(f'  Non-Political (EEO, FCC Admin, etc):          {stats["non_political"]:6,} ({stats["non_political"]/len(data)*100:5.1f}%)')
    print(f'  Unknown/Malformed:                            {stats["unknown"]:6,} ({stats["unknown"]/len(data)*100:5.1f}%)')
    print(f'\nEnhancements:')
    print(f'  Station call signs extracted from URLs:      {stats["station_extracted"]:6,}')
    print(f'  Years extracted from file paths:             {stats["year_extracted"]:6,}')
    print(f'\nOutput:')
    print(f'  Saved to: radio_ads_tagged.json')
    print('=' * 80)

    # Show examples
    print('\nEXAMPLES:')
    print('=' * 80)

    # Show one example of each type
    for rec_type in ['political_ad', 'political_matters', 'non_political']:
        example = next((r for r in cleaned_data if r['record_type'] == rec_type), None)
        if example:
            print(f'\n{rec_type.upper()}:')
            print(f'  Title: {example["title"][:80]}...')
            print(f'  Station: {example.get("station", "N/A")}')
            print(f'  Year: {example.get("year", "N/A")}')
            print(f'  Office: {example.get("office", "N/A")}')
            print(f'  Sponsor: {example.get("sponsor", "N/A")}')
            print(f'  Path: {example.get("file_path", "N/A")[:80]}')

if __name__ == '__main__':
    clean_data()
