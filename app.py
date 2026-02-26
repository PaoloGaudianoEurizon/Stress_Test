import streamlit as st
import pandas as pd
import numpy as np
import re

# ─── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Stress Test Mapping",
    page_icon="📊",
    layout="wide",
)

# ─── CUSTOM CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@400;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
}

.stApp {
    background: #f5f5f0;
    color: #1a1a1a;
}

.stButton > button {
    background: #ffffff;
    color: #1a1a1a;
    border: 1.5px solid #d4d0c8;
    border-radius: 8px;
    font-family: 'Syne', sans-serif;
    font-weight: 600;
    font-size: 0.85rem;
    transition: all 0.15s ease;
}
.stButton > button:hover {
    border-color: #1a1a1a;
    background: #1a1a1a;
    color: #ffffff;
}

h1, h2, h3 { font-family: 'Syne', sans-serif; }

.main-title {
    font-size: 2.4rem;
    font-weight: 800;
    letter-spacing: -1px;
    color: #1a1a1a;
    border-bottom: 3px solid #1a1a1a;
    padding-bottom: 0.4rem;
    margin-bottom: 0.3rem;
}

.subtitle {
    font-family: 'DM Mono', monospace;
    font-size: 0.75rem;
    color: #888880;
    margin-bottom: 2rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

.breadcrumb {
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    color: #888880;
    margin-bottom: 1.5rem;
    letter-spacing: 0.06em;
}
.breadcrumb span { color: #1a1a1a; font-weight: 600; }
.breadcrumb .sep { color: #c8c4bc; margin: 0 6px; }

.card-sub {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    color: #888880;
    margin-top: -10px;
    margin-bottom: 8px;
}

.scenario-table {
    width: 100%;
    border-collapse: collapse;
    font-family: 'DM Mono', monospace;
    font-size: 0.8rem;
    background: #ffffff;
    border-radius: 10px;
    overflow: hidden;
    box-shadow: 0 1px 4px rgba(0,0,0,0.07);
}
.scenario-table th {
    background: #1a1a1a;
    color: #f5f5f0;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    padding: 11px 16px;
    text-align: left;
    font-weight: 500;
    font-size: 0.72rem;
}
.scenario-table td {
    padding: 10px 16px;
    border-bottom: 1px solid #f0ede6;
    color: #2a2a2a;
}
.scenario-table tr:last-child td { border-bottom: none; }
.scenario-table tr:hover td { background: #fafaf7; }

.shock-pos { color: #0a7c45; font-weight: 600; }
.shock-neg { color: #c0392b; font-weight: 600; }
.shock-zero { color: #888880; }

.section-header {
    font-size: 0.68rem;
    font-family: 'DM Mono', monospace;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    color: #888880;
    margin: 1.8rem 0 0.9rem;
    display: flex;
    align-items: center;
    gap: 10px;
}
.section-header::after {
    content: '';
    flex: 1;
    height: 1px;
    background: #d4d0c8;
}

.stat-row {
    display: flex;
    gap: 14px;
    margin-bottom: 1.5rem;
    flex-wrap: wrap;
}
.stat-box {
    background: #ffffff;
    border: 1.5px solid #d4d0c8;
    border-radius: 10px;
    padding: 0.75rem 1.2rem;
    min-width: 130px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.stat-box .sv { font-size: 1.6rem; font-weight: 800; color: #1a1a1a; line-height: 1; }
.stat-box .sk { font-family: 'DM Mono', monospace; font-size: 0.63rem; color: #888880; text-transform: uppercase; letter-spacing: 0.07em; margin-top: 4px; }
</style>
""", unsafe_allow_html=True)

# ─── HELPERS ───────────────────────────────────────────────────────────────────

def parse_shock_value(val):
    if pd.isna(val):
        return np.nan
    s = str(val).replace(',', '.').strip()
    m = re.search(r'[-+]?\d+\.?\d*', s)
    return float(m.group()) if m else np.nan

def shock_direction(mean_val):
    if pd.isna(mean_val): return "mix"
    if mean_val > 0: return "pos"
    if mean_val < 0: return "neg"
    return "mix"

def mean_shock_for_group(df_sub):
    vals = df_sub['_shock_num'].dropna()
    return vals.mean() if len(vals) else np.nan

# ─── DATA ──────────────────────────────────────────────────────────────────────

FILE_PATH = "ListaxMapping.xlsx"

@st.cache_data
def load_data():
    df = pd.read_excel(FILE_PATH, sheet_name="Pivot", header=0)
    df.columns = ['Scenario', 'L1', 'L2', 'L3', 'ShockValue'] + list(df.columns[5:])
    df = df[['Scenario', 'L1', 'L2', 'L3', 'ShockValue']].dropna(subset=['L1'])
    df['_shock_num'] = df['ShockValue'].apply(parse_shock_value)
    for col in ['Scenario', 'L1', 'L2', 'L3']:
        df[col] = df[col].ffill()
    df = df[df['L1'].astype(str).str.strip().astype(bool)]
    return df

# ─── LAYOUT ────────────────────────────────────────────────────────────────────

st.markdown('<div class="main-title">Stress Test Mapping</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Asset class drill-down · Shock direction analysis</div>', unsafe_allow_html=True)

try:
    df = load_data()
except FileNotFoundError:
    st.error(f"File `{FILE_PATH}` non trovato nella repository. Verifica che sia nella root del progetto.")
    st.stop()

# ─── SESSION STATE ─────────────────────────────────────────────────────────────
if 'sel_l1' not in st.session_state: st.session_state.sel_l1 = None
if 'sel_l2' not in st.session_state: st.session_state.sel_l2 = None
if 'sel_l3' not in st.session_state: st.session_state.sel_l3 = None

# ─── BREADCRUMB ────────────────────────────────────────────────────────────────
def render_breadcrumb():
    parts = ['<span>All</span>']
    if st.session_state.sel_l1:
        parts.append(f'<span class="sep">/</span><span>{st.session_state.sel_l1}</span>')
    if st.session_state.sel_l2:
        parts.append(f'<span class="sep">/</span><span>{st.session_state.sel_l2}</span>')
    if st.session_state.sel_l3:
        parts.append(f'<span class="sep">/</span><span>{st.session_state.sel_l3}</span>')
    st.markdown(f'<div class="breadcrumb">{"".join(parts)}</div>', unsafe_allow_html=True)

render_breadcrumb()

# ─── RENDER CARDS ──────────────────────────────────────────────────────────────

def render_cards(items, df_filtered, col_name, on_select_key):
    items_sorted = sorted([i for i in items if str(i).strip()])
    if not items_sorted:
        return
    ncols = min(len(items_sorted), 4)
    cols = st.columns(ncols)
    for i, item in enumerate(items_sorted):
        sub = df_filtered[df_filtered[col_name] == item]
        mean_v = mean_shock_for_group(sub)
        n_scenarios = sub['Scenario'].nunique()
        d = shock_direction(mean_v)
        badge_color = {"pos": "#0a7c45", "neg": "#c0392b", "mix": "#b7770d"}[d]
        badge_sym   = {"pos": "▲ Positivo", "neg": "▼ Negativo", "mix": "~ Misto"}[d]

        with cols[i % ncols]:
            clicked = st.button(
                f"{item}",
                key=f"btn_{on_select_key}_{item}",
                use_container_width=True,
                help=f"{n_scenarios} scenari"
            )
            st.markdown(
                f'<div class="card-sub">'
                f'<span style="color:{badge_color};font-weight:600;">{badge_sym}</span>'
                f' &nbsp;·&nbsp; {n_scenarios} scenari</div>',
                unsafe_allow_html=True
            )
            if clicked:
                st.session_state[on_select_key] = item
                if on_select_key == 'sel_l1':
                    st.session_state.sel_l2 = None
                    st.session_state.sel_l3 = None
                elif on_select_key == 'sel_l2':
                    st.session_state.sel_l3 = None
                st.rerun()

# ─── LEVEL 1 ───────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">Mapping Livello 1 — Asset Class</div>', unsafe_allow_html=True)
l1_items = df['L1'].dropna().unique().tolist()
render_cards(l1_items, df, 'L1', 'sel_l1')

# ─── LEVEL 2 ───────────────────────────────────────────────────────────────────
if st.session_state.sel_l1:
    df_l1 = df[df['L1'] == st.session_state.sel_l1]
    l2_items = [i for i in df_l1['L2'].dropna().unique().tolist() if str(i).strip()]

    col_back, _ = st.columns([1, 5])
    with col_back:
        if st.button("← Torna a L1", key="back_l1"):
            st.session_state.sel_l1 = None
            st.session_state.sel_l2 = None
            st.session_state.sel_l3 = None
            st.rerun()

    if l2_items:
        st.markdown(f'<div class="section-header">Mapping Livello 2 — {st.session_state.sel_l1}</div>', unsafe_allow_html=True)
        render_cards(l2_items, df_l1, 'L2', 'sel_l2')

# ─── LEVEL 3 ───────────────────────────────────────────────────────────────────
if st.session_state.sel_l1 and st.session_state.sel_l2:
    df_l2 = df[(df['L1'] == st.session_state.sel_l1) & (df['L2'] == st.session_state.sel_l2)]
    l3_items = [i for i in df_l2['L3'].dropna().unique().tolist() if str(i).strip()]

    col_back2, _ = st.columns([1, 5])
    with col_back2:
        if st.button("← Torna a L2", key="back_l2"):
            st.session_state.sel_l2 = None
            st.session_state.sel_l3 = None
            st.rerun()

    if l3_items:
        st.markdown(f'<div class="section-header">Mapping Livello 3 — {st.session_state.sel_l2}</div>', unsafe_allow_html=True)
        render_cards(l3_items, df_l2, 'L3', 'sel_l3')

# ─── SCENARIOS TABLE ───────────────────────────────────────────────────────────
if st.session_state.sel_l1 and st.session_state.sel_l2 and st.session_state.sel_l3:
    df_l3 = df[
        (df['L1'] == st.session_state.sel_l1) &
        (df['L2'] == st.session_state.sel_l2) &
        (df['L3'] == st.session_state.sel_l3)
    ]

    col_back3, _ = st.columns([1, 5])
    with col_back3:
        if st.button("← Torna a L3", key="back_l3"):
            st.session_state.sel_l3 = None
            st.rerun()

    st.markdown(f'<div class="section-header">Scenari — {st.session_state.sel_l3}</div>', unsafe_allow_html=True)

    mean_v  = mean_shock_for_group(df_l3)
    n_sc    = df_l3['Scenario'].nunique()
    n_pos   = (df_l3['_shock_num'] > 0).sum()
    n_neg   = (df_l3['_shock_num'] < 0).sum()
    d       = shock_direction(mean_v)
    dir_col = {"pos": "#0a7c45", "neg": "#c0392b", "mix": "#b7770d"}[d]
    dir_lbl = {"pos": "▲ Positivo", "neg": "▼ Negativo", "mix": "~ Misto"}[d]

    st.markdown(f"""
    <div class="stat-row">
        <div class="stat-box"><div class="sv">{n_sc}</div><div class="sk">Scenari</div></div>
        <div class="stat-box"><div class="sv" style="color:{dir_col};font-size:1.1rem;">{dir_lbl}</div><div class="sk">Direzione prevalente</div></div>
        <div class="stat-box"><div class="sv" style="color:#0a7c45">{n_pos}</div><div class="sk">Shock positivi</div></div>
        <div class="stat-box"><div class="sv" style="color:#c0392b">{n_neg}</div><div class="sk">Shock negativi</div></div>
    </div>
    """, unsafe_allow_html=True)

    rows_html = ""
    for _, row in df_l3.sort_values('Scenario').iterrows():
        shock_num = row['_shock_num']
        shock_raw = str(row['ShockValue']) if not pd.isna(row['ShockValue']) else "—"
        try:
            is_num = not np.isnan(float(shock_num))
        except (TypeError, ValueError):
            is_num = False

        if is_num:
            cls   = "shock-pos" if shock_num > 0 else ("shock-neg" if shock_num < 0 else "shock-zero")
            arrow = "▲ " if shock_num > 0 else ("▼ " if shock_num < 0 else "")
        else:
            cls, arrow = "shock-zero", ""

        rows_html += f"<tr><td>{row['Scenario']}</td><td class='{cls}'>{arrow}{shock_raw}</td></tr>"

    st.markdown(f"""
    <table class="scenario-table">
        <thead><tr><th>Scenario</th><th>Shock Value</th></tr></thead>
        <tbody>{rows_html}</tbody>
    </table>
    """, unsafe_allow_html=True)

# ─── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(
    '<div style="font-family:DM Mono,monospace;font-size:0.6rem;color:#c8c4bc;text-align:center;">Stress Test Dashboard · ListaxMapping / Pivot</div>',
    unsafe_allow_html=True
)
