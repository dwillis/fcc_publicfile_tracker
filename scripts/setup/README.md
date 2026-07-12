# One-time setup scripts

These built the station roster and are not part of the recurring pipeline. Nothing
runs them automatically; the pipeline only reads their final output,
`urban_radio_stations_with_status.csv` (kept at the repo root).

Run in order, only when the station list needs to be rebuilt from scratch:

1. `fetch_radio_stations.py` — scrapes the
   [Wikipedia list of urban-format stations](https://en.wikipedia.org/wiki/List_of_urban-format_radio_stations_in_the_United_States)
   into `urban_radio_stations.csv`.
2. `get_fcc.py` — queries the FCC facility-search API to attach an FCC public-file
   RSS URL to each station, producing `urban_radio_stations_checked.csv`.
3. `url_checker.py` — hits each RSS URL and records its HTTP status in
   `urban_radio_stations_with_status.csv` (at the repo root).

These scripts are unmaintained and have known bugs (documented, not fixed, since
they're not on the hot path): `fetch_radio_stations.py` relies on Wikipedia's
`mw-headline` span markup, which the page may no longer use; `get_fcc.py` breaks
out of its facility-matching loop after the first result, so it doesn't actually
search for a city/state match; neither `get_fcc.py` nor `url_checker.py` sets a
request timeout.
