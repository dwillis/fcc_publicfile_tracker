#!/usr/bin/env python3
"""Sponsor-name normalization.

Pulled out of the old standardize_sponsors.py as pure functions (no file
I/O) so build_site.py can call them per-record instead of running a
separate standardization pass over an intermediate file.
"""
import re

# Canonical names for major presidential campaigns, whose filer-typed sponsor
# names vary the most (capitalization, "for President" suffixes, invoice
# numbers appended to the name).
CANONICAL_NAMES = {
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

ACRONYMS = {
    'PAC', 'INC', 'LLC', 'USA', 'US', 'MAGA', 'NAACP', 'DNC', 'RNC',
    'GOP', 'FEC', 'EEO', 'NC', 'DC', 'LA', 'NY', 'CA', 'TX', 'FL',
    'VA', 'MD', 'GA', 'MI', 'OH', 'PA', 'AZ', 'NV', 'WI', 'MN',
    'CO', 'OR', 'WA', 'MA', 'NJ', 'CT', 'IL', 'TN', 'SC',
    'ACTUM', 'YES', 'NO', 'PROP', 'DA', 'CEO', 'CFO', 'VP', 'AG',
    'HD', 'FM', 'AM', 'TV', 'WLLD', 'KLCA', 'FF', 'AI', 'IT', 'II', 'III'
}

LOWERCASE_WORDS = {
    'for', 'of', 'the', 'and', 'or', 'in', 'on', 'at', 'to', 'a', 'an',
    'as', 'but', 'by', 'nor', 'so', 'yet', 'vs', 'v'
}


def clean_sponsor_name(sponsor):
    """Strip invoice numbers, dates, and other filer-added noise from a sponsor name."""
    if not sponsor:
        return None

    cleaned = re.sub(r'\s+\d{5,}[\s\-\d]*$', '', sponsor)
    cleaned = re.sub(r'\s+\d{1,2}[-/]\d{1,2}[-/]\d{2,4}$', '', cleaned)
    cleaned = re.sub(r'\s+\d{6,8}$', '', cleaned)
    cleaned = re.sub(r'\s+-\s+\d+.*$', '', cleaned)
    cleaned = re.sub(r'^premier\s+network\s+', '', cleaned, flags=re.IGNORECASE)
    cleaned = ' '.join(cleaned.split())

    return cleaned.strip()


def match_canonical_name(sponsor):
    """Return a canonical campaign name if sponsor matches a known pattern, else None."""
    if not sponsor:
        return None

    sponsor_lower = sponsor.lower().strip()
    for config in CANONICAL_NAMES.values():
        for pattern in config['patterns']:
            if re.match(pattern, sponsor_lower):
                return config['canonical']

    return None


def standardize_sponsor_basic(sponsor):
    """Title-case a sponsor name while preserving known acronyms and lowercase connectors."""
    if not sponsor or sponsor.strip() == '':
        return None

    words = sponsor.split()
    standardized = []

    for i, word in enumerate(words):
        word_upper = word.upper().strip('.,!?;:')

        if word_upper in ACRONYMS:
            standardized.append(word_upper)
        elif i > 0 and word.lower() in LOWERCASE_WORDS:
            standardized.append(word.lower())
        else:
            standardized.append(word.title())

    result = ' '.join(standardized)

    result = re.sub(r'\bFor (President|Senate|Congress|Governor|Mayor|Council)\b',
                     r'for \1', result)
    result = re.sub(r'\bOf\b', 'of', result)
    result = re.sub(r'(?<!^)\bThe\b', 'the', result)
    result = result.replace(' Pac', ' PAC')
    result = result.replace(' Inc', ' INC')
    result = result.replace(' Llc', ' LLC')

    return result


def standardize_sponsor_advanced(sponsor):
    """Clean, canonicalize, then title-case a sponsor name."""
    if not sponsor:
        return None

    cleaned = clean_sponsor_name(sponsor)
    if not cleaned:
        return None

    canonical = match_canonical_name(cleaned)
    if canonical:
        return canonical

    return standardize_sponsor_basic(cleaned)
