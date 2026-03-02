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

.main-title {
    font-size: 2.1rem; font-weight: 700; color: #0e1117;
    margin-bottom: 0.2rem; line-height: 1.2;
}
.subtitle { font-size: 0.82rem; color: #6b6b6b; margin-bottom: 1.8rem; font-style: italic; }
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
    padding: 0.75rem 1.2rem;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
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

/* ── Default buttons ── */
.stButton > button {
    background: #ffffff; color: #31333f;
    border: 1px solid #d9d9d9; border-radius: 6px;
    font-size: 0.875rem; font-weight: 400; transition: all 0.1s ease;
}
.stButton > button:hover {
    border-color: #ff4b4b; color: #ff4b4b; background: #fff5f5;
}
</style>
""", unsafe_allow_html=True)

# ─── HELPERS ───────────────────────────────────────────────────────────────────

def parse_shock(val):
    """Returns (numeric_value, unit_string)."""
    if pd.isna(val):
        return np.nan, 'none'
    s  = str(val).strip()
    sl = s.lower()
    m  = re.search(r'[-+]?\d+\.?\d*', s)
    num = float(m.group()) if m else np.nan
    if 'bps'   in sl: unit = 'bps'
    elif 'rel %' in sl: unit = 'rel%'
    elif 'pct'  in sl: unit = 'pct'
    elif 'days' in sl: unit = 'days'
    elif m:            unit = 'number'
    else:              unit = 'other'
    return num, unit

def group_direction_score(sub):
    """
    Per a subset of rows, compute per-unit arithmetic mean.
    If all unit-means agree in sign → return a representative signed float.
    If units disagree in sign → return NaN (mixed).
    Ignores 'other'/'none' units.
    """
    unit_means = {}
    for u, g in sub.groupby('_unit'):
        if u in ('other', 'none'):
            continue
        vals = g['_num'].dropna()
        if len(vals) > 0:
            unit_means[u] = vals.mean()
    if not unit_means:
        return np.nan
    signs = set(1 if v > 0 else (-1 if v < 0 else 0) for v in unit_means.values())
    if len(signs) == 1:
        # All units agree → return mean of the unit means (preserves sign)
        return float(np.mean(list(unit_means.values())))
    return np.nan   # mixed

def scenario_direction(score):
    """Returns 'pos', 'neg', or 'mixed' from a score."""
    if pd.isna(score): return 'mixed'
    if score > 0: return 'pos'
    if score < 0: return 'neg'
    return 'mixed'

def clean_items(series):
    return sorted([str(i) for i in series.dropna().unique()
                   if str(i).strip() not in ('', 'nan')])

# ─── DATA ──────────────────────────────────────────────────────────────────────
FILE_PATH = "ListaxMapping.xlsx"

@st.cache_data
def load_data():
    df = pd.read_excel(FILE_PATH, sheet_name="Pivot", header=0)
    df.columns = ['Scenario', 'L1', 'L2', 'L3', 'ShockValue', 'ColF'] + list(df.columns[6:])
    df = df[['Scenario', 'L1', 'L2', 'L3', 'ShockValue', 'ColF']].copy()
    for col in ['Scenario', 'L1', 'L2', 'L3']:
        df[col] = df[col].ffill()
    df['ColF'] = df['ColF'].fillna('').astype(str).str.strip()
    df = df.dropna(subset=['L1'])
    df = df[df['L1'].astype(str).str.strip().astype(bool)]
    df = df[df['L1'].astype(str).str.lower() != 'nan']
    parsed = df['ShockValue'].apply(lambda v: pd.Series(parse_shock(v), index=['_num', '_unit']))
    df['_num']  = parsed['_num']
    df['_unit'] = parsed['_unit']

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
    st.error(f"File `{FILE_PATH}` not found in repository.")
    st.stop()

desc_map = dict(zip(dm['Stress_Scenarios'], dm['Long_des']))

# ─── SESSION STATE ─────────────────────────────────────────────────────────────
defaults = {
    'sel_l1_set':    set(),
    'sel_l1_single': None,
    'sel_l2':        None,
    'sel_l3':        None,
    'mode':          'drill',
    'shock_filter':  'all',
    # quick_view = {'col': str, 'item': str, 'dir': 'pos'|'neg'} | None
    'quick_view':    None,
    # multi_dir_filter: {'dir': 'pos'|'neg', 'areas': set()} | None
    'multi_dir_filter': None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─── HEADER ────────────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">📊 Stress Test Mapping</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Asset class drill-down · Shock direction analysis</div>',
            unsafe_allow_html=True)

col_m1, col_m2, col_m3 = st.columns([2, 2, 8])
with col_m1:
    if st.button("🔍 Single-Asset", use_container_width=True):
        st.session_state.update({'mode': 'drill', 'sel_l1_set': set(), 'sel_l1_single': None,
                                  'sel_l2': None, 'sel_l3': None, 'shock_filter': 'all',
                                  'quick_view': None, 'multi_dir_filter': None})
        st.rerun()
with col_m2:
    if st.button("🔀 Multi-Asset", use_container_width=True):
        st.session_state.update({'mode': 'multi', 'sel_l2': None, 'sel_l3': None,
                                  'shock_filter': 'all', 'quick_view': None, 'multi_dir_filter': None})
        st.rerun()
with col_m3:
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
        width:310px; z-index:9999;
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
                <div class="mp-row">For each scenario, all shocks belonging to the selected <b>asset class</b> (or sub-level) are collected.</div>
                <div class="mp-row">Since shocks use different units (pct, bps, rel%, days), the mean is computed <b>separately per unit type</b> to avoid mixing incompatible scales — then the signs of those means are compared:</div>
                <div class="mp-row"><span class="mp-green">▲ Positive</span> — all unit-type means are positive, so the net effect on the asset class is positive.</div>
                <div class="mp-row"><span class="mp-red">▼ Negative</span> — all unit-type means are negative.</div>
                <div class="mp-row"><span class="mp-amber">~ Mixed</span> — unit-type means have conflicting signs (e.g. pct shocks average to +5% but bps shocks average to −80bps), so no single direction can be assigned. In Multi-Asset mode, also includes scenarios positive in one area and negative in another.</div>
                <div class="mp-row" style="margin-top:8px;color:#9ca3af;font-size:0.65rem;">
                Direction re-evaluates as you drill down: at L2 it uses only that L2's shocks, at L3 only that L3's shocks.</div>
            </div>
        </div>
        <span class="method-label">Direction methodology</span>
    </div>
    """, unsafe_allow_html=True)
st.markdown("---")

# ─── JS: color Positive/Negative buttons ──────────────────────────────────────
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

# ─── DIRECTION COUNTS PER GROUP ───────────────────────────────────────────────
def count_directions(df_sub, group_cols):
    """
    For each unique scenario within df_sub, compute direction based on
    per-unit mean over the given group_cols filter.
    Returns (n_pos, n_neg, n_mixed).
    """
    n_pos, n_neg, n_mixed = 0, 0, 0
    for _, sc_df in df_sub.groupby('Scenario'):
        score = group_direction_score(sc_df)
        d = scenario_direction(score)
        if d == 'pos':   n_pos   += 1
        elif d == 'neg': n_neg   += 1
        else:            n_mixed += 1
    return n_pos, n_neg, n_mixed

def get_scenario_directions(df_sub):
    """Returns dict {scenario: 'pos'|'neg'|'mixed'} for df_sub."""
    result = {}
    for sc, sc_df in df_sub.groupby('Scenario'):
        score = group_direction_score(sc_df)
        result[sc] = scenario_direction(score)
    return result

# ─── EXPORT ───────────────────────────────────────────────────────────────────
def build_export_bytes(df_sub, label="export"):
    """
    Full export: all rows from df_sub (no shock filtering).
    Columns: Scenario | Description | Detail (col F) | L1 | L2 | L3 | ShockValue | Unit
    """
    rows = []
    for _, r in df_sub.sort_values(['Scenario', 'L1', 'L2', 'L3']).iterrows():
        scenario = str(r['Scenario'])
        rows.append({
            'Scenario':    scenario,
            'Description': desc_map.get(scenario.strip(), ''),
            'Detail':      str(r.get('ColF', '')),
            'L1':          str(r.get('L1', '')),
            'L2':          str(r.get('L2', '')),
            'L3':          str(r.get('L3', '')),
            'ShockValue':  str(r['ShockValue']) if not pd.isna(r['ShockValue']) else '',
        })
    export_df = pd.DataFrame(rows)
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine='openpyxl') as writer:
        export_df.to_excel(writer, index=False, sheet_name='Scenarios')
        ws = writer.sheets['Scenarios']
        for col_cells in ws.columns:
            max_len = max((len(str(c.value or '')) for c in col_cells), default=10)
            ws.column_dimensions[col_cells[0].column_letter].width = min(max_len + 4, 60)
    buf.seek(0)
    return buf.getvalue()

def render_export_row(df_full, df_display, fname_base):
    """Renders count info + export button. df_full = all rows (for export), df_display = filtered for view."""
    n = df_display['Scenario'].nunique()
    col_info, col_dl, _ = st.columns([2, 1.8, 6])
    with col_info:
        st.markdown(
            f'<div style="font-size:0.72rem;color:#6b6b6b;padding-top:8px;">'
            f'{"1 scenario found" if n == 1 else f"{n} scenarios found"}</div>',
            unsafe_allow_html=True
        )
    with col_dl:
        st.download_button(
            label="⬇ Export Excel",
            data=build_export_bytes(df_full),
            file_name=f"{fname_base}.xlsx".replace(' ', '_'),
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key=f"dl_{fname_base}_{id(df_display)}",
            use_container_width=True,
        )

# ─── SCENARIO TABLE HTML ──────────────────────────────────────────────────────
def build_grouped_table_html(df_display, th_class=""):
    """
    One row per unique Scenario. df_display should already be filtered to the
    shocks you want to SHOW (pos or neg or all). Export uses the full dataset.
    """
    rows_html = ""
    th_attr   = f' class="{th_class}"' if th_class else ''

    for scenario in sorted(df_display['Scenario'].unique()):
        sc_rows  = df_display[df_display['Scenario'] == scenario].sort_values('L3')
        long_des = desc_map.get(str(scenario).strip(), '')
        des_html = f'<div class="long-des">{long_des}</div>' if long_des else ''

        factors_html = '<div class="factor-list">'
        for _, r in sc_rows.iterrows():
            num      = r['_num']
            shock_raw = str(r['ShockValue']) if not pd.isna(r['ShockValue']) else "—"
            l3_name  = str(r['L3']) if str(r.get('L3', '')).strip() not in ('', 'nan') else '—'
            try:   is_num = not np.isnan(float(num))
            except: is_num = False
            if is_num and num > 0:
                val_cls, arrow = "factor-val-pos", "▲ "
            elif is_num and num < 0:
                val_cls, arrow = "factor-val-neg", "▼ "
            else:
                val_cls, arrow = "factor-val-zero", ""
            factors_html += (
                f'<div class="factor-row">'
                f'<span class="factor-name">{l3_name}</span>'
                f'<span class="{val_cls}">{arrow}{shock_raw}</span>'
                f'</div>'
            )
        factors_html += '</div>'
        rows_html += f"""
        <tr>
            <td style="width:35%"><strong>{scenario}</strong>{des_html}</td>
            <td>{factors_html}</td>
        </tr>"""

    return f"""
    <table class="scenario-table">
        <thead><tr>
            <th{th_attr}>Scenario</th>
            <th{th_attr}>Factors (L3) · Shock Value</th>
        </tr></thead>
        <tbody>{rows_html}</tbody>
    </table>"""

# ─── QUICK-VIEW ───────────────────────────────────────────────────────────────
def render_quick_view(df_context, col_name):
    """
    Shown when quick_view state matches col_name.
    Filters scenarios by per-unit direction, displays only matching-sign shocks,
    but exports ALL shocks for those scenarios.
    """
    qv = st.session_state.quick_view
    if qv is None or qv['col'] != col_name:
        return
    item, direction = qv['item'], qv['dir']

    df_item = df_context[df_context[col_name] == item].copy()

    # Compute per-scenario direction
    sc_dirs = get_scenario_directions(df_item)
    matching_scenarios = [sc for sc, d in sc_dirs.items() if d == direction]

    if direction == 'pos':
        th_class = "pos-th"
        label    = f"▲ Positive scenarios — {item}"
        # Show only positive shocks
        df_display = df_item[df_item['Scenario'].isin(matching_scenarios) & (df_item['_num'] > 0)]
    else:
        th_class = "neg-th"
        label    = f"▼ Negative scenarios — {item}"
        # Show only negative shocks
        df_display = df_item[df_item['Scenario'].isin(matching_scenarios) & (df_item['_num'] < 0)]

    # Full data for those scenarios (for export)
    df_full_export = df_item[df_item['Scenario'].isin(matching_scenarios)]

    st.markdown(f'<div class="section-header">{label}</div>', unsafe_allow_html=True)
    col_close, _ = st.columns([1.2, 8])
    with col_close:
        if st.button("✕ Close", key=f"close_qv_{col_name}_{item}_{direction}"):
            st.session_state.quick_view = None
            st.rerun()

    if not matching_scenarios:
        st.info("No scenarios found for this selection.")
        return

    render_export_row(df_full_export, df_display, f"scenarios_{item}_{direction}")
    st.markdown(build_grouped_table_html(df_display, th_class), unsafe_allow_html=True)

# ─── CARD RENDERER ────────────────────────────────────────────────────────────
def render_cards(items, df_filtered, col_name, on_select_key, multi=False, show_mini=False):
    if not items: return
    ncols = min(len(items), 4)
    cols  = st.columns(ncols)

    for i, item in enumerate(items):
        sub  = df_filtered[df_filtered[col_name] == item]
        # Count unique scenarios by per-unit direction
        n_pos, n_neg, _ = count_directions(sub, col_name)
        is_sel   = (item in st.session_state.sel_l1_set) if multi else (st.session_state.get(on_select_key) == item)
        btn_label = f"{'✓ ' if is_sel else ''}{item}"

        with cols[i % ncols]:
            clicked = st.button(btn_label, key=f"btn_{on_select_key}_{item}", use_container_width=True)

            if show_mini:
                mc1, mc2 = st.columns(2)
                with mc1:
                    if st.button(f"▲ {n_pos}  Positive",
                                 key=f"mini_pos_{on_select_key}_{item}",
                                 use_container_width=True):
                        if multi:
                            # Add area to selection and set direction filter
                            st.session_state.sel_l1_set.add(item)
                            st.session_state.shock_filter = 'pos'
                            st.session_state.quick_view   = None
                        else:
                            st.session_state.quick_view = {'col': col_name, 'item': item, 'dir': 'pos'}
                        st.rerun()
                with mc2:
                    if st.button(f"▼ {n_neg}  Negative",
                                 key=f"mini_neg_{on_select_key}_{item}",
                                 use_container_width=True):
                        if multi:
                            # Add area to selection and set direction filter
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

# ─── STAT BOXES (L3 drill) ────────────────────────────────────────────────────
def render_stat_boxes(df_sub):
    """Show total scenarios + filter buttons for L3 drill-down view."""
    n_sc                = df_sub['Scenario'].nunique()
    n_pos, n_neg, _     = count_directions(df_sub, 'L3')
    cur_filter          = st.session_state.shock_filter

    c0, c1, c2, c3 = st.columns([1.4, 1.4, 1.4, 7])
    with c0:
        st.markdown(f"""<div class="stat-box">
            <div class="sv">{n_sc}</div>
            <div class="sk">Total Scenarios</div>
        </div>""", unsafe_allow_html=True)
    with c1:
        active_pos = cur_filter == 'pos'
        if st.button(f"▲ {n_pos}  positive", key="filter_pos", use_container_width=True):
            st.session_state.shock_filter = 'all' if active_pos else 'pos'
            st.rerun()
        if active_pos:
            st.markdown('<div style="height:3px;background:#16a34a;border-radius:2px;margin-top:-6px;"></div>',
                        unsafe_allow_html=True)
    with c2:
        active_neg = cur_filter == 'neg'
        if st.button(f"▼ {n_neg}  negative", key="filter_neg", use_container_width=True):
            st.session_state.shock_filter = 'all' if active_neg else 'neg'
            st.rerun()
        if active_neg:
            st.markdown('<div style="height:3px;background:#dc2626;border-radius:2px;margin-top:-6px;"></div>',
                        unsafe_allow_html=True)

# ─── SCENARIO TABLE (L3 drill) ────────────────────────────────────────────────
def render_scenario_table(df_sub):
    """
    For L3 drill-down: filter scenarios by per-unit direction,
    display only matching-sign shocks, export full.
    """
    render_stat_boxes(df_sub)
    f = st.session_state.shock_filter

    sc_dirs = get_scenario_directions(df_sub)

    if f == 'pos':
        matching = [sc for sc, d in sc_dirs.items() if d == 'pos']
        th_class, direction = "pos-th", "pos"
    elif f == 'neg':
        matching = [sc for sc, d in sc_dirs.items() if d == 'neg']
        th_class, direction = "neg-th", "neg"
    else:
        matching  = list(sc_dirs.keys())
        th_class, direction = "", "all"

    if not matching:
        st.info("No scenarios found for this filter.")
        return

    df_matching = df_sub[df_sub['Scenario'].isin(matching)]

    # Display: show only shocks with the correct sign (or all if no filter)
    if f == 'pos':
        df_display = df_matching[df_matching['_num'] > 0]
    elif f == 'neg':
        df_display = df_matching[df_matching['_num'] < 0]
    else:
        df_display = df_matching

    fname = f"scenarios_{st.session_state.get('sel_l3','export')}_{direction}"
    render_export_row(df_matching, df_display, fname)   # export full, display filtered count
    st.markdown(build_grouped_table_html(df_display, th_class), unsafe_allow_html=True)


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

    # L1
    st.markdown('<div class="section-header">Level 1 Mapping — Asset Class</div>',
                unsafe_allow_html=True)
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
else:
    qv  = st.session_state.quick_view
    mdf = st.session_state.multi_dir_filter   # {'dir': 'pos'|'neg', 'areas': set()}

    st.markdown(
        '<div class="hint-box">'
        '💡 Select one or more Level-1 areas. With a single area you see all its scenarios. '
        'With multiple areas you see scenarios <strong>common to all</strong>.<br>'
        '🎯 Use the <strong>▲ Positive / ▼ Negative</strong> buttons on each card to see '
        'cross-area direction filtering: select the same direction on multiple cards to intersect.'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown('<div class="section-header">Select Asset Class (multi-select)</div>',
                unsafe_allow_html=True)
    render_cards(clean_items(df['L1']), df, 'L1', 'sel_l1_set', multi=True, show_mini=True)

    # ── Quick-view (single-area direction view from mini buttons) ──────────────
    if qv and qv['col'] == 'L1':
        render_quick_view(df, 'L1')

    # ── Normal multi-select view ───────────────────────────────────────────────
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

        # Build df_show: rows for selected L1s
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
            # ── Direction filter for multi-area ────────────────────────────────
            # Per each selected L1, compute per-scenario direction using ONLY
            # that L1's rows. A scenario qualifies for 'pos' if it is positive
            # in EVERY selected L1 (intersection).
            st.markdown(f'<div class="section-header">{label}</div>', unsafe_allow_html=True)

            # Direction filter buttons
            all_scenarios = sorted(df_show['Scenario'].unique())

            # Compute direction per (scenario, L1)
            dir_matrix = {}  # {scenario: {L1: direction}}
            for l1 in selected_list:
                sub_l1 = df_show[df_show['L1'] == l1]
                for sc, sc_df in sub_l1.groupby('Scenario'):
                    score = group_direction_score(sc_df)
                    dir_matrix.setdefault(sc, {})[l1] = scenario_direction(score)

            def filter_by_direction(direction):
                """Scenarios where direction holds in ALL selected L1s."""
                return [sc for sc in all_scenarios
                        if all(dir_matrix.get(sc, {}).get(l1) == direction
                               for l1 in selected_list)]

            pos_scenarios   = filter_by_direction('pos')
            neg_scenarios   = filter_by_direction('neg')
            mixed_scenarios = [sc for sc in all_scenarios
                               if sc not in pos_scenarios and sc not in neg_scenarios]

            cur_mf = st.session_state.shock_filter

            # ── Tooltip HTML ──
            tooltip_css = """
            <style>
            .tip-wrap { display:inline-flex; align-items:center; gap:6px; position:relative; }
            .tip-icon {
                display:inline-flex; align-items:center; justify-content:center;
                width:16px; height:16px; border-radius:50%;
                background:#e5e7eb; color:#6b7280;
                font-size:0.65rem; font-weight:700; cursor:default;
                flex-shrink:0;
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
                'pos': "Scenarios with a <b>positive net shock</b> across all selected asset classes (avg per unit type is positive in each area).",
                'neg': "Scenarios with a <b>negative net shock</b> across all selected asset classes (avg per unit type is negative in each area).",
                'mix': "Scenarios whose shock direction <b>differs across the selected areas</b> — e.g. positive in Equity but negative in FX. They appear here because they are common to all areas, but do not have a single direction.",
            }

            def tip_icon(key):
                return (f'<span class="tip-icon">?'
                        f'<span class="tip-text">{tips[key]}</span>'
                        f'</span>')

            st.markdown(tooltip_css, unsafe_allow_html=True)

            cfa, cfb, cfc, cfd, _ = st.columns([1.1, 1.3, 1.3, 1.3, 3])
            with cfa:
                st.markdown(f"""<div class="stat-box">
                    <div class="sv">{len(all_scenarios)}</div>
                    <div class="sk">Total common</div>
                </div>""", unsafe_allow_html=True)
            with cfb:
                active_pos = cur_mf == 'pos'
                st.markdown(
                    f'<div style="font-size:0.68rem;color:#16a34a;font-weight:600;margin-bottom:2px;">'
                    f'▲ Positive {tip_icon("pos")}</div>',
                    unsafe_allow_html=True
                )
                if st.button(f"▲ {len(pos_scenarios)}  positive",
                             key="mf_pos", use_container_width=True):
                    st.session_state.shock_filter = 'all' if active_pos else 'pos'
                    st.rerun()
                if active_pos:
                    st.markdown('<div style="height:3px;background:#16a34a;border-radius:2px;margin-top:-6px;"></div>',
                                unsafe_allow_html=True)
            with cfc:
                active_neg = cur_mf == 'neg'
                st.markdown(
                    f'<div style="font-size:0.68rem;color:#dc2626;font-weight:600;margin-bottom:2px;">'
                    f'▼ Negative {tip_icon("neg")}</div>',
                    unsafe_allow_html=True
                )
                if st.button(f"▼ {len(neg_scenarios)}  negative",
                             key="mf_neg", use_container_width=True):
                    st.session_state.shock_filter = 'all' if active_neg else 'neg'
                    st.rerun()
                if active_neg:
                    st.markdown('<div style="height:3px;background:#dc2626;border-radius:2px;margin-top:-6px;"></div>',
                                unsafe_allow_html=True)
            with cfd:
                active_mix = cur_mf == 'mix'
                st.markdown(
                    f'<div style="font-size:0.68rem;color:#b45309;font-weight:600;margin-bottom:2px;">'
                    f'~ Mixed {tip_icon("mix")}</div>',
                    unsafe_allow_html=True
                )
                if st.button(f"~ {len(mixed_scenarios)}  mixed",
                             key="mf_mix", use_container_width=True):
                    st.session_state.shock_filter = 'all' if active_mix else 'mix'
                    st.rerun()
                if active_mix:
                    st.markdown('<div style="height:3px;background:#b45309;border-radius:2px;margin-top:-6px;"></div>',
                                unsafe_allow_html=True)

            # Apply filter
            if cur_mf == 'pos':
                active_scenarios = pos_scenarios
                th_class, sign_filter = "pos-th", "pos"
            elif cur_mf == 'neg':
                active_scenarios = neg_scenarios
                th_class, sign_filter = "neg-th", "neg"
            elif cur_mf == 'mix':
                active_scenarios = mixed_scenarios
                th_class, sign_filter = "mix-th", "mix"
            else:
                active_scenarios = all_scenarios
                th_class, sign_filter = "", "all"

            if not active_scenarios:
                st.info("No scenarios match this direction filter across all selected areas.")
            else:
                df_active = df_show[df_show['Scenario'].isin(active_scenarios)]

                # Display: only matching-sign shocks (if filtered); export: full
                if sign_filter == 'pos':
                    df_display = df_active[df_active['_num'] > 0]
                elif sign_filter == 'neg':
                    df_display = df_active[df_active['_num'] < 0]
                else:
                    df_display = df_active  # all or mix: show all shocks

                fname = f"multi_{'_'.join(selected_list)}_{sign_filter}"
                render_export_row(df_active, df_display, fname)

                # Build multi-area table: path = L1 › L2 › L3
                rows_html = ""
                for scenario in sorted(df_display['Scenario'].unique()):
                    sc_rows  = df_display[df_display['Scenario'] == scenario]
                    long_des = desc_map.get(str(scenario).strip(), '')
                    des_html = f'<div class="long-des">{long_des}</div>' if long_des else ''
                    factors_html = '<div class="factor-list">'
                    for _, r in sc_rows.sort_values(['L1','L2','L3']).iterrows():
                        num       = r['_num']
                        shock_raw = str(r['ShockValue']) if not pd.isna(r['ShockValue']) else "—"
                        path = " › ".join([str(r[c]) for c in ['L1','L2','L3']
                                           if str(r.get(c, '')).strip() not in ('', 'nan')])
                        try:   is_num = not np.isnan(float(num))
                        except: is_num = False
                        if is_num and num > 0:
                            val_cls, arrow = "factor-val-pos", "▲ "
                        elif is_num and num < 0:
                            val_cls, arrow = "factor-val-neg", "▼ "
                        else:
                            val_cls, arrow = "factor-val-zero", ""
                        factors_html += (
                            f'<div class="factor-row">'
                            f'<span class="factor-name">{path}</span>'
                            f'<span class="{val_cls}">{arrow}{shock_raw}</span>'
                            f'</div>'
                        )
                    factors_html += '</div>'
                    rows_html += f"""
                    <tr>
                        <td style="width:35%"><strong>{scenario}</strong>{des_html}</td>
                        <td>{factors_html}</td>
                    </tr>"""

                th_attr = f' class="{th_class}"' if th_class else ''
                st.markdown(f"""
                <table class="scenario-table">
                    <thead><tr>
                        <th{th_attr}>Scenario</th>
                        <th{th_attr}>Shocks by selected area</th>
                    </tr></thead>
                    <tbody>{rows_html}</tbody>
                </table>""", unsafe_allow_html=True)

    else:
        st.markdown(
            '<div style="font-size:0.78rem;color:#6b7280;margin-top:1rem;">'
            '← Click on one or more asset classes to view scenarios.</div>',
            unsafe_allow_html=True
        )

# ─── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(
    '<div style="font-size:0.6rem;color:#9ca3af;text-align:center;">'
    'Stress Test Dashboard · ListaxMapping / Pivot · MAIN</div>',
    unsafe_allow_html=True
)
