import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import re

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

/* ── Card subtitle: stress label ── */
.card-sub {
    font-size: 0.72rem; color: #6b6b6b;
    margin-top: -10px; margin-bottom: 4px; min-height: 16px;
}
.stress-pos { color: #16a34a; font-weight: 600; font-size: 0.72rem; }
.stress-neg { color: #dc2626; font-weight: 600; font-size: 0.72rem; }
.stress-mix { color: #b45309; font-weight: 600; font-size: 0.72rem; }

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
    padding: 0.75rem 1.2rem; min-width: 130px;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}
.stat-box .sv { font-size: 1.6rem; font-weight: 700; color: #0e1117; line-height: 1; }
.stat-box .sk { font-size: 0.65rem; color: #6b6b6b; text-transform: uppercase;
    letter-spacing: 0.06em; margin-top: 4px; }

/* ── Scenario table: grouped layout ── */
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
.scenario-table td {
    padding: 10px 16px; border-bottom: 1px solid #f0f0f0;
    color: #31333f; vertical-align: top;
}
.scenario-table tr:last-child td { border-bottom: none; }
.scenario-table tr:hover td { background: #fafafa; }

/* ── Factor rows inside scenario cell ── */
.factor-list { display: flex; flex-direction: column; gap: 4px; margin-top: 6px; }
.factor-row {
    display: flex; justify-content: space-between; align-items: baseline;
    background: #f9fafb; border-radius: 4px; padding: 3px 8px;
    font-size: 0.78rem;
}
.factor-name { color: #374151; font-size: 0.78rem; }
.factor-val-pos { color: #16a34a; font-weight: 600; white-space: nowrap; margin-left: 12px; }
.factor-val-neg { color: #dc2626; font-weight: 600; white-space: nowrap; margin-left: 12px; }
.factor-val-zero { color: #6b6b6b; white-space: nowrap; margin-left: 12px; }

.shock-pos { color: #16a34a; font-weight: 600; }
.shock-neg { color: #dc2626; font-weight: 600; }
.shock-zero { color: #6b6b6b; }
.long-des { font-size: 0.72rem; color: #6b6b6b; margin-top: 3px; line-height: 1.45; }

/* ── Multi-mode shock list ── */
.shock-list { display: flex; flex-direction: column; gap: 3px; }
.shock-row-item { display: flex; gap: 6px; align-items: baseline; }
.shock-path { font-size: 0.63rem; color: #aaaaaa; }

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

def parse_shock_value(val):
    if pd.isna(val): return np.nan
    s = str(val).replace(',', '.').strip()
    m = re.search(r'[-+]?\d+\.?\d*', s)
    return float(m.group()) if m else np.nan

def mean_shock_for_group(df_sub):
    vals = df_sub['_shock_num'].dropna()
    return vals.mean() if len(vals) else np.nan

def stress_label_html(mean_val):
    """Returns HTML span with stress direction label."""
    if pd.isna(mean_val):
        return '<span class="stress-mix">~ Stress misto</span>'
    if mean_val > 0:
        return '<span class="stress-pos">▲ Stress positivo</span>'
    if mean_val < 0:
        return '<span class="stress-neg">▼ Stress negativo</span>'
    return '<span class="stress-mix">~ Stress neutro</span>'

def clean_items(series):
    return sorted([str(i) for i in series.dropna().unique()
                   if str(i).strip() not in ('', 'nan')])

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

    # Carica sheet 'Lista Scenari' col F (index 5) = info aggiuntiva per export
    try:
        ls = pd.read_excel(FILE_PATH, sheet_name="Lista Scenari", header=0)
        # Col A (index 0) = Scenario name, Col F (index 5) = extra info
        ls_cols = ls.columns.tolist()
        ls_exp  = ls.iloc[:, [0, 5]].copy()
        ls_exp.columns = ['Scenario', 'ExtraInfo']
        ls_exp = ls_exp.dropna(subset=['Scenario'])
        ls_exp['Scenario']   = ls_exp['Scenario'].astype(str).str.strip()
        ls_exp['ExtraInfo']  = ls_exp['ExtraInfo'].fillna('').astype(str).str.strip()
    except Exception:
        ls_exp = pd.DataFrame(columns=['Scenario', 'ExtraInfo'])

    return df, dm, ls_exp

try:
    df, dm, ls_exp = load_data()
except FileNotFoundError:
    st.error(f"File `{FILE_PATH}` non trovato nella repository.")
    st.stop()

desc_map  = dict(zip(dm['Stress_Scenarios'], dm['Long_des']))
extra_map = dict(zip(ls_exp['Scenario'], ls_exp['ExtraInfo']))

# ─── SESSION STATE ─────────────────────────────────────────────────────────────
defaults = {
    'sel_l1_set':    set(),
    'sel_l1_single': None,
    'sel_l2':        None,
    'sel_l3':        None,
    'mode':          'drill',
    'shock_filter':  'all',
    # quick_view = {'col': 'L1'|'L2', 'item': str, 'dir': 'pos'|'neg'} or None
    'quick_view':    None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─── HEADER ────────────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">📊 Stress Test Mapping</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Asset class drill-down · Shock direction analysis</div>', unsafe_allow_html=True)

col_m1, col_m2, col_m3 = st.columns([2, 2, 8])
with col_m1:
    if st.button("🔍 Drill-down", use_container_width=True):
        st.session_state.update({'mode': 'drill', 'sel_l1_set': set(), 'sel_l1_single': None,
                                  'sel_l2': None, 'sel_l3': None, 'shock_filter': 'all', 'quick_view': None})
        st.rerun()
with col_m2:
    if st.button("🔀 Multi-area", use_container_width=True):
        st.session_state.update({'mode': 'multi', 'sel_l2': None, 'sel_l3': None,
                                  'shock_filter': 'all', 'quick_view': None})
        st.rerun()
st.markdown("---")

# ─── JS: colora bottoni Positivi/Negativi via MutationObserver ─────────────────
components.html("""
<script>
(function() {
    function styleMiniBtns(doc) {
        doc.querySelectorAll('button').forEach(function(btn) {
            var txt = (btn.innerText || btn.textContent || '').trim();
            if (txt.includes('Positivi')) {
                btn.style.setProperty('background-color', '#16a34a', 'important');
                btn.style.setProperty('color', '#ffffff', 'important');
                btn.style.setProperty('border', '1.5px solid #15803d', 'important');
                btn.style.setProperty('font-size', '0.72rem', 'important');
                btn.style.setProperty('font-weight', '600', 'important');
                btn.style.setProperty('min-height', '28px', 'important');
                btn.style.setProperty('height', '28px', 'important');
                btn.style.setProperty('padding', '0 8px', 'important');
                btn.style.setProperty('border-radius', '5px', 'important');
            } else if (txt.includes('Negativi')) {
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

import io

# ─── EXPORT ────────────────────────────────────────────────────────────────────
def build_export_bytes(df_sub, label="export"):
    """
    Builds an Excel file (bytes) from df_sub, one row per (Scenario, L3 factor).
    Columns: Scenario | Descrizione | ExtraInfo (col F Lista Scenari) | L1 | L2 | L3 | ShockValue
    """
    rows = []
    for _, r in df_sub.sort_values(['Scenario', 'L1', 'L2', 'L3']).iterrows():
        scenario  = str(r['Scenario'])
        long_des  = desc_map.get(scenario.strip(), '')
        extra     = extra_map.get(scenario.strip(), '')
        rows.append({
            'Scenario':     scenario,
            'Descrizione':  long_des,
            'Info (col F)': extra,
            'L1':           str(r.get('L1', '')),
            'L2':           str(r.get('L2', '')),
            'L3':           str(r.get('L3', '')),
            'ShockValue':   str(r['ShockValue']) if not pd.isna(r['ShockValue']) else '',
        })
    export_df = pd.DataFrame(rows)

    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine='openpyxl') as writer:
        export_df.to_excel(writer, index=False, sheet_name='Scenari')
        ws = writer.sheets['Scenari']
        # Auto-width
        for col_cells in ws.columns:
            max_len = max((len(str(c.value or '')) for c in col_cells), default=10)
            ws.column_dimensions[col_cells[0].column_letter].width = min(max_len + 4, 50)
    buf.seek(0)
    return buf.getvalue()

# ─── GROUPED SCENARIO TABLE ────────────────────────────────────────────────────
def build_grouped_table_html(df_sub, th_class=""):
    """
    One row per unique Scenario.
    Col 1: scenario name + description.
    Col 2: L3 factors grouped with shock values.
    """
    rows_html = ""
    th_attr = f' class="{th_class}"' if th_class else ''

    for scenario in sorted(df_sub['Scenario'].unique()):
        sc_rows  = df_sub[df_sub['Scenario'] == scenario].sort_values('L3')
        long_des = desc_map.get(str(scenario).strip(), '')
        des_html = f'<div class="long-des">{long_des}</div>' if long_des else ''

        factors_html = '<div class="factor-list">'
        for _, r in sc_rows.iterrows():
            shock_num = r['_shock_num']
            shock_raw = str(r['ShockValue']) if not pd.isna(r['ShockValue']) else "—"
            l3_name   = str(r['L3']) if str(r.get('L3', '')).strip() not in ('', 'nan') else '—'
            try:   is_num = not np.isnan(float(shock_num))
            except: is_num = False
            if is_num and shock_num > 0:
                val_cls = "factor-val-pos"; arrow = "▲ "
            elif is_num and shock_num < 0:
                val_cls = "factor-val-neg"; arrow = "▼ "
            else:
                val_cls = "factor-val-zero"; arrow = ""
            factors_html += (
                f'<div class="factor-row">'
                f'<span class="factor-name">{l3_name}</span>'
                f'<span class="{val_cls}">{arrow}{shock_raw}</span>'
                f'</div>'
            )
        factors_html += '</div>'

        rows_html += f"""
        <tr>
            <td><strong>{scenario}</strong>{des_html}</td>
            <td>{factors_html}</td>
        </tr>"""

    return f"""
    <table class="scenario-table">
        <thead><tr>
            <th{th_attr}>Scenario</th>
            <th{th_attr}>Fattori (L3) · Shock Value</th>
        </tr></thead>
        <tbody>{rows_html}</tbody>
    </table>"""

# ─── QUICK-VIEW ────────────────────────────────────────────────────────────────
def render_quick_view(df_context, col_name):
    """Render filtered scenario table if quick_view matches this col_name."""
    qv = st.session_state.quick_view
    if qv is None or qv['col'] != col_name:
        return
    item      = qv['item']
    direction = qv['dir']

    df_item = df_context[df_context[col_name] == item]
    if direction == 'pos':
        df_show  = df_item[df_item['_shock_num'] > 0]
        th_class = "pos-th"
        label    = f"▲ Scenari positivi — {item}"
    else:
        df_show  = df_item[df_item['_shock_num'] < 0]
        th_class = "neg-th"
        label    = f"▼ Scenari negativi — {item}"

    st.markdown(f'<div class="section-header">{label}</div>', unsafe_allow_html=True)
    col_close, _ = st.columns([1.2, 8])
    with col_close:
        if st.button("✕ Chiudi", key=f"close_qv_{col_name}_{item}_{direction}"):
            st.session_state.quick_view = None
            st.rerun()

    if df_show.empty:
        st.info("Nessuno scenario trovato per questa selezione.")
    else:
        n = df_show['Scenario'].nunique()
        col_info, col_dl, _ = st.columns([2, 1.5, 6])
        with col_info:
            st.markdown(
                f'<div style="font-size:0.72rem;color:#6b6b6b;padding-top:8px;">'
                f'{"1 scenario trovato" if n == 1 else f"{n} scenari trovati"}</div>',
                unsafe_allow_html=True
            )
        with col_dl:
            fname = f"scenari_{item}_{direction}.xlsx".replace(' ', '_')
            st.download_button(
                label="⬇ Esporta Excel",
                data=build_export_bytes(df_show),
                file_name=fname,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key=f"dl_qv_{col_name}_{item}_{direction}",
                use_container_width=True,
            )
        st.markdown(build_grouped_table_html(df_show, th_class), unsafe_allow_html=True)

# ─── CARD RENDERER ─────────────────────────────────────────────────────────────
def render_cards(items, df_filtered, col_name, on_select_key, multi=False, show_mini=False):
    """
    Renders cards. Each card shows:
      - Main button (item name)
      - Stress direction label (based on mean shock)
      - Optional mini pos/neg buttons (show_mini=True for L1 and L2)
    """
    if not items: return
    ncols = min(len(items), 4)
    cols  = st.columns(ncols)

    for i, item in enumerate(items):
        sub      = df_filtered[df_filtered[col_name] == item]
        # Conta scenari UNICI con almeno uno shock pos/neg (non righe shock)
        n_pos    = int(sub[sub['_shock_num'] > 0]['Scenario'].nunique())
        n_neg    = int(sub[sub['_shock_num'] < 0]['Scenario'].nunique())
        mean_v   = mean_shock_for_group(sub)
        is_sel   = (item in st.session_state.sel_l1_set) if multi else (st.session_state.get(on_select_key) == item)
        btn_label = f"{'✓ ' if is_sel else ''}{item}"

        with cols[i % ncols]:
            clicked = st.button(btn_label, key=f"btn_{on_select_key}_{item}", use_container_width=True)
            # Stress direction label from mean shock
            st.markdown(
                f'<div class="card-sub">{stress_label_html(mean_v)}</div>',
                unsafe_allow_html=True
            )

            if show_mini:
                mc1, mc2 = st.columns(2)
                with mc1:
                    if st.button(
                        f"▲ {n_pos}  Positivi",
                        key=f"mini_pos_{on_select_key}_{item}",
                        use_container_width=True
                    ):
                        st.session_state.quick_view = {'col': col_name, 'item': item, 'dir': 'pos'}
                        st.rerun()
                with mc2:
                    if st.button(
                        f"▼ {n_neg}  Negativi",
                        key=f"mini_neg_{on_select_key}_{item}",
                        use_container_width=True
                    ):
                        st.session_state.quick_view = {'col': col_name, 'item': item, 'dir': 'neg'}
                        st.rerun()

            if clicked:
                st.session_state.quick_view = None
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

# ─── STAT BOXES WITH FILTER ────────────────────────────────────────────────────
def render_stat_boxes(df_sub):
    n_sc  = df_sub['Scenario'].nunique()
    n_pos = int((df_sub['_shock_num'] > 0).sum())
    n_neg = int((df_sub['_shock_num'] < 0).sum())
    cur_filter = st.session_state.shock_filter

    c0, c1, c2, c3 = st.columns([1.4, 1.4, 1.4, 7])
    with c0:
        st.markdown(f"""<div class="stat-box">
            <div class="sv">{n_sc}</div>
            <div class="sk">Scenari totali</div>
        </div>""", unsafe_allow_html=True)
    with c1:
        active_pos = cur_filter == 'pos'
        if st.button(f"▲ {n_pos}  positivi", key="filter_pos", use_container_width=True):
            st.session_state.shock_filter = 'all' if active_pos else 'pos'
            st.rerun()
        if active_pos:
            st.markdown('<div style="height:3px;background:#16a34a;border-radius:2px;margin-top:-6px;"></div>',
                        unsafe_allow_html=True)
    with c2:
        active_neg = cur_filter == 'neg'
        if st.button(f"▼ {n_neg}  negativi", key="filter_neg", use_container_width=True):
            st.session_state.shock_filter = 'all' if active_neg else 'neg'
            st.rerun()
        if active_neg:
            st.markdown('<div style="height:3px;background:#dc2626;border-radius:2px;margin-top:-6px;"></div>',
                        unsafe_allow_html=True)
    return n_pos, n_neg

# ─── SCENARIO TABLE (L3 drill-down) ────────────────────────────────────────────
def render_scenario_table(df_sub, multi_mode=False):
    render_stat_boxes(df_sub)

    f = st.session_state.shock_filter
    if f == 'pos':
        df_filtered = df_sub[df_sub['_shock_num'] > 0]
        if df_filtered.empty:
            st.info("Nessuno scenario con shock positivo.")
            return
    elif f == 'neg':
        df_filtered = df_sub[df_sub['_shock_num'] < 0]
        if df_filtered.empty:
            st.info("Nessuno scenario con shock negativo.")
            return
    else:
        df_filtered = df_sub

    if not multi_mode:
        # Export button
        n_sc = df_filtered['Scenario'].nunique()
        col_info2, col_dl2, _ = st.columns([2, 1.5, 6])
        with col_info2:
            st.markdown(
                f'<div style="font-size:0.72rem;color:#6b6b6b;padding-top:8px;">'
                f'{"1 scenario" if n_sc == 1 else f"{n_sc} scenari"}</div>',
                unsafe_allow_html=True
            )
        with col_dl2:
            st.download_button(
                label="⬇ Esporta Excel",
                data=build_export_bytes(df_filtered),
                file_name=f"scenari_{st.session_state.get('sel_l3','export')}.xlsx".replace(' ', '_'),
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="dl_l3",
                use_container_width=True,
            )
        # Grouped: scenario name + L3 factors
        st.markdown(build_grouped_table_html(df_filtered), unsafe_allow_html=True)
    else:
        # Multi-area: group by scenario, list L1›L2›L3 paths
        rows_html = ""
        for scenario in sorted(df_filtered['Scenario'].unique()):
            sc_rows  = df_filtered[df_filtered['Scenario'] == scenario]
            long_des = desc_map.get(str(scenario).strip(), '')
            des_html = f'<div class="long-des">{long_des}</div>' if long_des else ''

            factors_html = '<div class="factor-list">'
            for _, r in sc_rows.iterrows():
                shock_num = r['_shock_num']
                shock_raw = str(r['ShockValue']) if not pd.isna(r['ShockValue']) else "—"
                path = " › ".join([str(r[c]) for c in ['L1','L2','L3']
                                   if str(r.get(c, '')).strip() not in ('', 'nan')])
                try:   is_num = not np.isnan(float(shock_num))
                except: is_num = False
                if is_num and shock_num > 0:
                    val_cls = "factor-val-pos"; arrow = "▲ "
                elif is_num and shock_num < 0:
                    val_cls = "factor-val-neg"; arrow = "▼ "
                else:
                    val_cls = "factor-val-zero"; arrow = ""
                factors_html += (
                    f'<div class="factor-row">'
                    f'<span class="factor-name">{path}</span>'
                    f'<span class="{val_cls}">{arrow}{shock_raw}</span>'
                    f'</div>'
                )
            factors_html += '</div>'
            rows_html += f"""
            <tr>
                <td><strong>{scenario}</strong>{des_html}</td>
                <td>{factors_html}</td>
            </tr>"""

        st.markdown(f"""
        <table class="scenario-table">
            <thead><tr><th>Scenario</th><th>Shock per area selezionata</th></tr></thead>
            <tbody>{rows_html}</tbody>
        </table>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# MODE A — DRILL-DOWN
# Struttura: ogni livello mostra la propria quick-view DOPO le sue card,
# indipendentemente dai livelli figli. Il drill continua solo se quick_view
# non appartiene al livello corrente o superiore.
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.mode == 'drill':
    qv = st.session_state.quick_view   # shorthand

    parts = ['<span>All</span>']
    if st.session_state.sel_l1_single:
        parts.append(f'<span class="sep">/</span><span>{st.session_state.sel_l1_single}</span>')
    if st.session_state.sel_l2:
        parts.append(f'<span class="sep">/</span><span>{st.session_state.sel_l2}</span>')
    if st.session_state.sel_l3:
        parts.append(f'<span class="sep">/</span><span>{st.session_state.sel_l3}</span>')
    st.markdown(f'<div class="breadcrumb">{"".join(parts)}</div>', unsafe_allow_html=True)

    # ── L1 ──────────────────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">Mapping Livello 1 — Asset Class</div>', unsafe_allow_html=True)
    render_cards(clean_items(df['L1']), df, 'L1', 'sel_l1_single', multi=False, show_mini=True)

    # Quick-view L1: shown when qv is for L1; stops further drill
    if qv and qv['col'] == 'L1':
        render_quick_view(df, 'L1')

    # ── L2: visible when L1 selected AND qv is not for L1 ───────────────────────
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
            st.markdown(f'<div class="section-header">Livello 2 — {st.session_state.sel_l1_single}</div>',
                        unsafe_allow_html=True)
            render_cards(l2_items, df_l1, 'L2', 'sel_l2', multi=False, show_mini=True)

            # Quick-view L2: shown when qv is for L2; stops further drill
            if qv and qv['col'] == 'L2':
                render_quick_view(df_l1, 'L2')

            # ── L3: visible when L2 selected AND qv is not for L2 ───────────────
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
                    st.markdown(f'<div class="section-header">Livello 3 — {st.session_state.sel_l2}</div>',
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
                    st.markdown(f'<div class="section-header">Scenari — {st.session_state.sel_l3}</div>',
                                unsafe_allow_html=True)
                    render_scenario_table(df_l3, multi_mode=False)


# ══════════════════════════════════════════════════════════════════════════════
# MODE B — MULTI-AREA
# ══════════════════════════════════════════════════════════════════════════════
else:
    qv = st.session_state.quick_view

    st.markdown(
        '<div class="hint-box">💡 Seleziona una o più aree di Livello 1. '
        'Con una sola area vedi tutti i suoi scenari. '
        'Con più aree vedi gli scenari <strong>comuni a tutte</strong>, con i rispettivi shock per area.</div>',
        unsafe_allow_html=True
    )

    st.markdown('<div class="section-header">Seleziona Asset Class (multi-selezione)</div>',
                unsafe_allow_html=True)
    render_cards(clean_items(df['L1']), df, 'L1', 'sel_l1_set', multi=True, show_mini=True)

    if qv and qv['col'] == 'L1':
        render_quick_view(df, 'L1')

    elif st.session_state.sel_l1_set:
        pills_html = " ".join([f'<span class="sel-pill">✓ {x}</span>'
                                for x in sorted(st.session_state.sel_l1_set)])
        st.markdown(f'<div style="margin:8px 0 4px;">{pills_html}</div>', unsafe_allow_html=True)

        col_clear, _ = st.columns([1.5, 8])
        with col_clear:
            if st.button("✕ Deseleziona tutto", key="clear_multi"):
                st.session_state.update({'sel_l1_set': set(), 'shock_filter': 'all', 'quick_view': None})
                st.rerun()

        selected_list = list(st.session_state.sel_l1_set)

        if len(selected_list) == 1:
            df_show = df[df['L1'].isin(selected_list)].copy()
            label   = f"Scenari in: {selected_list[0]}"
        else:
            sets_per_l1 = [set(df[df['L1'] == l1]['Scenario'].unique()) for l1 in selected_list]
            common  = sets_per_l1[0].intersection(*sets_per_l1[1:])
            df_show = df[df['L1'].isin(selected_list) & df['Scenario'].isin(common)].copy()
            label   = f"Scenari comuni a: {' · '.join(sorted(selected_list))}"

        st.markdown(f'<div class="section-header">{label}</div>', unsafe_allow_html=True)

        if df_show.empty:
            st.info("Nessuno scenario presente contemporaneamente in tutte le aree selezionate.")
        else:
            render_scenario_table(df_show, multi_mode=(len(selected_list) > 1))

    else:
        st.markdown(
            '<div style="font-size:0.78rem;color:#6b7280;margin-top:1rem;">'
            '← Clicca su una o più asset class per visualizzare gli scenari.</div>',
            unsafe_allow_html=True
        )

# ─── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(
    '<div style="font-size:0.6rem;color:#9ca3af;text-align:center;">'
    'Stress Test Dashboard · ListaxMapping / Pivot · MAIN</div>',
    unsafe_allow_html=True
)
