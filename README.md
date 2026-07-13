# FCC Public File Tracker

Tracks documents filed to FCC public inspection files at ~880 urban-format
radio stations, with a focus on political advertising disclosures, and
publishes them as a searchable table at
[the GitHub Pages site](https://dwillis.github.io/fcc_publicfile_tracker/).

## How it works

Each station's FCC public file exposes an RSS feed of newly uploaded
documents. Twice a day, `.github/workflows/publish.yaml` runs the pipeline
below and redeploys the site:

1. **`rss_parser.py`** fetches every station's RSS feed (list of stations:
   `urban_radio_stations_with_status.csv`) and appends new entries, deduped
   by RSS entry id, to `data/raw/YYYY.jsonl` (one compact JSON object per
   line, sharded by the year the entry was filed).
2. **`build_site.py`** reads all of `data/raw/*.jsonl`, classifies each
   filing by its FCC folder path (political ad, political matters
   disclosure, or non-political), normalizes sponsor names
   (`sponsors.py`), and writes `docs/data/filings-YYYY.json` +
   `docs/data/manifest.json` — the data the frontend loads.

`data/raw/` is the only data committed to the repo; `docs/data/` is a build
output, regenerated on every run, and not tracked in git.

## The site

`docs/index.html` + `docs/app.js` is a plain HTML/JS filings table — no
build step, no framework, no CDN dependency. It loads one year's shard by
default (or all years, on request), and lets you filter by state, office
type, and a text search, sort any column, page through results, and export
the current filter as a CSV. Every row links to the station's political
files on `publicfiles.fcc.gov` (the FCC blocks direct links to individual
PDFs, so you browse to the document from there using the row's folder path).

Office and sponsor names are exactly what station staff typed into the FCC
public file system, so expect inconsistency — this is an exploration tool
for finding filings and reading the underlying documents, not a polished
analysis. Each row is an upload event from a station's RSS feed: the date
is when the file was uploaded, while the folder path carries the
political-file year it was filed under, which can be an earlier year
(stations backfile old documents). The site's year filter — and the
data/filings-YYYY.json shards — use that folder year, not the upload date.
Stations also sometimes move or delete files after uploading, so a row can
outlive the document it announced.

To run it locally: `python -m http.server -d docs`, then open
`http://localhost:8000/`. You'll need `docs/data/` populated first — see
below.

## Running the pipeline locally

```bash
pip install -r requirements.txt
python rss_parser.py     # fetch new filings into data/raw/
python build_site.py     # rebuild docs/data/ from data/raw/
```

## One-time setup scripts

`scripts/setup/` holds the scripts that originally built
`urban_radio_stations_with_status.csv` (scraping a Wikipedia station list,
matching stations to FCC RSS feeds, checking feed URLs). They're not part
of the recurring pipeline — see `scripts/setup/README.md`.

## Contributing

Contributions are welcome:

1. Fork the repository.
2. Create a new branch: `git checkout -b feature/your-feature`.
3. Make your changes and commit them: `git commit -m 'Add some feature'`.
4. Push to the branch: `git push origin feature/your-feature`.
5. Submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).

## Contact

For any questions or inquiries, please contact [dwillis@gmail.com](mailto:dwillis@gmail.com).
