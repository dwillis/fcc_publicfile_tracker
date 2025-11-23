# Data Cleaning Summary

## Overview

The FCC public file data has been cleaned and tagged to improve usability for building a single-page application to display political radio ad information.

## Files Created

### Analysis Files
- **`non_political_ads_analysis.py`** - Script to categorize and analyze non-political FCC filings
- **`non_political_ads.json`** - Structured data containing all non-political records, categorized
- **`non_political_ads_report.txt`** - Detailed text report of non-political filings

### Cleaned Data
- **`tag_and_clean_data.py`** - Main data cleaning script
- **`radio_ads_tagged.json`** - Cleaned and enhanced dataset (recommended for SPA development)

## Data Statistics

### Total Records: 60,614

| Category | Count | Percentage |
|----------|-------|------------|
| Political Ads (Political Files) | 56,458 | 93.1% |
| Political Matters & Controversial Issues | 157 | 0.3% |
| Non-Political FCC Filings | 3,999 | 6.6% |

### Enhancements Applied

- ✅ **Station call signs extracted**: 60,546 records (99.9%)
- ✅ **Years extracted from file paths**: 56,956 records (94.0%)
- ✅ **Record type tagging**: All 60,614 records tagged
- ✅ **Improved office/sponsor parsing**: 56,181 usable political ad records (99.5%)

## Political Ads Breakdown

### By Office Type

| Office | Count |
|--------|-------|
| Non-Candidate Issue Ads | 23,604 |
| President | 8,063 |
| Local | 7,394 |
| State | 6,954 |
| US Senate | 4,590 |
| US House | 3,584 |
| Other | 2,269 |

### Parsing Quality

- **Records with sponsor**: 17,129 (30.3%)
- **Records without sponsor**: 39,329 (69.7%)
  - These are filed directly at the category level (e.g., "Political Files/2024/Non-Candidate Issue Ads")
  - This is normal FCC filing structure
- **Records with office**: 56,458 (100%)
- **Usable records** (has year + office): 56,181 (99.5%)

## Political Matters & Controversial Issues

This category contains 157 records related to political issue advocacy:

### Organizations Found

- ACTION NC (13 records)
- Progress NC (12 records)
- Black Political Caucus (7 records)
- Black Voters Matter (5 records)
- EQUALITY MICHIGAN (4 records)
- ADVANCE CAROLINA (4 records)
- THE JUSTICE PROJECT (3 records)
- VOTEORG (2 records)
- COALITION FOR BETTER 2050 (2 records)
- Others (individual records)

**Note**: These are legitimate political issue ads but filed under a different FCC category. They should be included in any political advertising analysis.

## Non-Political File Categories

| Category | Count |
|----------|-------|
| Equal Employment Opportunity Records | 2,453 |
| FCC Authorizations | 511 |
| Ownership Reports | 493 |
| Time Brokerage Agreements | 178 |
| Political Matters Disclosures | 157 |
| Local Public Notice Announcements | 116 |
| FCC Investigations or Complaints | 49 |
| Applications and Related Materials | 44 |
| Foreign Government-Provided Programming | 43 |
| Citizen Agreements | 39 |
| Donor Lists | 39 |
| Information | 17 |
| Joint Sales Agreements | 17 |

## New Data Schema

The cleaned dataset (`radio_ads_tagged.json`) has the following fields:

```json
{
  "id": "https://publicfiles.fcc.gov/am-profile/WAOK/...",
  "title": "Original RSS feed title",
  "url": "Direct PDF download link",
  "updated": "ISO 8601 timestamp",
  "record_type": "political_ad | political_matters | non_political",
  "facility_id": 63775,
  "station": "WAOK-AM",
  "year": 2024,
  "office": "US Senate | President | Local | etc",
  "sponsor": "Candidate or organization name (or null)",
  "file_path": "Full path extracted from title",
  "state": "State (for newer records)",
  "city": "City (for newer records)",
  "station_url": "RSS feed URL (for newer records)"
}
```

## Recommendations for SPA Development

1. **Use `radio_ads_tagged.json`** as your data source

2. **Filter options**:
   - By `record_type` to show only political content
   - By `year` for timeline views
   - By `office` for election type filtering
   - By `station` for station-specific views

3. **Handle missing sponsors**:
   - 69.7% of political ads don't have a sponsor in the file path
   - These are category-level filings and should be grouped by `office` type

4. **Include Political Matters**:
   - Don't forget the 157 "political_matters" records
   - These contain important issue advocacy data

5. **Station information**:
   - 99.9% of records have station call signs extracted
   - Use this for geographic or station-based visualizations

## Data Quality Notes

### Strengths
- Near-complete station extraction (99.9%)
- Excellent office parsing (100% for political ads)
- Clear categorization of political vs non-political
- Year extraction for 94% of records

### Limitations
- 69.7% of political ads lack sponsor names (FCC filing structure limitation)
- Some Political Matters records lack specific organization names
- Older records may not have state/city information
- Some edge cases in parsing complex file paths

## Next Steps

For building the SPA, consider:
1. Creating aggregation views for records without sponsors
2. Building search/filter interfaces for records with sponsors
3. Visualizing trends over time using the `year` field
4. Mapping data using `station`, `state`, and `city` fields
5. Providing direct PDF access via the `url` field
