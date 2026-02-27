import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.colors import qualitative
from io import BytesIO

# ─── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(layout="wide", page_title="Portfolio Analytics", page_icon="📈")

# ─── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@400;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Syne', sans-serif; }

.stApp { background: #f5f5f0; color: #1a1a1a; }

/* ── Buttons ── */
.stButton > button {
    background: #ffffff; color: #1a1a1a;
    border: 1.5px solid #d4d0c8; border-radius: 8px;
    font-family: 'Syne', sans-serif; font-weight: 600; font-size: 0.85rem;
    transition: all 0.15s ease;
}
.stButton > button:hover { border-color: #1a1a1a; background: #1a1a1a; color: #ffffff; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1.5px solid #e8e4dc;
}
section[data-testid="stSidebar"] * { font-family: 'Syne', sans-serif; }
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stMultiSelect label,
section[data-testid="stSidebar"] .stDateInput label,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.7rem !important;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #888880 !important;
    font-weight: 500 !important;
}
section[data-testid="stSidebar"] .stSelectbox > div > div,
section[data-testid="stSidebar"] .stMultiSelect > div > div {
    background: #f5f5f0;
    border: 1.5px solid #d4d0c8;
    border-radius: 8px;
    font-family: 'DM Mono', monospace;
    font-size: 0.8rem;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent;
    border-bottom: 2px solid #d4d0c8;
    gap: 0;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    border: none;
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #888880;
    padding: 8px 20px;
    border-bottom: 3px solid transparent;
    margin-bottom: -2px;
}
.stTabs [aria-selected="true"] {
    color: #1a1a1a !important;
    border-bottom: 3px solid #1a1a1a !important;
    font-weight: 700;
}
.stTabs [data-baseweb="tab"]:hover { color: #1a1a1a; }

/* ── Titles ── */
.page-title {
    font-size: 2rem; font-weight: 800; letter-spacing: -0.5px; color: #1a1a1a;
    border-bottom: 3px solid #1a1a1a; padding-bottom: 0.4rem; margin-bottom: 0.25rem;
}
.page-subtitle {
    font-family: 'DM Mono', monospace; font-size: 0.72rem; color: #888880;
    margin-bottom: 1.8rem; letter-spacing: 0.08em; text-transform: uppercase;
}
.section-header {
    font-size: 0.68rem; font-family: 'DM Mono', monospace; text-transform: uppercase;
    letter-spacing: 0.14em; color: #888880; margin: 2rem 0 1rem;
    display: flex; align-items: center; gap: 10px;
}
.section-header::after { content: ''; flex: 1; height: 1px; background: #d4d0c8; }

/* ── Stat boxes ── */
.stat-row { display: flex; gap: 14px; margin-bottom: 1.5rem; flex-wrap: wrap; }
.stat-box {
    background: #ffffff; border: 1.5px solid #d4d0c8; border-radius: 10px;
    padding: 0.8rem 1.3rem; min-width: 140px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.stat-box .sv { font-size: 1.5rem; font-weight: 800; color: #1a1a1a; line-height: 1; }
.stat-box .sk {
    font-family: 'DM Mono', monospace; font-size: 0.62rem; color: #888880;
    text-transform: uppercase; letter-spacing: 0.07em; margin-top: 4px;
}

/* ── Info / warning boxes ── */
.info-box {
    background: #fff8e8; border: 1.5px solid #f0d080; border-radius: 8px;
    padding: 0.7rem 1.1rem; font-family: 'DM Mono', monospace; font-size: 0.74rem;
    color: #7a5a00; margin: 1rem 0;
}

/* ── Download button ── */
.stDownloadButton > button {
    background: #f5f5f0; color: #1a1a1a;
    border: 1.5px solid #d4d0c8; border-radius: 8px;
    font-family: 'DM Mono', monospace; font-weight: 500; font-size: 0.72rem;
    letter-spacing: 0.04em;
    transition: all 0.15s ease;
}
.stDownloadButton > button:hover { background: #1a1a1a; color: #ffffff; border-color: #1a1a1a; }

/* ── Dataframe ── */
.stDataFrame { border: 1.5px solid #d4d0c8; border-radius: 10px; overflow: hidden; }
[data-testid="stDataFrameResizable"] { font-family: 'DM Mono', monospace; font-size: 0.78rem; }

/* ── Selectbox inside main area ── */
.stSelectbox > div > div {
    background: #ffffff; border: 1.5px solid #d4d0c8;
    border-radius: 8px; font-family: 'DM Mono', monospace; font-size: 0.82rem;
}

/* ── Plotly chart container ── */
.stPlotlyChart {
    background: #ffffff; border: 1.5px solid #e8e4dc;
    border-radius: 12px; overflow: hidden;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    padding: 8px;
    margin-bottom: 1rem;
}

/* ── Divider ── */
hr { border: none; border-top: 1.5px solid #d4d0c8; margin: 2rem 0; }

/* ── Sidebar title ── */
.sidebar-logo {
    font-family: 'Syne', sans-serif; font-size: 1.1rem; font-weight: 800;
    color: #1a1a1a; letter-spacing: -0.3px; margin-bottom: 1.5rem;
    padding-bottom: 0.8rem; border-bottom: 2px solid #1a1a1a;
}

h2 { font-family: 'Syne', sans-serif !important; font-weight: 700 !important; font-size: 1.1rem !important; color: #1a1a1a !important; }
h1 { font-family: 'Syne', sans-serif !important; font-weight: 800 !important; }
</style>
""", unsafe_allow_html=True)

# ─── PLOTLY THEME ──────────────────────────────────────────────────────────────
PLOT_LAYOUT = dict(
    template="plotly_white",
    font=dict(family="DM Mono, monospace", size=11, color="#1a1a1a"),
    paper_bgcolor="#ffffff",
    plot_bgcolor="#ffffff",
    xaxis=dict(showgrid=True, gridcolor="#f0ede6", linecolor="#d4d0c8", tickfont=dict(size=10)),
    yaxis=dict(showgrid=True, gridcolor="#f0ede6", linecolor="#d4d0c8", tickfont=dict(size=10)),
    legend=dict(
        bgcolor="#ffffff", bordercolor="#d4d0c8", borderwidth=1,
        font=dict(family="DM Mono, monospace", size=10)
    ),
    margin=dict(l=50, r=30, t=40, b=50),
    hoverlabel=dict(
        bgcolor="#1a1a1a", font_color="#f5f5f0",
        font_family="DM Mono, monospace", font_size=11, bordercolor="#1a1a1a"
    )
)

# ─── TABS ──────────────────────────────────────────────────────────────────────
tab_corr, tab_stress, tab_exposure, tab_legenda = st.tabs(
    ["Correlation", "Stress Test", "Exposure", "Legend"]
)

# ─── SIDEBAR ───────────────────────────────────────────────────────────────────
st.sidebar.markdown('<div class="sidebar-logo">Portfolio Analytics</div>', unsafe_allow_html=True)

chart_type = st.sidebar.selectbox(
    "Select chart",
    ["EGQ vs Index and Cash", "E7X vs Funds"]
)

# ─── DATA LOADERS ──────────────────────────────────────────────────────────────
@st.cache_data
def load_corr_data(path):
    df = pd.read_excel(path, sheet_name="Correlation Clean")
    df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0])
    df = df.set_index(df.columns[0]).sort_index()
    return df

@st.cache_data
def load_stress_data(path):
    xls = pd.ExcelFile(path)
    records = []
    for sheet_name in xls.sheet_names:
        if "&&" in sheet_name:
            portfolio, scenario_name = sheet_name.split("&&", 1)
        else:
            portfolio, scenario_name = sheet_name, sheet_name
        df = pd.read_excel(xls, sheet_name=sheet_name)
        df = df.rename(columns={
            df.columns[0]: "Date",
            df.columns[2]: "Scenario",
            df.columns[4]: "StressPnL"
        })
        df["Date"] = pd.to_datetime(df["Date"])
        df["Portfolio"] = portfolio
        df["ScenarioName"] = scenario_name
        records.append(df[["Date", "Scenario", "StressPnL", "Portfolio", "ScenarioName"]])
    return pd.concat(records, ignore_index=True)

@st.cache_data
def load_exposure_data(path):
    df = pd.read_excel(path, sheet_name="MeasuresSeries")
    df = df.rename(columns={
        df.columns[0]: "Date",
        df.columns[3]: "Portfolio",
        df.columns[4]: "Equity Exposure",
        df.columns[5]: "Duration",
        df.columns[6]: "Spread Duration"
    })
    df["Date"] = pd.to_datetime(df["Date"])
    df.columns = df.columns.str.strip()
    return df

@st.cache_data
def load_legenda_sheet(sheet_name, usecols):
    return pd.read_excel("Legenda.xlsx", sheet_name=sheet_name, usecols=usecols)

corrEGQ = load_corr_data("corrEGQ.xlsx")
corrE7X = load_corr_data("corrE7X.xlsx")

stress_path  = "stress_test_totEGQ.xlsx" if chart_type == "EGQ vs Index and Cash" else "stress_test_totE7X.xlsx"
stress_data  = load_stress_data(stress_path)
stress_title = "EGQ Flexible Multistrategy" if chart_type == "EGQ vs Index and Cash" else "E7X Dynamic Asset Allocation"

exposure_data = load_exposure_data("E7X_Exposure.xlsx")

palette = qualitative.Plotly

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — CORRELATION
# ══════════════════════════════════════════════════════════════════════════════
with tab_corr:
    df = (corrEGQ if chart_type == "EGQ vs Index and Cash" else corrE7X).copy()
    chart_title = ("EGQ Flexible Multistrategy vs Index and Cash"
                   if chart_type == "EGQ vs Index and Cash"
                   else "E7X Dynamic Asset Allocation vs Funds")
    reference_asset = "EGQ" if chart_type == "EGQ vs Index and Cash" else "E7X"

    st.markdown(f'<div class="page-title">{chart_title}</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Rolling Correlation Analysis</div>', unsafe_allow_html=True)

    # Date range
    st.sidebar.markdown('<div style="font-family:DM Mono,monospace;font-size:0.68rem;text-transform:uppercase;letter-spacing:0.1em;color:#888880;margin-top:1rem;">Date Range — Correlation</div>', unsafe_allow_html=True)
    start_date, end_date = st.sidebar.date_input(
        "Select start and end date",
        value=(df.index.min().date(), df.index.max().date()),
        min_value=df.index.min().date(),
        max_value=df.index.max().date()
    )
    df = df.loc[pd.to_datetime(start_date):pd.to_datetime(end_date)]

    # Series selector
    st.sidebar.markdown('<div style="font-family:DM Mono,monospace;font-size:0.68rem;text-transform:uppercase;letter-spacing:0.1em;color:#888880;margin-top:1rem;">Series — Correlation</div>', unsafe_allow_html=True)
    selected_series = st.sidebar.multiselect(
        "Select series",
        options=df.columns.tolist(),
        default=df.columns.tolist()
    )
    if not selected_series:
        st.warning("Please select at least one series.")
        st.stop()

    color_map = {s: palette[i % len(palette)] for i, s in enumerate(selected_series)}

    # Stat boxes
    mean_vals = df[selected_series].mean() * 100
    st.markdown(f"""
    <div class="stat-row">
        <div class="stat-box">
            <div class="sv">{len(selected_series)}</div>
            <div class="sk">Series selected</div>
        </div>
        <div class="stat-box">
            <div class="sv">{start_date.strftime('%d/%m/%y')} → {end_date.strftime('%d/%m/%y')}</div>
            <div class="sk">Period</div>
        </div>
        <div class="stat-box">
            <div class="sv">{mean_vals.mean():.1f}%</div>
            <div class="sk">Avg correlation</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Time series
    st.markdown('<div class="section-header">Correlation Time Series</div>', unsafe_allow_html=True)
    fig_ts = go.Figure()
    for col in selected_series:
        fig_ts.add_trace(go.Scatter(
            x=df.index, y=df[col] * 100, mode="lines", name=col,
            line=dict(color=color_map[col], width=1.8),
            hovertemplate="%{y:.2f}%<extra></extra>"
        ))
    fig_ts.update_layout(
        **PLOT_LAYOUT, height=500, hovermode="x unified",
        yaxis=dict(**PLOT_LAYOUT["yaxis"], ticksuffix="%"),
        xaxis_title="Date", yaxis_title="Correlation (%)"
    )
    st.plotly_chart(fig_ts, use_container_width=True)

    df_download = df[selected_series] * 100
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_download.to_excel(writer, sheet_name="Time Series Data")
    st.download_button(
        "📥 Download time series data as Excel", data=output.getvalue(),
        file_name="time_series_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="download_time_series"
    )

    # Radar
    st.markdown('<div class="section-header">Correlation Radar</div>', unsafe_allow_html=True)
    snapshot_date = df.index.max()
    snapshot  = df.loc[snapshot_date, selected_series]
    mean_corr = df[selected_series].mean()

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=snapshot.values * 100, theta=snapshot.index,
        name=f"End date ({snapshot_date.date()})", line=dict(width=2.5, color="#1a1a1a")
    ))
    fig_radar.add_trace(go.Scatterpolar(
        r=mean_corr.values * 100, theta=mean_corr.index,
        name="Period mean", line=dict(dash="dot", width=1.8, color="#888880")
    ))
    fig_radar.update_layout(
        **{k: v for k, v in PLOT_LAYOUT.items() if k not in ('xaxis', 'yaxis')},
        polar=dict(radialaxis=dict(visible=True, range=[-100, 100], ticksuffix="%",
                                   gridcolor="#d4d0c8", linecolor="#d4d0c8")),
        height=580
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    # Summary stats
    st.markdown('<div class="section-header">Summary Statistics</div>', unsafe_allow_html=True)
    sheet_main   = "EGQ" if chart_type == "EGQ vs Index and Cash" else "E7X"
    legenda_main = load_legenda_sheet(sheet_name=sheet_main, usecols="A:C")
    ticker_to_name = dict(zip(legenda_main["Ticker"], legenda_main["Name"]))

    stats_df = pd.DataFrame(index=selected_series)
    stats_df.insert(0, "Name", [ticker_to_name.get(t, "") for t in selected_series])
    stats_df["Mean (%)"] = df[selected_series].mean() * 100
    stats_df["Min (%)"]  = df[selected_series].min()  * 100
    stats_df["Min Date"] = [df[col][df[col] == df[col].min()].index.max() for col in selected_series]
    stats_df["Max (%)"]  = df[selected_series].max()  * 100
    stats_df["Max Date"] = [df[col][df[col] == df[col].max()].index.max() for col in selected_series]
    stats_df["Min Date"] = pd.to_datetime(stats_df["Min Date"]).dt.strftime("%d/%m/%Y")
    stats_df["Max Date"] = pd.to_datetime(stats_df["Max Date"]).dt.strftime("%d/%m/%Y")

    st.dataframe(
        stats_df.style.format({"Mean (%)": "{:.2f}%", "Min (%)": "{:.2f}%", "Max (%)": "{:.2f}%"}),
        use_container_width=True
    )

    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        stats_df.to_excel(writer, sheet_name="Summary Stats")
    st.download_button(
        "📥 Download summary statistics as Excel", data=output.getvalue(),
        file_name="summary_statistics.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="download_summary_stats"
    )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — STRESS TEST
# ══════════════════════════════════════════════════════════════════════════════
with tab_stress:
    st.markdown(f'<div class="page-title">{stress_title}</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Stress Test PnL Analysis</div>', unsafe_allow_html=True)

    # Date selector
    st.sidebar.markdown('<div style="font-family:DM Mono,monospace;font-size:0.68rem;text-transform:uppercase;letter-spacing:0.1em;color:#888880;margin-top:1rem;">Date — Stress Test</div>', unsafe_allow_html=True)
    all_dates    = stress_data["Date"].dropna().sort_values().unique()
    date_options = [d.strftime("%Y/%m/%d") for d in all_dates]
    selected_date_str = st.sidebar.selectbox("Select date", date_options, key="stress_date")
    selected_date = pd.to_datetime(selected_date_str, format="%Y/%m/%d")
    df_filtered   = stress_data[stress_data["Date"] == selected_date]

    if df_filtered.empty:
        st.warning("No data available for the selected date.")
        st.stop()

    # Portfolio selector
    st.sidebar.markdown('<div style="font-family:DM Mono,monospace;font-size:0.68rem;text-transform:uppercase;letter-spacing:0.1em;color:#888880;margin-top:1rem;">Series — Stress Test</div>', unsafe_allow_html=True)
    available_portfolios = df_filtered["Portfolio"].dropna().sort_values().unique().tolist()
    selected_portfolios  = st.sidebar.multiselect("Select series", options=available_portfolios, default=available_portfolios)
    if not selected_portfolios:
        st.warning("Please select at least one portfolio.")
        st.stop()
    df_filtered = df_filtered[df_filtered["Portfolio"].isin(selected_portfolios)]

    # Scenario selector
    st.sidebar.markdown('<div style="font-family:DM Mono,monospace;font-size:0.68rem;text-transform:uppercase;letter-spacing:0.1em;color:#888880;margin-top:1rem;">Scenarios — Stress Test</div>', unsafe_allow_html=True)
    available_scenarios = df_filtered["ScenarioName"].dropna().sort_values().unique().tolist()
    selected_scenarios  = st.sidebar.multiselect("Select stress scenarios", options=available_scenarios, default=available_scenarios)
    if not selected_scenarios:
        st.warning("Please select at least one stress scenario.")
        st.stop()
    df_filtered = df_filtered[df_filtered["ScenarioName"].isin(selected_scenarios)]

    df_filtered["ScenarioName"] = pd.Categorical(df_filtered["ScenarioName"], categories=selected_scenarios, ordered=True)
    df_filtered["Portfolio"]    = pd.Categorical(df_filtered["Portfolio"],    categories=selected_portfolios, ordered=True)

    # Stat boxes
    n_pos_stress = int((df_filtered["StressPnL"] > 0).sum())
    n_neg_stress = int((df_filtered["StressPnL"] < 0).sum())
    st.markdown(f"""
    <div class="stat-row">
        <div class="stat-box"><div class="sv">{len(selected_scenarios)}</div><div class="sk">Scenarios</div></div>
        <div class="stat-box"><div class="sv">{len(selected_portfolios)}</div><div class="sk">Portfolios</div></div>
        <div class="stat-box"><div class="sv" style="color:#0a7c45">▲ {n_pos_stress}</div><div class="sk">Positive PnL</div></div>
        <div class="stat-box"><div class="sv" style="color:#c0392b">▼ {n_neg_stress}</div><div class="sk">Negative PnL</div></div>
    </div>
    """, unsafe_allow_html=True)

    # Grouped bar
    st.markdown('<div class="section-header">Stress Test PnL</div>', unsafe_allow_html=True)
    fig_bar = go.Figure()
    for i, portfolio in enumerate(selected_portfolios):
        df_port = df_filtered[df_filtered["Portfolio"] == portfolio]
        if df_port.empty:
            continue
        fig_bar.add_trace(go.Bar(
            x=df_port["ScenarioName"], y=df_port["StressPnL"],
            name=portfolio, marker_color=palette[i % len(palette)],
            text=df_port["StressPnL"], textposition="auto",
            marker_line_width=0
        ))
    fig_bar.update_layout(
        **PLOT_LAYOUT, barmode="group", height=520,
        xaxis_title="Scenario", yaxis_title="Stress PnL (bps)"
    )
    fig_bar.add_hline(y=0, line_color="#1a1a1a", line_width=1, line_dash="dot")
    st.plotly_chart(fig_bar, use_container_width=True)

    df_dl = df_filtered[df_filtered["Portfolio"].isin(selected_portfolios)][["Portfolio", "ScenarioName", "StressPnL"]]
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_dl.to_excel(writer, sheet_name="Stress Test PnL", index=False)
    st.download_button(
        "📥 Download Stress PnL data as Excel", data=output.getvalue(),
        file_name="stress_test_pnl.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="download_stress_pnl"
    )

    # Comparison Analysis
    st.markdown("---")
    st.markdown('<div class="section-header">Comparison Analysis — Portfolio vs Bucket</div>', unsafe_allow_html=True)

    default_portfolio = "EGQ" if chart_type == "EGQ vs Index and Cash" else "E7X"
    default_index = selected_portfolios.index(default_portfolio) if default_portfolio in selected_portfolios else 0
    selected_portfolio = st.selectbox("Analysis portfolio", selected_portfolios, index=default_index, key="stress_analysis_port")

    df_analysis = df_filtered[df_filtered["Portfolio"] == selected_portfolio][["ScenarioName", "StressPnL"]]
    df_bucket   = df_filtered[df_filtered["Portfolio"] != selected_portfolio][["ScenarioName", "StressPnL"]]

    if df_bucket.empty:
        st.markdown('<div class="info-box">⚠️ Not enough portfolios selected for bucket comparison.</div>', unsafe_allow_html=True)
    else:
        df_bucket_stats = (
            df_bucket.groupby("ScenarioName", as_index=False)
            .agg(bucket_median=("StressPnL", "median"),
                 q25=("StressPnL", lambda x: x.quantile(0.25)),
                 q75=("StressPnL", lambda x: x.quantile(0.75)))
        )
        df_plot = df_analysis.merge(df_bucket_stats, on="ScenarioName", how="inner")

        fig = go.Figure()
        for _, r in df_plot.iterrows():
            fig.add_trace(go.Scatter(
                x=[r["q25"], r["q75"]], y=[r["ScenarioName"], r["ScenarioName"]],
                mode="lines", line=dict(width=14, color="rgba(255,0,0,0.25)"),
                showlegend=False, hoverinfo="skip"
            ))
        fig.add_trace(go.Scatter(
            x=df_plot["bucket_median"], y=df_plot["ScenarioName"],
            mode="markers", marker=dict(size=9, color="red"),
            name="Bucket median"
        ))
        fig.add_trace(go.Scatter(
            x=df_plot["StressPnL"], y=df_plot["ScenarioName"],
            mode="markers", marker=dict(size=14, symbol="star", color="orange"),
            name=selected_portfolio
        ))
        fig.update_layout(**PLOT_LAYOUT, height=600, hovermode="y",
                          xaxis_title="Stress PnL (bps)", yaxis_title="Scenario")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown(
            """
            <div style="display: flex; align-items: center; font-family: 'DM Mono', monospace; font-size: 0.68rem; color: #888880;">
                <span style="margin-right: 4px;">Note: the shaded areas</span>
                <div style="width: 20px; height: 14px; background-color: rgba(255,0,0,0.25); margin: 0 4px; border: 1px solid rgba(0,0,0,0.1);"></div>
                <span>represent the dispersion between the 25th and 75th percentile of the Bucket.</span>
            </div>
            """,
            unsafe_allow_html=True
        )

        df_dl2 = df_plot.rename(columns={"bucket_median": "Bucket Portfolio Median",
                                          "q25": "25% Quantile", "q75": "75% Quantile",
                                          "StressPnL": selected_portfolio})
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df_dl2.to_excel(writer, sheet_name="Portfolio vs Bucket", index=False)
        st.download_button(
            f"📥 Download {selected_portfolio} vs Bucket data as Excel", data=output.getvalue(),
            file_name=f"{selected_portfolio}_vs_bucket.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key=f"download_{selected_portfolio}_vs_bucket"
        )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — EXPOSURE
# ══════════════════════════════════════════════════════════════════════════════
with tab_exposure:
    if chart_type == "E7X vs Funds":
        st.markdown('<div class="page-title">E7X Dynamic Asset Allocation vs Funds</div>', unsafe_allow_html=True)
        st.markdown('<div class="page-subtitle">Portfolio Exposure Analysis</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="page-title">EGQ Flexible Multistrategy vs Index and Cash</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">ℹ️ Analysis not performed for this subset.</div>', unsafe_allow_html=True)

    if chart_type == "E7X vs Funds":
        st.sidebar.markdown('<div style="font-family:DM Mono,monospace;font-size:0.68rem;text-transform:uppercase;letter-spacing:0.1em;color:#888880;margin-top:1rem;">Date — Exposure</div>', unsafe_allow_html=True)
        all_dates_exp  = exposure_data["Date"].dropna().sort_values().unique()
        date_opts_exp  = [d.strftime("%Y/%m/%d") for d in all_dates_exp]
        sel_date_exp_s = st.sidebar.selectbox("Select date", date_opts_exp, index=len(date_opts_exp)-1, key="exp_date")
        sel_date_exp   = pd.to_datetime(sel_date_exp_s, format="%Y/%m/%d")
        df_exp_filt    = exposure_data[exposure_data["Date"] == sel_date_exp]

        if df_exp_filt.empty:
            st.warning("No data available for the selected date.")
            st.stop()

        st.sidebar.markdown('<div style="font-family:DM Mono,monospace;font-size:0.68rem;text-transform:uppercase;letter-spacing:0.1em;color:#888880;margin-top:1rem;">Series — Exposure</div>', unsafe_allow_html=True)
        avail_ports_exp = df_exp_filt["Portfolio"].dropna().sort_values().unique().tolist()
        sel_ports_exp   = st.sidebar.multiselect("Select portfolios", options=avail_ports_exp, default=avail_ports_exp)
        if not sel_ports_exp:
            st.warning("Please select at least one portfolio.")
            st.stop()
        df_exp_filt = df_exp_filt[df_exp_filt["Portfolio"].isin(sel_ports_exp)]

        metrics = ["Equity Exposure", "Duration", "Spread Duration"]

        # Stat boxes
        eq_mean  = df_exp_filt["Equity Exposure"].mean()
        dur_mean = df_exp_filt["Duration"].mean()
        st.markdown(f"""
        <div class="stat-row">
            <div class="stat-box"><div class="sv">{len(sel_ports_exp)}</div><div class="sk">Portfolios</div></div>
            <div class="stat-box"><div class="sv">{eq_mean:.1f}</div><div class="sk">Avg Equity Exp.</div></div>
            <div class="stat-box"><div class="sv">{dur_mean:.1f}</div><div class="sk">Avg Duration</div></div>
        </div>
        """, unsafe_allow_html=True)

        # Grouped bar
        st.markdown('<div class="section-header">Exposure by Portfolio</div>', unsafe_allow_html=True)
        df_plot_exp = df_exp_filt.melt(id_vars=["Portfolio"], value_vars=metrics, var_name="Metric", value_name="Value")
        fig_exp = go.Figure()
        for i, portfolio in enumerate(sel_ports_exp):
            df_port = df_plot_exp[df_plot_exp["Portfolio"] == portfolio]
            fig_exp.add_trace(go.Bar(
                x=df_port["Metric"], y=df_port["Value"], name=portfolio,
                marker_color=palette[i % len(palette)],
                text=df_port["Value"].round(1), textposition="auto",
                texttemplate="%{text:.1f}", marker_line_width=0
            ))
        fig_exp.update_layout(**PLOT_LAYOUT, barmode="group", height=500,
                              xaxis_title="Metric", yaxis_title="Value")
        st.plotly_chart(fig_exp, use_container_width=True)

        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df_exp_filt.to_excel(writer, sheet_name="Exposure Data", index=False)
        st.download_button(
            "📥 Download Exposure data as Excel", data=output.getvalue(),
            file_name="exposure_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="download_exposure"
        )

        # Comparison Analysis
        st.markdown("---")
        st.markdown('<div class="section-header">Comparison Analysis — Portfolio vs Bucket</div>', unsafe_allow_html=True)

        default_portfolio_exp = "E7X"
        default_index_exp = sel_ports_exp.index(default_portfolio_exp) if default_portfolio_exp in sel_ports_exp else 0
        sel_port_exp = st.selectbox("Analysis portfolio", sel_ports_exp, index=default_index_exp, key="exp_analysis_port")

        df_analysis_exp = df_exp_filt[df_exp_filt["Portfolio"] == sel_port_exp][["Portfolio"] + metrics]
        df_bucket_exp   = df_exp_filt[df_exp_filt["Portfolio"] != sel_port_exp][["Portfolio"] + metrics]

        if df_bucket_exp.empty:
            st.markdown('<div class="info-box">⚠️ Not enough portfolios selected for bucket comparison.</div>', unsafe_allow_html=True)
        else:
            df_bucket_stats_exp = df_bucket_exp[metrics].agg(
                ["median", lambda x: x.quantile(0.25), lambda x: x.quantile(0.75)]
            ).T
            df_bucket_stats_exp.columns = ["bucket_median", "q25", "q75"]

            df_plot_comp = df_analysis_exp.melt(id_vars=["Portfolio"], value_vars=metrics, var_name="Metric", value_name="Value")
            df_plot_comp = df_plot_comp.merge(
                df_bucket_stats_exp.reset_index().rename(columns={"index": "Metric"}), on="Metric", how="left"
            )

            fig_comp = go.Figure()
            for _, r in df_plot_comp.iterrows():
                fig_comp.add_trace(go.Scatter(
                    x=[r["q25"], r["q75"]], y=[r["Metric"], r["Metric"]],
                    mode="lines", line=dict(width=14, color="rgba(0,0,255,0.25)"),
                    showlegend=False, hoverinfo="skip"
                ))
            fig_comp.add_trace(go.Scatter(
                x=df_plot_comp["bucket_median"], y=df_plot_comp["Metric"],
                mode="markers", marker=dict(size=9, color="blue"),
                name="Bucket median"
            ))
            fig_comp.add_trace(go.Scatter(
                x=df_plot_comp["Value"], y=df_plot_comp["Metric"],
                mode="markers", marker=dict(size=14, symbol="star", color="orange"),
                name=sel_port_exp
            ))
            fig_comp.update_layout(**PLOT_LAYOUT, height=600, hovermode="y",
                                   xaxis_title="Exposure Value", yaxis_title="Metric")
            st.plotly_chart(fig_comp, use_container_width=True)

            st.markdown(
                """
                <div style="display: flex; align-items: center; font-family: 'DM Mono', monospace; font-size: 0.68rem; color: #888880;">
                    <span style="margin-right: 4px;">Note: the shaded areas</span>
                    <div style="width: 20px; height: 14px; background-color: rgba(0,0,255,0.25); margin: 0 4px; border: 1px solid rgba(0,0,0,0.1);"></div>
                    <span>represent the dispersion between the 25th and 75th percentile of the Bucket.</span>
                </div>
                """,
                unsafe_allow_html=True
            )

            df_dl_comp = df_plot_comp.rename(columns={
                "bucket_median": "Bucket Portfolio Median", "q25": "25% Quantile",
                "q75": "75% Quantile", "Value": sel_port_exp
            })
            output = BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                df_dl_comp.to_excel(writer, sheet_name="Exposure Comparison", index=False)
            st.download_button(
                f"📥 Download {sel_port_exp} vs Bucket Exposure data as Excel", data=output.getvalue(),
                file_name=f"{sel_port_exp}_vs_bucket_exposure.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key=f"download_{sel_port_exp}_vs_bucket_exposure"
            )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — LEGEND
# ══════════════════════════════════════════════════════════════════════════════
with tab_legenda:
    legend_title = ("EGQ Flexible Multistrategy vs Index and Cash"
                    if chart_type == "EGQ vs Index and Cash"
                    else "E7X Dynamic Asset Allocation vs Funds")
    st.markdown(f'<div class="page-title">{legend_title}</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Reference · Tickers & Scenarios</div>', unsafe_allow_html=True)

    sheet_main   = "EGQ" if chart_type == "EGQ vs Index and Cash" else "E7X"
    legenda_main = load_legenda_sheet(sheet_name=sheet_main, usecols="A:C")

    st.markdown('<div class="section-header">Series</div>', unsafe_allow_html=True)
    st.dataframe(legenda_main, use_container_width=True, hide_index=True)

    st.markdown("---")

    legenda_scenari = load_legenda_sheet(sheet_name="Scenari", usecols="A:C")
    st.markdown('<div class="section-header">Stress Test Scenarios</div>', unsafe_allow_html=True)
    st.dataframe(legenda_scenari, use_container_width=True, hide_index=True)
