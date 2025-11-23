# FCC Political Radio Ads Heatmap

This directory contains the GitHub Pages deployment for the FCC Political Radio Ads Heatmap visualization.

## Files

- `index.html` - Interactive heatmap visualization (source: `heatmap.html`)
- `radio_ads_heatmap.json` - Optimized data file (~19 MB)

## Automatic Updates

This directory is automatically updated by the GitHub Actions workflow `.github/workflows/deploy-heatmap.yaml`:

1. **Data Collection**: Scrapes latest FCC public file data
2. **Data Processing**:
   - Tags and cleans data (`tag_and_clean_data.py`)
   - Standardizes sponsor names (`standardize_sponsors.py`)
   - Creates optimized JSON (`create_minimal_json.py`)
3. **Deployment**: Copies files to this directory and deploys to GitHub Pages

The workflow runs:
- On every push to the main branch
- Twice daily at 12:00 and 18:00 UTC
- Manually via workflow dispatch

## Viewing the Heatmap

Once GitHub Pages is enabled, the heatmap will be available at:
`https://[username].github.io/fcc_publicfile_tracker/`

## Data Source

Data is collected from FCC public inspection files for urban radio stations nationwide, focusing on political advertising from 2018-2025.
