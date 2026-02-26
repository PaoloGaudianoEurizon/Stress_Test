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

html, body, [class*="css"] { font-family: 'Syne', sans-serif; }

.stApp { background: #f5f5f0; color: #1a1a1a; }

/* Buttons — default */
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

/* Selected card button style via data attribute trick */
div[data-selected="true"] .stButton > button {
    background: #1a1a1a !important;
    color: #ffffff !important;
    border-color: #1a1a1a !important;
}

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
    margin-bottom: 10px;
    min-height: 18px;
}

/* Selected indicator pill */
.sel-pill {
    display: inline-block;
    background: #1a1a1a;
    color: #f5f5f0;
    border-radius: 4px;
    font-family: 'DM Mono', monospace;
    font-size: 0.62rem;
    padding: 1px 7px;
    margin-bottom: 10px;
    letter-spacing: 0.04em;
}

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

.hint-box {
    background: #fff8e8;
    border: 1.5px solid #f0d080;
    border-radius: 8px;
    padding: 0.6rem 1rem;
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    color: #7a5a00;
    margin-bottom: 1.2rem;
}

/* Scenario table */
.scenario-table {
    width: 100%;
    border-collapse: collapse;
    font-family: 'DM Mono', monospace;
    font-size: 0.78rem;
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
    font-size: 0.7rem;
}
.scenario-table td {
    padding: 10px 16px;
    border-bottom: 1px solid #f0ede6;
    color: #2a2a2a;
    vertical-align: top;
}
.scenario-table tr:last-child td { border-bottom: none; }
.scenario-table tr:hover td { background: #fafaf7; }
.shock-pos { color: #0a7c45; font-weight: 600; }
.shock-neg { color: #c0392b; font-weight: 600; }
.shock-zero { color: #888880; }
.long-des { font-size: 0.72rem; color: #666660; margin-top: 3px; line-height: 1.4; }

/* Asset tag pills in multi-scenario table */
.asset-tag {
    display: inline-block;
    background: #f0ede6;
    color: #555550;
    border-radius: 4px;
    font-size: 0.6rem;
    padding: 1px 6px;
    margin: 1px 2px;
    font-family: 'DM Mono', monospace;
}

.stat-row { display: flex; gap: 14px; margin-bottom: 1.5rem; flex-wrap: wrap; }
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

/* Clear selection button */
div[data-testid="stHorizontalBlock"] .stButton > button[kind="secondary"] {
    font-size: 0.72rem;
    padding: 4px 10px;
}
</style>
""", unsafe_allow_html=True)

# ─── HELPERS ───────────────────────────────────────────────────────────────────

def parse_shock_value(val):
    if pd.isna(val): return np.nan
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

def direction_label(d):
    return {"pos": ("▲ Positivo", "#0a7c45"),
            "neg": ("▼ Negativo", "#c0392b"),
            "mix": ("~ Misto",    "#b7770d")}[d]

def clean_items(series):
    """Return non-blank unique values from a series."""
    return sorted([str(i) for i in series.dropna().unique() if str(i).strip() not in ('', 'nan')])

# ─── DATA ──────────────────────────────────────────────────────────────────────

FILE_PATH = "ListaxMapping.xlsx"

@st.cache_data
def load_data():
    # ── Pivot sheet
    df = pd.read_excel(FILE_PATH, sheet_name="Pivot", header=0)
    df.columns = ['Scenario', 'L1', 'L2', 'L3', 'ShockValue'] + list(df.columns[5:])
    df = df[['Scenario', 'L1', 'L2', 'L3', 'ShockValue']].copy()
    for col in ['Scenario', 'L1', 'L2', 'L3']:
        df[col] = df[col].ffill()
    df = df.dropna(subset=['L1'])
    df = df[df['L1'].astype(str).str.strip().astype(bool)]
    df = df[df['L1'].astype(str).str.lower() != 'nan']
    df['_shock_num'] = df['ShockValue'].apply(parse_shock_value)

    # ── MAIN sheet — long descriptions
    try:
        dm = pd.read_excel(FILE_PATH, sheet_name="MAIN", header=0)
        # Columns A=Stress_Scenarios, D=Long_des (index 0 and 3)
        dm = dm.iloc[:, [0, 3]].copy()
        dm.columns = ['Stress_Scenarios', 'Long_des']
        dm = dm.dropna(subset=['Stress_Scenarios'])
        dm['Stress_Scenarios'] = dm['Stress_Scenarios'].astype(str).str.strip()
        dm['Long_des'] = dm['Long_des'].fillna('').astype(str).str.strip()
    except Exception:
        dm = pd.DataFrame(columns=['Stress_Scenarios', 'Long_des'])

    return df, dm

try:
    df, dm = load_data()
except FileNotFoundError:
    st.error(f"File `{FILE_PATH}` non trovato nella repository.")
    st.stop()

# Build lookup dict scenario → long description
desc_map = dict(zip(dm['Stress_Scenarios'], dm['Long_des']))

# ─── SESSION STATE ─────────────────────────────────────────────────────────────
if 'sel_l1_set' not in st.session_state: st.session_state.sel_l1_set = set()   # multi-select
if 'sel_l2'     not in st.session_state: st.session_state.sel_l2     = None
if 'sel_l3'     not in st.session_state: st.session_state.sel_l3     = None
if 'mode'       not in st.session_state: st.session_state.mode       = 'drill'  # 'drill' | 'multi'

# ─── LAYOUT HEADER ─────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">Stress Test Mapping</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Asset class drill-down · Shock direction analysis</div>', unsafe_allow_html=True)

# Mode toggle
col_m1, col_m2, col_m3 = st.columns([2, 2, 8])
with col_m1:
    if st.button("🔍 Drill-down", use_container_width=True):
        st.session_state.mode = 'drill'
        st.session_state.sel_l1_set = set()
        st.session_state.sel_l2 = None
        st.session_state.sel_l3 = None
        st.rerun()
with col_m2:
    if st.button("🔀 Multi-area", use_container_width=True):
        st.session_state.mode = 'multi'
        st.session_state.sel_l2 = None
        st.session_state.sel_l3 = None
        st.rerun()

st.markdown("---")

# ─── SHARED: render card row ───────────────────────────────────────────────────

def render_cards(items, df_filtered, col_name, on_select_key, multi=False):
    """
    multi=False → single select (drill mode, L1/L2/L3)
    multi=True  → toggle into sel_l1_set (multi mode, L1 only)
    """
    if not items:
        return
    ncols = min(len(items), 4)
    cols = st.columns(ncols)
    for i, item in enumerate(items):
        sub = df_filtered[df_filtered[col_name] == item]
        mean_v = mean_shock_for_group(sub)
        n_sc = sub['Scenario'].nunique()
        d = shock_direction(mean_v)
        lbl, col_hex = direction_label(d)

        # Is this item currently selected?
        if multi:
            is_sel = item in st.session_state.sel_l1_set
        else:
            is_sel = (st.session_state.get(on_select_key) == item)

        btn_label = f"{'✓ ' if is_sel else ''}{item}"

        with cols[i % ncols]:
            clicked = st.button(btn_label, key=f"btn_{on_select_key}_{item}", use_container_width=True)
            st.markdown(
                f'<div class="card-sub">'
                f'<span style="color:{col_hex};font-weight:600;">{lbl}</span>'
                f'&nbsp;·&nbsp;{n_sc} scenari</div>',
                unsafe_allow_html=True
            )
            if clicked:
                if multi:
                    if item in st.session_state.sel_l1_set:
                        st.session_state.sel_l1_set.discard(item)
                    else:
                        st.session_state.sel_l1_set.add(item)
                else:
                    cur = st.session_state.get(on_select_key)
                    st.session_state[on_select_key] = None if cur == item else item
                    # Reset deeper levels
                    if on_select_key == 'sel_l1_single':
                        st.session_state.sel_l2 = None
                        st.session_state.sel_l3 = None
                    elif on_select_key == 'sel_l2':
                        st.session_state.sel_l3 = None
                st.rerun()

# ─── SCENARIO TABLE RENDERER ───────────────────────────────────────────────────

def render_scenario_table(df_sub, show_asset_cols=False):
    """Render the final scenario table with shock value, direction arrow, and long description."""
    mean_v = mean_shock_for_group(df_sub)
    n_sc   = df_sub['Scenario'].nunique()
    n_pos  = (df_sub['_shock_num'] > 0).sum()
    n_neg  = (df_sub['_shock_num'] < 0).sum()
    d      = shock_direction(mean_v)
    lbl, col_hex = direction_label(d)

    st.markdown(f"""
    <div class="stat-row">
        <div class="stat-box"><div class="sv">{n_sc}</div><div class="sk">Scenari</div></div>
        <div class="stat-box"><div class="sv" style="color:{col_hex};font-size:1.05rem;">{lbl}</div><div class="sk">Direzione prevalente</div></div>
        <div class="stat-box"><div class="sv" style="color:#0a7c45">{n_pos}</div><div class="sk">Shock positivi</div></div>
        <div class="stat-box"><div class="sv" style="color:#c0392b">{n_neg}</div><div class="sk">Shock negativi</div></div>
    </div>
    """, unsafe_allow_html=True)

    rows_html = ""
    for _, row in df_sub.sort_values('Scenario').iterrows():
        shock_num = row['_shock_num']
        shock_raw = str(row['ShockValue']) if not pd.isna(row['ShockValue']) else "—"
        long_des  = desc_map.get(str(row['Scenario']).strip(), '')

        try:
            is_num = not np.isnan(float(shock_num))
        except (TypeError, ValueError):
            is_num = False

        if is_num:
            cls   = "shock-pos" if shock_num > 0 else ("shock-neg" if shock_num < 0 else "shock-zero")
            arrow = "▲ " if shock_num > 0 else ("▼ " if shock_num < 0 else "")
        else:
            cls, arrow = "shock-zero", ""

        des_html = f'<div class="long-des">{long_des}</div>' if long_des else ''

        # Optional: show which L1/L2/L3 this row belongs to (in multi mode)
        asset_html = ""
        if show_asset_cols:
            tags = []
            for c in ['L1', 'L2', 'L3']:
                v = str(row.get(c, '')).strip()
                if v and v != 'nan':
                    tags.append(f'<span class="asset-tag">{v}</span>')
            asset_html = f'<td>{"".join(tags)}</td>'

        rows_html += f"""
        <tr>
            <td><strong>{row['Scenario']}</strong>{des_html}</td>
            <td class='{cls}'>{arrow}{shock_raw}</td>
            {asset_html}
        </tr>"""

    extra_th = "<th>Asset path</th>" if show_asset_cols else ""
    st.markdown(f"""
    <table class="scenario-table">
        <thead><tr><th>Scenario</th><th>Shock Value</th>{extra_th}</tr></thead>
        <tbody>{rows_html}</tbody>
    </table>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# MODE A — DRILL-DOWN
# ══════════════════════════════════════════════════════════════════════════════

if st.session_state.mode == 'drill':

    if 'sel_l1_single' not in st.session_state: st.session_state.sel_l1_single = None

    # Breadcrumb
    parts = ['<span>All</span>']
    if st.session_state.sel_l1_single:
        parts.append(f'<span class="sep">/</span><span>{st.session_state.sel_l1_single}</span>')
    if st.session_state.sel_l2:
        parts.append(f'<span class="sep">/</span><span>{st.session_state.sel_l2}</span>')
    if st.session_state.sel_l3:
        parts.append(f'<span class="sep">/</span><span>{st.session_state.sel_l3}</span>')
    st.markdown(f'<div class="breadcrumb">{"".join(parts)}</div>', unsafe_allow_html=True)

    # ── L1
    st.markdown('<div class="section-header">Mapping Livello 1 — Asset Class</div>', unsafe_allow_html=True)
    l1_items = clean_items(df['L1'])
    render_cards(l1_items, df, 'L1', 'sel_l1_single', multi=False)

    # ── L2
    if st.session_state.sel_l1_single:
        df_l1 = df[df['L1'] == st.session_state.sel_l1_single]
        l2_items = clean_items(df_l1['L2'])

        col_b, _ = st.columns([1, 5])
        with col_b:
            if st.button("← Reset L1", key="back_l1"):
                st.session_state.sel_l1_single = None
                st.session_state.sel_l2 = None
                st.session_state.sel_l3 = None
                st.rerun()

        if l2_items:
            st.markdown(f'<div class="section-header">Mapping Livello 2 — {st.session_state.sel_l1_single}</div>', unsafe_allow_html=True)
            render_cards(l2_items, df_l1, 'L2', 'sel_l2', multi=False)

    # ── L3
    if st.session_state.sel_l1_single and st.session_state.sel_l2:
        df_l2 = df[(df['L1'] == st.session_state.sel_l1_single) & (df['L2'] == st.session_state.sel_l2)]
        l3_items = clean_items(df_l2['L3'])

        col_b2, _ = st.columns([1, 5])
        with col_b2:
            if st.button("← Reset L2", key="back_l2"):
                st.session_state.sel_l2 = None
                st.session_state.sel_l3 = None
                st.rerun()

        if l3_items:
            st.markdown(f'<div class="section-header">Mapping Livello 3 — {st.session_state.sel_l2}</div>', unsafe_allow_html=True)
            render_cards(l3_items, df_l2, 'L3', 'sel_l3', multi=False)

    # ── Scenarios
    if st.session_state.sel_l1_single and st.session_state.sel_l2 and st.session_state.sel_l3:
        df_l3 = df[
            (df['L1'] == st.session_state.sel_l1_single) &
            (df['L2'] == st.session_state.sel_l2) &
            (df['L3'] == st.session_state.sel_l3)
        ]
        col_b3, _ = st.columns([1, 5])
        with col_b3:
            if st.button("← Reset L3", key="back_l3"):
                st.session_state.sel_l3 = None
                st.rerun()

        st.markdown(f'<div class="section-header">Scenari — {st.session_state.sel_l3}</div>', unsafe_allow_html=True)
        render_scenario_table(df_l3, show_asset_cols=False)


# ══════════════════════════════════════════════════════════════════════════════
# MODE B — MULTI-AREA
# ══════════════════════════════════════════════════════════════════════════════

else:
    st.markdown(
        '<div class="hint-box">💡 Seleziona una o più aree di Livello 1 — vedrai tutti gli scenari che le stressano contemporaneamente.</div>',
        unsafe_allow_html=True
    )

    # ── L1 multi-select cards
    st.markdown('<div class="section-header">Seleziona Asset Class (multi-selezione)</div>', unsafe_allow_html=True)
    l1_items = clean_items(df['L1'])
    render_cards(l1_items, df, 'L1', 'sel_l1_set', multi=True)

    # ── Show selected pills + clear button
    if st.session_state.sel_l1_set:
        pills_html = " ".join([f'<span class="sel-pill">✓ {x}</span>' for x in sorted(st.session_state.sel_l1_set)])
        st.markdown(f'<div style="margin:8px 0 4px;">{pills_html}</div>', unsafe_allow_html=True)

        col_clear, _ = st.columns([1, 6])
        with col_clear:
            if st.button("✕ Deseleziona tutto", key="clear_multi"):
                st.session_state.sel_l1_set = set()
                st.rerun()

        # ── Filter: scenarios that appear in ALL selected L1 areas
        selected_list = list(st.session_state.sel_l1_set)

        # Get scenario sets per L1
        sets_per_l1 = [set(df[df['L1'] == l1]['Scenario'].unique()) for l1 in selected_list]
        common_scenarios = sets_per_l1[0].intersection(*sets_per_l1[1:]) if sets_per_l1 else set()

        if len(selected_list) == 1:
            # Single selection: show all rows for that L1
            df_show = df[df['L1'].isin(selected_list)].copy()
            show_asset = True
            label = f"Scenari che stressano: {selected_list[0]}"
        else:
            # Multiple: show only scenarios common to all selected L1s
            df_show = df[
                df['L1'].isin(selected_list) & df['Scenario'].isin(common_scenarios)
            ].drop_duplicates(subset=['Scenario']).copy()
            show_asset = False
            label = f"Scenari comuni a: {' · '.join(sorted(selected_list))}"

        st.markdown(f'<div class="section-header">{label}</div>', unsafe_allow_html=True)

        if df_show.empty:
            st.info("Nessuno scenario stessa contemporaneamente tutte le aree selezionate.")
        else:
            render_scenario_table(df_show, show_asset_cols=show_asset)
    else:
        st.markdown('<div style="font-family:DM Mono,monospace;font-size:0.78rem;color:#888880;margin-top:1rem;">← Clicca su una o più asset class per visualizzare gli scenari.</div>', unsafe_allow_html=True)


# ─── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(
    '<div style="font-family:DM Mono,monospace;font-size:0.6rem;color:#c8c4bc;text-align:center;">Stress Test Dashboard · ListaxMapping / Pivot · MAIN</div>',
    unsafe_allow_html=True
)
