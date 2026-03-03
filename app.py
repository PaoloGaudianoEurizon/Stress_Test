import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import re
import io
from datetime import datetime

# ─── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Stress Test Mapping", page_icon="📊", layout="wide")

# ─── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* ── Base ── */
.stApp { background: #0b0e17; font-family: 'Inter', sans-serif; }
[data-testid="stAppViewContainer"] { background: #0b0e17; }
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stToolbar"] { display: none; }
section[data-testid="stMain"] { padding-top: 0 !important; }

/* ── Navbar ── */
.fin-navbar {
    background: linear-gradient(90deg, #10151f 0%, #141928 50%, #111623 100%);
    border-bottom: 1px solid #1e2a3a;
    padding: 12px 28px 11px;
    margin: -3rem -4rem 0 -4rem;
    display: flex; align-items: center; justify-content: space-between;
}
.fin-brand { display: flex; align-items: center; gap: 14px; }
.fin-logo {
    width: 38px; height: 38px; border-radius: 9px;
    background: linear-gradient(135deg, #e63946 0%, #9b1d23 100%);
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem; font-weight: 800; color: #fff; letter-spacing: -0.5px;
    box-shadow: 0 0 14px rgba(230,57,70,0.35); flex-shrink: 0;
}
.fin-title { font-size: 1rem; font-weight: 700; color: #e2e8f0; letter-spacing: -0.02em; }
.fin-subtitle { font-size: 0.62rem; color: #4a5568; margin-top: 2px; letter-spacing: 0.06em; text-transform: uppercase; }
.fin-nav-right { display: flex; align-items: center; gap: 24px; }
.fin-meta-group { display: flex; gap: 20px; }
.fin-meta-item { text-align: right; }
.fin-meta-val { font-family: 'JetBrains Mono', monospace; font-size: 0.76rem; color: #8899aa; font-weight: 500; }
.fin-meta-label { font-size: 0.55rem; color: #3d4f63; text-transform: uppercase; letter-spacing: 0.07em; margin-top: 2px; }
.fin-separator { width: 1px; height: 28px; background: #1e2a3a; }
.fin-badge {
    background: #0e1520; border: 1px solid #1e2a3a;
    border-radius: 4px; padding: 4px 9px;
    font-size: 0.60rem; color: #3d5066; letter-spacing: 0.06em; text-transform: uppercase;
    font-family: 'JetBrains Mono', monospace;
}
.fin-status { display: flex; align-items: center; gap: 6px; font-size: 0.62rem; color: #4a6741; letter-spacing: 0.04em; }
.fin-status-dot {
    width: 7px; height: 7px; border-radius: 50%; background: #22c55e;
    box-shadow: 0 0 6px rgba(34,197,94,0.6); animation: pulse-green 2s infinite;
}
@keyframes pulse-green { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }

/* ── KPI strip ── */
.kpi-strip {
    display: flex; align-items: stretch;
    background: #0d1220; border-bottom: 1px solid #1a2236;
    margin: 0 -4rem; padding: 0 28px; gap: 0;
}
.kpi-cell { padding: 11px 24px 11px 0; display: flex; flex-direction: column; justify-content: center; min-width: 100px; }
.kpi-val { font-family: 'JetBrains Mono', monospace; font-size: 1.25rem; font-weight: 600; color: #c4cdd8; line-height: 1; }
.kpi-val.g { color: #22c55e; }
.kpi-val.r { color: #ef4444; }
.kpi-val.a { color: #f59e0b; }
.kpi-val.b { color: #60a5fa; }
.kpi-lbl { font-size: 0.56rem; color: #3d5066; text-transform: uppercase; letter-spacing: 0.08em; margin-top: 4px; }
.kpi-div { width: 1px; background: #1a2236; margin: 8px 24px 8px 0; align-self: stretch; flex-shrink: 0; }
.spark-wrap { display: flex; align-items: flex-end; gap: 2px; height: 24px; padding: 0 0 2px; }
.spark-bar { border-radius: 2px 2px 0 0; width: 6px; }

/* ── Section headers ── */
.section-header {
    font-size: 0.68rem; font-weight: 600; color: #4a5568;
    margin: 1.5rem 0 0.7rem; display: flex; align-items: center; gap: 10px;
    text-transform: uppercase; letter-spacing: 0.1em;
}
.section-header::before { content: ''; width: 3px; height: 12px; background: linear-gradient(180deg,#e63946,#9b1d23); border-radius: 2px; flex-shrink: 0; }
.section-header::after { content: ''; flex: 1; height: 1px; background: #111827; }

/* ── Breadcrumb ── */
.breadcrumb { font-size: 0.70rem; color: #2d3748; margin-bottom: 1rem; font-family: 'JetBrains Mono', monospace; display: flex; align-items: center; }
.breadcrumb span { color: #64748b; }
.breadcrumb .sep { color: #1e293b; margin: 0 8px; }
.breadcrumb .active { color: #94a3b8; font-weight: 500; }

/* ── Hint box ── */
.hint-box {
    background: #0d1220; border: 1px solid #1a2236; border-left: 2px solid #3b82f6;
    border-radius: 6px; padding: 0.7rem 1.1rem;
    font-size: 0.74rem; color: #64748b; margin-bottom: 1.2rem; line-height: 1.65;
}

/* ── Sel pill ── */
.sel-pill {
    display: inline-block; background: #3d0e11; color: #f87171;
    border: 1px solid #7f1d1d; border-radius: 3px;
    font-size: 0.63rem; padding: 2px 8px; margin: 2px;
    font-weight: 500; letter-spacing: 0.02em; font-family: 'JetBrains Mono', monospace;
}

/* ── Stat boxes ── */
.stat-box { background: #0d1220; border: 1px solid #1a2236; border-radius: 7px; padding: 0.8rem 1.1rem; }
.stat-box .sv { font-family: 'JetBrains Mono', monospace; font-size: 1.5rem; font-weight: 600; color: #c4cdd8; line-height: 1; }
.stat-box .sk { font-size: 0.56rem; color: #3d5066; text-transform: uppercase; letter-spacing: 0.09em; margin-top: 5px; }

/* ── Scenario table ── */
.scenario-table { width: 100%; border-collapse: collapse; font-size: 0.80rem; background: #0d1220; border-radius: 8px; overflow: hidden; border: 1px solid #1a2236; }
.scenario-table th { background: #e63946; color: #fff; padding: 9px 14px; text-align: left; font-weight: 600; font-size: 0.65rem; letter-spacing: 0.08em; text-transform: uppercase; }
.scenario-table th.pos-th { background: #14532d; border-bottom: 2px solid #22c55e; }
.scenario-table th.neg-th { background: #7f1d1d; border-bottom: 2px solid #ef4444; }
.scenario-table th.mix-th { background: #78350f; border-bottom: 2px solid #f59e0b; }
.scenario-table td { padding: 9px 14px; border-bottom: 1px solid #111827; color: #94a3b8; vertical-align: top; }
.scenario-table tr:last-child td { border-bottom: none; }
.scenario-table tr:hover td { background: #0f1623; }
.scenario-table strong { color: #e2e8f0; font-family: 'JetBrains Mono', monospace; font-size: 0.76rem; }

/* ── Factor rows ── */
.factor-list { display: flex; flex-direction: column; gap: 3px; margin-top: 5px; }
.factor-row { display: flex; justify-content: space-between; align-items: baseline; background: #090c14; border: 1px solid #111827; border-radius: 3px; padding: 3px 9px; }
.factor-name { color: #3d5066; font-size: 0.72rem; flex: 1; padding-right: 10px; }
.factor-val-pos  { color: #22c55e; font-weight: 600; white-space: nowrap; font-family: 'JetBrains Mono', monospace; font-size: 0.70rem; }
.factor-val-neg  { color: #ef4444; font-weight: 600; white-space: nowrap; font-family: 'JetBrains Mono', monospace; font-size: 0.70rem; }
.factor-val-zero { color: #2d3748; white-space: nowrap; font-family: 'JetBrains Mono', monospace; font-size: 0.70rem; }
.long-des { font-size: 0.66rem; color: #2d3d50; margin-top: 4px; line-height: 1.5; font-style: italic; }

/* ── Buttons ── */
.stButton > button {
    background: #0d1220 !important; color: #64748b !important;
    border: 1px solid #1a2236 !important; border-radius: 5px !important;
    font-size: 0.80rem !important; transition: all 0.15s ease !important;
    font-family: 'Inter', sans-serif !important;
}
.stButton > button:hover { border-color: #e63946 !important; color: #e2e8f0 !important; background: #130b0d !important; }
.stDownloadButton > button {
    background: #0d1220 !important; color: #64748b !important;
    border: 1px solid #1a2236 !important; border-radius: 5px !important;
    font-size: 0.76rem !important; transition: all 0.15s ease !important;
    font-family: 'JetBrains Mono', monospace !important;
}
.stDownloadButton > button:hover { background: #0f1929 !important; color: #94a3b8 !important; border-color: #2a3d55 !important; }

/* ── Methodology tooltip ── */
.method-tip { display:inline-flex; align-items:center; gap:7px; }
.method-icon {
    display:inline-flex; align-items:center; justify-content:center;
    width:18px; height:18px; border-radius:50%;
    background:#0d1220; border:1px solid #1e2a3a;
    color:#3d5066; font-size:0.63rem; font-weight:700;
    cursor:default; flex-shrink:0; position:relative;
}
.method-label { font-size:0.65rem; color:#2d3d50; letter-spacing:0.05em; text-transform:uppercase; }
.method-icon:hover .method-popup { display:block; }
.method-popup {
    display:none; position:absolute; left:24px; top:-8px;
    background:#060911; color:#94a3b8; border:1px solid #1a2236;
    font-size:0.67rem; line-height:1.7; padding:13px 15px;
    border-radius:8px; width:320px; z-index:9999;
    box-shadow: 0 12px 40px rgba(0,0,0,0.7);
}
.method-popup b { color:#e2e8f0; }
.method-popup .mp-title { font-size:0.68rem; font-weight:700; color:#c4cdd8; border-bottom:1px solid #111827; padding-bottom:7px; margin-bottom:9px; font-family:'JetBrains Mono',monospace; }
.mp-row { margin-bottom:6px; }
.mp-green { color:#4ade80; font-weight:600; }
.mp-red   { color:#f87171; font-weight:600; }
.mp-amber { color:#fbbf24; font-weight:600; }

/* ── Tip icons ── */
.tip-icon {
    display:inline-flex; align-items:center; justify-content:center;
    width:13px; height:13px; border-radius:50%;
    background:#0d1220; border:1px solid #1a2236;
    color:#2d3d50; font-size:0.56rem; font-weight:700;
    cursor:default; flex-shrink:0; position:relative; vertical-align:middle;
}
.tip-icon:hover .tip-text { display:block; }
.tip-text {
    display:none; position:absolute; left:18px; top:-4px;
    background:#060911; color:#94a3b8; border:1px solid #1a2236;
    font-size:0.65rem; line-height:1.5; padding:8px 11px; border-radius:6px;
    width:230px; z-index:9999; box-shadow:0 6px 24px rgba(0,0,0,0.6);
}

/* ── Row borders ── */
.sc-row-name { padding:9px 12px; border-bottom:1px solid #0f1623; border-left:1px solid #1a2236; min-height:44px; }
.sc-row-factors { padding:5px 12px; border-bottom:1px solid #0f1623; border-left:1px solid #1a2236; }
</style>
""", unsafe_allow_html=True)

# ─── HELPERS ───────────────────────────────────────────────────────────────────
def parse_shock(val):
    if pd.isna(val): return np.nan, 'none'
    s = str(val).strip(); sl = s.lower()
    m = re.search(r'[-+]?\d+\.?\d*', s)
    num = float(m.group()) if m else np.nan
    if 'bps'    in sl: unit = 'bps'
    elif 'rel %' in sl: unit = 'rel%'
    elif 'pct'  in sl: unit = 'pct'
    elif 'days' in sl: unit = 'days'
    elif m:            unit = 'number'
    else:              unit = 'other'
    return num, unit

def to_bps(num, unit):
    if pd.isna(num): return np.nan
    if unit == 'bps':  return num
    if unit == 'pct':  return num * 100
    if unit == 'rel%': return num * 100
    return np.nan

def group_direction_score(sub):
    bps = [to_bps(r['_num'], r['_unit']) for _, r in sub.iterrows()]
    bps = [v for v in bps if not np.isnan(v)]
    return float(np.mean(bps)) if bps else np.nan

def scenario_direction(score):
    if pd.isna(score): return 'zero'
    if score > 0: return 'pos'
    if score < 0: return 'neg'
    return 'zero'

def clean_items(series):
    return sorted([str(i) for i in series.dropna().unique()
                   if str(i).strip() not in ('', 'nan')])

# ─── DATA ──────────────────────────────────────────────────────────────────────
FILE_PATH = "ListaxMapping.xlsx"

@st.cache_data
def load_data():
    df = pd.read_excel(FILE_PATH, sheet_name="Pivot", header=0)
    df.columns = ['Scenario','L1','L2','L3','ShockValue','ColF'] + list(df.columns[6:])
    df = df[['Scenario','L1','L2','L3','ShockValue','ColF']].copy()
    for col in ['Scenario','L1','L2','L3']: df[col] = df[col].ffill()
    df['ColF'] = df['ColF'].fillna('').astype(str).str.strip()
    df = df.dropna(subset=['L1'])
    df = df[df['L1'].astype(str).str.strip().astype(bool)]
    df = df[df['L1'].astype(str).str.lower() != 'nan']
    parsed = df['ShockValue'].apply(lambda v: pd.Series(parse_shock(v), index=['_num','_unit']))
    df['_num'] = parsed['_num']; df['_unit'] = parsed['_unit']
    try:
        dm = pd.read_excel(FILE_PATH, sheet_name="MAIN", header=0)
        dm = dm.iloc[:,[0,3]].copy(); dm.columns = ['Stress_Scenarios','Long_des']
        dm = dm.dropna(subset=['Stress_Scenarios'])
        dm['Stress_Scenarios'] = dm['Stress_Scenarios'].astype(str).str.strip()
        dm['Long_des'] = dm['Long_des'].fillna('').astype(str).str.strip()
    except Exception:
        dm = pd.DataFrame(columns=['Stress_Scenarios','Long_des'])
    return df, dm

try:
    df, dm = load_data()
except FileNotFoundError:
    st.error(f"File `{FILE_PATH}` not found."); st.stop()

desc_map = dict(zip(dm['Stress_Scenarios'], dm['Long_des']))

# ─── EXPORT ────────────────────────────────────────────────────────────────────
def build_export_bytes(df_sub):
    rows = []
    for _, r in df_sub.sort_values(['Scenario','L1','L2','L3']).iterrows():
        sc = str(r['Scenario'])
        rows.append({'Scenario': sc, 'Description': desc_map.get(sc.strip(),''),
                     'Detail': str(r.get('ColF','')), 'L1': str(r.get('L1','')),
                     'L2': str(r.get('L2','')), 'L3': str(r.get('L3','')),
                     'ShockValue': str(r['ShockValue']) if not pd.isna(r['ShockValue']) else ''})
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine='openpyxl') as writer:
        edf = pd.DataFrame(rows)
        edf.to_excel(writer, index=False, sheet_name='Scenarios')
        ws = writer.sheets['Scenarios']
        for cc in ws.columns:
            ws.column_dimensions[cc[0].column_letter].width = min(
                max(len(str(c.value or '')) for c in cc)+4, 60)
    buf.seek(0); return buf.getvalue()

# ─── SESSION STATE ─────────────────────────────────────────────────────────────
for k, v in {'sel_l1_set': set(), 'sel_l1_single': None, 'sel_l2': None, 'sel_l3': None,
              'mode': 'drill', 'shock_filter': 'all', 'quick_view': None, 'multi_dir_filter': None}.items():
    if k not in st.session_state: st.session_state[k] = v

# ─── HEADER ────────────────────────────────────────────────────────────────────
_date  = datetime.now().strftime("%d %b %Y")
_time  = datetime.now().strftime("%H:%M")
_n_sc  = df['Scenario'].nunique()
_n_l1  = df['L1'].nunique()
_n_row = len(df)
_all_dirs = {sc: scenario_direction(group_direction_score(g)) for sc, g in df.groupby('Scenario')}
_tot_pos  = sum(1 for d in _all_dirs.values() if d == 'pos')
_tot_neg  = sum(1 for d in _all_dirs.values() if d == 'neg')
_tot_mix  = sum(1 for d in _all_dirs.values() if d == 'zero')

_l1_counts = df.groupby('L1')['Scenario'].nunique().sort_values(ascending=False)
_max_c = max(_l1_counts.values) if len(_l1_counts) else 1

# ── Donut SVG (pos / neg / mixed breakdown) ──────────────────────────────────
import math
def _donut_svg(pos, neg, mix, total, r=26, stroke=6):
    if total == 0: return ""
    cx = cy = r + stroke + 2
    size = (r + stroke + 2) * 2
    circ = 2 * math.pi * r
    def arc(value, color, offset):
        dash = circ * value / total
        return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{color}" '
                f'stroke-width="{stroke}" stroke-dasharray="{dash:.2f} {circ:.2f}" '
                f'stroke-dashoffset="-{offset:.2f}" stroke-linecap="butt"/>')
    o1 = 0
    o2 = circ * pos / total
    o3 = o2 + circ * neg / total
    segs = arc(pos, "#22c55e", o1) + arc(neg, "#ef4444", o2) + arc(mix, "#f59e0b", o3)
    pct = int(100 * neg / total) if total else 0
    return (f'<svg width="{size}" height="{size}" style="transform:rotate(-90deg)">'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#1a2236" stroke-width="{stroke}"/>'
            f'{segs}</svg>')

_donut = _donut_svg(_tot_pos, _tot_neg, _tot_mix, _n_sc)

# ── Horizontal stacked bar (per-L1 pos/neg) ──────────────────────────────────
def _stacked_bar_svg(pos, neg, total, w=80, h=6):
    if total == 0: return ""
    pw = int(w * pos / total); nw = int(w * neg / total); mw = w - pw - nw
    return (f'<svg width="{w}" height="{h}" style="border-radius:2px;overflow:hidden">'
            f'<rect x="0" y="0" width="{pw}" height="{h}" fill="#22c55e" opacity="0.85"/>'
            f'<rect x="{pw}" y="0" width="{nw}" height="{h}" fill="#ef4444" opacity="0.85"/>'
            f'<rect x="{pw+nw}" y="0" width="{mw}" height="{h}" fill="#f59e0b" opacity="0.6"/>'
            f'</svg>')

# ── Spark bars (scenario count per L1) ───────────────────────────────────────
_spark = ''.join(
    f'<div class="spark-bar" style="height:{max(4,int(22*v/_max_c))}px;'
    f'background:#e63946;opacity:{0.35+0.65*v/_max_c:.2f};"></div>'
    for v in _l1_counts.values)

# ── Risk gauge SVG (needle pointing to neg% of total) ────────────────────────
def _gauge_svg(neg_pct, w=60, h=34):
    # semi-circle gauge, green→yellow→red, needle at neg_pct
    angle = 180 * neg_pct  # 0=all pos (left), 1=all neg (right)
    rad   = math.radians(180 - angle)
    cx, cy, r = w/2, h-2, h-6
    nx = cx + r * math.cos(rad)
    ny = cy - r * math.sin(rad)
    # arc segments
    def arc_d(start_a, end_a, radius):
        s = math.radians(start_a); e = math.radians(end_a)
        x1,y1 = cx+radius*math.cos(s), cy-radius*math.sin(s)
        x2,y2 = cx+radius*math.cos(e), cy-radius*math.sin(e)
        large = 1 if abs(end_a-start_a)>180 else 0
        return f"M {x1:.1f} {y1:.1f} A {radius} {radius} 0 {large} 0 {x2:.1f} {y2:.1f}"
    return (f'<svg width="{w}" height="{h}">'
            f'<path d="{arc_d(180,120,r)}" stroke="#22c55e" stroke-width="4" fill="none" stroke-linecap="round"/>'
            f'<path d="{arc_d(120,60,r)}" stroke="#f59e0b" stroke-width="4" fill="none" stroke-linecap="round"/>'
            f'<path d="{arc_d(60,0,r)}" stroke="#ef4444" stroke-width="4" fill="none" stroke-linecap="round"/>'
            f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{nx:.1f}" y2="{ny:.1f}" '
            f'stroke="#e2e8f0" stroke-width="1.5" stroke-linecap="round"/>'
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="2.5" fill="#e2e8f0"/>'
            f'</svg>')

_neg_pct = _tot_neg / _n_sc if _n_sc else 0
_gauge   = _gauge_svg(_neg_pct)

st.markdown(f"""
<div class="fin-navbar">
  <div class="fin-brand">
    <div class="fin-logo">ST</div>
    <div>
      <div class="fin-title">Stress Test Mapping</div>
      <div class="fin-subtitle">Risk Scenario Analysis &nbsp;·&nbsp; Shock Direction Engine</div>
    </div>
  </div>
  <div class="fin-nav-right">
    <div style="display:flex;flex-direction:column;align-items:center;gap:2px;">
      {_gauge}
      <div style="font-size:0.52rem;color:#3d5066;text-transform:uppercase;letter-spacing:0.06em;">Risk Skew</div>
    </div>
    <div class="fin-separator"></div>
    <div class="fin-meta-group">
      <div class="fin-meta-item"><div class="fin-meta-val">{_n_sc}</div><div class="fin-meta-label">Scenarios</div></div>
      <div class="fin-meta-item"><div class="fin-meta-val">{_n_l1}</div><div class="fin-meta-label">Asset Classes</div></div>
      <div class="fin-meta-item"><div class="fin-meta-val">{_n_row:,}</div><div class="fin-meta-label">Shock Factors</div></div>
    </div>
    <div class="fin-separator"></div>
    <div class="fin-meta-item"><div class="fin-meta-val">{_date}</div><div class="fin-meta-label">As of &nbsp;·&nbsp; {_time}</div></div>
    <div class="fin-separator"></div>
    <div class="fin-status"><div class="fin-status-dot"></div>LIVE</div>
    <div class="fin-badge">ListaxMapping</div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="kpi-strip">
  <div class="kpi-cell">
    <div style="display:flex;align-items:center;gap:12px;">
      {_donut}
      <div>
        <div class="kpi-val">{_n_sc}</div>
        <div class="kpi-lbl">Total Scenarios</div>
      </div>
    </div>
  </div>
  <div class="kpi-div"></div>
  <div class="kpi-cell"><div class="kpi-val g">▲ {_tot_pos}</div><div class="kpi-lbl">Net Positive</div></div>
  <div class="kpi-div"></div>
  <div class="kpi-cell"><div class="kpi-val r">▼ {_tot_neg}</div><div class="kpi-lbl">Net Negative</div></div>
  <div class="kpi-div"></div>
  <div class="kpi-cell"><div class="kpi-val a">~ {_tot_mix}</div><div class="kpi-lbl">Mixed / Zero</div></div>
  <div class="kpi-div"></div>
  <div class="kpi-cell">
    <div class="kpi-val b">{_n_l1}</div>
    <div class="kpi-lbl">Asset Classes</div>
    <div style="margin-top:5px">{_stacked_bar_svg(_tot_pos,_tot_neg,_n_sc,w=70)}</div>
    <div style="display:flex;gap:8px;margin-top:3px;font-size:0.52rem;color:#3d5066;">
      <span style="color:#22c55e">{int(100*_tot_pos/_n_sc) if _n_sc else 0}%↑</span>
      <span style="color:#ef4444">{int(100*_tot_neg/_n_sc) if _n_sc else 0}%↓</span>
    </div>
  </div>
  <div class="kpi-div"></div>
  <div class="kpi-cell" style="padding-right:0">
    <div class="spark-wrap">{_spark}</div>
    <div class="kpi-lbl">Scenarios by class</div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div style="height:18px;"></div>', unsafe_allow_html=True)

_heatmap_placeholder = st.empty()
col_m1, col_m2, col_m3 = st.columns([2.4, 2.4, 7.2])
with col_m1:
    if st.button("🔍 Single Asset Class Analysis", use_container_width=True):
        st.session_state.update({'mode':'drill','sel_l1_set':set(),'sel_l1_single':None,
                                  'sel_l2':None,'sel_l3':None,'shock_filter':'all',
                                  'quick_view':None,'multi_dir_filter':None}); st.rerun()
with col_m2:
    if st.button("🔀 Multi Asset Class Analysis", use_container_width=True):
        st.session_state.update({'mode':'multi','sel_l2':None,'sel_l3':None,
                                  'shock_filter':'all','quick_view':None,'multi_dir_filter':None}); st.rerun()
with col_m3:
    c_dl, c_meth, _ = st.columns([2.2, 2.6, 2.4])
    with c_dl:
        st.download_button(label="⬇ Download All Scenarios", data=build_export_bytes(df),
                           file_name="all_scenarios.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                           key="dl_all", use_container_width=True)
    with c_meth:
        st.markdown("""
        <div class="method-tip" style="margin-top:8px;">
          <div class="method-icon">?
            <div class="method-popup">
              <div class="mp-title">📐 Direction Methodology</div>
              <div class="mp-row">All shocks are converted to a <b>common unit (bps)</b>:
              pct × 100 = bps, rel% × 100 = bps. Days are excluded (time horizon, not stress direction).</div>
              <div class="mp-row">The <b>arithmetic mean</b> of converted values determines direction:</div>
              <div class="mp-row"><span class="mp-green">▲ Positive</span> — mean &gt; 0: net upward shock.</div>
              <div class="mp-row"><span class="mp-red">▼ Negative</span> — mean &lt; 0: net downward shock.</div>
              <div class="mp-row"><span class="mp-amber">~ Mixed</span> — mean = 0 (symmetric shocks cancel out).
              In Multi-Asset mode also includes scenarios positive in one area, negative in another.</div>
              <div class="mp-row" style="color:#2d3d50;font-size:0.63rem;margin-top:8px;">
              Direction re-evaluates at each drill level using only that level's shocks.</div>
            </div>
          </div>
          <span class="method-label">Direction methodology</span>
        </div>""", unsafe_allow_html=True)

st.markdown('<div style="height:4px;border-bottom:1px solid #111827;margin:8px 0 2px;"></div>',
            unsafe_allow_html=True)

# ─── JS: style direction buttons ──────────────────────────────────────────────
components.html("""
<script>
(function() {
    function style(doc) {
        doc.querySelectorAll('button').forEach(function(btn) {
            var t = (btn.innerText||btn.textContent||'').trim();
            if (t.includes('Positive')) {
                btn.style.setProperty('background-color','#14532d','important');
                btn.style.setProperty('color','#22c55e','important');
                btn.style.setProperty('border','1px solid #166534','important');
                btn.style.setProperty('font-size','0.70rem','important');
                btn.style.setProperty('font-weight','600','important');
                btn.style.setProperty('min-height','28px','important');
                btn.style.setProperty('height','28px','important');
                btn.style.setProperty('padding','0 8px','important');
                btn.style.setProperty('border-radius','4px','important');
                btn.style.setProperty('font-family','JetBrains Mono,monospace','important');
            } else if (t.includes('Negative')) {
                btn.style.setProperty('background-color','#7f1d1d','important');
                btn.style.setProperty('color','#f87171','important');
                btn.style.setProperty('border','1px solid #991b1b','important');
                btn.style.setProperty('font-size','0.70rem','important');
                btn.style.setProperty('font-weight','600','important');
                btn.style.setProperty('min-height','28px','important');
                btn.style.setProperty('height','28px','important');
                btn.style.setProperty('padding','0 8px','important');
                btn.style.setProperty('border-radius','4px','important');
                btn.style.setProperty('font-family','JetBrains Mono,monospace','important');
            } else if (t.startsWith('~') && t.includes('Mixed')) {
                btn.style.setProperty('background-color','#78350f','important');
                btn.style.setProperty('color','#fbbf24','important');
                btn.style.setProperty('border','1px solid #92400e','important');
                btn.style.setProperty('font-size','0.70rem','important');
                btn.style.setProperty('font-weight','600','important');
                btn.style.setProperty('min-height','28px','important');
                btn.style.setProperty('height','28px','important');
                btn.style.setProperty('padding','0 8px','important');
                btn.style.setProperty('border-radius','4px','important');
                btn.style.setProperty('font-family','JetBrains Mono,monospace','important');
            }
        });
    }
    style(window.parent.document);
    new MutationObserver(function(){ style(window.parent.document); })
        .observe(window.parent.document.body, {childList:true, subtree:true});
})();
</script>
""", height=0)

# ─── DIRECTION COUNTS ──────────────────────────────────────────────────────────
def count_directions(df_sub, _):
    n_pos = n_neg = n_zero = 0
    for _, sc_df in df_sub.groupby('Scenario'):
        d = scenario_direction(group_direction_score(sc_df))
        if d == 'pos': n_pos += 1
        elif d == 'neg': n_neg += 1
        else: n_zero += 1
    return n_pos, n_neg, n_zero

def get_scenario_directions(df_sub):
    return {sc: scenario_direction(group_direction_score(g))
            for sc, g in df_sub.groupby('Scenario')}

def render_heatmap_panel():
    """Render L1 scenario distribution heatmap — called after count_directions is defined."""
    l1_dir_data = []
    for l1, l1_df in df.groupby('L1'):
        np_, nn_, nz_ = count_directions(l1_df, 'L1')
        tot_ = np_ + nn_ + nz_
        l1_dir_data.append({'l1': l1, 'pos': np_, 'neg': nn_, 'mix': nz_, 'tot': tot_})
    l1_dir_data.sort(key=lambda x: x['tot'], reverse=True)
    cells = ''
    for d in l1_dir_data:
        if d['tot'] == 0: continue
        pw = int(60 * d['pos'] / d['tot']); nw = int(60 * d['neg'] / d['tot'])
        mw = 60 - pw - nw
        neg_pct = int(100 * d['neg'] / d['tot'])
        color = '#ef4444' if neg_pct > 60 else '#f59e0b' if neg_pct > 40 else '#22c55e'
        cells += (
            f'<div class="hm-cell">'
            f'<div class="hm-label">{d["l1"][:14]}</div>'
            f'<svg width="60" height="5" style="border-radius:2px;overflow:hidden;margin:3px 0">'
            f'<rect x="0" y="0" width="{pw}" height="5" fill="#22c55e" opacity="0.9"/>'
            f'<rect x="{pw}" y="0" width="{nw}" height="5" fill="#ef4444" opacity="0.9"/>'
            f'<rect x="{pw+nw}" y="0" width="{mw}" height="5" fill="#f59e0b" opacity="0.7"/>'
            f'</svg>'
            f'<div class="hm-count" style="color:{color}">{d["tot"]}</div>'
            f'</div>'
        )
    st.markdown(f"""
<style>
.hm-strip {{display:flex;flex-wrap:wrap;gap:6px;background:#080b12;border:1px solid #141e2e;
    border-radius:8px;padding:10px 16px;margin-bottom:14px;}}
.hm-cell {{display:flex;flex-direction:column;align-items:flex-start;background:#0d1220;
    border:1px solid #141e2e;border-radius:5px;padding:6px 10px;min-width:90px;}}
.hm-label {{font-size:0.60rem;color:#4a5568;letter-spacing:0.04em;text-transform:uppercase;white-space:nowrap;}}
.hm-count {{font-family:'JetBrains Mono',monospace;font-size:0.80rem;font-weight:600;line-height:1;}}
.hm-title {{font-size:0.58rem;color:#2d3d50;text-transform:uppercase;letter-spacing:0.08em;
    margin-bottom:7px;display:flex;align-items:center;gap:8px;width:100%;}}
.hm-title::after {{content:'';flex:1;height:1px;background:#141e2e;}}
</style>
<div class="hm-strip">
  <div style="width:100%"><div class="hm-title">&#9658; Scenario distribution by asset class</div></div>
  {cells}
</div>
""", unsafe_allow_html=True)


# ─── EXPORT ROW ────────────────────────────────────────────────────────────────
def render_export_row(df_full, df_display, fname_base):
    n = df_display['Scenario'].nunique()
    c_info, c_dl, _ = st.columns([2.8, 1.8, 6])
    with c_info:
        st.markdown(
            f'<div style="font-size:0.68rem;color:#3d5066;padding-top:9px;">'
            f'{"1 scenario" if n==1 else f"{n} scenarios"} &nbsp;·&nbsp;'
            f'<span style="font-style:italic;font-size:0.63rem;color:#2d3d50;">'
            f' export includes all shocks per scenario</span></div>',
            unsafe_allow_html=True)
    with c_dl:
        st.download_button(label="⬇ Export Excel", data=build_export_bytes(df_full),
                           file_name=f"{fname_base}.xlsx".replace(' ','_'),
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                           key=f"dl_{fname_base}_{id(df_display)}", use_container_width=True)

# ─── TABLE HELPERS ─────────────────────────────────────────────────────────────
def _factors_html(sc_rows, path_mode=False):
    html = '<div class="factor-list" style="margin-top:0">'
    for _, r in sc_rows.iterrows():
        num = r['_num']; sv = str(r['ShockValue']) if not pd.isna(r['ShockValue']) else '—'
        if path_mode:
            lbl = ' › '.join(str(r[c]) for c in ['L1','L2','L3']
                             if str(r.get(c,'')).strip() not in ('','nan'))
        else:
            lbl = str(r['L3']) if str(r.get('L3','')).strip() not in ('','nan') else '—'
        try: is_n = not np.isnan(float(num))
        except: is_n = False
        if is_n and num > 0:   vc, ar = 'factor-val-pos', '▲ '
        elif is_n and num < 0: vc, ar = 'factor-val-neg', '▼ '
        else:                  vc, ar = 'factor-val-zero', ''
        html += (f'<div class="factor-row"><span class="factor-name">{lbl}</span>'
                 f'<span class="{vc}">{ar}{sv}</span></div>')
    return html + '</div>'

def build_grouped_table_html(df_display, th_class=""):
    th = f' class="{th_class}"' if th_class else ''
    rows = ''
    for sc in sorted(df_display['Scenario'].unique()):
        sc_rows = df_display[df_display['Scenario']==sc].sort_values('L3')
        ld = desc_map.get(str(sc).strip(),'')
        des = f'<div class="long-des">{ld}</div>' if ld else ''
        rows += (f'<tr><td style="width:35%"><strong>{sc}</strong>{des}</td>'
                 f'<td>{_factors_html(sc_rows)}</td></tr>')
    return (f'<table class="scenario-table"><thead><tr>'
            f'<th{th}>Scenario</th><th{th}>Factors (L3) · Shock Value</th>'
            f'</tr></thead><tbody>{rows}</tbody></table>')

def render_scenario_rows(df_display, df_all_shocks, th_class="", path_mode=False):
    th_colors = {"pos-th":"#14532d","neg-th":"#7f1d1d","mix-th":"#78350f"}
    tc = th_colors.get(th_class, "#1a0a0b")
    hdr = "Shocks by area · L1 › L2 › L3" if path_mode else "Factors (L3) · Shock Value"
    st.markdown(f"""
    <table class="scenario-table" style="margin-bottom:0"><thead><tr>
      <th class="{th_class}" style="background:{tc};width:28%">Scenario</th>
      <th class="{th_class}" style="background:{tc}">{hdr}</th>
      <th class="{th_class}" style="background:{tc};width:44px;text-align:center">↓</th>
    </tr></thead></table>""", unsafe_allow_html=True)
    for sc in sorted(df_display['Scenario'].unique()):
        sc_rows  = df_display[df_display['Scenario']==sc].sort_values(
            ['L1','L2','L3'] if path_mode else ['L3'])
        ld = desc_map.get(str(sc).strip(),'')
        des = f'<div class="long-des">{ld}</div>' if ld else ''
        fh  = _factors_html(sc_rows, path_mode)
        c_sc, c_fac, c_dl = st.columns([3, 6.3, 0.7])
        with c_sc:
            st.markdown(f'<div class="sc-row-name"><strong>{sc}</strong>{des}</div>',
                        unsafe_allow_html=True)
        with c_fac:
            st.markdown(f'<div class="sc-row-factors">{fh}</div>', unsafe_allow_html=True)
        with c_dl:
            df_sc = df_all_shocks[df_all_shocks['Scenario']==sc]
            st.download_button(label="⬇", data=build_export_bytes(df_sc),
                               file_name=f"scenario_{sc}.xlsx".replace(' ','_'),
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                               key=f"dl_sc_{sc}_{th_class}_{path_mode}",
                               use_container_width=True, help=f"Download all shocks for {sc}")

# ─── QUICK-VIEW ────────────────────────────────────────────────────────────────
def render_quick_view(df_context, col_name):
    qv = st.session_state.quick_view
    if qv is None or qv['col'] != col_name: return
    item, direction = qv['item'], qv['dir']
    df_item = df_context[df_context[col_name]==item].copy()
    sc_dirs = get_scenario_directions(df_item)
    matching = [sc for sc, d in sc_dirs.items() if d == direction]
    if direction == 'pos':
        th_class, label = "pos-th", f"▲ Positive scenarios — {item}"
        df_display = df_item[df_item['Scenario'].isin(matching) & (df_item['_num']>0)]
    else:
        th_class, label = "neg-th", f"▼ Negative scenarios — {item}"
        df_display = df_item[df_item['Scenario'].isin(matching) & (df_item['_num']<0)]
    df_exp = df_item[df_item['Scenario'].isin(matching)]
    st.markdown(f'<div class="section-header">{label}</div>', unsafe_allow_html=True)
    c_close, _ = st.columns([1.2, 8])
    with c_close:
        if st.button("✕ Close", key=f"close_qv_{col_name}_{item}_{direction}"):
            st.session_state.quick_view = None; st.rerun()
    if not matching:
        st.info("No scenarios found for this selection."); return
    render_export_row(df_exp, df_display, f"scenarios_{item}_{direction}")
    render_scenario_rows(df_display, df, th_class)

# ─── CARD RENDERER ─────────────────────────────────────────────────────────────
def render_cards(items, df_filtered, col_name, on_select_key, multi=False, show_mini=False):
    if not items: return
    cols = st.columns(min(len(items), 4))
    for i, item in enumerate(items):
        sub = df_filtered[df_filtered[col_name]==item]
        n_pos, n_neg, n_mix = count_directions(sub, col_name)
        tot = n_pos + n_neg + n_mix
        is_sel = (item in st.session_state.sel_l1_set) if multi else (st.session_state.get(on_select_key)==item)
        with cols[i % len(cols)]:
            clicked = st.button(f"{'✓ ' if is_sel else ''}{item}",
                                key=f"btn_{on_select_key}_{item}", use_container_width=True)
            # mini stacked bar pos/neg/mix under each button
            if tot > 0:
                pw = int(100*n_pos/tot); nw = int(100*n_neg/tot); mw = 100-pw-nw
                st.markdown(
                    f'<div style="margin:-8px 0 4px;height:3px;display:flex;'
                    f'border-radius:0 0 4px 4px;overflow:hidden;">'
                    f'<div style="width:{pw}%;background:#22c55e;opacity:0.85;"></div>'
                    f'<div style="width:{nw}%;background:#ef4444;opacity:0.85;"></div>'
                    f'<div style="width:{mw}%;background:#f59e0b;opacity:0.6;"></div>'
                    f'</div>', unsafe_allow_html=True)
            if show_mini:
                mc1, mc2 = st.columns(2)
                with mc1:
                    if st.button(f"▲ {n_pos}  Positive", key=f"mini_pos_{on_select_key}_{item}", use_container_width=True):
                        if multi: st.session_state.sel_l1_set.add(item); st.session_state.shock_filter='pos'; st.session_state.quick_view=None
                        else: st.session_state.quick_view={'col':col_name,'item':item,'dir':'pos'}
                        st.rerun()
                with mc2:
                    if st.button(f"▼ {n_neg}  Negative", key=f"mini_neg_{on_select_key}_{item}", use_container_width=True):
                        if multi: st.session_state.sel_l1_set.add(item); st.session_state.shock_filter='neg'; st.session_state.quick_view=None
                        else: st.session_state.quick_view={'col':col_name,'item':item,'dir':'neg'}
                        st.rerun()
            if clicked:
                st.session_state.quick_view = None
                if multi:
                    if item in st.session_state.sel_l1_set: st.session_state.sel_l1_set.discard(item)
                    else: st.session_state.sel_l1_set.add(item)
                    st.session_state.shock_filter='all'; st.session_state.multi_dir_filter=None
                else:
                    cur = st.session_state.get(on_select_key)
                    st.session_state[on_select_key] = None if cur==item else item
                    if on_select_key=='sel_l1_single': st.session_state.sel_l2=st.session_state.sel_l3=None
                    elif on_select_key=='sel_l2': st.session_state.sel_l3=None
                    st.session_state.shock_filter='all'
                st.rerun()

# ─── STAT BOXES ────────────────────────────────────────────────────────────────
def render_stat_boxes(df_sub):
    n_sc = df_sub['Scenario'].nunique()
    n_pos, n_neg, n_zero = count_directions(df_sub, 'L3')
    cur = st.session_state.shock_filter

    def tip_span(txt):
        return (f'<span class="tip-icon">?<span class="tip-text">{txt}</span></span>')

    if n_zero > 0:
        c0, c1, c2, c3, _ = st.columns([1.2, 1.3, 1.3, 1.3, 4.9])
    else:
        c0, c1, c2, _ = st.columns([1.4, 1.5, 1.5, 6.6])

    with c0:
        st.markdown(f'<div class="stat-box"><div class="sv">{n_sc}</div>'
                    f'<div class="sk">Total Scenarios</div></div>', unsafe_allow_html=True)
    with c1:
        active = cur=='pos'
        st.markdown(f'<div style="font-size:0.65rem;color:#22c55e;font-weight:600;margin-bottom:2px;">'
                    f'▲ Positive {tip_span("Average shock (bps) is positive — net upward stress.")}'
                    f'</div>', unsafe_allow_html=True)
        if st.button(f"▲ {n_pos}  Positive", key="filter_pos", use_container_width=True):
            st.session_state.shock_filter='all' if active else 'pos'; st.rerun()
        if active:
            st.markdown('<div style="height:2px;background:#22c55e;border-radius:1px;margin-top:-6px;"></div>',
                        unsafe_allow_html=True)
    with c2:
        active = cur=='neg'
        st.markdown(f'<div style="font-size:0.65rem;color:#ef4444;font-weight:600;margin-bottom:2px;">'
                    f'▼ Negative {tip_span("Average shock (bps) is negative — net downward stress.")}'
                    f'</div>', unsafe_allow_html=True)
        if st.button(f"▼ {n_neg}  Negative", key="filter_neg", use_container_width=True):
            st.session_state.shock_filter='all' if active else 'neg'; st.rerun()
        if active:
            st.markdown('<div style="height:2px;background:#ef4444;border-radius:1px;margin-top:-6px;"></div>',
                        unsafe_allow_html=True)
    if n_zero > 0:
        with c3:
            active = cur=='zero'
            st.markdown(f'<div style="font-size:0.65rem;color:#f59e0b;font-weight:600;margin-bottom:2px;">'
                        f'~ Mixed {tip_span("Mean shock = 0: symmetric pos/neg shocks cancel out.")}'
                        f'</div>', unsafe_allow_html=True)
            if st.button(f"~ {n_zero}  Mixed", key="filter_zero", use_container_width=True):
                st.session_state.shock_filter='all' if active else 'zero'; st.rerun()
            if active:
                st.markdown('<div style="height:2px;background:#f59e0b;border-radius:1px;margin-top:-6px;"></div>',
                            unsafe_allow_html=True)

# ─── SCENARIO TABLE ────────────────────────────────────────────────────────────
def render_scenario_table(df_sub):
    render_stat_boxes(df_sub)
    f = st.session_state.shock_filter
    sc_dirs = get_scenario_directions(df_sub)
    if   f=='pos':  matching,th_class,direction = [sc for sc,d in sc_dirs.items() if d=='pos'],"pos-th","pos"
    elif f=='neg':  matching,th_class,direction = [sc for sc,d in sc_dirs.items() if d=='neg'],"neg-th","neg"
    elif f=='zero': matching,th_class,direction = [sc for sc,d in sc_dirs.items() if d=='zero'],"mix-th","zero"
    else:           matching,th_class,direction = list(sc_dirs.keys()),"","all"
    if not matching: st.info("No scenarios found for this filter."); return
    df_m = df_sub[df_sub['Scenario'].isin(matching)]
    if   f=='pos': df_d = df_m[df_m['_num']>0]
    elif f=='neg': df_d = df_m[df_m['_num']<0]
    else:          df_d = df_m
    render_export_row(df_m, df_d, f"scenarios_{st.session_state.get('sel_l3','export')}_{direction}")
    render_scenario_rows(df_d, df, th_class)

# ══════════════════════════════════════════════════════════════════════════════
with _heatmap_placeholder.container():
    render_heatmap_panel()
# MODE A — SINGLE-ASSET
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.mode == 'drill':
    qv = st.session_state.quick_view
    parts = ['<span>All</span>']
    if st.session_state.sel_l1_single:
        parts.append(f'<span class="sep">›</span><span class="active">{st.session_state.sel_l1_single}</span>')
    if st.session_state.sel_l2:
        parts.append(f'<span class="sep">›</span><span class="active">{st.session_state.sel_l2}</span>')
    if st.session_state.sel_l3:
        parts.append(f'<span class="sep">›</span><span class="active">{st.session_state.sel_l3}</span>')
    st.markdown(f'<div class="breadcrumb">{"".join(parts)}</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-header">Level 1 — Asset Class</div>', unsafe_allow_html=True)
    render_cards(clean_items(df['L1']), df, 'L1', 'sel_l1_single', multi=False, show_mini=True)

    if qv and qv['col']=='L1':
        render_quick_view(df, 'L1')
    elif st.session_state.sel_l1_single:
        df_l1 = df[df['L1']==st.session_state.sel_l1_single]
        l2_items = clean_items(df_l1['L2'])
        cb, _ = st.columns([1,5])
        with cb:
            if st.button("← Reset L1", key="back_l1"):
                st.session_state.update({'sel_l1_single':None,'sel_l2':None,'sel_l3':None,
                                          'shock_filter':'all','quick_view':None}); st.rerun()
        if l2_items:
            st.markdown(f'<div class="section-header">Level 2 — {st.session_state.sel_l1_single}</div>',
                        unsafe_allow_html=True)
            render_cards(l2_items, df_l1, 'L2', 'sel_l2', multi=False, show_mini=True)
            if qv and qv['col']=='L2':
                render_quick_view(df_l1, 'L2')
            elif st.session_state.sel_l2:
                df_l2 = df[(df['L1']==st.session_state.sel_l1_single)&(df['L2']==st.session_state.sel_l2)]
                l3_items = clean_items(df_l2['L3'])
                cb2, _ = st.columns([1,5])
                with cb2:
                    if st.button("← Reset L2", key="back_l2"):
                        st.session_state.update({'sel_l2':None,'sel_l3':None,
                                                  'shock_filter':'all','quick_view':None}); st.rerun()
                if l3_items:
                    st.markdown(f'<div class="section-header">Level 3 — {st.session_state.sel_l2}</div>',
                                unsafe_allow_html=True)
                    render_cards(l3_items, df_l2, 'L3', 'sel_l3', multi=False, show_mini=False)
                if st.session_state.sel_l3:
                    df_l3 = df[(df['L1']==st.session_state.sel_l1_single)&
                               (df['L2']==st.session_state.sel_l2)&
                               (df['L3']==st.session_state.sel_l3)]
                    cb3, _ = st.columns([1,5])
                    with cb3:
                        if st.button("← Reset L3", key="back_l3"):
                            st.session_state.update({'sel_l3':None,'shock_filter':'all'}); st.rerun()
                    st.markdown(f'<div class="section-header">Scenarios — {st.session_state.sel_l3}</div>',
                                unsafe_allow_html=True)
                    render_scenario_table(df_l3)

# ══════════════════════════════════════════════════════════════════════════════
# MODE B — MULTI-ASSET
# ══════════════════════════════════════════════════════════════════════════════
else:
    qv = st.session_state.quick_view
    st.markdown('<div class="hint-box">💡 Select one or more Level-1 areas. '
                'With a single area you see all its scenarios. With multiple areas you see scenarios '
                '<strong style="color:#8899aa">common to all</strong>.<br>'
                '🎯 Use the <strong style="color:#8899aa">▲ / ▼</strong> mini-buttons on each card '
                'for cross-area direction filtering.</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-header">Select Asset Class (multi-select)</div>', unsafe_allow_html=True)
    render_cards(clean_items(df['L1']), df, 'L1', 'sel_l1_set', multi=True, show_mini=True)

    if qv and qv['col']=='L1':
        render_quick_view(df, 'L1')
    elif st.session_state.sel_l1_set:
        pills = ' '.join(f'<span class="sel-pill">✓ {x}</span>'
                         for x in sorted(st.session_state.sel_l1_set))
        st.markdown(f'<div style="margin:8px 0 4px;">{pills}</div>', unsafe_allow_html=True)
        cc, _ = st.columns([1.5,8])
        with cc:
            if st.button("✕ Clear selection", key="clear_multi"):
                st.session_state.update({'sel_l1_set':set(),'shock_filter':'all',
                                          'quick_view':None,'multi_dir_filter':None}); st.rerun()

        selected_list = sorted(st.session_state.sel_l1_set)
        if len(selected_list)==1:
            df_show = df[df['L1'].isin(selected_list)].copy()
            label   = f"Scenarios in: {selected_list[0]}"
        else:
            sets  = [set(df[df['L1']==l1]['Scenario'].unique()) for l1 in selected_list]
            common = sets[0].intersection(*sets[1:])
            df_show = df[df['L1'].isin(selected_list)&df['Scenario'].isin(common)].copy()
            label   = f"Common scenarios: {' · '.join(selected_list)}"

        if df_show.empty:
            st.info("No scenarios shared across all selected areas.")
        else:
            st.markdown(f'<div class="section-header">{label}</div>', unsafe_allow_html=True)
            all_sc = sorted(df_show['Scenario'].unique())
            dir_mx = {}
            for l1 in selected_list:
                for sc, sc_df in df_show[df_show['L1']==l1].groupby('Scenario'):
                    dir_mx.setdefault(sc,{})[l1] = scenario_direction(group_direction_score(sc_df))

            def fbd(d):
                return [sc for sc in all_sc
                        if all(dir_mx.get(sc,{}).get(l1)==d for l1 in selected_list)]

            pos_sc  = fbd('pos'); neg_sc = fbd('neg')
            zero_sc = [sc for sc in all_sc if sc not in pos_sc and sc not in neg_sc]
            has_z   = len(zero_sc)>0; cur_mf = st.session_state.shock_filter

            # tooltip CSS
            st.markdown("""<style>
            .tip-icon{display:inline-flex;align-items:center;justify-content:center;
              width:13px;height:13px;border-radius:50%;background:#0d1220;border:1px solid #1a2236;
              color:#2d3d50;font-size:0.56rem;font-weight:700;cursor:default;flex-shrink:0;position:relative;}
            .tip-icon:hover .tip-text{display:block;}
            .tip-text{display:none;position:absolute;left:18px;top:-4px;background:#060911;color:#94a3b8;
              border:1px solid #1a2236;font-size:0.65rem;line-height:1.5;padding:8px 11px;border-radius:6px;
              width:230px;z-index:9999;box-shadow:0 6px 24px rgba(0,0,0,0.6);}
            </style>""", unsafe_allow_html=True)

            def tip(txt):
                return f'<span class="tip-icon">?<span class="tip-text">{txt}</span></span>'

            if has_z: cfa,cfb,cfc,cfd,_ = st.columns([1.1,1.3,1.3,1.3,3])
            else:     cfa,cfb,cfc,_      = st.columns([1.2,1.4,1.4,5])

            with cfa:
                st.markdown(f'<div class="stat-box"><div class="sv">{len(all_sc)}</div>'
                            f'<div class="sk">Total common</div></div>', unsafe_allow_html=True)
            with cfb:
                active = cur_mf=='pos'
                st.markdown(f'<div style="font-size:0.65rem;color:#22c55e;font-weight:600;margin-bottom:2px;">'
                            f'▲ Positive {tip("Positive in all selected asset classes.")}</div>', unsafe_allow_html=True)
                if st.button(f"▲ {len(pos_sc)}  positive", key="mf_pos", use_container_width=True):
                    st.session_state.shock_filter='all' if active else 'pos'; st.rerun()
                if active:
                    st.markdown('<div style="height:2px;background:#22c55e;border-radius:1px;margin-top:-6px;"></div>',
                                unsafe_allow_html=True)
            with cfc:
                active = cur_mf=='neg'
                st.markdown(f'<div style="font-size:0.65rem;color:#ef4444;font-weight:600;margin-bottom:2px;">'
                            f'▼ Negative {tip("Negative in all selected asset classes.")}</div>', unsafe_allow_html=True)
                if st.button(f"▼ {len(neg_sc)}  negative", key="mf_neg", use_container_width=True):
                    st.session_state.shock_filter='all' if active else 'neg'; st.rerun()
                if active:
                    st.markdown('<div style="height:2px;background:#ef4444;border-radius:1px;margin-top:-6px;"></div>',
                                unsafe_allow_html=True)
            if has_z:
                with cfd:
                    active = cur_mf=='zero'
                    st.markdown(f'<div style="font-size:0.65rem;color:#f59e0b;font-weight:600;margin-bottom:2px;">'
                                f'~ Mixed {tip("No single direction: mean=0 or opposite directions across areas.")}</div>',
                                unsafe_allow_html=True)
                    if st.button(f"~ {len(zero_sc)}  Mixed", key="mf_zero", use_container_width=True):
                        st.session_state.shock_filter='all' if active else 'zero'; st.rerun()
                    if active:
                        st.markdown('<div style="height:2px;background:#f59e0b;border-radius:1px;margin-top:-6px;"></div>',
                                    unsafe_allow_html=True)

            if   cur_mf=='pos':  act_sc,th_class,sign = pos_sc,"pos-th","pos"
            elif cur_mf=='neg':  act_sc,th_class,sign = neg_sc,"neg-th","neg"
            elif cur_mf=='zero': act_sc,th_class,sign = zero_sc,"mix-th","zero"
            else:                act_sc,th_class,sign = all_sc,"","all"

            if not act_sc:
                st.info("No scenarios match this direction filter.")
            else:
                df_act = df_show[df_show['Scenario'].isin(act_sc)]
                if   sign=='pos': df_d = df_act[df_act['_num']>0]
                elif sign=='neg': df_d = df_act[df_act['_num']<0]
                else:             df_d = df_act
                render_export_row(df_act, df_d, f"multi_{'_'.join(selected_list)}_{sign}")
                render_scenario_rows(df_d, df, th_class, path_mode=True)
    else:
        st.markdown('<div style="font-size:0.74rem;color:#1e2a3a;margin-top:1.2rem;'
                    'font-family:JetBrains Mono,monospace;">'
                    '← Select one or more asset classes above to begin.</div>',
                    unsafe_allow_html=True)

# ─── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(f"""
<div style="border-top:1px solid #111827;padding:12px 0 4px;
    display:flex;justify-content:space-between;align-items:center;">
  <div style="font-size:0.58rem;color:#1e2a3a;font-family:'JetBrains Mono',monospace;letter-spacing:0.05em;">
    STRESS TEST DASHBOARD &nbsp;·&nbsp; ListaxMapping / Pivot · MAIN
  </div>
  <div style="font-size:0.58rem;color:#1e2a3a;font-family:'JetBrains Mono',monospace;">
    {_date} &nbsp;·&nbsp; {_n_sc} scenarios &nbsp;·&nbsp; {_n_row:,} shock factors
  </div>
</div>
""", unsafe_allow_html=True)
