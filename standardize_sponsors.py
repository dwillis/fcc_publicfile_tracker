#!/usr/bin/env python3
"""
Advanced sponsor name standardization with semantic matching.

This version handles:
1. Capitalization variations
2. Invoice/filing numbers appended to names
3. Separator variations (D, -D-, for)
4. Semantic duplicates (Harris vs Kamala Harris, Biden vs Joe Biden)
5. Common candidate variations
"""
import json
import re
from collections import defaultdict

# Canonical names for major political figures
CANONICAL_NAMES = {
    # Presidential campaigns 2020-2024
    'kamala harris': {
        'canonical': 'Kamala Harris for President',
        'patterns': [
            r'^kamala\s+harris\s+for\s+president',
            r'^harris\s+for\s+president',
            r'^kamala\s+harris\s+d\s+president',
            r'^harris\s+d\s+president',
            r'^harris-d-president',
            r'^kamala\s+harris$',
        ]
    },
    'joe biden': {
        'canonical': 'Joe Biden for President',
        'patterns': [
            r'^joe\s+biden\s+for\s+president',
            r'^biden\s+for\s+president',
            r'^joseph\s+biden\s+for\s+president',
            r'^joe\s+biden$',
            r'^joseph\s+biden$',
            r'^biden$',
        ]
    },
    'donald trump': {
        'canonical': 'Donald Trump for President',
        'patterns': [
            r'^donald\s+trump\s+for\s+president',
            r'^donald\s+j\.?\s+trump\s+for\s+president',
            r'^trump\s+for\s+president',
            r'^donald\s+trump$',
            r'^donald\s+j\.?\s+trump$',
        ]
    },
    'bernie sanders': {
        'canonical': 'Bernie Sanders for President',
        'patterns': [
            r'^bernie\s+sanders\s+for\s+president',
            r'^sanders\s+for\s+president',
            r'^bernie\s+sanders$',
        ]
    },
}

def clean_sponsor_name(sponsor):
    """
    Clean a sponsor name by removing invoice numbers, dates, and other noise.
    """
    if not sponsor:
        return None

    # Remove common noise patterns at the end
    # Remove trailing invoice/order numbers and dates
    cleaned = re.sub(r'\s+\d{5,}[\s\-\d]*$', '', sponsor)  # Remove trailing numbers (5+ digits)
    cleaned = re.sub(r'\s+\d{1,2}[-/]\d{1,2}[-/]\d{2,4}$', '', cleaned)  # Remove dates
    cleaned = re.sub(r'\s+\d{6,8}$', '', cleaned)  # Remove date-like numbers (MMDDYYYY)
    cleaned = re.sub(r'\s+-\s+\d+.*$', '', cleaned)  # Remove " - 123456..." patterns

    # Remove "Premier Network" prefix (radio network, not the sponsor)
    cleaned = re.sub(r'^premier\s+network\s+', '', cleaned, flags=re.IGNORECASE)

    # Clean up whitespace
    cleaned = ' '.join(cleaned.split())

    return cleaned.strip()

def match_canonical_name(sponsor):
    """
    Check if a sponsor matches a known canonical pattern.
    Returns canonical name if match found, otherwise None.
    """
    if not sponsor:
        return None

    sponsor_lower = sponsor.lower().strip()

    # Try to match against canonical patterns
    for key, config in CANONICAL_NAMES.items():
        for pattern in config['patterns']:
            if re.match(pattern, sponsor_lower):
                return config['canonical']

    return None

def standardize_sponsor_basic(sponsor):
    """
    Basic standardization: capitalization and common patterns.
    """
    if not sponsor or sponsor.strip() == '':
        return None

    # Common acronyms that should stay uppercase
    acronyms = {
        'PAC', 'INC', 'LLC', 'USA', 'US', 'MAGA', 'NAACP', 'DNC', 'RNC',
        'GOP', 'FEC', 'EEO', 'NC', 'DC', 'LA', 'NY', 'CA', 'TX', 'FL',
        'VA', 'MD', 'GA', 'MI', 'OH', 'PA', 'AZ', 'NV', 'WI', 'MN',
        'CO', 'OR', 'WA', 'MA', 'NJ', 'CT', 'IL', 'TN', 'SC',
        'ACTUM', 'YES', 'NO', 'PROP', 'DA', 'CEO', 'CFO', 'VP', 'AG',
        'HD', 'FM', 'AM', 'TV', 'WLLD', 'KLCA', 'FF', 'AI', 'IT', 'II', 'III'
    }

    lowercase_words = {
        'for', 'of', 'the', 'and', 'or', 'in', 'on', 'at', 'to', 'a', 'an',
        'as', 'but', 'by', 'nor', 'so', 'yet', 'vs', 'v'
    }

    words = sponsor.split()
    standardized = []

    for i, word in enumerate(words):
        word_upper = word.upper().strip('.,!?;:')

        if word_upper in acronyms:
            standardized.append(word_upper)
        elif i > 0 and word.lower() in lowercase_words:
            standardized.append(word.lower())
        elif word.upper() == word and len(word) > 1:
            standardized.append(word.title())
        else:
            standardized.append(word.title())

    result = ' '.join(standardized)

    # Special fixes
    result = re.sub(r'\bFor (President|Senate|Congress|Governor|Mayor|Council)\b',
                    r'for \1', result)
    result = re.sub(r'\bOf\b', 'of', result)
    result = re.sub(r'(?<!^)\bThe\b', 'the', result)
    result = result.replace(' Pac', ' PAC')
    result = result.replace(' Inc', ' INC')
    result = result.replace(' Llc', ' LLC')

    return result

def standardize_sponsor_advanced(sponsor):
    """
    Advanced standardization with semantic matching.
    """
    if not sponsor:
        return None

    # Step 1: Clean the sponsor name
    cleaned = clean_sponsor_name(sponsor)
    if not cleaned:
        return None

    # Step 2: Check for canonical name matches
    canonical = match_canonical_name(cleaned)
    if canonical:
        return canonical

    # Step 3: Apply basic standardization
    standardized = standardize_sponsor_basic(cleaned)

    return standardized

def create_advanced_mapping(data):
    """
    Create mapping with advanced standardization.
    """
    political_records = [d for d in data
        if (d['record_type'] in ['political_ad', 'political_matters'])
        and d.get('sponsor')
        and 'Entity' not in d.get('sponsor', '')
        and d.get('sponsor') != d.get('office')]

    # Create mapping
    mapping = {}
    for record in political_records:
        original = record['sponsor']
        if original not in mapping:
            standardized = standardize_sponsor_advanced(original)
            if standardized:
                mapping[original] = standardized

    # Generate statistics
    original_count = len(set(mapping.keys()))
    standardized_count = len(set(mapping.values()))
    merged_count = original_count - standardized_count

    # Find variations
    reverse_mapping = defaultdict(list)
    sponsor_counts = defaultdict(int)

    for record in political_records:
        sponsor = record['sponsor']
        sponsor_counts[sponsor] += 1

    for original, standardized in mapping.items():
        reverse_mapping[standardized].append((original, sponsor_counts[original]))

    variations_report = []
    for standardized, originals in reverse_mapping.items():
        if len(originals) > 1:
            total = sum(count for _, count in originals)
            variations_report.append({
                'standardized': standardized,
                'variations': originals,
                'total': total
            })

    variations_report.sort(key=lambda x: -x['total'])

    stats = {
        'original_count': original_count,
        'standardized_count': standardized_count,
        'merged_count': merged_count
    }

    return mapping, variations_report, stats

def apply_advanced_standardization(data, mapping):
    """
    Apply advanced standardization to all records.
    """
    standardized_data = []

    for record in data:
        new_record = record.copy()
        sponsor = record.get('sponsor')

        if sponsor and sponsor in mapping:
            new_record['sponsor_normalized'] = mapping[sponsor]
        elif sponsor:
            # Fallback to basic standardization for non-political sponsors
            new_record['sponsor_normalized'] = standardize_sponsor_basic(sponsor) or sponsor
        else:
            new_record['sponsor_normalized'] = None

        standardized_data.append(new_record)

    return standardized_data

def main():
    print('Loading data...')
    with open('radio_ads_tagged.json', 'r') as f:
        data = json.load(f)

    print(f'Loaded {len(data):,} records\n')

    print('Analyzing sponsor variations with advanced matching...')
    mapping, variations_report, stats = create_advanced_mapping(data)

    print(f'Original unique sponsors: {stats["original_count"]:,}')
    print(f'Standardized unique sponsors: {stats["standardized_count"]:,}')
    print(f'Sponsors merged: {stats["merged_count"]:,}\n')

    print('Applying advanced standardization...')
    standardized_data = apply_advanced_standardization(data, mapping)

    # Save files
    print('Saving standardized data...')
    with open('radio_ads_standardized.json', 'w') as f:
        json.dump(standardized_data, f, indent=2)

    with open('sponsor_mapping.json', 'w') as f:
        json.dump(mapping, f, indent=2, sort_keys=True)

    # Generate report
    print('Generating report...')
    report_lines = []
    report_lines.append('=' * 80)
    report_lines.append('ADVANCED SPONSOR STANDARDIZATION REPORT')
    report_lines.append('=' * 80)
    report_lines.append('')
    report_lines.append(f'Original unique sponsors: {stats["original_count"]:,}')
    report_lines.append(f'Standardized unique sponsors: {stats["standardized_count"]:,}')
    report_lines.append(f'Sponsors merged: {stats["merged_count"]:,}')
    report_lines.append(f'Reduction: {(stats["merged_count"]/stats["original_count"]*100):.1f}%')
    report_lines.append('')
    report_lines.append('=' * 80)
    report_lines.append('TOP MERGED SPONSORS')
    report_lines.append('=' * 80)
    report_lines.append('')

    for i, item in enumerate(variations_report[:100], 1):
        report_lines.append(f'{i}. {item["standardized"]} ({item["total"]:,} ads total)')
        sorted_variations = sorted(item['variations'], key=lambda x: -x[1])
        for original, count in sorted_variations[:15]:  # Show top 15 variations
            if original == item['standardized']:
                report_lines.append(f'   → "{original}" ({count:,} ads) [CANONICAL]')
            else:
                report_lines.append(f'   - "{original}" ({count:,} ads)')
        if len(item['variations']) > 15:
            report_lines.append(f'   ... and {len(item["variations"]) - 15} more variations')
        report_lines.append('')

    with open('sponsor_standardization_report.txt', 'w') as f:
        f.write('\n'.join(report_lines))

    # Print summary
    print()
    print('=' * 80)
    print('ADVANCED STANDARDIZATION COMPLETE')
    print('=' * 80)
    print()
    print(f'Original unique sponsors: {stats["original_count"]:,}')
    print(f'Standardized unique sponsors: {stats["standardized_count"]:,}')
    print(f'Sponsors merged: {stats["merged_count"]:,}')
    print(f'Reduction: {(stats["merged_count"]/stats["original_count"]*100):.1f}%')
    print()
    print('Files updated:')
    print('  - radio_ads_standardized.json')
    print('  - sponsor_mapping.json')
    print('  - sponsor_standardization_report.txt')
    print('=' * 80)

    # Show key examples
    print()
    print('KEY STANDARDIZATIONS:')
    print('-' * 80)

    # Find Harris variations
    harris_examples = [(k, v) for k, v in mapping.items() if 'harris' in k.lower() and 'president' in k.lower()]
    if harris_examples:
        print('\nHarris Presidential campaign variations:')
        for orig, std in sorted(set(harris_examples), key=lambda x: x[0])[:10]:
            print(f'  "{orig}" → "{std}"')

    # Find Biden variations
    biden_examples = [(k, v) for k, v in mapping.items() if 'biden' in k.lower() and 'president' in k.lower()]
    if biden_examples:
        print('\nBiden Presidential campaign variations:')
        for orig, std in sorted(set(biden_examples), key=lambda x: x[0])[:10]:
            print(f'  "{orig}" → "{std}"')

if __name__ == '__main__':
    main()
