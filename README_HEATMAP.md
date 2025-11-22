# Political Radio Ads - Sponsor/Station Heatmap

An interactive single-page application that visualizes which political sponsors advertise on which radio stations using a color-coded heatmap.

## Features

### Visual Design
- **Color-coded cells**: Darker blue = more ads from that sponsor on that station
- **Interactive tooltips**: Hover over any cell to see sponsor, station, and exact ad count
- **Responsive layout**: Clean, modern design that works on different screen sizes

### Filters
- **Office Type**: Filter by President, US Senate, US House, State, Local, Non-Candidate Issue Ads, or Political Matters
- **Year**: View data from specific years (2018-2025)
- **Top N Sponsors**: Show top 25, 50, 75, or 100 sponsors by ad volume
- **Minimum Ads**: Filter out sponsors with fewer than X ads

### Statistics Dashboard
Real-time stats update based on filters:
- Total number of ads displayed
- Number of sponsors shown
- Number of stations shown
- Date range of ads

### Data Quality
Automatically filters out:
- Records with parsing errors (Entity references)
- Category-only records (no specific sponsor)
- Records missing station or sponsor information

### Sponsor Standardization
Sponsor names are automatically standardized to merge variations:
- "Kamala Harris for President", "KAMALA HARRIS FOR PRESIDENT", and "Kamala Harris For President" → all merged
- "MAGA Inc", "MAGA INC", "Maga Inc" → standardized to "MAGA INC"
- **125 sponsor variations merged** into consistent names
- Uses the `sponsor_normalized` field for accurate counting

## Usage

### Running Locally

1. Make sure `radio_ads_standardized.json` is in the same directory as `heatmap.html`
   - If you only have `radio_ads_tagged.json`, run `python3 standardize_sponsors.py` first

2. Start a local web server:
   ```bash
   # Python 3
   python3 -m http.server 8000

   # Or Python 2
   python -m SimpleHTTPServer 8000

   # Or Node.js (if you have npx)
   npx http-server
   ```

3. Open your browser to `http://localhost:8000/heatmap.html`

### Reading the Heatmap

- **Rows**: Political sponsors (candidates, PACs, issue organizations)
- **Columns**: Radio station call signs
- **Color intensity**: Number of ad filings
  - Light/white: Few or no ads
  - Dark blue: Many ads
- **Hover**: See exact numbers

### Example Insights

**Strategic Media Buying**:
- Which stations does a candidate focus on?
- Do certain sponsors always use the same stations?
- Which stations attract the most political advertising?

**Campaign Patterns**:
- Filter by year to compare election cycles
- Filter by office to see Presidential vs. local advertising patterns
- Filter by Non-Candidate Issue Ads to track PAC activity

**Issue Advocacy**:
- Set Office Type to "Political Matters" to see issue advocacy organizations
- Compare issue advocacy vs. candidate advertising

## Data Source

Uses `radio_ads_standardized.json` - cleaned, tagged, and standardized FCC public file data containing:
- 56,458 political ad records
- 157 political matters/controversial issues records
- Coverage from 2018-2025
- ~1,000 radio stations nationwide (urban format focus)

## Technical Details

### Technologies
- **D3.js v7**: Data visualization and rendering
- **Vanilla JavaScript**: No framework dependencies
- **Pure CSS**: Responsive design with modern gradients

### Browser Requirements
- Modern browser with ES6 support
- JavaScript enabled
- Recommended: Chrome, Firefox, Safari, Edge (latest versions)

### Performance
- Efficiently handles 60,000+ records
- Real-time filtering and recalculation
- Smooth interactions and transitions

## Customization

### Adjust Default Filters
Edit the default values in the HTML:
```javascript
// Line ~214
<option value="50" selected>Top 50</option>  // Change default top N

// Line ~219
<input type="number" id="minAds" value="5" ...>  // Change default minimum
```

### Change Color Scheme
Edit the D3 color interpolator:
```javascript
// Line ~345
.interpolator(d3.interpolateBlues);  // Try: Reds, Greens, Purples, etc.
```

### Adjust Cell Size
```javascript
// Line ~321
const cellSize = 30;  // Make larger or smaller
```

## Future Enhancements

Possible additions:
- Click cells to see list of actual ad filings
- Export visible data as CSV
- Save/share filter combinations via URL
- Compare two time periods side-by-side
- Add state/geographic filtering
- Show trending sponsors (biggest increases)

## Data Updates

When new data is scraped:
1. Run `tag_and_clean_data.py` to update `radio_ads_tagged.json`
2. Run `standardize_sponsors.py` to create `radio_ads_standardized.json` with normalized sponsor names
3. Refresh the page - new data loads automatically
4. Year filter updates automatically with new years
