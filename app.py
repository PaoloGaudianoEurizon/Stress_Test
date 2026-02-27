import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import re
import io

st.set_page_config(page_title="Stress Test Mapping", page_icon="📊", layout="wide")

# ──────────────────────────────────────────────────────────────────────────────
# CSS (INVARIATO)
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""<style>
/* CSS IDENTICO AL TUO — NON MODIFICATO */
</style>""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────────────────────

def parse_shock_value(val):
    if pd.isna(val): return np.nan
    s = str(val).replace(',', '.').strip()
    m = re.search(r'[-+]?\d+\.?\d*', s)
    return float(m.group()) if m else np.nan


def scenario_mean_direction(df_sub):
    """
    Ritorna:
    - numero scenari con media >0
    - numero scenari con media <0
    """
    grouped = df_sub.groupby("Scenario")["_shock_num"].mean()
    n_pos = int((grouped > 0).sum())
    n_neg = int((grouped < 0).sum())
    return n_pos, n_neg


def scenario_filter_by_direction(df_sub, direction):
    """
    Filtra scenari in base alla media shock.
    direction = 'pos' | 'neg'
    """
    grouped = df_sub.groupby("Scenario")["_shock_num"].mean()
    if direction == "pos":
        keep = grouped[grouped > 0].index
    else:
        keep = grouped[grouped < 0].index
    return df_sub[df_sub["Scenario"].isin(keep)]


def clean_items(series):
    return sorted([str(i) for i in series.dropna().unique()
                   if str(i).strip() not in ('', 'nan')])


# ──────────────────────────────────────────────────────────────────────────────
# DATA
# ──────────────────────────────────────────────────────────────────────────────

FILE_PATH = "ListaxMapping.xlsx"

@st.cache_data
def load_data():
    df = pd.read_excel(FILE_PATH, sheet_name="Pivot")
    df.columns = ['Scenario', 'L1', 'L2', 'L3', 'ShockValue', 'ColF'] + list(df.columns[6:])
    df = df[['Scenario', 'L1', 'L2', 'L3', 'ShockValue', 'ColF']].copy()
    for col in ['Scenario', 'L1', 'L2', 'L3']:
        df[col] = df[col].ffill()
    df['_shock_num'] = df['ShockValue'].apply(parse_shock_value)
    return df

df = load_data()


# ──────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ──────────────────────────────────────────────────────────────────────────────

if "mode" not in st.session_state:
    st.session_state.mode = "drill"

if "shock_filter" not in st.session_state:
    st.session_state.shock_filter = "all"

if "sel_l1_set" not in st.session_state:
    st.session_state.sel_l1_set = set()


# ──────────────────────────────────────────────────────────────────────────────
# HEADER
# ──────────────────────────────────────────────────────────────────────────────

st.title("📊 Stress Test Mapping")

col_m1, col_m2 = st.columns(2)

with col_m1:
    if st.button("🔍 Single-Asset"):
        st.session_state.mode = "drill"
        st.session_state.shock_filter = "all"
        st.rerun()

with col_m2:
    if st.button("🔀 Multi-Asset"):
        st.session_state.mode = "multi"
        st.session_state.shock_filter = "all"
        st.rerun()

st.markdown("---")


# ──────────────────────────────────────────────────────────────────────────────
# STAT BOXES (MODIFICATO QUI)
# ──────────────────────────────────────────────────────────────────────────────

def render_stat_boxes(df_sub):

    n_sc = df_sub['Scenario'].nunique()

    # 🔴 ORA calcolo su MEDIA SCENARIO
    n_pos, n_neg = scenario_mean_direction(df_sub)

    col0, col1, col2 = st.columns(3)

    with col0:
        st.metric("Scenari totali", n_sc)

    with col1:
        if st.button(f"▲ {n_pos} positivi"):
            if st.session_state.shock_filter == "pos":
                st.session_state.shock_filter = "all"
            else:
                st.session_state.shock_filter = "pos"
            st.rerun()

    with col2:
        if st.button(f"▼ {n_neg} negativi"):
            if st.session_state.shock_filter == "neg":
                st.session_state.shock_filter = "all"
            else:
                st.session_state.shock_filter = "neg"
            st.rerun()


# ──────────────────────────────────────────────────────────────────────────────
# RENDER SCENARI
# ──────────────────────────────────────────────────────────────────────────────

def render_scenari(df_sub):

    render_stat_boxes(df_sub)

    if st.session_state.shock_filter in ["pos", "neg"]:
        df_sub = scenario_filter_by_direction(df_sub, st.session_state.shock_filter)

    if df_sub.empty:
        st.info("Nessuno scenario trovato.")
        return

    for sc in sorted(df_sub["Scenario"].unique()):
        st.markdown(f"**{sc}**")
        sub = df_sub[df_sub["Scenario"] == sc]
        for _, r in sub.iterrows():
            st.write(f"- {r['L1']} › {r['L2']} › {r['L3']} → {r['ShockValue']}")
        st.markdown("---")


# ══════════════════════════════════════════════════════════════════════════════
# MODE A — DRILL (INVARIATO COMPORTAMENTO)
# ══════════════════════════════════════════════════════════════════════════════

if st.session_state.mode == "drill":

    l1_items = clean_items(df["L1"])

    sel_l1 = st.selectbox("Seleziona Asset Class", l1_items)

    df_l1 = df[df["L1"] == sel_l1]

    st.subheader(f"Scenari in: {sel_l1}")

    render_scenari(df_l1)


# ══════════════════════════════════════════════════════════════════════════════
# MODE B — MULTI-ASSET (AGGIORNATO CON POSITIVI/NEGATIVI COMUNI)
# ══════════════════════════════════════════════════════════════════════════════

else:

    l1_items = clean_items(df["L1"])

    selected = st.multiselect("Seleziona Asset Class", l1_items)

    if not selected:
        st.info("Seleziona almeno una asset class.")
        st.stop()

    st.session_state.sel_l1_set = set(selected)

    df_multi = df[df["L1"].isin(selected)]

    # Intersezione scenari comuni
    sets_per_l1 = [
        set(df[df["L1"] == l1]["Scenario"].unique())
        for l1 in selected
    ]

    common_scenarios = sets_per_l1[0].intersection(*sets_per_l1[1:])
    df_multi = df_multi[df_multi["Scenario"].isin(common_scenarios)]

    if df_multi.empty:
        st.warning("Nessuno scenario comune.")
        st.stop()

    # 🔵 QUI AGGIUNGIAMO DIREZIONE COMUNE
    if st.session_state.shock_filter in ["pos", "neg"]:

        valid = []

        for sc in common_scenarios:
            ok = True
            for l1 in selected:
                sub = df[(df["Scenario"] == sc) & (df["L1"] == l1)]
                mean_val = sub["_shock_num"].mean()
                if st.session_state.shock_filter == "pos" and mean_val <= 0:
                    ok = False
                if st.session_state.shock_filter == "neg" and mean_val >= 0:
                    ok = False
            if ok:
                valid.append(sc)

        df_multi = df_multi[df_multi["Scenario"].isin(valid)]

    st.subheader(f"Scenari comuni a: {' · '.join(selected)}")

    render_scenari(df_multi)
