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
    background: #0d0f14;
    color: #e8e4dc;
}

h1, h2, h3 { font-family: 'Syne', sans-serif; }

.main-title {
    font-size: 2.6rem;
    font-weight: 800;
    letter-spacing: -1px;
    color: #e8e4dc;
    border-bottom: 2px solid #2a5cff;
    padding-bottom: 0.5rem;
    margin-bottom: 0.3rem;
}

.subtitle {
    font-family: 'DM Mono', monospace;
    font-size: 0.78rem;
    color: #6b7280;
    margin-bottom: 2rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

/* Breadcrumb */
.breadcrumb {
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    color: #6b7280;
    margin-bottom: 1.5rem;
    letter-spacing: 0.06em;
}
.breadcrumb span { color: #2a5cff; }
.breadcrumb .sep { color: #3a3f4b; margin: 0 6px; }

/* Card grid for L1/L2/L3 */
.card-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 12px;
    margin-bottom: 2rem;
}

.asset-card {
    background: #13161e;
    border: 1px solid #1e2330;
    border-radius: 10px;
    padding: 1.1rem 1.2rem;
    cursor: pointer;
    transition: all 0.18s ease;
    position: relative;
    overflow: hidden;
}
.asset-card:hover { border-color: #2a5cff; background: #181c28; }
.asset-card.selected { border-color: #2a5cff; background: #141828; }

.asset-card .label {
    font-size: 0.88rem;
    font-weight: 600;
    color: #e8e4dc;
    margin-bottom: 6px;
    line-height: 1.3;
}

.asset-card .meta {
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

.badge-pos {
    display: inline-block;
    background: #0d2b1a;
    color: #34d399;
    border: 1px solid #065f3b;
    border-radius: 4px;
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    padding: 2px 7px;
    font-weight: 500;
    margin-left: 6px;
}
.badge-neg {
    display: inline-block;
    background: #2b0d1a;
    color: #f87171;
    border: 1px solid #7f1d1d;
    border-radius: 4px;
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    padding: 2px 7px;
    font-weight: 500;
    margin-left: 6px;
}
.badge-mix {
    display: inline-block;
    background: #1a1a0d;
    color: #fbbf24;
    border: 1px solid #78350f;
    border-radius: 4px;
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    padding: 2px 7px;
    font-weight: 500;
    margin-left: 6px;
}

/* Scenario table */
.scenario-table {
    width: 100%;
    border-collapse: collapse;
    font-family: 'DM Mono', monospace;
    font-size: 0.78rem;
}
.scenario-table th {
    background: #13161e;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    padding: 10px 14px;
    border-bottom: 1px solid #1e2330;
    text-align: left;
    font-weight: 500;
}
.scenario-table td {
    padding: 9px 14px;
    border-bottom: 1px solid #13161e;
    color: #c8c4bc;
}
.scenario-table tr:hover td { background: #13161e; }

.shock-pos { color: #34d399; font-weight: 500; }
.shock-neg { color: #f87171; font-weight: 500; }
.shock-zero { color: #6b7280; }

.section-header {
    font-size: 0.7rem;
    font-family: 'DM Mono', monospace;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #6b7280;
    margin: 1.5rem 0 0.8rem;
    display: flex;
    align-items: center;
    gap: 8px;
}
.section-header::after {
    content: '';
    flex: 1;
    height: 1px;
    background: #1e2330;
}

.back-btn {
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    color: #2a5cff;
    background: none;
    border: 1px solid #1a2240;
    border-radius: 6px;
    padding: 5px 12px;
    cursor: pointer;
    margin-bottom: 1rem;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

.stat-row {
    display: flex;
    gap: 16px;
    margin-bottom: 1.5rem;
    flex-wrap: wrap;
}
.stat-box {
    background: #13161e;
    border: 1px solid #1e2330;
    border-radius: 8px;
    padding: 0.7rem 1.1rem;
    min-width: 140px;
}
.stat-box .sv { font-size: 1.5rem; font-weight: 700; color: #e8e4dc; }
.stat-box .sk { font-family: 'DM Mono', monospace; font-size: 0.65rem; color: #6b7280; text-transform: uppercase; letter-spacing: 0.07em; margin-top: 2px; }
</style>
""", unsafe_allow_html=True)

# ─── HELPERS ───────────────────────────────────────────────────────────────────

def parse_shock_value(val):
    """Extract numeric value from shock strings like '17.00pct', '-50bps', etc."""
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

def direction_badge(mean_val):
    d = shock_direction(mean_val)
    if d == "pos":   return '<span class="badge-pos">▲ +</span>'
    if d == "neg":   return '<span class="badge-neg">▼ −</span>'
    return '<span class="badge-mix">~ mix</span>'

def mean_shock_for_group(df_sub):
    vals = df_sub['_shock_num'].dropna()
    return vals.mean() if len(vals) else np.nan

@st.cache_data
def load_data(file):
    df = pd.read_excel(file, sheet_name="Pivot", header=0)
    df.columns = ['Scenario', 'L1', 'L2', 'L3', 'ShockValue'] + list(df.columns[5:])
    df = df[['Scenario', 'L1', 'L2', 'L3', 'ShockValue']].dropna(subset=['L1'])
    df['_shock_num'] = df['ShockValue'].apply(parse_shock_value)
    # Forward-fill merged cells if needed
    for col in ['Scenario', 'L1', 'L2', 'L3']:
        df[col] = df[col].ffill()
    return df

# ─── LAYOUT ────────────────────────────────────────────────────────────────────

st.markdown('<div class="main-title">Stress Test Mapping</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Asset class drill-down · Shock direction analysis</div>', unsafe_allow_html=True)

# File upload
uploaded = st.file_uploader("Carica il file Excel (ListaxMapping.xlsx)", type=["xlsx", "xls"])

if not uploaded:
    st.info("⬆️  Carica il file **ListaxMapping.xlsx** per iniziare.")
    st.stop()

df = load_data(uploaded)

# ─── SESSION STATE ─────────────────────────────────────────────────────────────
if 'sel_l1' not in st.session_state: st.session_state.sel_l1 = None
if 'sel_l2' not in st.session_state: st.session_state.sel_l2 = None
if 'sel_l3' not in st.session_state: st.session_state.sel_l3 = None

# ─── BREADCRUMB ────────────────────────────────────────────────────────────────
def breadcrumb():
    parts = ['<span class="sep">/</span> <span>All</span>']
    if st.session_state.sel_l1:
        parts.append(f'<span class="sep">/</span> <span>{st.session_state.sel_l1}</span>')
    if st.session_state.sel_l2:
        parts.append(f'<span class="sep">/</span> <span>{st.session_state.sel_l2}</span>')
    if st.session_state.sel_l3:
        parts.append(f'<span class="sep">/</span> <span>{st.session_state.sel_l3}</span>')
    st.markdown(f'<div class="breadcrumb">{"".join(parts)}</div>', unsafe_allow_html=True)

breadcrumb()

# ─── RENDER CARD GRID ──────────────────────────────────────────────────────────

def render_cards(items, df_filtered, col_name, on_select_key):
    """Render clickable cards for a list of items."""
    cols = st.columns(min(len(items), 4))
    for i, item in enumerate(sorted(items)):
        sub = df_filtered[df_filtered[col_name] == item]
        mean_v = mean_shock_for_group(sub)
        n_scenarios = sub['Scenario'].nunique()
        d = shock_direction(mean_v)
        badge_color = {"pos": "#34d399", "neg": "#f87171", "mix": "#fbbf24"}[d]
        badge_sym  = {"pos": "▲ +", "neg": "▼ −", "mix": "~ mix"}[d]
        mean_str = f"{mean_v:+.2f}" if not pd.isna(mean_v) else "n/a"

        with cols[i % min(len(items), 4)]:
            # Use button styled via markdown trick
            clicked = st.button(
                f"{item}",
                key=f"btn_{on_select_key}_{item}",
                use_container_width=True,
                help=f"{n_scenarios} scenari · shock medio {mean_str}"
            )
            st.markdown(
                f'<div style="font-family:DM Mono,monospace;font-size:0.66rem;'
                f'color:{badge_color};margin-top:-10px;margin-bottom:6px;">'
                f'{badge_sym} &nbsp; shock medio {mean_str} &nbsp;|&nbsp; {n_scenarios} scenari</div>',
                unsafe_allow_html=True
            )
            if clicked:
                st.session_state[on_select_key] = item
                # Reset deeper levels
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

    col_back, _ = st.columns([1, 5])
    with col_back:
        if st.button("← Torna a L1", key="back_l1"):
            st.session_state.sel_l1 = None
            st.session_state.sel_l2 = None
            st.session_state.sel_l3 = None
            st.rerun()

    st.markdown(f'<div class="section-header">Mapping Livello 2 — {st.session_state.sel_l1}</div>', unsafe_allow_html=True)
    l2_items = df_l1['L2'].dropna().unique().tolist()
    render_cards(l2_items, df_l1, 'L2', 'sel_l2')

# ─── LEVEL 3 ───────────────────────────────────────────────────────────────────
if st.session_state.sel_l1 and st.session_state.sel_l2:
    df_l2 = df[(df['L1'] == st.session_state.sel_l1) & (df['L2'] == st.session_state.sel_l2)]

    col_back2, _ = st.columns([1, 5])
    with col_back2:
        if st.button("← Torna a L2", key="back_l2"):
            st.session_state.sel_l2 = None
            st.session_state.sel_l3 = None
            st.rerun()

    st.markdown(f'<div class="section-header">Mapping Livello 3 — {st.session_state.sel_l2}</div>', unsafe_allow_html=True)
    l3_items = df_l2['L3'].dropna().unique().tolist()
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

    # Summary stats
    mean_v = mean_shock_for_group(df_l3)
    n_sc = df_l3['Scenario'].nunique()
    n_pos = (df_l3['_shock_num'] > 0).sum()
    n_neg = (df_l3['_shock_num'] < 0).sum()

    mean_str = f"{mean_v:+.2f}" if not pd.isna(mean_v) else "n/a"
    st.markdown(f"""
    <div class="stat-row">
        <div class="stat-box"><div class="sv">{n_sc}</div><div class="sk">Scenari</div></div>
        <div class="stat-box"><div class="sv">{mean_str}</div><div class="sk">Shock medio</div></div>
        <div class="stat-box"><div class="sv" style="color:#34d399">{n_pos}</div><div class="sk">Shock positivi</div></div>
        <div class="stat-box"><div class="sv" style="color:#f87171">{n_neg}</div><div class="sk">Shock negativi</div></div>
    </div>
    """, unsafe_allow_html=True)

    # Build table HTML
    rows_html = ""
    for _, row in df_l3.sort_values('Scenario').iterrows():
        shock_num = row['_shock_num']
        shock_raw = str(row['ShockValue']) if not pd.isna(row['ShockValue']) else "—"

        if not np.isnan(shock_num) if not pd.isna(shock_num) else False:
            cls = "shock-pos" if shock_num > 0 else ("shock-neg" if shock_num < 0 else "shock-zero")
            arrow = "▲ " if shock_num > 0 else ("▼ " if shock_num < 0 else "")
        else:
            cls = "shock-zero"
            arrow = ""

        rows_html += f"""
        <tr>
            <td>{row['Scenario']}</td>
            <td class="{cls}">{arrow}{shock_raw}</td>
        </tr>"""

    st.markdown(f"""
    <table class="scenario-table">
        <thead><tr><th>Scenario</th><th>Shock Value</th></tr></thead>
        <tbody>{rows_html}</tbody>
    </table>
    """, unsafe_allow_html=True)

# ─── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(
    '<div style="font-family:DM Mono,monospace;font-size:0.62rem;color:#2a3040;text-align:center;">Stress Test Dashboard · ListaxMapping / Pivot</div>',
    unsafe_allow_html=True
)
