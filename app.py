import streamlit as st
import pandas as pd
import numpy as np
import re
from io import BytesIO

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

/* Download all button — prominent */
div[data-dlall="true"] .stDownloadButton > button {
    background: #1a1a1a !important; color: #f5f5f0 !important;
    border: none !important; border-radius: 8px !important;
    font-family: 'DM Mono', monospace !important; font-size: 0.72rem !important;
    font-weight: 500 !important; letter-spacing: 0.05em !important;
    padding: 6px 14px !important;
}
div[data-dlall="true"] .stDownloadButton > button:hover {
    background: #333 !important;
}

/* Per-row download button — small icon style */
div[data-dlrow="true"] .stDownloadButton > button {
    background: transparent !important; color: #888880 !important;
    border: 1px solid #d4d0c8 !important; border-radius: 6px !important;
    font-size: 0.75rem !important; padding: 2px 8px !important;
    min-height: 0 !important; font-family: 'DM Mono', monospace !important;
    font-weight: 400 !important;
}
div[data-dlrow="true"] .stDownloadButton > button:hover {
    background: #1a1a1a !important; color: #fff !important; border-color: #1a1a1a !important;
}

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

/* Quick filter mini-buttons */
div[data-qfbtn="pos"] .stButton > button {
    border-color: #a8dfc3 !important; color: #0a7c45 !important; background: #e6f7ef !important;
    font-size: 0.62rem !important; padding: 2px 8px !important; border-radius: 20px !important;
    font-family: 'DM Mono', monospace !important; font-weight: 500 !important;
}
div[data-qfbtn="pos"] .stButton > button:hover {
    background: #0a7c45 !important; color: #fff !important; border-color: #0a7c45 !important;
}
div[data-qfbtn="neg"] .stButton > button {
    border-color: #f5c0ba !important; color: #c0392b !important; background: #fdecea !important;
    font-size: 0.62rem !important; padding: 2px 8px !important; border-radius: 20px !important;
    font-family: 'DM Mono', monospace !important; font-weight: 500 !important;
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

/* Stat boxes */
.stat-row { display: flex; gap: 14px; margin-bottom: 1.5rem; flex-wrap: wrap; }
.stat-box {
    background: #ffffff; border: 1.5px solid #d4d0c8; border-radius: 10px;
    padding: 0.75rem 1.2rem; min-width: 130px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.stat-box .sv { font-size: 1.6rem; font-weight: 800; color: #1a1a1a; line-height: 1; }
.stat-box .sk { font-family: 'DM Mono', monospace; font-size: 0.63rem; color: #888880; text-transform: uppercase; letter-spacing: 0.07em; margin-top: 4px; }

/* Table header row */
.tbl-header {
    display: flex; align-items: center;
    background: #1a1a1a; border-radius: 10px 10px 0 0;
    padding: 9px 16px;
    font-family: 'DM Mono', monospace; font-size: 0.68rem; font-weight: 500;
    text-transform: uppercase; letter-spacing: 0.08em; color: #f5f5f0;
    margin-bottom: 0;
}
/* Table body rows */
.tbl-row {
    background: #ffffff;
    border-left: 1.5px solid #e8e4dc;
    border-right: 1.5px solid #e8e4dc;
    border-bottom: 1px solid #f0ede6;
    padding: 8px 16px;
    font-family: 'DM Mono', monospace; font-size: 0.78rem;
}
.tbl-row:last-child {
    border-radius: 0 0 10px 10px;
    border-bottom: 1.5px solid #e8e4dc;
}
.tbl-row:hover { background: #fafaf7; }
.sc-name { font-weight: 700; font-family: 'Syne', sans-serif; font-size: 0.82rem; color: #1a1a1a; }
.sc-des { font-size: 0.71rem; color: #666660; margin-top: 2px; line-height: 1.4; font-family: 'Syne', sans-serif; font-weight: 400; }
.shock-pos { color: #0a7c45; font-weight: 600; }
.shock-neg { color: #c0392b; font-weight: 600; }
.shock-zero { color: #888880; }
.shock-list-inline { display: flex; flex-direction: column; gap: 2px; }
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
    return int((df_sub['_shock_num'] > 0).sum()), int((df_sub['_shock_num'] < 0).sum())

def shock_cls_arrow(shock_num):
    try:
        is_num = not np.isnan(float(shock_num))
    except:
        is_num = False
    if is_num and shock_num > 0:
        return "shock-pos", "▲ "
    elif is_num and shock_num < 0:
        return "shock-neg", "▼ "
    return "shock-zero", ""

# ─── EXCEL BUILDERS ────────────────────────────────────────────────────────────

def build_scenario_excel(scenario_name, df_full, desc_map):
    """All shocks for a single scenario across ALL asset classes."""
    df_sc = df_full[df_full['Scenario'] == scenario_name].copy()
    df_sc = df_sc[['Scenario', 'L1', 'L2', 'L3', 'ShockValue']].copy()
    df_sc.insert(1, 'Description', desc_map.get(str(scenario_name).strip(), ''))
    out = BytesIO()
    with pd.ExcelWriter(out, engine='openpyxl') as w:
        df_sc.to_excel(w, sheet_name='Scenario', index=False)
    return out.getvalue()

def build_scenarios_excel(scenarios_list, df_full, desc_map):
    """All shocks for a list of scenarios across ALL asset classes."""
    df_exp = df_full[df_full['Scenario'].isin(scenarios_list)].copy()
    df_exp = df_exp[['Scenario', 'L1', 'L2', 'L3', 'ShockValue']].copy()
    df_exp.insert(1, 'Description', df_exp['Scenario'].map(
        lambda s: desc_map.get(str(s).strip(), '')
    ))
    out = BytesIO()
    with pd.ExcelWriter(out, engine='openpyxl') as w:
        df_exp.to_excel(w, sheet_name='Scenarios', index=False)
    return out.getvalue()

def build_all_excel(df_full, desc_map):
    """Every scenario with every shock."""
    df_exp = df_full[['Scenario', 'L1', 'L2', 'L3', 'ShockValue']].copy()
    df_exp.insert(1, 'Description', df_exp['Scenario'].map(
        lambda s: desc_map.get(str(s).strip(), '')
    ))
    out = BytesIO()
    with pd.ExcelWriter(out, engine='openpyxl') as w:
        df_exp.to_excel(w, sheet_name='All Scenarios', index=False)
    return out.getvalue()

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
    'sel_l1_set': set(), 'sel_l1_single': None,
    'sel_l2': None, 'sel_l3': None,
    'mode': 'drill',
    'shock_filter': 'all',
    'quick_filter': None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─── HEADER ────────────────────────────────────────────────────────────────────
hdr_left, hdr_right = st.columns([8, 2])
with hdr_left:
    st.markdown('<div class="main-title">Stress Test Mapping</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Asset class drill-down · Shock direction analysis</div>', unsafe_allow_html=True)
with hdr_right:
    st.markdown('<div style="height:1.2rem;"></div>', unsafe_allow_html=True)
    st.markdown('<div data-dlall="true">', unsafe_allow_html=True)
    all_excel = build_all_excel(df, desc_map)
    st.download_button(
        label="⬇ Download All Scenarios",
        data=all_excel,
        file_name="all_scenarios_shocks.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="dl_all_scenarios",
        use_container_width=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)

col_m1, col_m2, col_m3 = st.columns([3, 3, 6])
with col_m1:
    if st.button("🔍 Single Asset Class Analysis", use_container_width=True):
        st.session_state.mode = 'drill'
        st.session_state.sel_l1_set = set()
        st.session_state.sel_l2 = None
        st.session_state.sel_l3 = None
        st.session_state.shock_filter = 'all'
        st.session_state.quick_filter = None
        st.rerun()
with col_m2:
    if st.button("🔀 Multi Asset Class Analysis", use_container_width=True):
        st.session_state.mode = 'multi'
        st.session_state.sel_l2 = None
        st.session_state.sel_l3 = None
        st.session_state.shock_filter = 'all'
        st.session_state.quick_filter = None
        st.rerun()
st.markdown("---")

# ─── QUICK FILTER BUTTONS ──────────────────────────────────────────────────────

def quick_filter_buttons(item, df_sub, level_key):
    n_pos, n_neg = count_pos_neg(df_sub)
    qf = st.session_state.quick_filter
    is_active_pos = qf and qf['item'] == item and qf['dir'] == 'pos' and qf['level'] == level_key
    is_active_neg = qf and qf['item'] == item and qf['dir'] == 'neg' and qf['level'] == level_key
    c_pos, c_neg, _ = st.columns([1, 1, 3])
    with c_pos:
        tag = "pos_active" if is_active_pos else "pos"
        st.markdown(f'<div data-qfbtn="{tag}">', unsafe_allow_html=True)
        if st.button(f"▲ {n_pos}", key=f"qf_pos_{level_key}_{item}", use_container_width=True):
            st.session_state.quick_filter = None if is_active_pos else {'level': level_key, 'item': item, 'dir': 'pos'}
            if not is_active_pos and level_key == 'L1':
                st.session_state.sel_l1_single = None
                st.session_state.sel_l2 = None
                st.session_state.sel_l3 = None
            elif not is_active_pos and level_key == 'L2':
                st.session_state.sel_l3 = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with c_neg:
        tag = "neg_active" if is_active_neg else "neg"
        st.markdown(f'<div data-qfbtn="{tag}">', unsafe_allow_html=True)
        if st.button(f"▼ {n_neg}", key=f"qf_neg_{level_key}_{item}", use_container_width=True):
            st.session_state.quick_filter = None if is_active_neg else {'level': level_key, 'item': item, 'dir': 'neg'}
            if not is_active_neg and level_key == 'L1':
                st.session_state.sel_l1_single = None
                st.session_state.sel_l2 = None
                st.session_state.sel_l3 = None
            elif not is_active_neg and level_key == 'L2':
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
            if show_qf:
                quick_filter_buttons(item, sub, col_name)
            if clicked:
                if st.session_state.quick_filter and st.session_state.quick_filter.get('item') == item:
                    st.session_state.quick_filter = None
                if multi:
                    st.session_state.sel_l1_set.discard(item) if item in st.session_state.sel_l1_set else st.session_state.sel_l1_set.add(item)
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

def render_scenario_table(df_sub, multi_mode=False):
    """
    Renders stat boxes + scenario table with per-row download buttons.
    Downloads always include ALL shocks for the scenario across the full dataset.
    """
    render_stat_boxes(df_sub)

    f = st.session_state.shock_filter
    if f == 'pos':
        df_filt = df_sub[df_sub['_shock_num'] > 0]
    elif f == 'neg':
        df_filt = df_sub[df_sub['_shock_num'] < 0]
    else:
        df_filt = df_sub

    if df_filt.empty:
        st.info("Nessuno scenario corrisponde al filtro selezionato.")
        return

    scenarios = sorted(df_filt['Scenario'].unique())

    # ── Table header
    if not multi_mode:
        st.markdown(
            '<div class="tbl-header">'
            '<div style="flex:5">Scenario</div>'
            '<div style="flex:2">Shock Value</div>'
            '<div style="flex:1;text-align:right;">Export</div>'
            '</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div class="tbl-header">'
            '<div style="flex:5">Scenario</div>'
            '<div style="flex:3">Shock per area selezionata</div>'
            '<div style="flex:1;text-align:right;">Export</div>'
            '</div>',
            unsafe_allow_html=True
        )

    # ── Rows
    for idx, scenario in enumerate(scenarios):
        sc_rows  = df_filt[df_filt['Scenario'] == scenario]
        long_des = desc_map.get(str(scenario).strip(), '')
        is_last  = (idx == len(scenarios) - 1)

        row_style = "tbl-row" + (" tbl-row-last" if is_last else "")

        with st.container():
            st.markdown(f'<div class="{row_style}">', unsafe_allow_html=True)

            if not multi_mode:
                # one row per scenario in drill mode (may have multiple paths, show first shock)
                first_row = sc_rows.iloc[0]
                sn  = first_row['_shock_num']
                sr  = str(first_row['ShockValue']) if not pd.isna(first_row['ShockValue']) else "—"
                cls, arrow = shock_cls_arrow(sn)
                des_html = f'<div class="sc-des">{long_des}</div>' if long_des else ''

                col_name, col_shock, col_dl = st.columns([5, 2, 1])
                with col_name:
                    st.markdown(f'<div class="sc-name">{scenario}</div>{des_html}', unsafe_allow_html=True)
                with col_shock:
                    st.markdown(f'<div style="padding-top:6px;" class="{cls}">{arrow}{sr}</div>', unsafe_allow_html=True)
            else:
                # multi mode: show all shocks per selected areas
                shock_items_html = ""
                for _, r in sc_rows.iterrows():
                    sn = r['_shock_num']
                    sr = str(r['ShockValue']) if not pd.isna(r['ShockValue']) else "—"
                    cls, arrow = shock_cls_arrow(sn)
                    path = " › ".join([str(r[c]) for c in ['L1', 'L2', 'L3']
                                       if str(r.get(c, '')).strip() not in ('', 'nan')])
                    shock_items_html += (
                        f'<div class="shock-row-item">'
                        f'<span class="{cls}">{arrow}{sr}</span>'
                        f'<span class="shock-path">{path}</span>'
                        f'</div>'
                    )

                des_html = f'<div class="sc-des">{long_des}</div>' if long_des else ''
                col_name, col_shock, col_dl = st.columns([5, 3, 1])
                with col_name:
                    st.markdown(f'<div class="sc-name">{scenario}</div>{des_html}', unsafe_allow_html=True)
                with col_shock:
                    st.markdown(f'<div class="shock-list-inline" style="padding-top:4px;">{shock_items_html}</div>', unsafe_allow_html=True)

            # ── Per-row download button (ALL shocks for this scenario from full df)
            with col_dl:
                sc_excel = build_scenario_excel(scenario, df, desc_map)
                st.markdown('<div data-dlrow="true">', unsafe_allow_html=True)
                st.download_button(
                    label="⬇",
                    data=sc_excel,
                    file_name=f"{scenario}_shocks.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key=f"dl_sc_{scenario}_{idx}",
                    help=f"Scarica tutti gli shock di {scenario}",
                )
                st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

    # ── Download visible list button
    st.markdown('<div style="margin-top:10px;"></div>', unsafe_allow_html=True)
    vis_excel = build_scenarios_excel(scenarios, df, desc_map)
    _, col_dl_all = st.columns([7, 3])
    with col_dl_all:
        st.markdown('<div data-dlall="true">', unsafe_allow_html=True)
        st.download_button(
            label="⬇ Scarica scenari visibili",
            data=vis_excel,
            file_name="scenari_selezionati_shocks.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key=f"dl_visible_{st.session_state.mode}_{st.session_state.shock_filter}",
            use_container_width=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

    if multi_mode:
        st.markdown(
            '<div style="font-family:DM Mono,monospace;font-size:0.65rem;color:#aaa;margin-top:6px;">'
            '⚠️ Valori raw dall\'Excel per ciascun path L1 › L2 › L3 — non medie. '
            'I download includono tutti gli shock dello scenario su tutte le asset class.</div>',
            unsafe_allow_html=True
        )

# ─── QUICK FILTER RESULT ───────────────────────────────────────────────────────

def maybe_show_quick_filter_result(df_source):
    qf = st.session_state.quick_filter
    if not qf:
        return False
    col_name  = qf['level']
    item      = qf['item']
    direction = qf['dir']
    df_item   = df_source[df_source[col_name] == item]
    df_show   = df_item[df_item['_shock_num'] > 0] if direction == 'pos' else df_item[df_item['_shock_num'] < 0]
    dir_label = "▲ Shock Positivi" if direction == 'pos' else "▼ Shock Negativi"
    dir_color = "#0a7c45" if direction == 'pos' else "#c0392b"

    st.markdown(f'<div class="section-header" style="color:{dir_color};">{dir_label} — {item}</div>', unsafe_allow_html=True)
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
# MODE A — SINGLE ASSET CLASS ANALYSIS
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

    st.markdown('<div class="section-header">Single Asset Class — Livello 1</div>', unsafe_allow_html=True)
    render_cards(clean_items(df['L1']), df, 'L1', 'sel_l1_single', multi=False, show_qf=True)

    qf = st.session_state.quick_filter
    if qf and qf['level'] == 'L1':
        maybe_show_quick_filter_result(df)

    elif st.session_state.sel_l1_single:
        df_l1    = df[df['L1'] == st.session_state.sel_l1_single]
        l2_items = clean_items(df_l1['L2'])

        col_b, _ = st.columns([1.2, 8])
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

            if qf and qf['level'] == 'L2':
                maybe_show_quick_filter_result(df_l1)

            elif st.session_state.sel_l2:
                df_l2    = df_l1[df_l1['L2'] == st.session_state.sel_l2]
                l3_items = clean_items(df_l2['L3'])

                col_b2, _ = st.columns([1.2, 8])
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

                    col_b3, _ = st.columns([1.2, 8])
                    with col_b3:
                        if st.button("← Reset L3", key="back_l3"):
                            st.session_state.sel_l3 = None
                            st.session_state.shock_filter = 'all'
                            st.session_state.quick_filter = None
                            st.rerun()

                    st.markdown(f'<div class="section-header">Scenari — {st.session_state.sel_l3}</div>', unsafe_allow_html=True)
                    render_scenario_table(df_l3, multi_mode=False)


# ══════════════════════════════════════════════════════════════════════════════
# MODE B — MULTI ASSET CLASS ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
else:
    st.markdown(
        '<div class="hint-box">💡 Seleziona una o più aree di Livello 1. '
        'Con una sola area vedi tutti i suoi scenari. '
        'Con più aree vedi gli scenari <strong>comuni a tutte</strong>, con i rispettivi shock per area.</div>',
        unsafe_allow_html=True
    )

    st.markdown('<div class="section-header">Multi Asset Class — Seleziona aree (multi-selezione)</div>', unsafe_allow_html=True)
    render_cards(clean_items(df['L1']), df, 'L1', 'sel_l1_set', multi=True, show_qf=False)

    if st.session_state.sel_l1_set:
        pills_html = " ".join([f'<span class="sel-pill">✓ {x}</span>' for x in sorted(st.session_state.sel_l1_set)])
        st.markdown(f'<div style="margin:8px 0 4px;">{pills_html}</div>', unsafe_allow_html=True)

        col_clear, _ = st.columns([1.8, 8])
        with col_clear:
            if st.button("✕ Deseleziona tutto", key="clear_multi"):
                st.session_state.sel_l1_set = set()
                st.session_state.shock_filter = 'all'
                st.rerun()

        selected_list = list(st.session_state.sel_l1_set)
        if len(selected_list) == 1:
            df_show  = df[df['L1'].isin(selected_list)].copy()
            label    = f"Scenari in: {selected_list[0]}"
            is_multi = False
        else:
            sets_per_l1 = [set(df[df['L1'] == l1]['Scenario'].unique()) for l1 in selected_list]
            common       = sets_per_l1[0].intersection(*sets_per_l1[1:])
            df_show      = df[df['L1'].isin(selected_list) & df['Scenario'].isin(common)].copy()
            label        = f"Scenari comuni a: {' · '.join(sorted(selected_list))}"
            is_multi     = True

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
