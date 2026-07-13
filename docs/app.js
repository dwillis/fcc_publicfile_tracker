/* FCC Public File Tracker — exploratory filings table. No dependencies. */

const FCC_PROFILE_PREFIX = 'https://publicfiles.fcc.gov/';
const PAGE_SIZE = 100;

const TYPE_LABELS = {
  political_ad: 'Political ad',
  political_matters: 'Political matters',
  non_political: 'Non-political',
  unknown: 'Unknown',
};

const state = {
  manifest: null,
  yearCache: new Map(), // year -> { cols, rows }
  currentYear: null,
  filtered: [],
  sortCol: 'date',
  sortDir: 'desc',
  page: 1,
};

const els = {};

function $(id) {
  return document.getElementById(id);
}

function escapeHtml(value) {
  if (value == null) return '';
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

/* The FCC blocks direct links to individual PDFs, so link to the station's
   political files (or its public file home for non-political rows) instead. */
function buildStationUrl(service, station, type) {
  if (!service || !station) return null;
  const base = `${FCC_PROFILE_PREFIX}${service}-profile/${station}`;
  const political = type === 'political_ad' || type === 'political_matters';
  return political ? `${base}/political-files` : base;
}

function debounce(fn, delay) {
  let timer = null;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}

function setStatus(message) {
  els.status.textContent = message || '';
}

async function fetchJson(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`${url} returned ${res.status}`);
  return res.json();
}

async function loadYear(year) {
  if (state.yearCache.has(year)) return state.yearCache.get(year);

  if (year === 'all') {
    setStatus('Loading all years — this pulls every shard, ~12MB total...');
    const years = state.manifest.years.map((y) => y.year);
    const cols = state.manifest.years.length ? await ensureCols() : [];
    const rows = [];
    for (const y of years) {
      const shard = await loadYear(y);
      rows.push(...shard.rows);
      setStatus(`Loading all years — ${y} done (${rows.length.toLocaleString()} rows so far)...`);
    }
    const combined = { cols, rows };
    state.yearCache.set('all', combined);
    setStatus('');
    return combined;
  }

  setStatus(`Loading ${year}...`);
  const data = await fetchJson(`data/filings-${year}.json`);
  state.yearCache.set(year, data);
  setStatus('');
  return data;
}

async function ensureCols() {
  const firstYear = state.manifest.years[0].year;
  const shard = await loadYear(firstYear);
  return shard.cols;
}

function colIndex(cols, name) {
  return cols.indexOf(name);
}

function applyFiltersAndSort(data) {
  const { cols, rows } = data;
  const iDate = colIndex(cols, 'date');
  const iStation = colIndex(cols, 'station');
  const iState = colIndex(cols, 'state');
  const iCity = colIndex(cols, 'city');
  const iOffice = colIndex(cols, 'office');
  const iSponsor = colIndex(cols, 'sponsor');
  const iType = colIndex(cols, 'type');
  const iPath = colIndex(cols, 'path');

  const stateFilter = els.stateSelect.value;
  const officeFilter = els.officeSelect.value;
  const politicalOnly = els.politicalOnly.checked;
  const search = els.searchInput.value.trim().toLowerCase();

  let out = rows.filter((r) => {
    if (politicalOnly && r[iType] !== 'political_ad' && r[iType] !== 'political_matters') return false;
    if (stateFilter !== 'all' && r[iState] !== stateFilter) return false;
    if (officeFilter !== 'all' && r[iOffice] !== officeFilter) return false;
    if (search) {
      const haystack = `${r[iSponsor] || ''} ${r[iStation] || ''} ${r[iPath] || ''}`.toLowerCase();
      if (!haystack.includes(search)) return false;
    }
    return true;
  });

  const sortIdx = colIndex(cols, state.sortCol);
  const dir = state.sortDir === 'asc' ? 1 : -1;
  out = out.slice().sort((a, b) => {
    const av = a[sortIdx] || '';
    const bv = b[sortIdx] || '';
    if (av < bv) return -1 * dir;
    if (av > bv) return 1 * dir;
    return 0;
  });

  return { cols, indices: { iDate, iStation, iState, iCity, iOffice, iSponsor, iType, iPath }, rows: out };
}

function renderTable() {
  const data = state.yearCache.get(state.currentYear);
  if (!data) return;

  const { cols, indices, rows } = applyFiltersAndSort(data);
  state.filtered = { cols, indices, rows };

  const total = rows.length;
  const pages = Math.max(1, Math.ceil(total / PAGE_SIZE));
  state.page = Math.min(state.page, pages);
  const start = (state.page - 1) * PAGE_SIZE;
  const pageRows = rows.slice(start, start + PAGE_SIZE);

  els.resultsCount.textContent =
    `${total.toLocaleString()} filing${total === 1 ? '' : 's'} matched` +
    (data.rows.length !== total ? ` (of ${data.rows.length.toLocaleString()} loaded)` : '');
  els.pageInfo.textContent = `Page ${state.page} of ${pages}`;
  els.prevBtn.disabled = state.page <= 1;
  els.nextBtn.disabled = state.page >= pages;

  const { iDate, iStation, iState, iCity, iOffice, iSponsor, iType, iPath } = indices;

  els.tbody.innerHTML = pageRows.map((r) => {
    const location = [r[iCity], r[iState]].filter(Boolean).join(', ');
    const stationUrl = buildStationUrl(r[cols.indexOf('service')], r[iStation], r[iType]);
    const pathTitle = escapeHtml(r[iPath] || '');
    return `<tr>
      <td>${escapeHtml(r[iDate])}</td>
      <td>${escapeHtml(r[iStation])}</td>
      <td>${escapeHtml(location)}</td>
      <td>${escapeHtml(r[iOffice])}</td>
      <td title="${pathTitle}">${escapeHtml(r[iSponsor])}</td>
      <td>${escapeHtml(TYPE_LABELS[r[iType]] || r[iType])}</td>
      <td>${stationUrl ? `<a href="${escapeHtml(stationUrl)}" target="_blank" rel="noopener">Station filings ↗</a>` : ''}</td>
    </tr>`;
  }).join('');
}

function updateSortIndicators() {
  document.querySelectorAll('th[data-col]').forEach((th) => {
    th.classList.remove('sort-asc', 'sort-desc');
    if (th.dataset.col === state.sortCol) {
      th.classList.add(state.sortDir === 'asc' ? 'sort-asc' : 'sort-desc');
    }
  });
}

function exportCsv() {
  const { cols, indices, rows } = state.filtered;
  if (!rows || !rows.length) return;

  const { iDate, iStation, iState, iCity, iOffice, iSponsor, iType, iPath } = indices;
  const serviceIdx = cols.indexOf('service');
  const header = ['Date', 'Station', 'State', 'City', 'Office', 'Sponsor', 'Type', 'Folder path', 'Station filings URL'];

  const csvEscape = (value) => {
    const s = value == null ? '' : String(value);
    return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
  };

  const lines = [header.map(csvEscape).join(',')];
  rows.forEach((r) => {
    lines.push([
      r[iDate], r[iStation], r[iState], r[iCity], r[iOffice], r[iSponsor],
      TYPE_LABELS[r[iType]] || r[iType], r[iPath], buildStationUrl(r[serviceIdx], r[iStation], r[iType]),
    ].map(csvEscape).join(','));
  });

  const blob = new Blob([lines.join('\n')], { type: 'text/csv' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `fcc-filings-${state.currentYear}.csv`;
  a.click();
  URL.revokeObjectURL(url);
}

async function onYearChange() {
  state.currentYear = els.yearSelect.value;
  state.page = 1;
  try {
    await loadYear(state.currentYear);
    renderTable();
  } catch (err) {
    setStatus(`Error loading data: ${err.message}`);
  }
}

function onFilterChange() {
  state.page = 1;
  renderTable();
}

async function init() {
  try {
    state.manifest = await fetchJson('data/manifest.json');
  } catch (err) {
    setStatus(
      `Could not load manifest.json (${err.message}). docs/data/ is a build artifact, ` +
      'not checked into git — run "python build_site.py" from the repo root to generate it. ' +
      'On GitHub Pages, it only exists after the publish workflow has run, and the Pages ' +
      'source (Settings → Pages) must be set to "GitHub Actions".'
    );
    return;
  }

  els.generated.textContent = state.manifest.generated
    ? `Data current as of ${state.manifest.generated}`
    : '';

  const years = state.manifest.years.map((y) => y.year).sort().reverse();
  els.yearSelect.innerHTML = years.map((y) => {
    const info = state.manifest.years.find((entry) => entry.year === y);
    return `<option value="${y}">${y} (${info.rows.toLocaleString()})</option>`;
  }).join('') + `<option value="all">All years (${state.manifest.total.toLocaleString()})</option>`;

  els.stateSelect.innerHTML = '<option value="all">All states</option>' +
    state.manifest.states.map((s) => `<option value="${escapeHtml(s)}">${escapeHtml(s)}</option>`).join('');

  els.officeSelect.innerHTML = '<option value="all">All offices</option>' +
    state.manifest.offices.map((o) => `<option value="${escapeHtml(o)}">${escapeHtml(o)}</option>`).join('');

  els.yearSelect.value = years[0];
  await onYearChange();
}

document.addEventListener('DOMContentLoaded', () => {
  els.yearSelect = $('yearSelect');
  els.stateSelect = $('stateSelect');
  els.officeSelect = $('officeSelect');
  els.politicalOnly = $('politicalOnly');
  els.searchInput = $('searchInput');
  els.exportBtn = $('exportBtn');
  els.resultsCount = $('resultsCount');
  els.tbody = document.querySelector('#filingsTable tbody');
  els.prevBtn = $('prevBtn');
  els.nextBtn = $('nextBtn');
  els.pageInfo = $('pageInfo');
  els.status = $('status');
  els.generated = $('generated');

  els.yearSelect.addEventListener('change', onYearChange);
  els.stateSelect.addEventListener('change', onFilterChange);
  els.officeSelect.addEventListener('change', onFilterChange);
  els.politicalOnly.addEventListener('change', onFilterChange);
  els.searchInput.addEventListener('input', debounce(onFilterChange, 250));
  els.exportBtn.addEventListener('click', exportCsv);
  els.prevBtn.addEventListener('click', () => { state.page -= 1; renderTable(); });
  els.nextBtn.addEventListener('click', () => { state.page += 1; renderTable(); });

  document.querySelectorAll('th[data-col]').forEach((th) => {
    th.addEventListener('click', () => {
      const col = th.dataset.col;
      if (state.sortCol === col) {
        state.sortDir = state.sortDir === 'asc' ? 'desc' : 'asc';
      } else {
        state.sortCol = col;
        state.sortDir = col === 'date' ? 'desc' : 'asc';
      }
      updateSortIndicators();
      state.page = 1;
      renderTable();
    });
  });
  updateSortIndicators();

  init();
});
