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

.card-sub {
    font-size: 0.72rem; color: #6b6b6b;
    margin-top: -10px; margin-bottom: 4px; min-height: 16px;
}

/* ── Bottoni default ── */
.qv-header {
    font-size: 0.82rem; font-weight: 600; color: #0e1117;
    padding: 8px 14px; border-radius: 6px 6px 0 0;
    display: flex; align-items: center; gap: 8px;
}
.qv-header.pos { background: #15803d; color: white; }
.qv-header.neg { background: #b91c1c; color: white; }

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
.scenario-table th.pos-th { background: #15803d; }
.scenario-table th.neg-th { background: #b91c1c; }
.scenario-table td {
    padding: 10px 16px; border-bottom: 1px solid #f0f0f0;
    color: #31333f; vertical-align: top;
}
.scenario-table tr:last-child td { border-bottom: none; }
.scenario-table tr:hover td { background: #fafafa; }

.shock-pos { color: #15803d; font-weight: 600; }
.shock-neg { color: #b91c1c; font-weight: 600; }
.shock-zero { color: #6b6b6b; }
.long-des { font-size: 0.72rem; color: #6b6b6b; margin-top: 4px; line-height: 1.45; }
.shock-list { display: flex; flex-direction: column; gap: 3px; }
.shock-row-item { display: flex; gap: 6px; align-items: baseline; }
.shock-path { font-size: 0.63rem; color: #aaaaaa; }

/* ── Bottoni default ── */
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

    return df, dm

try:
    df, dm = load_data()
except FileNotFoundError:
    st.error(f"File `{FILE_PATH}` non trovato nella repository.")
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
    # quick-view: when a mini pos/neg button is clicked on a L1/L2 card
    # stores {'col': 'L1'|'L2', 'item': str, 'dir': 'pos'|'neg'}
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
        st.session_state.mode        = 'drill'
        st.session_state.sel_l1_set  = set()
        st.session_state.sel_l2      = None
        st.session_state.sel_l3      = None
        st.session_state.shock_filter= 'all'
        st.session_state.quick_view  = None
        st.rerun()
with col_m2:
    if st.button("🔀 Multi-area", use_container_width=True):
        st.session_state.mode        = 'multi'
        st.session_state.sel_l2      = None
        st.session_state.sel_l3      = None
        st.session_state.shock_filter= 'all'
        st.session_state.quick_view  = None
        st.rerun()
st.markdown("---")

# ─── JS: colora bottoni mini Positivi/Negativi via MutationObserver ───────────
components.html("""
<script>
(function() {
    function styleMiniBtns(doc) {
        doc.querySelectorAll('button').forEach(function(btn) {
            var txt = btn.innerText || btn.textContent || '';
            if (txt.includes('Positivi')) {
                btn.style.setProperty('background-color', '#15803d', 'important');
                btn.style.setProperty('color', '#ffffff', 'important');
                btn.style.setProperty('border', '1.5px solid #14532d', 'important');
                btn.style.setProperty('font-size', '0.72rem', 'important');
                btn.style.setProperty('font-weight', '600', 'important');
                btn.style.setProperty('min-height', '30px', 'important');
                btn.style.setProperty('height', '30px', 'important');
                btn.style.setProperty('border-radius', '5px', 'important');
                btn.setAttribute('data-mini', 'pos');
            } else if (txt.includes('Negativi')) {
                btn.style.setProperty('background-color', '#b91c1c', 'important');
                btn.style.setProperty('color', '#ffffff', 'important');
                btn.style.setProperty('border', '1.5px solid #7f1d1d', 'important');
                btn.style.setProperty('font-size', '0.72rem', 'important');
                btn.style.setProperty('font-weight', '600', 'important');
                btn.style.setProperty('min-height', '30px', 'important');
                btn.style.setProperty('height', '30px', 'important');
                btn.style.setProperty('border-radius', '5px', 'important');
                btn.setAttribute('data-mini', 'neg');
            }
        });
    }
    var target = window.parent.document.body;
    styleMiniBtns(window.parent.document);
    var observer = new MutationObserver(function() {
        styleMiniBtns(window.parent.document);
    });
    observer.observe(target, { childList: true, subtree: true });
})();
</script>
""", height=0)

# ─── INLINE SCENARIO TABLE (for quick-view and drill) ─────────────────────────
def build_scenario_table_html(df_sub, th_class=""):
    """Returns the HTML string of a scenario table."""
    rows_html = ""
    for _, row in df_sub.sort_values('Scenario').iterrows():
        shock_num = row['_shock_num']
        shock_raw = str(row['ShockValue']) if not pd.isna(row['ShockValue']) else "—"
        long_des  = desc_map.get(str(row['Scenario']).strip(), '')
        try:   is_num = not np.isnan(float(shock_num))
        except: is_num = False
        cls   = ("shock-pos" if shock_num > 0 else "shock-neg") if is_num and shock_num != 0 else "shock-zero"
        arrow = ("▲ " if shock_num > 0 else "▼ ") if is_num and shock_num != 0 else ""
        des_html = f'<div class="long-des">{long_des}</div>' if long_des else ''
        rows_html += f"""
        <tr>
            <td><strong>{row['Scenario']}</strong>{des_html}</td>
            <td class='{cls}'>{arrow}{shock_raw}</td>
        </tr>"""
    th_extra = f' class="{th_class}"' if th_class else ''
    return f"""
    <table class="scenario-table">
        <thead><tr><th{th_extra}>Scenario</th><th{th_extra}>Shock Value</th></tr></thead>
        <tbody>{rows_html}</tbody>
    </table>"""

def render_quick_view(df_context, col_name):
    """
    If quick_view is set and matches col_name, render the filtered scenario table
    inline, with a close button.
    """
    qv = st.session_state.quick_view
    if qv is None or qv['col'] != col_name:
        return
    item = qv['item']
    direction = qv['dir']

    df_item = df_context[df_context[col_name] == item]
    if direction == 'pos':
        df_show = df_item[df_item['_shock_num'] > 0]
        th_class = "pos-th"
        label    = f"▲ Scenari positivi — {item}"
        hdr_cls  = "pos"
    else:
        df_show = df_item[df_item['_shock_num'] < 0]
        th_class = "neg-th"
        label    = f"▼ Scenari negativi — {item}"
        hdr_cls  = "neg"

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
        st.markdown(
            f'<div style="font-size:0.72rem;color:#6b6b6b;margin-bottom:8px;">'
            f'{"1 scenario trovato" if n==1 else f"{n} scenari trovati"}</div>',
            unsafe_allow_html=True
        )
        st.markdown(build_scenario_table_html(df_show, th_class), unsafe_allow_html=True)

# ─── CARD RENDERER ─────────────────────────────────────────────────────────────
def render_cards(items, df_filtered, col_name, on_select_key, multi=False, show_mini=False):
    """
    show_mini=True  → mostra due bottoni cliccabili ▲pos / ▼neg sotto ogni card.
                      Cliccandoli appare la tabella scenari filtrata inline.
    show_mini=False → solo conteggio scenari (L3).
    """
    if not items: return
    ncols = min(len(items), 4)
    cols  = st.columns(ncols)

    for i, item in enumerate(items):
        sub   = df_filtered[df_filtered[col_name] == item]
        n_sc  = sub['Scenario'].nunique()
        n_pos = int((sub['_shock_num'] > 0).sum())
        n_neg = int((sub['_shock_num'] < 0).sum())
        is_sel    = (item in st.session_state.sel_l1_set) if multi else (st.session_state.get(on_select_key) == item)
        btn_label = f"{'✓ ' if is_sel else ''}{item}"

        with cols[i % ncols]:
            # ── Main selection button ──
            clicked = st.button(btn_label, key=f"btn_{on_select_key}_{item}", use_container_width=True)
            st.markdown(f'<div class="card-sub">{n_sc} scenari</div>', unsafe_allow_html=True)

            if show_mini:
                mc1, mc2 = st.columns(2)
                with mc1:
                    st.markdown('<span class="mini-pos-marker"></span>', unsafe_allow_html=True)
                    if st.button(
                        f"▲ {n_pos}  Positivi",
                        key=f"mini_pos_{on_select_key}_{item}",
                        use_container_width=True
                    ):
                        st.session_state.quick_view = {
                            'col': col_name, 'item': item, 'dir': 'pos'
                        }
                        st.rerun()
                with mc2:
                    st.markdown('<span class="mini-neg-marker"></span>', unsafe_allow_html=True)
                    if st.button(
                        f"▼ {n_neg}  Negativi",
                        key=f"mini_neg_{on_select_key}_{item}",
                        use_container_width=True
                    ):
                        st.session_state.quick_view = {
                            'col': col_name, 'item': item, 'dir': 'neg'
                        }
                        st.rerun()

            # ── Handle main button click ──
            if clicked:
                st.session_state.quick_view = None   # close any quick-view
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
    """Scenari totali + bottoni filtro ▲positivi / ▼negativi."""
    n_sc  = df_sub['Scenario'].nunique()
    n_pos = int((df_sub['_shock_num'] > 0).sum())
    n_neg = int((df_sub['_shock_num'] < 0).sum())

    cur_filter = st.session_state.shock_filter
    c0, c1, c2, c3 = st.columns([1.4, 1.4, 1.4, 7])

    with c0:
        st.markdown(f"""
        <div class="stat-box">
            <div class="sv">{n_sc}</div>
            <div class="sk">Scenari totali</div>
        </div>""", unsafe_allow_html=True)

    with c1:
        active_pos = cur_filter == 'pos'
        if st.button(f"▲ {n_pos}  positivi", key="filter_pos", use_container_width=True,
                     help="Filtra solo scenari con shock positivo"):
            st.session_state.shock_filter = 'all' if active_pos else 'pos'
            st.rerun()
        if active_pos:
            st.markdown('<div style="height:3px;background:#15803d;border-radius:2px;margin-top:-6px;"></div>',
                        unsafe_allow_html=True)

    with c2:
        active_neg = cur_filter == 'neg'
        if st.button(f"▼ {n_neg}  negativi", key="filter_neg", use_container_width=True,
                     help="Filtra solo scenari con shock negativo"):
            st.session_state.shock_filter = 'all' if active_neg else 'neg'
            st.rerun()
        if active_neg:
            st.markdown('<div style="height:3px;background:#b91c1c;border-radius:2px;margin-top:-6px;"></div>',
                        unsafe_allow_html=True)

    return n_pos, n_neg

# ─── SCENARIO TABLE (livello L3) ───────────────────────────────────────────────
def render_scenario_table(df_sub, multi_mode=False):
    n_pos, n_neg = render_stat_boxes(df_sub)

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
        st.markdown(build_scenario_table_html(df_filtered), unsafe_allow_html=True)

    else:
        rows_html = ""
        scenarios = sorted(df_filtered['Scenario'].unique())

        for scenario in scenarios:
            sc_rows  = df_filtered[df_filtered['Scenario'] == scenario]
            long_des = desc_map.get(str(scenario).strip(), '')
            des_html = f'<div class="long-des">{long_des}</div>' if long_des else ''

            shock_items = ""
            for _, r in sc_rows.iterrows():
                shock_num = r['_shock_num']
                shock_raw = str(r['ShockValue']) if not pd.isna(r['ShockValue']) else "—"
                try:   is_num = not np.isnan(float(shock_num))
                except: is_num = False
                cls   = ("shock-pos" if shock_num > 0 else "shock-neg") if is_num and shock_num != 0 else "shock-zero"
                arrow = ("▲ " if shock_num > 0 else "▼ ") if is_num and shock_num != 0 else ""
                path  = " › ".join([str(r[c]) for c in ['L1','L2','L3'] if str(r.get(c,'')).strip() not in ('','nan')])
                shock_items += f'<div class="shock-row-item"><span class="{cls}">{arrow}{shock_raw}</span><span class="shock-path">{path}</span></div>'

            rows_html += f"""
            <tr>
                <td><strong>{scenario}</strong>{des_html}</td>
                <td><div class="shock-list">{shock_items}</div></td>
            </tr>"""

        st.markdown(f"""
        <table class="scenario-table">
            <thead><tr><th>Scenario</th><th>Shock per area selezionata</th></tr></thead>
            <tbody>{rows_html}</tbody>
        </table>""", unsafe_allow_html=True)

        st.markdown(
            '<div style="font-size:0.65rem;color:#9ca3af;margin-top:8px;">'
            '⚠️ I valori sono quelli raw dall\'Excel per ciascuna combinazione L1 › L2 › L3, non medie.</div>',
            unsafe_allow_html=True
        )


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

    # ── L1: con mini box cliccabili ──
    st.markdown('<div class="section-header">Mapping Livello 1 — Asset Class</div>', unsafe_allow_html=True)
    render_cards(clean_items(df['L1']), df, 'L1', 'sel_l1_single', multi=False, show_mini=True)
    # Quick-view inline per L1
    render_quick_view(df, 'L1')

    if st.session_state.sel_l1_single and st.session_state.quick_view is None:
        df_l1    = df[df['L1'] == st.session_state.sel_l1_single]
        l2_items = clean_items(df_l1['L2'])
        col_b, _ = st.columns([1, 5])
        with col_b:
            if st.button("← Reset L1", key="back_l1"):
                st.session_state.sel_l1_single = None
                st.session_state.sel_l2        = None
                st.session_state.sel_l3        = None
                st.session_state.shock_filter  = 'all'
                st.session_state.quick_view    = None
                st.rerun()
        if l2_items:
            # ── L2: con mini box cliccabili ──
            st.markdown(f'<div class="section-header">Livello 2 — {st.session_state.sel_l1_single}</div>', unsafe_allow_html=True)
            render_cards(l2_items, df_l1, 'L2', 'sel_l2', multi=False, show_mini=True)
            # Quick-view inline per L2
            render_quick_view(df_l1, 'L2')

    if (st.session_state.sel_l1_single and st.session_state.sel_l2
            and st.session_state.quick_view is None):
        df_l2    = df[(df['L1'] == st.session_state.sel_l1_single) & (df['L2'] == st.session_state.sel_l2)]
        l3_items = clean_items(df_l2['L3'])
        col_b2, _ = st.columns([1, 5])
        with col_b2:
            if st.button("← Reset L2", key="back_l2"):
                st.session_state.sel_l2       = None
                st.session_state.sel_l3       = None
                st.session_state.shock_filter = 'all'
                st.session_state.quick_view   = None
                st.rerun()
        if l3_items:
            # ── L3: senza mini box ──
            st.markdown(f'<div class="section-header">Livello 3 — {st.session_state.sel_l2}</div>', unsafe_allow_html=True)
            render_cards(l3_items, df_l2, 'L3', 'sel_l3', multi=False, show_mini=False)

    if (st.session_state.sel_l1_single and st.session_state.sel_l2
            and st.session_state.sel_l3 and st.session_state.quick_view is None):
        df_l3 = df[
            (df['L1'] == st.session_state.sel_l1_single) &
            (df['L2'] == st.session_state.sel_l2) &
            (df['L3'] == st.session_state.sel_l3)
        ]
        col_b3, _ = st.columns([1, 5])
        with col_b3:
            if st.button("← Reset L3", key="back_l3"):
                st.session_state.sel_l3       = None
                st.session_state.shock_filter = 'all'
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

    # ── L1 multi: con mini box cliccabili ──
    st.markdown('<div class="section-header">Seleziona Asset Class (multi-selezione)</div>', unsafe_allow_html=True)
    render_cards(clean_items(df['L1']), df, 'L1', 'sel_l1_set', multi=True, show_mini=True)
    # Quick-view inline per L1 anche in multi mode
    render_quick_view(df, 'L1')

    if st.session_state.sel_l1_set and st.session_state.quick_view is None:
        pills_html = " ".join([f'<span class="sel-pill">✓ {x}</span>' for x in sorted(st.session_state.sel_l1_set)])
        st.markdown(f'<div style="margin:8px 0 4px;">{pills_html}</div>', unsafe_allow_html=True)

        col_clear, _ = st.columns([1.5, 8])
        with col_clear:
            if st.button("✕ Deseleziona tutto", key="clear_multi"):
                st.session_state.sel_l1_set   = set()
                st.session_state.shock_filter = 'all'
                st.session_state.quick_view   = None
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

    elif not st.session_state.sel_l1_set and st.session_state.quick_view is None:
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
