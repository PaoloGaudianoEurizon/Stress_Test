import streamlit as st
import pandas as pd
import numpy as np
import re

# ─── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Stress Test Mapping", page_icon="📊", layout="wide")

# ─── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@400;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Syne', sans-serif; }
.stApp { background: #f5f5f0; color: #1a1a1a; }

.stButton > button {
    background: #ffffff; color: #1a1a1a;
    border: 1.5px solid #d4d0c8; border-radius: 8px;
    font-family: 'Syne', sans-serif; font-weight: 600; font-size: 0.85rem;
    transition: all 0.15s ease;
}
.stButton > button:hover { border-color: #1a1a1a; background: #1a1a1a; color: #ffffff; }

.main-title {
    font-size: 2.4rem; font-weight: 800; letter-spacing: -1px; color: #1a1a1a;
    border-bottom: 3px solid #1a1a1a; padding-bottom: 0.4rem; margin-bottom: 0.3rem;
}
.subtitle {
    font-family: 'DM Mono', monospace; font-size: 0.75rem; color: #888880;
    margin-bottom: 2rem; letter-spacing: 0.08em; text-transform: uppercase;
}
.breadcrumb {
    font-family: 'DM Mono', monospace; font-size: 0.72rem; color: #888880;
    margin-bottom: 1.5rem; letter-spacing: 0.06em;
}
.breadcrumb span { color: #1a1a1a; font-weight: 600; }
.breadcrumb .sep { color: #c8c4bc; margin: 0 6px; }

.card-sub {
    font-family: 'DM Mono', monospace; font-size: 0.65rem; color: #888880;
    margin-top: -10px; margin-bottom: 4px; min-height: 18px;
}

/* Quick filter mini-buttons row */
.qf-row {
    display: flex; gap: 5px; margin-bottom: 12px; flex-wrap: wrap;
}
/* These are rendered via st.button with custom key, styled small via CSS override */
div[data-qfbtn="true"] .stButton > button {
    font-size: 0.62rem !important;
    padding: 2px 8px !important;
    border-radius: 20px !important;
    font-family: 'DM Mono', monospace !important;
    font-weight: 500 !important;
    min-height: 0 !important;
    height: auto !important;
    line-height: 1.4 !important;
}
div[data-qfbtn="pos"] .stButton > button {
    border-color: #a8dfc3 !important; color: #0a7c45 !important; background: #e6f7ef !important;
}
div[data-qfbtn="pos"] .stButton > button:hover {
    background: #0a7c45 !important; color: #fff !important; border-color: #0a7c45 !important;
}
div[data-qfbtn="neg"] .stButton > button {
    border-color: #f5c0ba !important; color: #c0392b !important; background: #fdecea !important;
}
div[data-qfbtn="neg"] .stButton > button:hover {
    background: #c0392b !important; color: #fff !important; border-color: #c0392b !important;
}
div[data-qfbtn="pos_active"] .stButton > button {
    background: #0a7c45 !important; color: #fff !important; border-color: #0a7c45 !important;
    font-size: 0.62rem !important; padding: 2px 8px !important; border-radius: 20px !important;
    font-family: 'DM Mono', monospace !important; font-weight: 500 !important;
}
div[data-qfbtn="neg_active"] .stButton > button {
    background: #c0392b !important; color: #fff !important; border-color: #c0392b !important;
    font-size: 0.62rem !important; padding: 2px 8px !important; border-radius: 20px !important;
    font-family: 'DM Mono', monospace !important; font-weight: 500 !important;
}

.sel-pill {
    display: inline-block; background: #1a1a1a; color: #f5f5f0;
    border-radius: 4px; font-family: 'DM Mono', monospace; font-size: 0.62rem;
    padding: 1px 8px; margin: 2px; letter-spacing: 0.04em;
}
.section-header {
    font-size: 0.68rem; font-family: 'DM Mono', monospace; text-transform: uppercase;
    letter-spacing: 0.14em; color: #888880; margin: 1.8rem 0 0.9rem;
    display: flex; align-items: center; gap: 10px;
}
.section-header::after { content: ''; flex: 1; height: 1px; background: #d4d0c8; }

.hint-box {
    background: #fff8e8; border: 1.5px solid #f0d080; border-radius: 8px;
    padding: 0.6rem 1rem; font-family: 'DM Mono', monospace; font-size: 0.72rem;
    color: #7a5a00; margin-bottom: 1.2rem;
}

/* Quick-filter result banner */
.qf-banner {
    background: #fff; border: 1.5px solid #d4d0c8; border-radius: 8px;
    padding: 0.5rem 1rem; font-family: 'DM Mono', monospace; font-size: 0.72rem;
    color: #555; margin-bottom: 1rem; display: flex; align-items: center; gap: 8px;
}

/* Stat boxes */
.stat-row { display: flex; gap: 14px; margin-bottom: 1.5rem; flex-wrap: wrap; }
.stat-box {
    background: #ffffff; border: 1.5px solid #d4d0c8; border-radius: 10px;
    padding: 0.75rem 1.2rem; min-width: 130px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.stat-box .sv { font-size: 1.6rem; font-weight: 800; color: #1a1a1a; line-height: 1; }
.stat-box .sk { font-family: 'DM Mono', monospace; font-size: 0.63rem; color: #888880; text-transform: uppercase; letter-spacing: 0.07em; margin-top: 4px; }

/* Scenario table */
.scenario-table {
    width: 100%; border-collapse: collapse; font-family: 'DM Mono', monospace;
    font-size: 0.78rem; background: #ffffff; border-radius: 10px;
    overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,0.07);
}
.scenario-table th {
    background: #1a1a1a; color: #f5f5f0; text-transform: uppercase;
    letter-spacing: 0.08em; padding: 11px 16px; text-align: left;
    font-weight: 500; font-size: 0.7rem;
}
.scenario-table td {
    padding: 10px 16px; border-bottom: 1px solid #f0ede6;
    color: #2a2a2a; vertical-align: top;
}
.scenario-table tr:last-child td { border-bottom: none; }
.scenario-table tr:hover td { background: #fafaf7; }
.shock-pos { color: #0a7c45; font-weight: 600; }
.shock-neg { color: #c0392b; font-weight: 600; }
.shock-zero { color: #888880; }
.long-des { font-size: 0.71rem; color: #666660; margin-top: 4px; line-height: 1.45; font-family: 'Syne', sans-serif; font-weight: 400; }
.shock-list { display: flex; flex-direction: column; gap: 3px; }
.shock-row-item { display: flex; gap: 6px; align-items: baseline; }
.shock-path { font-size: 0.62rem; color: #aaa; }
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
    return sorted([str(i) for i in series.dropna().unique()
                   if str(i).strip() not in ('', 'nan')])

def count_pos_neg(df_sub):
    n_pos = int((df_sub['_shock_num'] > 0).sum())
    n_neg = int((df_sub['_shock_num'] < 0).sum())
    return n_pos, n_neg

# ─── DATA ──────────────────────────────────────────────────────────────────────
FILE_PATH = "ListaxMapping.xlsx"

@st.cache_data
def load_data():
    df = pd.read_excel(FILE_PATH, sheet_name="Pivot", header=0)
    df.columns = ['Scenario', 'L1', 'L2', 'L3', 'ShockValue'] + list(df.columns[5:])
    df = df[['Scenario', 'L1', 'L2', 'L3', 'ShockValue']].copy()
    for col in ['Scenario', 'L1', 'L2', 'L3']:
        df[col] = df[col].ffill()
    df = df.dropna(subset=['L1'])
    df = df[df['L1'].astype(str).str.strip().astype(bool)]
    df = df[df['L1'].astype(str).str.lower() != 'nan']
    df['_shock_num'] = df['ShockValue'].apply(parse_shock_value)
    try:
        dm = pd.read_excel(FILE_PATH, sheet_name="MAIN", header=0)
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

desc_map = dict(zip(dm['Stress_Scenarios'], dm['Long_des']))

# ─── SESSION STATE ─────────────────────────────────────────────────────────────
defaults = {
    'sel_l1_set': set(),
    'sel_l1_single': None,
    'sel_l2': None,
    'sel_l3': None,
    'mode': 'drill',
    'shock_filter': 'all',
    # quick filter: {'level': 'L1'/'L2', 'item': str, 'dir': 'pos'/'neg'}
    'quick_filter': None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─── HEADER ────────────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">Stress Test Mapping</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Asset class drill-down · Shock direction analysis</div>', unsafe_allow_html=True)

col_m1, col_m2, col_m3 = st.columns([2, 2, 8])
with col_m1:
    if st.button("🔍 Drill-down", use_container_width=True):
        st.session_state.mode = 'drill'
        st.session_state.sel_l1_set = set()
        st.session_state.sel_l2 = None
        st.session_state.sel_l3 = None
        st.session_state.shock_filter = 'all'
        st.session_state.quick_filter = None
        st.rerun()
with col_m2:
    if st.button("🔀 Multi-area", use_container_width=True):
        st.session_state.mode = 'multi'
        st.session_state.sel_l2 = None
        st.session_state.sel_l3 = None
        st.session_state.shock_filter = 'all'
        st.session_state.quick_filter = None
        st.rerun()
st.markdown("---")

# ─── QUICK FILTER BUTTONS (small pills under each card) ───────────────────────

def quick_filter_buttons(item, df_sub, level_key):
    """
    Renders two small pill buttons (▲ pos, ▼ neg) under a card.
    Uses a Streamlit container with custom data attribute via markdown trick.
    """
    n_pos, n_neg = count_pos_neg(df_sub)
    qf = st.session_state.quick_filter
    is_active_pos = qf and qf['item'] == item and qf['dir'] == 'pos' and qf['level'] == level_key
    is_active_neg = qf and qf['item'] == item and qf['dir'] == 'neg' and qf['level'] == level_key

    c_pos, c_neg, c_rest = st.columns([1, 1, 3])

    with c_pos:
        tag_pos = "pos_active" if is_active_pos else "pos"
        st.markdown(f'<div data-qfbtn="{tag_pos}">', unsafe_allow_html=True)
        if st.button(f"▲ {n_pos}", key=f"qf_pos_{level_key}_{item}", use_container_width=True,
                     help=f"{n_pos} shock positivi in {item}"):
            if is_active_pos:
                st.session_state.quick_filter = None
            else:
                st.session_state.quick_filter = {'level': level_key, 'item': item, 'dir': 'pos'}
                # clear drill selections below
                if level_key == 'L1':
                    st.session_state.sel_l1_single = None
                    st.session_state.sel_l2 = None
                    st.session_state.sel_l3 = None
                elif level_key == 'L2':
                    st.session_state.sel_l3 = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with c_neg:
        tag_neg = "neg_active" if is_active_neg else "neg"
        st.markdown(f'<div data-qfbtn="{tag_neg}">', unsafe_allow_html=True)
        if st.button(f"▼ {n_neg}", key=f"qf_neg_{level_key}_{item}", use_container_width=True,
                     help=f"{n_neg} shock negativi in {item}"):
            if is_active_neg:
                st.session_state.quick_filter = None
            else:
                st.session_state.quick_filter = {'level': level_key, 'item': item, 'dir': 'neg'}
                if level_key == 'L1':
                    st.session_state.sel_l1_single = None
                    st.session_state.sel_l2 = None
                    st.session_state.sel_l3 = None
                elif level_key == 'L2':
                    st.session_state.sel_l3 = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ─── CARD RENDERER ─────────────────────────────────────────────────────────────

def render_cards(items, df_filtered, col_name, on_select_key, multi=False, show_qf=False):
    if not items: return
    ncols = min(len(items), 4)
    cols = st.columns(ncols)
    for i, item in enumerate(items):
        sub = df_filtered[df_filtered[col_name] == item]
        mean_v = mean_shock_for_group(sub)
        n_sc = sub['Scenario'].nunique()
        d = shock_direction(mean_v)
        lbl, col_hex = direction_label(d)
        is_sel = (item in st.session_state.sel_l1_set) if multi else (st.session_state.get(on_select_key) == item)
        btn_label = f"{'✓ ' if is_sel else ''}{item}"

        with cols[i % ncols]:
            clicked = st.button(btn_label, key=f"btn_{on_select_key}_{item}", use_container_width=True)
            st.markdown(
                f'<div class="card-sub"><span style="color:{col_hex};font-weight:600;">{lbl}</span>'
                f'&nbsp;·&nbsp;{n_sc} scenari</div>',
                unsafe_allow_html=True
            )
            # Quick filter mini-buttons
            if show_qf:
                quick_filter_buttons(item, sub, col_name)

            if clicked:
                # Clicking the main card clears any quick filter for that item
                if st.session_state.quick_filter and st.session_state.quick_filter.get('item') == item:
                    st.session_state.quick_filter = None
                if multi:
                    if item in st.session_state.sel_l1_set:
                        st.session_state.sel_l1_set.discard(item)
                    else:
                        st.session_state.sel_l1_set.add(item)
                    st.session_state.shock_filter = 'all'
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

# ─── STAT BOXES ────────────────────────────────────────────────────────────────

def render_stat_boxes(df_sub):
    mean_v = mean_shock_for_group(df_sub)
    n_sc   = df_sub['Scenario'].nunique()
    n_pos  = int((df_sub['_shock_num'] > 0).sum())
    n_neg  = int((df_sub['_shock_num'] < 0).sum())
    d      = shock_direction(mean_v)
    lbl, col_hex = direction_label(d)
    cur_filter = st.session_state.shock_filter

    c0, c1, c2, c3, _ = st.columns([1.4, 1.8, 1.4, 1.4, 5])
    with c0:
        st.markdown(f'<div class="stat-box"><div class="sv">{n_sc}</div><div class="sk">Scenari totali</div></div>', unsafe_allow_html=True)
    with c1:
        st.markdown(f'<div class="stat-box"><div class="sv" style="color:{col_hex};font-size:1.05rem;">{lbl}</div><div class="sk">Direzione prevalente</div></div>', unsafe_allow_html=True)
    with c2:
        if st.button(f"▲ {n_pos}  positivi", key="filter_pos", use_container_width=True):
            st.session_state.shock_filter = 'all' if cur_filter == 'pos' else 'pos'
            st.rerun()
        if cur_filter == 'pos':
            st.markdown('<div style="height:3px;background:#0a7c45;border-radius:2px;margin-top:-6px;"></div>', unsafe_allow_html=True)
    with c3:
        if st.button(f"▼ {n_neg}  negativi", key="filter_neg", use_container_width=True):
            st.session_state.shock_filter = 'all' if cur_filter == 'neg' else 'neg'
            st.rerun()
        if cur_filter == 'neg':
            st.markdown('<div style="height:3px;background:#c0392b;border-radius:2px;margin-top:-6px;"></div>', unsafe_allow_html=True)

# ─── SCENARIO TABLE ────────────────────────────────────────────────────────────

def render_scenario_table(df_sub, multi_mode=False, banner_text=None):
    render_stat_boxes(df_sub)

    f = st.session_state.shock_filter
    if f == 'pos':
        df_filt = df_sub[df_sub['_shock_num'] > 0]
    elif f == 'neg':
        df_filt = df_sub[df_sub['_shock_num'] < 0]
    else:
        df_filt = df_sub

    if banner_text:
        st.markdown(f'<div class="qf-banner">{banner_text}</div>', unsafe_allow_html=True)

    if df_filt.empty:
        st.info("Nessuno scenario corrisponde al filtro selezionato.")
        return

    if not multi_mode:
        rows_html = ""
        for _, row in df_filt.sort_values('Scenario').iterrows():
            shock_num = row['_shock_num']
            shock_raw = str(row['ShockValue']) if not pd.isna(row['ShockValue']) else "—"
            long_des  = desc_map.get(str(row['Scenario']).strip(), '')
            try:   is_num = not np.isnan(float(shock_num))
            except: is_num = False
            cls   = ("shock-pos" if shock_num > 0 else "shock-neg") if is_num and shock_num != 0 else "shock-zero"
            arrow = ("▲ " if shock_num > 0 else "▼ ") if is_num and shock_num != 0 else ""
            des_html = f'<div class="long-des">{long_des}</div>' if long_des else ''
            rows_html += f"<tr><td><strong>{row['Scenario']}</strong>{des_html}</td><td class='{cls}'>{arrow}{shock_raw}</td></tr>"

        st.markdown(f"""
        <table class="scenario-table">
            <thead><tr><th>Scenario</th><th>Shock Value</th></tr></thead>
            <tbody>{rows_html}</tbody>
        </table>""", unsafe_allow_html=True)
    else:
        rows_html = ""
        for scenario in sorted(df_filt['Scenario'].unique()):
            sc_rows  = df_filt[df_filt['Scenario'] == scenario]
            long_des = desc_map.get(str(scenario).strip(), '')
            des_html = f'<div class="long-des">{long_des}</div>' if long_des else ''
            shock_items = ""
            for _, r in sc_rows.iterrows():
                sn = r['_shock_num']
                sr = str(r['ShockValue']) if not pd.isna(r['ShockValue']) else "—"
                try:   is_num = not np.isnan(float(sn))
                except: is_num = False
                cls   = ("shock-pos" if sn > 0 else "shock-neg") if is_num and sn != 0 else "shock-zero"
                arrow = ("▲ " if sn > 0 else "▼ ") if is_num and sn != 0 else ""
                path  = " › ".join([str(r[c]) for c in ['L1','L2','L3'] if str(r.get(c,'')).strip() not in ('','nan')])
                shock_items += f'<div class="shock-row-item"><span class="{cls}">{arrow}{sr}</span><span class="shock-path">{path}</span></div>'
            rows_html += f"<tr><td><strong>{scenario}</strong>{des_html}</td><td><div class='shock-list'>{shock_items}</div></td></tr>"

        st.markdown(f"""
        <table class="scenario-table">
            <thead><tr><th>Scenario</th><th>Shock per area selezionata</th></tr></thead>
            <tbody>{rows_html}</tbody>
        </table>""", unsafe_allow_html=True)
        st.markdown(
            '<div style="font-family:DM Mono,monospace;font-size:0.65rem;color:#aaa;margin-top:8px;">'
            '⚠️ Valori raw dall\'Excel per ciascun path L1 › L2 › L3 — non medie.</div>',
            unsafe_allow_html=True)

# ─── QUICK FILTER RESULT (shown when a quick filter is active) ─────────────────

def maybe_show_quick_filter_result(df_source):
    """If a quick_filter is set, show the filtered table right after the cards."""
    qf = st.session_state.quick_filter
    if not qf:
        return False
    col_name = qf['level']
    item     = qf['item']
    direction = qf['dir']

    df_item = df_source[df_source[col_name] == item]
    if direction == 'pos':
        df_show = df_item[df_item['_shock_num'] > 0]
        dir_label = "▲ Shock Positivi"
        dir_color = "#0a7c45"
    else:
        df_show = df_item[df_item['_shock_num'] < 0]
        dir_label = "▼ Shock Negativi"
        dir_color = "#c0392b"

    st.markdown(
        f'<div class="section-header" style="color:{dir_color};">'
        f'{dir_label} — {item}</div>',
        unsafe_allow_html=True
    )

    col_reset, _ = st.columns([1.5, 8])
    with col_reset:
        if st.button("✕ Chiudi filtro", key="close_qf"):
            st.session_state.quick_filter = None
            st.rerun()

    if df_show.empty:
        st.info(f"Nessuno scenario con shock {'positivo' if direction == 'pos' else 'negativo'} in {item}.")
    else:
        render_scenario_table(df_show, multi_mode=False)

    return True


# ══════════════════════════════════════════════════════════════════════════════
# MODE A — DRILL-DOWN
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.mode == 'drill':

    parts = ['<span>All</span>']
    if st.session_state.sel_l1_single:
        parts.append(f'<span class="sep">/</span><span>{st.session_state.sel_l1_single}</span>')
    if st.session_state.sel_l2:
        parts.append(f'<span class="sep">/</span><span>{st.session_state.sel_l2}</span>')
    if st.session_state.sel_l3:
        parts.append(f'<span class="sep">/</span><span>{st.session_state.sel_l3}</span>')
    st.markdown(f'<div class="breadcrumb">{"".join(parts)}</div>', unsafe_allow_html=True)

    # ── L1 cards + quick filter buttons
    st.markdown('<div class="section-header">Mapping Livello 1 — Asset Class</div>', unsafe_allow_html=True)
    render_cards(clean_items(df['L1']), df, 'L1', 'sel_l1_single', multi=False, show_qf=True)

    # If a quick filter is active at L1 level, show results and stop drilling
    qf = st.session_state.quick_filter
    if qf and qf['level'] == 'L1':
        maybe_show_quick_filter_result(df)

    elif st.session_state.sel_l1_single:
        df_l1 = df[df['L1'] == st.session_state.sel_l1_single]
        l2_items = clean_items(df_l1['L2'])

        col_b, _ = st.columns([1, 5])
        with col_b:
            if st.button("← Reset L1", key="back_l1"):
                st.session_state.sel_l1_single = None
                st.session_state.sel_l2 = None
                st.session_state.sel_l3 = None
                st.session_state.shock_filter = 'all'
                st.session_state.quick_filter = None
                st.rerun()

        if l2_items:
            st.markdown(f'<div class="section-header">Livello 2 — {st.session_state.sel_l1_single}</div>', unsafe_allow_html=True)
            render_cards(l2_items, df_l1, 'L2', 'sel_l2', multi=False, show_qf=True)

            # Quick filter at L2 level
            if qf and qf['level'] == 'L2':
                maybe_show_quick_filter_result(df_l1)

            elif st.session_state.sel_l2:
                df_l2 = df_l1[df_l1['L2'] == st.session_state.sel_l2]
                l3_items = clean_items(df_l2['L3'])

                col_b2, _ = st.columns([1, 5])
                with col_b2:
                    if st.button("← Reset L2", key="back_l2"):
                        st.session_state.sel_l2 = None
                        st.session_state.sel_l3 = None
                        st.session_state.shock_filter = 'all'
                        st.session_state.quick_filter = None
                        st.rerun()

                if l3_items:
                    st.markdown(f'<div class="section-header">Livello 3 — {st.session_state.sel_l2}</div>', unsafe_allow_html=True)
                    render_cards(l3_items, df_l2, 'L3', 'sel_l3', multi=False, show_qf=False)

                if st.session_state.sel_l3:
                    df_l3 = df_l2[df_l2['L3'] == st.session_state.sel_l3]

                    col_b3, _ = st.columns([1, 5])
                    with col_b3:
                        if st.button("← Reset L3", key="back_l3"):
                            st.session_state.sel_l3 = None
                            st.session_state.shock_filter = 'all'
                            st.session_state.quick_filter = None
                            st.rerun()

                    st.markdown(f'<div class="section-header">Scenari — {st.session_state.sel_l3}</div>', unsafe_allow_html=True)
                    render_scenario_table(df_l3, multi_mode=False)


# ══════════════════════════════════════════════════════════════════════════════
# MODE B — MULTI-AREA
# ══════════════════════════════════════════════════════════════════════════════
else:
    st.markdown(
        '<div class="hint-box">💡 Seleziona una o più aree di Livello 1. '
        'Con una sola area vedi tutti i suoi scenari. '
        'Con più aree vedi gli scenari <strong>comuni a tutte</strong>, con i rispettivi shock per area.</div>',
        unsafe_allow_html=True
    )

    st.markdown('<div class="section-header">Seleziona Asset Class (multi-selezione)</div>', unsafe_allow_html=True)
    render_cards(clean_items(df['L1']), df, 'L1', 'sel_l1_set', multi=True, show_qf=False)

    if st.session_state.sel_l1_set:
        pills_html = " ".join([f'<span class="sel-pill">✓ {x}</span>' for x in sorted(st.session_state.sel_l1_set)])
        st.markdown(f'<div style="margin:8px 0 4px;">{pills_html}</div>', unsafe_allow_html=True)

        col_clear, _ = st.columns([1.5, 8])
        with col_clear:
            if st.button("✕ Deseleziona tutto", key="clear_multi"):
                st.session_state.sel_l1_set = set()
                st.session_state.shock_filter = 'all'
                st.rerun()

        selected_list = list(st.session_state.sel_l1_set)
        if len(selected_list) == 1:
            df_show = df[df['L1'].isin(selected_list)].copy()
            label = f"Scenari in: {selected_list[0]}"
            is_multi = False
        else:
            sets_per_l1 = [set(df[df['L1'] == l1]['Scenario'].unique()) for l1 in selected_list]
            common = sets_per_l1[0].intersection(*sets_per_l1[1:])
            df_show = df[df['L1'].isin(selected_list) & df['Scenario'].isin(common)].copy()
            label = f"Scenari comuni a: {' · '.join(sorted(selected_list))}"
            is_multi = True

        st.markdown(f'<div class="section-header">{label}</div>', unsafe_allow_html=True)
        if df_show.empty:
            st.info("Nessuno scenario stessa contemporaneamente tutte le aree selezionate.")
        else:
            render_scenario_table(df_show, multi_mode=is_multi)
    else:
        st.markdown(
            '<div style="font-family:DM Mono,monospace;font-size:0.78rem;color:#888880;margin-top:1rem;">'
            '← Clicca su una o più asset class per visualizzare gli scenari.</div>',
            unsafe_allow_html=True
        )

# ─── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(
    '<div style="font-family:DM Mono,monospace;font-size:0.6rem;color:#c8c4bc;text-align:center;">'
    'Stress Test Dashboard · ListaxMapping / Pivot · MAIN</div>',
    unsafe_allow_html=True
)
