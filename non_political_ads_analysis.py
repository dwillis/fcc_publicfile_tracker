#!/usr/bin/env python3
"""
Analyze and categorize non-political records in radio_ads.json
"""
import json
from collections import defaultdict

def analyze_non_political_ads():
    # Load data
    with open('radio_ads.json', 'r') as f:
        data = json.load(f)

    # Categorize records
    political_ads = []
    non_political = defaultdict(list)
    malformed = []

    for item in data:
        title = item.get('title', '')

        # Extract the file path from title
        if ' in ' in title:
            path = title.split(' in ')[1].split(' on ')[0]

            if path.startswith('Political Files/'):
                political_ads.append(item)
            else:
                # Get the top-level category
                category = path.split('/')[0]
                non_political[category].append(item)
        else:
            malformed.append(item)

    # Generate report
    report = []
    report.append('=' * 80)
    report.append('NON-POLITICAL FILE ANALYSIS')
    report.append('=' * 80)
    report.append('')
    report.append(f'Total records: {len(data):,}')
    report.append(f'Political Files: {len(political_ads):,} ({len(political_ads)/len(data)*100:.1f}%)')
    report.append(f'Non-Political Files: {sum(len(v) for v in non_political.values()):,} ({sum(len(v) for v in non_political.values())/len(data)*100:.1f}%)')
    report.append(f'Malformed titles: {len(malformed):,}')
    report.append('')

    # Sort categories by count
    categories_sorted = sorted(non_political.items(), key=lambda x: -len(x[1]))

    report.append('NON-POLITICAL CATEGORIES:')
    report.append('-' * 80)
    for category, items in categories_sorted:
        report.append(f'{len(items):6,} records - {category}')

    report.append('')
    report.append('=' * 80)
    report.append('DETAILED EXAMPLES')
    report.append('=' * 80)

    # Show examples for each category
    for category, items in categories_sorted:
        report.append('')
        report.append(f'{category} ({len(items):,} records)')
        report.append('-' * 80)

        # Show up to 5 examples
        for item in items[:5]:
            title = item.get('title', '')
            if ' in ' in title:
                path = title.split(' in ')[1].split(' on ')[0]
            else:
                path = 'N/A'

            report.append(f'  Full Path: {path}')
            report.append(f'  Sponsor (parsed): {item.get("sponsor", "N/A")}')
            report.append(f'  Office (parsed): {item.get("office", "N/A")}')
            report.append(f'  Station: {item.get("station", "N/A")}')
            report.append(f'  Updated: {item.get("updated", "N/A")}')
            report.append(f'  URL: {item.get("url", "N/A")}')
            report.append('')

    # Save report
    with open('non_political_ads_report.txt', 'w') as f:
        f.write('\n'.join(report))

    # Create JSON with categorized non-political records
    output = {
        'summary': {
            'total_records': len(data),
            'political_files': len(political_ads),
            'non_political_files': sum(len(v) for v in non_political.values()),
            'malformed': len(malformed)
        },
        'categories': {}
    }

    for category, items in categories_sorted:
        output['categories'][category] = {
            'count': len(items),
            'records': items
        }

    if malformed:
        output['categories']['Malformed Titles'] = {
            'count': len(malformed),
            'records': malformed
        }

    with open('non_political_ads.json', 'w') as f:
        json.dump(output, f, indent=2)

    print('\n'.join(report))
    print('')
    print('=' * 80)
    print(f'Reports saved:')
    print(f'  - non_political_ads_report.txt (detailed text report)')
    print(f'  - non_political_ads.json (structured data)')
    print('=' * 80)

if __name__ == '__main__':
    analyze_non_political_ads()
