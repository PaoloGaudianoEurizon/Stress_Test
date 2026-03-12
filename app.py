import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import re
import io

# ─── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Stress Test Mapping", page_icon="📊", layout="wide")

# ─── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.stApp { background: #ffffff; }
[data-testid="stAppViewContainer"] { background: #ffffff; }

/* ── Header brand ── */
.fin-header { display: flex; align-items: center; gap: 14px; margin-bottom: 0.3rem; }
.fin-logo {
    width: 40px; height: 40px; border-radius: 9px;
    background: linear-gradient(135deg, #ff4b4b 0%, #c0121f 100%);
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem; font-weight: 800; color: #fff;
    box-shadow: 0 2px 8px rgba(255,75,75,0.3); flex-shrink: 0;
}
.fin-brand-text .main-title {
    font-size: 1.7rem; font-weight: 700; color: #0e1117; line-height: 1.1; margin: 0;
}
.fin-brand-text .subtitle {
    font-size: 0.78rem; color: #6b6b6b; margin: 2px 0 0; font-style: italic;
}

/* ── Asset class strip ── */
.hm-strip {
    display: flex; flex-wrap: wrap; gap: 6px; align-items: flex-end;
    background: #f8f9fb; border: 1px solid #e6e6e6; border-radius: 8px;
    padding: 10px 14px; margin: 0.9rem 0 1.4rem;
}
.hm-strip-title {
    font-size: 0.58rem; color: #9ca3af; text-transform: uppercase;
    letter-spacing: 0.08em; width: 100%; margin-bottom: 4px;
    display: flex; align-items: center; gap: 8px;
}
.hm-strip-title::after { content: ''; flex: 1; height: 1px; background: #e6e6e6; }
.hm-cell {
    display: flex; flex-direction: column; align-items: center;
    background: #ffffff; border: 1px solid #e6e6e6; border-radius: 5px;
    padding: 6px 10px 5px; min-width: 72px; gap: 2px;
}
.hm-label { font-size: 0.58rem; color: #6b7280; letter-spacing: 0.03em; text-transform: uppercase; white-space: nowrap; text-align: center; }
.hm-count { font-size: 0.92rem; font-weight: 700; color: #0e1117; line-height: 1; }

.breadcrumb { font-size: 0.78rem; color: #6b6b6b; margin-bottom: 1.2rem; }
.breadcrumb span { color: #0e1117; font-weight: 600; }
.breadcrumb .sep { color: #cccccc; margin: 0 6px; }

.section-header {
    font-size: 1.1rem; font-weight: 600; color: #0e1117;
    margin: 1.6rem 0 0.8rem;
    display: flex; align-items: center; gap: 10px;
    border-left: 4px solid #ff4b4b; padding-left: 10px;
}
.section-header::after { content: ''; flex: 1; height: 1px; background: #e6e6e6; }

.sel-pill {
    display: inline-block; background: #ff4b4b; color: #ffffff;
    border-radius: 4px; font-size: 0.68rem; padding: 2px 9px; margin: 2px;
}
.hint-box {
    background: #f0f2f6; border: 1px solid #d9d9d9; border-radius: 6px;
    padding: 0.6rem 1rem; font-size: 0.78rem; color: #31333f; margin-bottom: 1.2rem;
}

/* ── Stat boxes ── */
.stat-box {
    background: #ffffff; border: 1px solid #e6e6e6; border-radius: 8px;
    padding: 0.75rem 1.2rem; box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}
.stat-box .sv { font-size: 1.6rem; font-weight: 700; color: #0e1117; line-height: 1; }
.stat-box .sk { font-size: 0.65rem; color: #6b6b6b; text-transform: uppercase;
    letter-spacing: 0.06em; margin-top: 4px; }

/* ── Scenario table ── */
.scenario-table {
    width: 100%; border-collapse: collapse; font-size: 0.82rem;
    background: #ffffff; border-radius: 8px; overflow: hidden;
    border: 1px solid #e6e6e6;
}
.scenario-table th {
    background: #ff4b4b; color: #ffffff;
    padding: 10px 16px; text-align: left;
    font-weight: 600; font-size: 0.75rem; letter-spacing: 0.03em;
}
.scenario-table th.pos-th { background: #16a34a; }
.scenario-table th.neg-th { background: #dc2626; }
.scenario-table th.mix-th { background: #b45309; }
.scenario-table td {
    padding: 10px 16px; border-bottom: 1px solid #f0f0f0;
    color: #31333f; vertical-align: top;
}
.scenario-table tr:last-child td { border-bottom: none; }
.scenario-table tr:hover td { background: #fafafa; }

/* ── Factor rows ── */
.factor-list { display: flex; flex-direction: column; gap: 4px; margin-top: 6px; }
.factor-row {
    display: flex; justify-content: space-between; align-items: baseline;
    background: #f9fafb; border-radius: 4px; padding: 3px 8px; font-size: 0.78rem;
}
.factor-name { color: #374151; font-size: 0.78rem; flex: 1; padding-right: 8px; }
.factor-val-pos { color: #16a34a; font-weight: 600; white-space: nowrap; }
.factor-val-neg { color: #dc2626; font-weight: 600; white-space: nowrap; }
.factor-val-zero { color: #6b6b6b; white-space: nowrap; }

.long-des { font-size: 0.72rem; color: #6b6b6b; margin-top: 3px; line-height: 1.45; }

/* ── Scenario type badge ── */
.type-badge {
    display: inline-block; font-size: 0.6rem; font-weight: 700; letter-spacing: 0.05em;
    padding: 1px 6px; border-radius: 3px; margin-left: 6px; vertical-align: middle;
}
.type-brs { background: #dbeafe; color: #1d4ed8; }
.type-ec  { background: #dcfce7; color: #15803d; }

/* ── Default buttons ── */
.stButton > button {
    background: #ffffff; color: #31333f;
    border: 1px solid #d9d9d9; border-radius: 6px;
    font-size: 0.875rem; font-weight: 400; transition: all 0.1s ease;
}
.stButton > button:hover { border-color: #ff4b4b; color: #ff4b4b; background: #fff5f5; }
</style>
""", unsafe_allow_html=True)

# ─── HELPERS ───────────────────────────────────────────────────────────────────

def to_bps(value, unit):
    if pd.isna(value) or pd.isna(unit):
        return np.nan
    unit = str(unit).strip().lower()
    if unit == 'bps':    return float(value)
    if unit == 'pct':    return float(value) * 100
    if unit == 'rel %':  return float(value) * 100
    return np.nan

def group_direction_score(sub):
    bps_vals = [to_bps(r['Value'], r['Unit']) for _, r in sub.iterrows()]
    bps_vals = [v for v in bps_vals if not np.isnan(v)]
    return float(np.mean(bps_vals)) if bps_vals else np.nan

def scenario_direction(score):
    if pd.isna(score): return 'zero'
    if score > 0:      return 'pos'
    if score < 0:      return 'neg'
    return 'zero'

def count_directions(df_sub):
    n_pos = n_neg = n_zero = 0
    for _, sc_df in df_sub.groupby('Scenario'):
        d = scenario_direction(group_direction_score(sc_df))
        if d == 'pos':   n_pos  += 1
        elif d == 'neg': n_neg  += 1
        else:            n_zero += 1
    return n_pos, n_neg, n_zero

def get_scenario_directions(df_sub):
    return {sc: scenario_direction(group_direction_score(sc_df))
            for sc, sc_df in df_sub.groupby('Scenario')}

def clean_items(series):
    return sorted([str(i) for i in series.dropna().unique()
                   if str(i).strip() not in ('', 'nan')])

def format_shock(value, unit):
    if pd.isna(value):
        return "—"
    unit = str(unit).strip() if not pd.isna(unit) else ''
    val_str = f"{value:+.1f}" if not pd.isna(value) else "—"
    if unit:
        return f"{val_str} {unit}"
    return val_str

# ─── DATA ──────────────────────────────────────────────────────────────────────
FILE_PATH = "Lista_scenari_shocks.xlsx"

@st.cache_data
def load_data():
    df = pd.read_excel(FILE_PATH, sheet_name="Shocks")
    df = df.rename(columns={'Livello 1': 'L1', 'Livello 2': 'L2', 'Livello 3': 'L3'})

    for col in ['Scenario', 'Scenario Type', 'L1', 'L2', 'L3', 'Factor', 'Unit']:
        df[col] = df[col].astype(str).str.strip()
        df[col] = df[col].replace('nan', np.nan)

    df = df.dropna(subset=['Scenario', 'L1'])
    df = df[df['L1'].str.strip().astype(bool)]

    desc_map = (
        df.dropna(subset=['Description'])
          .drop_duplicates(subset='Scenario')[['Scenario', 'Description']]
          .set_index('Scenario')['Description']
          .to_dict()
    ) if 'Description' in df.columns else {}
    type_map = (
        df.drop_duplicates(subset='Scenario')[['Scenario', 'Scenario Type']]
          .set_index('Scenario')['Scenario Type']
          .to_dict()
    )
    return df, desc_map, type_map

try:
    df, desc_map, type_map = load_data()
except FileNotFoundError:
    st.error(f"File `{FILE_PATH}` not found.")
    st.stop()

# ─── GEO DATA ─────────────────────────────────────────────────────────────────


# ── Factor → ISO3 specifico (paese singolo) ───────────────────────────────────
FACTOR_TO_ISO3 = {
    # Europe
    'Austria ATX': 'AUT', 'Belgium 20': 'BEL', 'DAX 30': 'DEU',
    'Denmark OMX Copenhag20': 'DNK', 'FTSE 100': 'GBR',
    'FTSE All Share - FTSE 100': 'GBR', 'France CAC 40': 'FRA',
    'Greece ASE/General': 'GRC', 'Ireland ISEQ/General': 'IRL',
    'Italy S&P MIB': 'ITA', 'Italy S&P MIB - MSCI EUROPE(EUR)': 'ITA',
    'Luxembourg LUXX': 'LUX', 'Netherlands AEX Stk': 'NLD',
    'Poland WIG': 'POL', 'Portugal PSI 20': 'PRT',
    'Spain IBEX 35': 'ESP', 'Sweden OMX': 'SWE', 'Switzerland SMI': 'CHE',
    # Emerging Markets - indici
    'Brazil Bovespa': 'BRA', 'China Shanghai SECmp': 'CHN',
    'China Shenzhen SEAll': 'CHN', 'Czech Republic PX 50': 'CZE',
    'Hungary BUX': 'HUN', 'India BSE 100': 'IND',
    'Korea KOSPI Comp': 'KOR', 'Mexican Bolsa': 'MEX',
    'Pakistan KSE 100': 'PAK', 'Philippines PSEi': 'PHL',
    'Russia RTS': 'RUS', 'Taiwan TSEC': 'TWN', 'Taiwan TWSE': 'TWN',
    'Turkey ISE Natl 100': 'TUR',
    # Emerging Markets - Country Allocation
    'Argentina': 'ARG', 'Brazil': 'BRA', 'China Domestic': 'CHN',
    'China Offshore': 'CHN', 'Hungary': 'HUN', 'Indonesia': 'IDN',
    'Mexico': 'MEX', 'Pakistan': 'PAK', 'Qatar': 'QAT',
    'Saudi Arabia': 'SAU', 'South Africa': 'ZAF', 'Taiwan': 'TWN',
    'Turkey': 'TUR', 'Ukraine': 'UKR', 'Venezuela': 'VEN', 'Viet Nam': 'VNM',
    # Pacific ex Japan
    'Hang Seng': 'HKG', 'S&P ASX 200': 'AUS', 'Singapore StraitsTms': 'SGP',
    # North America
    'Canada': 'CAN',
    # Japan
    'NIKKEI 225': 'JPN', 'NIKKEI 225 - MSCI World Net TR': 'JPN',
    'MSCI Japan - MSCI World Net TR': 'JPN', 'MSCI Japan - MSCI EUROPE(EUR)': 'JPN',
    # US
    'S&P 500': 'USA', 'Nasdaq': 'USA', 'VIX': 'USA', 'VIX Volatility': 'USA',
    'S&P Mid Cap': 'USA', 'S&P Small Cap': 'USA',
    'Russell 1000 - Russell 2000': 'USA',
    'Russell 3000 Growth - Russell 3000 Value': 'USA',
}

# ISO3 -> Area
_ISO3_TO_AREA = {
    'USA': 'US', 'CAN': 'North America',
    'GBR': 'Europe', 'DEU': 'Europe', 'FRA': 'Europe', 'ITA': 'Europe',
    'ESP': 'Europe', 'CHE': 'Europe', 'NLD': 'Europe', 'BEL': 'Europe',
    'SWE': 'Europe', 'NOR': 'Europe', 'DNK': 'Europe', 'FIN': 'Europe',
    'AUT': 'Europe', 'POL': 'Europe', 'PRT': 'Europe', 'GRC': 'Europe',
    'IRL': 'Europe', 'LUX': 'Europe',
    'JPN': 'Japan',
    'AUS': 'Pacific ex Japan', 'HKG': 'Pacific ex Japan',
    'SGP': 'Pacific ex Japan', 'NZL': 'Pacific ex Japan',
    'KOR': 'Pacific ex Japan', 'TWN': 'Pacific ex Japan',
    'CHN': 'Emerging Markets', 'IND': 'Emerging Markets',
    'BRA': 'Emerging Markets', 'MEX': 'Emerging Markets',
    'RUS': 'Emerging Markets', 'ZAF': 'Emerging Markets',
    'TUR': 'Emerging Markets', 'SAU': 'Emerging Markets',
    'IDN': 'Emerging Markets', 'THA': 'Emerging Markets',
    'MYS': 'Emerging Markets', 'PHL': 'Emerging Markets',
    'PAK': 'Emerging Markets', 'ARG': 'Emerging Markets',
    'CHL': 'Emerging Markets', 'COL': 'Emerging Markets',
    'PER': 'Emerging Markets', 'VEN': 'Emerging Markets',
    'EGY': 'Emerging Markets', 'MAR': 'Emerging Markets',
    'NGA': 'Emerging Markets', 'QAT': 'Emerging Markets',
    'ARE': 'Emerging Markets', 'ISR': 'Emerging Markets',
    'HUN': 'Emerging Markets', 'CZE': 'Emerging Markets',
    'UKR': 'Emerging Markets', 'VNM': 'Emerging Markets',
}


@st.cache_data
def load_geo_data():
    df_raw = pd.read_excel(FILE_PATH, sheet_name="Shocks")
    if 'Country' not in df_raw.columns:
        return pd.DataFrame(columns=[
            'Scenario', 'Scenario Type', 'Area', 'ISO3', 'Value', 'Factor', 'level'
        ])

    sub = df_raw[df_raw['Country'].notna()][
        ['Scenario', 'Scenario Type', 'Factor', 'Country', 'Value']
    ].copy()

    rows = []
    for _, r in sub.iterrows():
        iso3_specific = FACTOR_TO_ISO3.get(str(r['Factor']).strip())
        rows.append({
            'Scenario':      r['Scenario'],
            'Scenario Type': r['Scenario Type'],
            'Area':          r['Country'],
            'ISO3':          iso3_specific if iso3_specific else None,
            'Value':         r['Value'],
            'Factor':        r['Factor'],
            'level':         'country' if iso3_specific else 'area',
        })
    return pd.DataFrame(rows)



try:
    geo_df = load_geo_data()
    GEO_AVAILABLE = not geo_df.empty
except Exception:
    geo_df = pd.DataFrame()
    GEO_AVAILABLE = False


# ─── EXPORT ───────────────────────────────────────────────────────────────────
def build_export_bytes(df_sub, include_all_scenarios=False):
    cols_out = ['Scenario', 'Scenario Type', 'Description', 'Factor',
                'Value', 'Unit', 'Extra', 'L3', 'L2', 'L1']
    cols_out = [c for c in cols_out if c in df_sub.columns]

    if include_all_scenarios:
        all_known = set(desc_map.keys()) | set(type_map.keys())
        present   = set(df_sub['Scenario'].unique())
        missing   = all_known - present
        if missing:
            empty_rows = pd.DataFrame([{
                'Scenario':      sc,
                'Scenario Type': type_map.get(sc, ''),
                'Description':   desc_map.get(sc, ''),
                'Factor': '', 'Value': np.nan, 'Unit': '',
                'Extra': '', 'L3': '', 'L2': '', 'L1': '',
            } for sc in sorted(missing)])
            df_sub = pd.concat([df_sub, empty_rows], ignore_index=True)

    export_df = df_sub[cols_out].sort_values(
        ['Scenario', 'L1', 'L2', 'L3'], na_position='last'
    ).copy()
    export_df = export_df.rename(columns={'L1': 'Livello 1', 'L2': 'Livello 2', 'L3': 'Livello 3'})

    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine='openpyxl') as writer:
        export_df.to_excel(writer, index=False, sheet_name='Scenarios')
        ws = writer.sheets['Scenarios']
        for col_cells in ws.columns:
            max_len = max((len(str(c.value or '')) for c in col_cells), default=10)
            ws.column_dimensions[col_cells[0].column_letter].width = min(max_len + 4, 60)
    buf.seek(0)
    return buf.getvalue()

# ─── SESSION STATE ─────────────────────────────────────────────────────────────
for k, v in {
    'sel_l1_set': set(), 'sel_l1_single': None, 'sel_l2': None, 'sel_l3': None,
    'mode': 'drill', 'shock_filter': 'all', 'quick_view': None, 'multi_dir_filter': None,
    'scenario_type': 'All', 'geo_area': None,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─── HEADER ────────────────────────────────────────────────────────────────────
_n_sc = df['Scenario'].nunique()
_n_l1 = df['L1'].nunique()

st.markdown(f"""
<div class="fin-header">
  <div class="fin-logo">ST</div>
  <div class="fin-brand-text">
    <div class="main-title">Stress Test Mapping</div>
    <div class="subtitle">Asset class drill-down · Shock direction analysis</div>
  </div>
</div>
""", unsafe_allow_html=True)

_l1_counts = df.groupby('L1')['Scenario'].nunique().sort_values(ascending=False)
_max_c = max(_l1_counts.values) if len(_l1_counts) else 1

_hm_cells = ''
for l1_name, cnt in _l1_counts.items():
    bar_h = max(3, int(16 * cnt / _max_c))
    bar_svg = (f'<svg width="48" height="16" style="display:block;margin-top:3px">'
               f'<rect x="0" y="{16-bar_h}" width="48" height="{bar_h}" '
               f'fill="#ff4b4b" rx="2" opacity="0.7"/>'
               f'</svg>')
    _hm_cells += (f'<div class="hm-cell">'
                  f'<div class="hm-label">{str(l1_name)[:15]}</div>'
                  f'<div class="hm-count">{cnt}</div>'
                  f'{bar_svg}'
                  f'</div>')

st.markdown(f"""
<div class="hm-strip">
  <div class="hm-strip-title">
    Scenarios per asset class &nbsp;·&nbsp; {_n_sc} total &nbsp;·&nbsp; {_n_l1} classes
  </div>
  {_hm_cells}
</div>
""", unsafe_allow_html=True)

# Mode buttons + download all
col_m1, col_m2, col_m3, col_m4 = st.columns([2, 2, 2, 6])
with col_m1:
    if st.button("🔍 Single Asset Class Analysis", use_container_width=True):
        st.session_state.update({'mode': 'drill', 'sel_l1_set': set(), 'sel_l1_single': None,
                                  'sel_l2': None, 'sel_l3': None, 'shock_filter': 'all',
                                  'quick_view': None, 'multi_dir_filter': None, 'geo_area': None})
        st.rerun()
with col_m2:
    if st.button("🔀 Multi Asset Class Analysis", use_container_width=True):
        st.session_state.update({'mode': 'multi', 'sel_l2': None, 'sel_l3': None,
                                  'shock_filter': 'all', 'quick_view': None,
                                  'multi_dir_filter': None, 'geo_area': None})
        st.rerun()
with col_m3:
    if st.button("🌍 Geographic Map", use_container_width=True):
        st.session_state.update({'mode': 'map', 'geo_area': None})
        st.rerun()
with col_m4:
    inner_left, inner_right = st.columns([5, 3])
    with inner_right:
        st.download_button(
            label="⬇ Download All Scenarios",
            data=build_export_bytes(df, include_all_scenarios=True),
            file_name="all_scenarios.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="dl_all",
            use_container_width=True,
        )
with col_m4:
    st.markdown("""
    <style>
    .method-tip { display:inline-flex; align-items:center; gap:7px; margin-top:6px; }
    .method-icon {
        display:inline-flex; align-items:center; justify-content:center;
        width:20px; height:20px; border-radius:50%;
        background:#f3f4f6; border:1px solid #d1d5db;
        color:#6b7280; font-size:0.72rem; font-weight:700;
        cursor:default; flex-shrink:0; position:relative;
    }
    .method-label { font-size:0.72rem; color:#9ca3af; }
    .method-icon:hover .method-popup { display:block; }
    .method-popup {
        display:none; position:absolute; left:26px; top:-8px;
        background:#1f2937; color:#f9fafb;
        font-size:0.70rem; line-height:1.6;
        padding:10px 13px; border-radius:8px;
        width:320px; z-index:9999;
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    }
    .method-popup b { color:#ffffff; }
    .method-popup .mp-title {
        font-size:0.72rem; font-weight:700; color:#e5e7eb;
        border-bottom:1px solid #374151; padding-bottom:5px; margin-bottom:7px;
    }
    .mp-row { margin-bottom:5px; }
    .mp-green { color:#4ade80; font-weight:600; }
    .mp-red   { color:#f87171; font-weight:600; }
    .mp-amber { color:#fbbf24; font-weight:600; }
    </style>
    <div class="method-tip">
        <div class="method-icon">?
            <div class="method-popup">
                <div class="mp-title">📐 How scenario direction is determined</div>
                <div class="mp-row">For each scenario, all shocks belonging to the selected <b>asset class</b> (or sub-level) are collected and converted to a <b>common unit (bps)</b>:</div>
                <div class="mp-row">· bps → as-is &nbsp;· pct × 100 &nbsp;· rel% × 100</div>
                <div class="mp-row"><b>Excluded</b>: pct/yr, Price, Index Level, FX Rate — these are absolute levels, not directional shocks.</div>
                <div class="mp-row">The <b>arithmetic mean</b> of all converted values is computed:</div>
                <div class="mp-row"><span class="mp-green">▲ Positive</span> — mean &gt; 0</div>
                <div class="mp-row"><span class="mp-red">▼ Negative</span> — mean &lt; 0</div>
                <div class="mp-row"><span class="mp-amber">~ Mixed</span> — mean = 0, or no directional shocks available</div>
                <div class="mp-row" style="margin-top:8px;color:#9ca3af;font-size:0.65rem;">
                Direction re-evaluates as you drill down: at L2 only that L2's shocks are used, at L3 only that L3's shocks.</div>
            </div>
        </div>
        <span class="method-label">Direction methodology</span>
    </div>
    """, unsafe_allow_html=True)
st.markdown("---")

# ─── FILTRO SCENARIO TYPE ──────────────────────────────────────────────────────
_sc_brs   = df[df['Scenario Type'] == 'BRS']['Scenario'].nunique()
_sc_ec    = df[df['Scenario Type'] == 'EC']['Scenario'].nunique()
_sc_all   = df['Scenario'].nunique()
_cur_type = st.session_state.scenario_type

def _chip_cls(kind, active):
    return f"chip-visual chip-{kind}" + (" chip-active" if active else "")

st.markdown("""
<style>
.chip-visual { pointer-events: none; display: inline-flex; align-items: center;
    gap: 5px; font-size: 0.72rem; font-weight: 600; padding: 5px 16px;
    border-radius: 20px; border: 1.5px solid transparent; white-space: nowrap;
    user-select: none; }
.chip-all  { background:#f3f4f6; color:#374151; border-color:#d1d5db; }
.chip-brs  { background:#eff6ff; color:#1d4ed8; border-color:#bfdbfe; }
.chip-ec   { background:#f0fdf4; color:#15803d; border-color:#bbf7d0; }
.chip-all.chip-active  { background:#1f2937; color:#fff;    border-color:#1f2937; }
.chip-brs.chip-active  { background:#1d4ed8; color:#fff;    border-color:#1d4ed8; }
.chip-ec.chip-active   { background:#15803d; color:#fff;    border-color:#15803d; }
div[data-testid="stHorizontalBlock"]:has(button[data-testid="baseButton-secondary"]) {
    margin-top: -2.15rem !important;
    height: 2.1rem !important;
    overflow: visible !important;
    position: relative !important;
    z-index: 20 !important;
}
div[data-testid="stHorizontalBlock"]:has(button[data-testid="baseButton-secondary"])
  button[data-testid="baseButton-secondary"] {
    opacity: 0 !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    cursor: pointer !important;
    width: 100% !important;
    height: 2.1rem !important;
    padding: 0 !important;
    position: relative !important;
    z-index: 20 !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown(f"""
<div style="display:flex;align-items:center;gap:8px;background:#f8f9fb;
            border:1px solid #e6e6e6;border-radius:8px;padding:7px 14px;
            margin-bottom:0.6rem;">
  <span style="font-size:0.65rem;color:#9ca3af;text-transform:uppercase;
               letter-spacing:0.08em;white-space:nowrap;margin-right:4px;">Scenario type</span>
  <span class="{_chip_cls('all', _cur_type=='All')}">All
    <span style="font-weight:400;font-size:0.65rem;">({_sc_all})</span></span>
  <span class="{_chip_cls('brs', _cur_type=='BRS')}">BRS
    <span style="font-weight:400;font-size:0.65rem;">({_sc_brs})</span></span>
  <span class="{_chip_cls('ec',  _cur_type=='EC')}">EC
    <span style="font-weight:400;font-size:0.65rem;">({_sc_ec})</span></span>
</div>
""", unsafe_allow_html=True)

_tc1, _tc2, _tc3, _tc_spacer = st.columns([1, 1, 1, 9])
with _tc1:
    if st.button(f"All", key="tf_all", use_container_width=True):
        st.session_state.update({'scenario_type': 'All', 'sel_l1_single': None,
                                  'sel_l2': None, 'sel_l3': None, 'sel_l1_set': set(),
                                  'shock_filter': 'all', 'quick_view': None})
        st.rerun()
with _tc2:
    if st.button(f"BRS", key="tf_brs", use_container_width=True):
        st.session_state.update({'scenario_type': 'BRS', 'sel_l1_single': None,
                                  'sel_l2': None, 'sel_l3': None, 'sel_l1_set': set(),
                                  'shock_filter': 'all', 'quick_view': None})
        st.rerun()
with _tc3:
    if st.button(f"EC", key="tf_ec", use_container_width=True):
        st.session_state.update({'scenario_type': 'EC', 'sel_l1_single': None,
                                  'sel_l2': None, 'sel_l3': None, 'sel_l1_set': set(),
                                  'shock_filter': 'all', 'quick_view': None})
        st.rerun()

_type_sel = st.session_state.scenario_type
if _type_sel in ('BRS', 'EC'):
    df = df[df['Scenario Type'] == _type_sel]

st.markdown("---")

# ─── JS colora bottoni ─────────────────────────────────────────────────────────
components.html("""
<script>
(function() {
    function styleMiniBtns(doc) {
        doc.querySelectorAll('button').forEach(function(btn) {
            var txt = (btn.innerText || btn.textContent || '').trim();
            if (txt.includes('Positive')) {
                btn.style.setProperty('background-color', '#16a34a', 'important');
                btn.style.setProperty('color', '#ffffff', 'important');
                btn.style.setProperty('border', '1.5px solid #15803d', 'important');
                btn.style.setProperty('font-size', '0.72rem', 'important');
                btn.style.setProperty('font-weight', '600', 'important');
                btn.style.setProperty('min-height', '28px', 'important');
                btn.style.setProperty('height', '28px', 'important');
                btn.style.setProperty('padding', '0 8px', 'important');
                btn.style.setProperty('border-radius', '5px', 'important');
            } else if (txt.includes('Negative')) {
                btn.style.setProperty('background-color', '#dc2626', 'important');
                btn.style.setProperty('color', '#ffffff', 'important');
                btn.style.setProperty('border', '1.5px solid #b91c1c', 'important');
                btn.style.setProperty('font-size', '0.72rem', 'important');
                btn.style.setProperty('font-weight', '600', 'important');
                btn.style.setProperty('min-height', '28px', 'important');
                btn.style.setProperty('height', '28px', 'important');
                btn.style.setProperty('padding', '0 8px', 'important');
                btn.style.setProperty('border-radius', '5px', 'important');
            } else if (txt.includes('Mixed')) {
                btn.style.setProperty('background-color', '#1f2937', 'important');
                btn.style.setProperty('color', '#ffffff', 'important');
                btn.style.setProperty('border', '1.5px solid #111827', 'important');
                btn.style.setProperty('font-size', '0.72rem', 'important');
                btn.style.setProperty('font-weight', '600', 'important');
                btn.style.setProperty('min-height', '28px', 'important');
                btn.style.setProperty('height', '28px', 'important');
                btn.style.setProperty('padding', '0 8px', 'important');
                btn.style.setProperty('border-radius', '5px', 'important');
            }
        });
    }
    var target = window.parent.document.body;
    styleMiniBtns(window.parent.document);
    var observer = new MutationObserver(function() { styleMiniBtns(window.parent.document); });
    observer.observe(target, { childList: true, subtree: true });
})();
</script>
""", height=0)

# ─── EXPORT ROW ───────────────────────────────────────────────────────────────
def render_export_row(df_full, df_display, fname_base):
    n = df_display['Scenario'].nunique()
    scenarios_to_export = df_display['Scenario'].unique()
    df_export = df[df['Scenario'].isin(scenarios_to_export)]
    col_info, col_dl, _ = st.columns([2.5, 2, 6])
    with col_info:
        st.markdown(
            f'<div style="font-size:0.72rem;color:#6b6b6b;padding-top:8px;">'
            f'{"1 scenario found" if n == 1 else f"{n} scenarios found"}<br>'
            f'<span style="font-size:0.65rem;color:#9ca3af;font-style:italic;">'
            f'Export includes all shocks for these scenarios.</span>'
            f'</div>',
            unsafe_allow_html=True
        )
    with col_dl:
        st.download_button(
            label="⬇ Export Excel",
            data=build_export_bytes(df_export),
            file_name=f"{fname_base}.xlsx".replace(' ', '_'),
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key=f"dl_{fname_base}_{id(df_display)}",
            use_container_width=True,
        )

# ─── SCENARIO ROWS ─────────────────────────────────────────────────────────────
def render_scenario_rows(df_display, df_all_shocks, th_class="", path_mode=False):
    th_color = {"pos-th": "#16a34a", "neg-th": "#dc2626",
                "mix-th": "#b45309"}.get(th_class, "#ff4b4b")

    st.markdown(f"""
    <table class="scenario-table" style="margin-bottom:0">
        <thead><tr>
            <th class="{th_class}" style="background:{th_color};width:30%">Scenario</th>
            <th class="{th_class}" style="background:{th_color}">Factors (L3) · Shock Value</th>
            <th class="{th_class}" style="background:{th_color};width:40px"></th>
        </tr></thead>
    </table>""", unsafe_allow_html=True)

    for scenario in sorted(df_display['Scenario'].unique()):
        sc_rows  = df_display[df_display['Scenario'] == scenario].sort_values('L3')
        long_des = desc_map.get(str(scenario).strip(), '')
        sc_type  = type_map.get(str(scenario).strip(), '')
        badge_cls = 'type-brs' if sc_type == 'BRS' else 'type-ec'

        factors_html = '<div class="factor-list" style="margin-top:0">'
        for _, r in sc_rows.iterrows():
            val  = r['Value']
            unit = r['Unit'] if not pd.isna(r['Unit']) else ''
            shock_str = format_shock(val, unit)

            _fc = str(r.get('Factor', '')).strip()
            _factor_suffix = (
                f' <span style="color:#9ca3af;font-size:0.72rem;font-weight:400;">· {_fc}</span>'
                if _fc not in ('', 'nan') else ''
            )
            if path_mode:
                _path = " › ".join([str(r[c]) for c in ['L1', 'L2', 'L3']
                                    if str(r.get(c, '')).strip() not in ('', 'nan')])
                factor_label = _path + _factor_suffix
            else:
                _l3 = str(r['L3']) if str(r.get('L3', '')).strip() not in ('', 'nan') else '—'
                factor_label = _l3 + _factor_suffix

            try:
                is_num = not pd.isna(val)
                num = float(val)
            except:
                is_num = False
                num = np.nan

            bps_v = to_bps(val, unit)
            if not pd.isna(bps_v):
                if bps_v > 0:   val_cls, arrow = "factor-val-pos", "▲ "
                elif bps_v < 0: val_cls, arrow = "factor-val-neg", "▼ "
                else:           val_cls, arrow = "factor-val-zero", ""
            elif is_num and num > 0:   val_cls, arrow = "factor-val-pos", "▲ "
            elif is_num and num < 0:   val_cls, arrow = "factor-val-neg", "▼ "
            else:                      val_cls, arrow = "factor-val-zero", ""

            factors_html += (f'<div class="factor-row">'
                             f'<span class="factor-name">{factor_label}</span>'
                             f'<span class="{val_cls}">{arrow}{shock_str}</span>'
                             f'</div>')
        factors_html += '</div>'
        des_html = f'<div class="long-des">{long_des}</div>' if long_des else ''
        badge_html = f'<span class="type-badge {badge_cls}">{sc_type}</span>'

        col_sc, col_factors, col_dl = st.columns([3, 6, 0.7])
        with col_sc:
            st.markdown(
                f'<div style="padding:8px 12px;border-bottom:1px solid #f0f0f0;'
                f'border-left:1px solid #e6e6e6;min-height:48px;">'
                f'<strong>{scenario}</strong>{badge_html}{des_html}</div>',
                unsafe_allow_html=True
            )
        with col_factors:
            st.markdown(
                f'<div style="padding:4px 12px;border-bottom:1px solid #f0f0f0;'
                f'border-left:1px solid #e6e6e6;">{factors_html}</div>',
                unsafe_allow_html=True
            )
        with col_dl:
            df_sc_full = df_all_shocks[df_all_shocks['Scenario'] == scenario]
            st.download_button(
                label="⬇",
                data=build_export_bytes(df_sc_full),
                file_name=f"scenario_{scenario}.xlsx".replace(' ', '_'),
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key=f"dl_sc_{scenario}_{th_class}",
                use_container_width=True,
                help=f"Download all shocks for {scenario}",
            )

# ─── QUICK-VIEW ───────────────────────────────────────────────────────────────
def render_quick_view(df_context, col_name):
    qv = st.session_state.quick_view
    if qv is None or qv['col'] != col_name:
        return
    item, direction = qv['item'], qv['dir']
    df_item  = df_context[df_context[col_name] == item].copy()
    sc_dirs  = get_scenario_directions(df_item)
    matching = [sc for sc, d in sc_dirs.items() if d == direction]

    if direction == 'pos':
        th_class   = "pos-th"
        label      = f"▲ Positive scenarios — {item}"
        df_display = df_item[df_item['Scenario'].isin(matching)]
        df_display = df_display[df_display['Value'].notna() & (df_display['Value'] > 0)]
    elif direction == 'neg':
        th_class   = "neg-th"
        label      = f"▼ Negative scenarios — {item}"
        df_display = df_item[df_item['Scenario'].isin(matching)]
        df_display = df_display[df_display['Value'].notna() & (df_display['Value'] < 0)]
    else:
        th_class   = "mix-th"
        label      = f"~ Mixed scenarios — {item}"
        df_display = df_item[df_item['Scenario'].isin(matching)]

    st.markdown(f'<div class="section-header">{label}</div>', unsafe_allow_html=True)
    col_close, _ = st.columns([1.2, 8])
    with col_close:
        if st.button("✕ Close", key=f"close_qv_{col_name}_{item}_{direction}"):
            st.session_state.quick_view = None
            st.rerun()
    if not matching:
        st.info("No scenarios found for this selection.")
        return
    render_export_row(df_item[df_item['Scenario'].isin(matching)], df_display,
                      f"scenarios_{item}_{direction}")
    render_scenario_rows(df_display, df, th_class)

# ─── CARD RENDERER ────────────────────────────────────────────────────────────
def render_cards(items, df_filtered, col_name, on_select_key, multi=False, show_mini=False):
    if not items: return
    ncols = min(len(items), 4)
    cols  = st.columns(ncols)

    for i, item in enumerate(items):
        sub   = df_filtered[df_filtered[col_name] == item]
        n_pos, n_neg, n_zero = count_directions(sub)
        is_sel    = (item in st.session_state.sel_l1_set) if multi else (st.session_state.get(on_select_key) == item)
        btn_label = f"{'✓ ' if is_sel else ''}{item}"

        with cols[i % ncols]:
            clicked = st.button(btn_label, key=f"btn_{on_select_key}_{item}", use_container_width=True)
            if show_mini:
                mc1, mc2, mc3 = st.columns(3)
                with mc1:
                    if st.button(f"▲ {n_pos}  Positive",
                                 key=f"mini_pos_{on_select_key}_{item}",
                                 use_container_width=True):
                        if multi:
                            st.session_state.sel_l1_set.add(item)
                            st.session_state.shock_filter = 'pos'
                            st.session_state.quick_view   = None
                        else:
                            st.session_state.quick_view = {'col': col_name, 'item': item, 'dir': 'pos'}
                        st.rerun()
                with mc2:
                    if st.button(f"~ {n_zero}  Mixed",
                                 key=f"mini_zero_{on_select_key}_{item}",
                                 use_container_width=True):
                        if multi:
                            st.session_state.sel_l1_set.add(item)
                            st.session_state.shock_filter = 'zero'
                            st.session_state.quick_view   = None
                        else:
                            st.session_state.quick_view = {'col': col_name, 'item': item, 'dir': 'zero'}
                        st.rerun()
                with mc3:
                    if st.button(f"▼ {n_neg}  Negative",
                                 key=f"mini_neg_{on_select_key}_{item}",
                                 use_container_width=True):
                        if multi:
                            st.session_state.sel_l1_set.add(item)
                            st.session_state.shock_filter = 'neg'
                            st.session_state.quick_view   = None
                        else:
                            st.session_state.quick_view = {'col': col_name, 'item': item, 'dir': 'neg'}
                        st.rerun()
            if clicked:
                st.session_state.quick_view = None
                if multi:
                    if item in st.session_state.sel_l1_set:
                        st.session_state.sel_l1_set.discard(item)
                    else:
                        st.session_state.sel_l1_set.add(item)
                    st.session_state.shock_filter     = 'all'
                    st.session_state.multi_dir_filter = None
                else:
                    cur = st.session_state.get(on_select_key)
                    st.session_state[on_select_key] = None if cur == item else item
                    if on_select_key == 'sel_l1_single':
                        st.session_state.sel_l2 = None
                        st.session_state.sel_l3 = None
                    elif on_select_key == 'sel_l2':
                        st.session_state.sel_l3 = None
                    st.session_state.shock_filter = 'all'
                st.rerun()

# ─── STAT BOXES ───────────────────────────────────────────────────────────────
def render_stat_boxes(df_sub):
    n_sc                 = df_sub['Scenario'].nunique()
    n_pos, n_neg, n_zero = count_directions(df_sub)
    cur_filter           = st.session_state.shock_filter

    tip_style = ('display:inline-flex;align-items:center;justify-content:center;'
                 'width:14px;height:14px;border-radius:50%;background:#e5e7eb;color:#6b7280;'
                 'font-size:0.6rem;font-weight:700;cursor:default;vertical-align:middle;')

    if n_zero > 0:
        c0, c1, c2, c3, _ = st.columns([1.2, 1.2, 1.2, 1.2, 5])
    else:
        c0, c1, c2, _ = st.columns([1.4, 1.4, 1.4, 7])

    with c0:
        st.markdown(f"""<div class="stat-box">
            <div class="sv">{n_sc}</div>
            <div class="sk">Total Scenarios</div>
        </div>""", unsafe_allow_html=True)
    with c1:
        active_pos = cur_filter == 'pos'
        st.markdown(
            f'<div style="font-size:0.68rem;color:#16a34a;font-weight:600;margin-bottom:2px;">'
            f'▲ Positive <span style="{tip_style}" title="Scenarios whose average shock (converted to bps) is positive.">?</span>'
            f'</div>', unsafe_allow_html=True)
        if st.button(f"▲ {n_pos}  Positive", key="filter_pos", use_container_width=True):
            st.session_state.shock_filter = 'all' if active_pos else 'pos'
            st.rerun()
        if active_pos:
            st.markdown('<div style="height:3px;background:#16a34a;border-radius:2px;margin-top:-6px;"></div>',
                        unsafe_allow_html=True)
    with c2:
        active_neg = cur_filter == 'neg'
        st.markdown(
            f'<div style="font-size:0.68rem;color:#dc2626;font-weight:600;margin-bottom:2px;">'
            f'▼ Negative <span style="{tip_style}" title="Scenarios whose average shock (converted to bps) is negative.">?</span>'
            f'</div>', unsafe_allow_html=True)
        if st.button(f"▼ {n_neg}  Negative", key="filter_neg", use_container_width=True):
            st.session_state.shock_filter = 'all' if active_neg else 'neg'
            st.rerun()
        if active_neg:
            st.markdown('<div style="height:3px;background:#dc2626;border-radius:2px;margin-top:-6px;"></div>',
                        unsafe_allow_html=True)
    if n_zero > 0:
        with c3:
            active_zero = cur_filter == 'zero'
            st.markdown(
                '<div style="font-size:0.68rem;color:#b45309;font-weight:600;margin-bottom:2px;">'
                '~ Mixed <span style="display:inline-flex;align-items:center;justify-content:center;'
                'width:14px;height:14px;border-radius:50%;background:#e5e7eb;color:#6b7280;'
                'font-size:0.6rem;font-weight:700;cursor:default;vertical-align:middle;" '
                'title="Scenarios with a mean shock of exactly zero.">?</span></div>',
                unsafe_allow_html=True)
            if st.button(f"~ {n_zero}  Mixed", key="filter_zero", use_container_width=True):
                st.session_state.shock_filter = 'all' if active_zero else 'zero'
                st.rerun()
            if active_zero:
                st.markdown('<div style="height:3px;background:#b45309;border-radius:2px;margin-top:-6px;"></div>',
                            unsafe_allow_html=True)

# ─── SCENARIO TABLE ───────────────────────────────────────────────────────────
def render_scenario_table(df_sub):
    render_stat_boxes(df_sub)
    f       = st.session_state.shock_filter
    sc_dirs = get_scenario_directions(df_sub)

    if f == 'pos':
        matching          = [sc for sc, d in sc_dirs.items() if d == 'pos']
        th_class, sign    = "pos-th", "pos"
    elif f == 'neg':
        matching          = [sc for sc, d in sc_dirs.items() if d == 'neg']
        th_class, sign    = "neg-th", "neg"
    elif f == 'zero':
        matching          = [sc for sc, d in sc_dirs.items() if d == 'zero']
        th_class, sign    = "mix-th", "zero"
    else:
        matching          = list(sc_dirs.keys())
        th_class, sign    = "", "all"

    if not matching:
        st.info("No scenarios found for this filter.")
        return

    df_matching = df_sub[df_sub['Scenario'].isin(matching)]

    if f == 'pos':
        df_display = df_matching[df_matching['Value'].notna() & (df_matching['Value'] > 0)]
    elif f == 'neg':
        df_display = df_matching[df_matching['Value'].notna() & (df_matching['Value'] < 0)]
    else:
        df_display = df_matching

    fname = f"scenarios_{st.session_state.get('sel_l3', st.session_state.get('sel_l2', 'export'))}_{sign}"
    render_export_row(df_matching, df_display, fname)
    render_scenario_rows(df_display, df, th_class)


# ══════════════════════════════════════════════════════════════════════════════
# MODE A — SINGLE-ASSET DRILL-DOWN
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.mode == 'drill':
    qv = st.session_state.quick_view

    parts = ['<span>All</span>']
    if st.session_state.sel_l1_single:
        parts.append(f'<span class="sep">/</span><span>{st.session_state.sel_l1_single}</span>')
    if st.session_state.sel_l2:
        parts.append(f'<span class="sep">/</span><span>{st.session_state.sel_l2}</span>')
    if st.session_state.sel_l3:
        parts.append(f'<span class="sep">/</span><span>{st.session_state.sel_l3}</span>')
    st.markdown(f'<div class="breadcrumb">{"".join(parts)}</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-header">Level 1 Mapping — Asset Class</div>', unsafe_allow_html=True)
    render_cards(clean_items(df['L1']), df, 'L1', 'sel_l1_single', multi=False, show_mini=True)

    if qv and qv['col'] == 'L1':
        render_quick_view(df, 'L1')

    elif st.session_state.sel_l1_single:
        df_l1    = df[df['L1'] == st.session_state.sel_l1_single]
        l2_items = clean_items(df_l1['L2'])

        col_b, _ = st.columns([1, 5])
        with col_b:
            if st.button("← Reset L1", key="back_l1"):
                st.session_state.update({'sel_l1_single': None, 'sel_l2': None,
                                          'sel_l3': None, 'shock_filter': 'all', 'quick_view': None})
                st.rerun()

        if l2_items:
            st.markdown(f'<div class="section-header">Level 2 — {st.session_state.sel_l1_single}</div>',
                        unsafe_allow_html=True)
            render_cards(l2_items, df_l1, 'L2', 'sel_l2', multi=False, show_mini=True)

            if qv and qv['col'] == 'L2':
                render_quick_view(df_l1, 'L2')

            elif st.session_state.sel_l2:
                df_l2    = df[(df['L1'] == st.session_state.sel_l1_single) &
                              (df['L2'] == st.session_state.sel_l2)]
                l3_items = clean_items(df_l2['L3'])

                col_b2, _ = st.columns([1, 5])
                with col_b2:
                    if st.button("← Reset L2", key="back_l2"):
                        st.session_state.update({'sel_l2': None, 'sel_l3': None,
                                                  'shock_filter': 'all', 'quick_view': None})
                        st.rerun()

                if l3_items:
                    st.markdown(f'<div class="section-header">Level 3 — {st.session_state.sel_l2}</div>',
                                unsafe_allow_html=True)
                    render_cards(l3_items, df_l2, 'L3', 'sel_l3', multi=False, show_mini=False)

                if st.session_state.sel_l3:
                    df_l3 = df[(df['L1'] == st.session_state.sel_l1_single) &
                               (df['L2'] == st.session_state.sel_l2) &
                               (df['L3'] == st.session_state.sel_l3)]
                    col_b3, _ = st.columns([1, 5])
                    with col_b3:
                        if st.button("← Reset L3", key="back_l3"):
                            st.session_state.update({'sel_l3': None, 'shock_filter': 'all'})
                            st.rerun()
                    st.markdown(f'<div class="section-header">Scenarios — {st.session_state.sel_l3}</div>',
                                unsafe_allow_html=True)
                    render_scenario_table(df_l3)


# ══════════════════════════════════════════════════════════════════════════════
# MODE B — MULTI-ASSET
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.mode == 'multi':
    qv = st.session_state.quick_view

    st.markdown(
        '<div class="hint-box">'
        '💡 Select one or more Level-1 areas. With a single area you see all its scenarios. '
        'With multiple areas you see scenarios <strong>common to all</strong>.<br>'
        '🎯 Use <strong>▲ Positive / ▼ Negative</strong> buttons on each card to cross-filter by direction.'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown('<div class="section-header">Select Asset Class (multi-select)</div>', unsafe_allow_html=True)
    render_cards(clean_items(df['L1']), df, 'L1', 'sel_l1_set', multi=True, show_mini=True)

    if qv and qv['col'] == 'L1':
        render_quick_view(df, 'L1')

    elif st.session_state.sel_l1_set:
        pills_html = " ".join([f'<span class="sel-pill">✓ {x}</span>'
                                for x in sorted(st.session_state.sel_l1_set)])
        st.markdown(f'<div style="margin:8px 0 4px;">{pills_html}</div>', unsafe_allow_html=True)

        col_clear, _ = st.columns([1.5, 8])
        with col_clear:
            if st.button("✕ Clear selection", key="clear_multi"):
                st.session_state.update({'sel_l1_set': set(), 'shock_filter': 'all',
                                          'quick_view': None, 'multi_dir_filter': None})
                st.rerun()

        selected_list = sorted(st.session_state.sel_l1_set)

        if len(selected_list) == 1:
            df_show = df[df['L1'].isin(selected_list)].copy()
            label   = f"Scenarios in: {selected_list[0]}"
        else:
            sets_per_l1 = [set(df[df['L1'] == l1]['Scenario'].unique()) for l1 in selected_list]
            common      = sets_per_l1[0].intersection(*sets_per_l1[1:])
            df_show     = df[df['L1'].isin(selected_list) & df['Scenario'].isin(common)].copy()
            label       = f"Common scenarios: {' · '.join(selected_list)}"

        if df_show.empty:
            st.info("No scenarios shared across all selected areas.")
        else:
            st.markdown(f'<div class="section-header">{label}</div>', unsafe_allow_html=True)
            all_scenarios = sorted(df_show['Scenario'].unique())

            dir_matrix = {}
            for l1 in selected_list:
                sub_l1 = df_show[df_show['L1'] == l1]
                for sc, sc_df in sub_l1.groupby('Scenario'):
                    dir_matrix.setdefault(sc, {})[l1] = scenario_direction(group_direction_score(sc_df))

            def filter_by_direction(direction):
                return [sc for sc in all_scenarios
                        if all(dir_matrix.get(sc, {}).get(l1) == direction for l1 in selected_list)]

            pos_scenarios  = filter_by_direction('pos')
            neg_scenarios  = filter_by_direction('neg')
            zero_scenarios = [sc for sc in all_scenarios
                              if sc not in pos_scenarios and sc not in neg_scenarios]
            has_zero       = len(zero_scenarios) > 0
            cur_mf         = st.session_state.shock_filter

            tooltip_css = """
            <style>
            .tip-wrap { display:inline-flex; align-items:center; gap:6px; position:relative; }
            .tip-icon {
                display:inline-flex; align-items:center; justify-content:center;
                width:16px; height:16px; border-radius:50%;
                background:#e5e7eb; color:#6b7280;
                font-size:0.65rem; font-weight:700; cursor:default; flex-shrink:0;
            }
            .tip-icon:hover .tip-text { display:block; }
            .tip-text {
                display:none; position:absolute; left:22px; top:-4px;
                background:#1f2937; color:#f9fafb;
                font-size:0.68rem; line-height:1.45;
                padding:7px 10px; border-radius:6px;
                width:240px; z-index:9999;
                box-shadow: 0 4px 12px rgba(0,0,0,0.25);
            }
            </style>
            """
            tips = {
                'pos': "Scenarios positive in <b>all selected asset classes</b>.",
                'neg': "Scenarios negative in <b>all selected asset classes</b>.",
                'zer': "No clear single direction across all selected areas.",
            }
            def tip_icon(key):
                return f'<span class="tip-icon">?<span class="tip-text">{tips[key]}</span></span>'

            st.markdown(tooltip_css, unsafe_allow_html=True)

            if has_zero:
                cfa, cfb, cfc, cfd, _ = st.columns([1.1, 1.3, 1.3, 1.3, 3])
            else:
                cfa, cfb, cfc, _ = st.columns([1.2, 1.4, 1.4, 5])

            with cfa:
                st.markdown(f"""<div class="stat-box">
                    <div class="sv">{len(all_scenarios)}</div>
                    <div class="sk">Total common</div>
                </div>""", unsafe_allow_html=True)
            with cfb:
                active_pos = cur_mf == 'pos'
                st.markdown(f'<div style="font-size:0.68rem;color:#16a34a;font-weight:600;margin-bottom:2px;">▲ Positive {tip_icon("pos")}</div>',
                            unsafe_allow_html=True)
                if st.button(f"▲ {len(pos_scenarios)}  positive", key="mf_pos", use_container_width=True):
                    st.session_state.shock_filter = 'all' if active_pos else 'pos'
                    st.rerun()
                if active_pos:
                    st.markdown('<div style="height:3px;background:#16a34a;border-radius:2px;margin-top:-6px;"></div>',
                                unsafe_allow_html=True)
            with cfc:
                active_neg = cur_mf == 'neg'
                st.markdown(f'<div style="font-size:0.68rem;color:#dc2626;font-weight:600;margin-bottom:2px;">▼ Negative {tip_icon("neg")}</div>',
                            unsafe_allow_html=True)
                if st.button(f"▼ {len(neg_scenarios)}  negative", key="mf_neg", use_container_width=True):
                    st.session_state.shock_filter = 'all' if active_neg else 'neg'
                    st.rerun()
                if active_neg:
                    st.markdown('<div style="height:3px;background:#dc2626;border-radius:2px;margin-top:-6px;"></div>',
                                unsafe_allow_html=True)
            if has_zero:
                with cfd:
                    active_zero = cur_mf == 'zero'
                    st.markdown(f'<div style="font-size:0.68rem;color:#b45309;font-weight:600;margin-bottom:2px;">~ Mixed {tip_icon("zer")}</div>',
                                unsafe_allow_html=True)
                    if st.button(f"~ {len(zero_scenarios)}  Mixed", key="mf_zero", use_container_width=True):
                        st.session_state.shock_filter = 'all' if active_zero else 'zero'
                        st.rerun()
                    if active_zero:
                        st.markdown('<div style="height:3px;background:#b45309;border-radius:2px;margin-top:-6px;"></div>',
                                    unsafe_allow_html=True)

            if cur_mf == 'pos':
                active_scenarios = pos_scenarios; th_class, sign_filter = "pos-th", "pos"
            elif cur_mf == 'neg':
                active_scenarios = neg_scenarios; th_class, sign_filter = "neg-th", "neg"
            elif cur_mf == 'zero':
                active_scenarios = zero_scenarios; th_class, sign_filter = "mix-th", "zero"
            else:
                active_scenarios = all_scenarios; th_class, sign_filter = "", "all"

            if not active_scenarios:
                st.info("No scenarios match this direction filter across all selected areas.")
            else:
                df_active = df_show[df_show['Scenario'].isin(active_scenarios)]
                if sign_filter == 'pos':   df_display = df_active[df_active['Value'].notna() & (df_active['Value'] > 0)]
                elif sign_filter == 'neg': df_display = df_active[df_active['Value'].notna() & (df_active['Value'] < 0)]
                else:                      df_display = df_active
                fname = f"multi_{'_'.join(selected_list)}_{sign_filter}"
                render_export_row(df_active, df_display, fname)
                render_scenario_rows(df_display, df, th_class, path_mode=True)
    else:
        st.markdown(
            '<div style="font-size:0.78rem;color:#6b7280;margin-top:1rem;">'
            '← Click on one or more asset classes to view scenarios.</div>',
            unsafe_allow_html=True
        )


# ══════════════════════════════════════════════════════════════════════════════

# ══════════════════════════════════════════════════════════════════════════════
# MODE C — GEOGRAPHIC MAP
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.mode == 'map':
    import plotly.graph_objects as go

    if not GEO_AVAILABLE or geo_df.empty:
        st.warning("Geographic data not available.")
    else:
        _type_sel_geo = st.session_state.scenario_type
        geo_filtered = geo_df.copy()
        if _type_sel_geo in ('BRS', 'EC'):
            valid_scenarios = df['Scenario'].unique()
            geo_filtered = geo_filtered[geo_filtered['Scenario'].isin(valid_scenarios)]

        # Normalizza: vecchio formato stringa -> reset a None
        if not isinstance(st.session_state.geo_area, (dict, type(None))):
            st.session_state.geo_area = None
        sel = st.session_state.geo_area  # None | {'type':'area'|'country', 'value':str}

        # ── Aggrega per paese specifico (level=='country') ────────────────────
        country_df = geo_filtered[geo_filtered['level'] == 'country'].copy()
        country_agg = (
            country_df.groupby(['ISO3', 'Area'])['Scenario']
            .nunique().reset_index()
            .rename(columns={'Scenario': 'n_sc'})
        )

        max_n = max(country_agg['n_sc'].max() if not country_agg.empty else 1, 1)

        # ── Hover text per paese specifico ────────────────────────────────────
        hover_texts = []
        for _, row in country_agg.iterrows():
            scs = sorted(country_df[country_df['ISO3'] == row['ISO3']]['Scenario'].unique())
            sc_list = '<br>'.join(f'  · {s}' for s in scs[:8])
            if len(scs) > 8:
                sc_list += f'<br>  ... +{len(scs)-8} more'
            hover_texts.append(
                f"<b>{row['ISO3']} ({row['Area']})</b>"
                f"<br>Specific scenarios: <b>{row['n_sc']}</b>"
                f"<br><br>{sc_list}"
            )

        # ── Figura: solo paesi specifici colorati, resto grigio ───────────────
        fig = go.Figure()

        # Layer 1: paesi specifici (rosso, intensità = n scenari)
        if not country_agg.empty:
            fig.add_trace(go.Choropleth(
                locations=country_agg['ISO3'],
                z=country_agg['n_sc'],
                customdata=list(zip(
                    country_agg['ISO3'],
                    country_agg['Area'],
                    hover_texts,
                )),
                hovertemplate='%{customdata[2]}<extra></extra>',
                colorscale=[
                    [0.0, '#fee2e2'], [0.33, '#f87171'],
                    [0.66, '#dc2626'], [1.0,  '#7f1d1d'],
                ],
                zmin=0, zmax=max_n,
                marker_line_color='#e5e7eb', marker_line_width=0.6,
                showscale=True,
                colorbar=dict(
                    title=dict(text='Country\nscenarios', font=dict(size=10, color='#6b7280')),
                    tickfont=dict(size=9, color='#6b7280'),
                    len=0.45, thickness=11, x=1.01,
                    bgcolor='rgba(255,255,255,0.9)',
                    bordercolor='#e6e6e6', borderwidth=1,
                ),
            ))

        # Layer 2: highlight selezione corrente
        if sel:
            if sel['type'] == 'country':
                hi_rows = country_agg[country_agg['ISO3'] == sel['value']]
                if not hi_rows.empty:
                    fig.add_trace(go.Choropleth(
                        locations=[sel['value']],
                        z=[hi_rows['n_sc'].values[0]],
                        colorscale=[[0, '#ff4b4b'], [1, '#ff4b4b']],
                        showscale=False,
                        marker_line_color='#ff4b4b', marker_line_width=3,
                        hoverinfo='skip',
                    ))
            else:  # area selezionata: evidenzia tutti i paesi specifici dell'area
                area_iso3 = country_agg[country_agg['Area'] == sel['value']]['ISO3'].tolist()
                area_z    = country_agg[country_agg['Area'] == sel['value']]['n_sc'].tolist()
                if area_iso3:
                    fig.add_trace(go.Choropleth(
                        locations=area_iso3, z=area_z,
                        colorscale=[[0, '#ff4b4b'], [1, '#ff4b4b']],
                        showscale=False,
                        marker_line_color='#ff4b4b', marker_line_width=3,
                        hoverinfo='skip',
                    ))

        fig.update_layout(
            geo=dict(
                showframe=False, showcoastlines=True,
                coastlinecolor='#d1d5db', showland=True, landcolor='#f3f4f6',
                showocean=True, oceancolor='#eff6ff', showlakes=False,
                showcountries=True, countrycolor='#e5e7eb',
                projection_type='natural earth', bgcolor='#ffffff',
            ),
            paper_bgcolor='#ffffff', plot_bgcolor='#ffffff',
            margin=dict(l=0, r=0, t=8, b=0), height=480,
        )

        # ── Info strip ────────────────────────────────────────────────────────
        n_countries  = country_agg['ISO3'].nunique()
        n_areas      = geo_filtered['Area'].nunique()
        n_sc_geo     = geo_filtered['Scenario'].nunique()
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:16px;background:#f8f9fb;' 
            f'border:1px solid #e6e6e6;border-radius:8px;padding:8px 16px;margin-bottom:0.8rem;">' 
            f'<span style="font-size:0.65rem;color:#9ca3af;text-transform:uppercase;letter-spacing:0.08em;">Coverage</span>' 
            f'<span style="font-size:0.82rem;font-weight:700;color:#0e1117;">{n_countries} countries</span>' 
            f'<span style="color:#e6e6e6;">|</span>' 
            f'<span style="font-size:0.82rem;color:#6b7280;">{n_areas} areas · {n_sc_geo} scenarios</span>' 
            f'<span style="color:#e6e6e6;">|</span>' 
            f'<span style="font-size:0.72rem;color:#9ca3af;font-style:italic;">Click paese → scenari specifici + area &nbsp;·&nbsp; Click card area → tutti gli scenari area</span>' 
            f'</div>',
            unsafe_allow_html=True
        )

        # ── Mappa ─────────────────────────────────────────────────────────────
        event = st.plotly_chart(
            fig, use_container_width=True,
            on_select='rerun', key='geo_map', selection_mode='points',
        )

        if event and hasattr(event, 'selection') and event.selection:
            pts = event.selection.get('points', [])
            if pts:
                clicked_iso = pts[0].get('location')
                if clicked_iso:
                    # Controlla se è un paese specifico nel layer 0
                    if clicked_iso in country_agg['ISO3'].values:
                        new_sel = {'type': 'country', 'value': clicked_iso}
                    else:
                        area = _ISO3_TO_AREA.get(clicked_iso)
                        new_sel = {'type': 'area', 'value': area} if area else None
                    if new_sel and new_sel != st.session_state.geo_area:
                        st.session_state.geo_area = new_sel
                        st.rerun()

        # ── Cards area (sempre visibili sotto la mappa) ───────────────────────
        area_counts = (
            geo_filtered.groupby('Area')['Scenario']
            .nunique().reset_index()
            .rename(columns={'Scenario': 'n_sc'})
            .sort_values('n_sc', ascending=False)
            .reset_index(drop=True)
        )
        st.markdown('<div class="section-header">Geographic areas</div>', unsafe_allow_html=True)
        ncards = min(len(area_counts), 6)
        card_cols = st.columns(ncards)
        for i, crow in area_counts.iterrows():
            if i >= 6: break
            is_active = (sel and sel['type'] == 'area' and sel['value'] == crow['Area'])
            label = f"{'✓ ' if is_active else ''}{crow['Area']} ({crow['n_sc']})"
            with card_cols[i % ncards]:
                if st.button(label, key=f"geo_area_{crow['Area'].replace(' ', '_')}",
                             use_container_width=True):
                    new_sel = {'type': 'area', 'value': crow['Area']}
                    st.session_state.geo_area = None if (sel == new_sel) else new_sel
                    st.rerun()

        st.markdown("---")

        # ── Pannello dettaglio ─────────────────────────────────────────────────
        if sel:
            col_hdr, col_close = st.columns([8, 1.2])
            with col_close:
                if st.button("✕ Deselect", key="geo_desel"):
                    st.session_state.geo_area = None
                    st.rerun()

            if sel['type'] == 'country':
                iso3      = sel['value']
                area_name = country_agg[country_agg['ISO3'] == iso3]['Area'].values
                area_name = area_name[0] if len(area_name) else iso3

                # ── A) Scenari con fattori specifici di questo paese ──────────
                sc_specific = sorted(
                    country_df[country_df['ISO3'] == iso3]['Scenario'].unique()
                )
                with col_hdr:
                    st.markdown(
                        f'<div class="section-header">🏳 {iso3} ({area_name}) — ' 
                        f'{len(sc_specific)} specific scenario{"s" if len(sc_specific)!=1 else ""}</div>',
                        unsafe_allow_html=True
                    )
                df_specific = df[df['Scenario'].isin(sc_specific)].copy()
                if not df_specific.empty:
                    render_export_row(df_specific, df_specific,
                                      f"geo_country_{iso3}_specific")
                    render_scenario_rows(df_specific, df, th_class="", path_mode=True)
                else:
                    st.info("No shock detail for specific country scenarios.")

                # ── B) Tutti gli scenari dell'area ────────────────────────────
                sc_area = sorted(
                    geo_filtered[geo_filtered['Area'] == area_name]['Scenario'].unique()
                )
                sc_area_only = [s for s in sc_area if s not in sc_specific]

                st.markdown(
                    f'<div class="section-header" style="margin-top:2rem;">🌍 All {area_name} scenarios ' 
                    f'({len(sc_area)} total)</div>',
                    unsafe_allow_html=True
                )
                df_area = df[df['Scenario'].isin(sc_area)].copy()
                if not df_area.empty:
                    render_export_row(df_area, df_area, f"geo_area_{area_name}")
                    render_scenario_rows(df_area, df, th_class="", path_mode=True)

            else:  # type == 'area'
                area_name = sel['value']
                sc_area   = sorted(
                    geo_filtered[geo_filtered['Area'] == area_name]['Scenario'].unique()
                )
                with col_hdr:
                    st.markdown(
                        f'<div class="section-header">🌍 {area_name} — ' 
                        f'{len(sc_area)} scenario{"s" if len(sc_area)!=1 else ""}</div>',
                        unsafe_allow_html=True
                    )
                df_area = df[df['Scenario'].isin(sc_area)].copy()
                if df_area.empty:
                    st.info("No shock detail available.")
                else:
                    render_export_row(df_area, df_area, f"geo_{area_name.replace(' ','_')}")
                    render_scenario_rows(df_area, df, th_class="", path_mode=True)


# ─── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("<br><br>", unsafe_allow_html=True)
_type_label = f" · Filter: {_type_sel}" if _type_sel != 'All' else ''
st.markdown(
    f'<div style="font-size:0.6rem;color:#9ca3af;text-align:center;">'
    f'Stress Test Dashboard · Lista_scenari_shocks.xlsx · {_n_sc} scenarios · {_n_l1} asset classes{_type_label}</div>',
    unsafe_allow_html=True
)
