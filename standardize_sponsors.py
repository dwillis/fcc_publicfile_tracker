#!/usr/bin/env python3
"""
Standardize sponsor names in radio_ads_tagged.json

This script:
1. Identifies sponsor name variations (capitalization differences)
2. Creates a standardized version of each sponsor name
3. Adds a sponsor_normalized field to each record
4. Generates a mapping file for review
"""
import json
import re
from collections import defaultdict

def standardize_sponsor_name(sponsor):
    """
    Standardize a sponsor name using consistent capitalization rules.

    Rules:
    - Use title case for most words
    - Keep common acronyms in uppercase (PAC, INC, LLC, etc.)
    - Handle "for" specially (lowercase in middle of names)
    - Handle "of" and other small words
    """
    if not sponsor or sponsor.strip() == '':
        return None

    # Common acronyms that should stay uppercase
    acronyms = {
        'PAC', 'INC', 'LLC', 'USA', 'US', 'MAGA', 'NAACP', 'DNC', 'RNC',
        'GOP', 'FEC', 'EEO', 'NC', 'DC', 'LA', 'NY', 'CA', 'TX', 'FL',
        'VA', 'MD', 'GA', 'MI', 'OH', 'PA', 'AZ', 'NV', 'WI', 'MN',
        'CO', 'OR', 'WA', 'MA', 'NJ', 'CT', 'IL', 'TN', 'NC', 'SC',
        'ACTUM', 'YES', 'NO', 'PROP', 'DA', 'CEO', 'CFO', 'VP', 'AG',
        'HD', 'FM', 'AM', 'TV', 'WLLD', 'KLCA', 'FF', 'AI', 'IT'
    }

    # Words that should be lowercase (unless at start)
    lowercase_words = {
        'for', 'of', 'the', 'and', 'or', 'in', 'on', 'at', 'to', 'a', 'an',
        'as', 'but', 'by', 'nor', 'so', 'yet', 'vs', 'v'
    }

    # Split into words
    words = sponsor.split()
    standardized = []

    for i, word in enumerate(words):
        # Check if it's an acronym (all caps in original or known acronym)
        word_upper = word.upper().strip('.,!?;:')

        if word_upper in acronyms:
            # Keep as acronym
            standardized.append(word_upper)
        elif i > 0 and word.lower() in lowercase_words:
            # Lowercase for small words (but not at start)
            standardized.append(word.lower())
        elif word.upper() == word and len(word) > 1:
            # If entirely uppercase in original, convert to title case
            # unless it's a known acronym
            standardized.append(word.title())
        else:
            # Use title case
            standardized.append(word.title())

    result = ' '.join(standardized)

    # Special fixes
    # Fix "For President" -> "for President" (middle of name)
    result = re.sub(r'\bFor (President|Senate|Congress|Governor|Mayor|Council)\b',
                    r'for \1', result)

    # Fix "Of" -> "of" (middle of name)
    result = re.sub(r'\bOf\b', 'of', result)

    # Fix "The" -> "the" (middle of name)
    result = re.sub(r'(?<!^)\bThe\b', 'the', result)

    # Fix common patterns
    result = result.replace(' Pac', ' PAC')
    result = result.replace(' Inc', ' INC')
    result = result.replace(' Llc', ' LLC')

    return result

def create_standardization_mapping(data):
    """
    Create a mapping of original sponsors to standardized versions.
    """
    # Get all political records with sponsors
    political_records = [d for d in data
        if (d['record_type'] in ['political_ad', 'political_matters'])
        and d.get('sponsor')
        and 'Entity' not in d.get('sponsor', '')
        and d.get('sponsor') != d.get('office')]

    # Group by normalized lowercase version
    sponsor_groups = defaultdict(set)
    for record in political_records:
        sponsor = record['sponsor']
        normalized_key = sponsor.lower().strip()
        sponsor_groups[normalized_key].add(sponsor)

    # Create mapping: all variations -> standardized version
    mapping = {}
    variations_report = []

    for normalized_key, variations in sponsor_groups.items():
        # Pick the standardized form
        # Use the most common variation as base, then apply standardization
        variation_counts = defaultdict(int)
        for record in political_records:
            if record['sponsor'].lower().strip() == normalized_key:
                variation_counts[record['sponsor']] += 1

        # Get most common form
        most_common = max(variation_counts.items(), key=lambda x: x[1])[0]

        # Standardize it
        standardized = standardize_sponsor_name(most_common)

        # Map all variations to this standardized form
        for variation in variations:
            mapping[variation] = standardized

        # Track variations for report
        if len(variations) > 1:
            total_count = sum(variation_counts.values())
            variations_report.append({
                'standardized': standardized,
                'variations': sorted(variations),
                'counts': dict(variation_counts),
                'total': total_count
            })

    # Sort report by total count
    variations_report.sort(key=lambda x: -x['total'])

    return mapping, variations_report

def apply_standardization(data, mapping):
    """
    Apply sponsor standardization to all records.
    """
    standardized_data = []
    stats = {
        'total_records': len(data),
        'records_with_sponsors': 0,
        'sponsors_standardized': 0,
        'sponsors_unchanged': 0
    }

    for record in data:
        new_record = record.copy()
        sponsor = record.get('sponsor')

        if sponsor:
            stats['records_with_sponsors'] += 1

            if sponsor in mapping:
                standardized = mapping[sponsor]
                new_record['sponsor_normalized'] = standardized

                if standardized != sponsor:
                    stats['sponsors_standardized'] += 1
                else:
                    stats['sponsors_unchanged'] += 1
            else:
                # No mapping (non-political or filtered out)
                new_record['sponsor_normalized'] = sponsor
                stats['sponsors_unchanged'] += 1
        else:
            new_record['sponsor_normalized'] = None

        standardized_data.append(new_record)

    return standardized_data, stats

def main():
    print('Loading data...')
    with open('radio_ads_tagged.json', 'r') as f:
        data = json.load(f)

    print(f'Loaded {len(data):,} records\n')

    print('Analyzing sponsor variations...')
    mapping, variations_report = create_standardization_mapping(data)

    print(f'Found {len(mapping):,} sponsor names')
    print(f'Identified {len(variations_report):,} sponsors with multiple variations\n')

    print('Applying standardization...')
    standardized_data, stats = apply_standardization(data, mapping)

    # Save standardized data
    print('Saving standardized data...')
    with open('radio_ads_standardized.json', 'w') as f:
        json.dump(standardized_data, f, indent=2)

    # Save mapping for review
    print('Saving sponsor mapping...')
    with open('sponsor_mapping.json', 'w') as f:
        json.dump(mapping, f, indent=2, sort_keys=True)

    # Generate variations report
    print('Generating variations report...')
    report_lines = []
    report_lines.append('=' * 80)
    report_lines.append('SPONSOR STANDARDIZATION REPORT')
    report_lines.append('=' * 80)
    report_lines.append('')
    report_lines.append(f'Total records: {stats["total_records"]:,}')
    report_lines.append(f'Records with sponsors: {stats["records_with_sponsors"]:,}')
    report_lines.append(f'Sponsors standardized: {stats["sponsors_standardized"]:,}')
    report_lines.append(f'Sponsors unchanged: {stats["sponsors_unchanged"]:,}')
    report_lines.append('')
    report_lines.append(f'Unique sponsor names (original): {len(mapping):,}')
    report_lines.append(f'Unique sponsor names (standardized): {len(set(mapping.values())):,}')
    report_lines.append(f'Sponsors merged: {len(mapping) - len(set(mapping.values())):,}')
    report_lines.append('')
    report_lines.append('=' * 80)
    report_lines.append('SPONSORS WITH MULTIPLE VARIATIONS')
    report_lines.append('=' * 80)
    report_lines.append('')

    for i, item in enumerate(variations_report[:50], 1):
        report_lines.append(f'{i}. {item["standardized"]} ({item["total"]:,} ads total)')
        for variation in sorted(item['variations']):
            count = item['counts'][variation]
            if variation == item['standardized']:
                report_lines.append(f'   → "{variation}" ({count:,} ads) [STANDARDIZED]')
            else:
                report_lines.append(f'   - "{variation}" ({count:,} ads)')
        report_lines.append('')

    with open('sponsor_standardization_report.txt', 'w') as f:
        f.write('\n'.join(report_lines))

    # Print summary
    print()
    print('=' * 80)
    print('STANDARDIZATION COMPLETE')
    print('=' * 80)
    print()
    print(f'Total records: {stats["total_records"]:,}')
    print(f'Sponsors standardized: {stats["sponsors_standardized"]:,}')
    print(f'Sponsors unchanged: {stats["sponsors_unchanged"]:,}')
    print()
    print(f'Original unique sponsors: {len(mapping):,}')
    print(f'Standardized unique sponsors: {len(set(mapping.values())):,}')
    print(f'Sponsors merged: {len(mapping) - len(set(mapping.values())):,}')
    print()
    print('Files created:')
    print('  - radio_ads_standardized.json (data with sponsor_normalized field)')
    print('  - sponsor_mapping.json (all variations -> standardized mapping)')
    print('  - sponsor_standardization_report.txt (detailed report)')
    print('=' * 80)

    # Show examples
    print()
    print('EXAMPLE STANDARDIZATIONS:')
    print('-' * 80)
    examples = [
        ('KAMALA HARRIS FOR PRESIDENT', mapping.get('KAMALA HARRIS FOR PRESIDENT')),
        ('Kamala Harris For President', mapping.get('Kamala Harris For President')),
        ('MAGA INC', mapping.get('MAGA INC')),
        ('Black PAC', mapping.get('Black PAC')),
        ('JOE BIDEN FOR PRESIDENT', mapping.get('JOE BIDEN FOR PRESIDENT'))
    ]

    for original, standardized in examples:
        if original in mapping:
            print(f'  "{original}" → "{standardized}"')

if __name__ == '__main__':
    main()
