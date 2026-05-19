"""
STP & Human-Touch Dashboard
SpareBank 1 Forvaltning — Fund Settlements

Tab 1: Visual overview (reads from session state)
Tab 2: Data + label inputs (writes to session state)
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import date, timedelta

# ---------- BRAND ----------
VANN    = "#005AA4"   # primary blue
FJELL   = "#002776"   # dark blue
FROST   = "#7EB5D2"   # light blue
SYRIN   = "#D3D3EA"   # lilac
SAND    = "#F8E9DD"   # warm neutral
NORDLYS = "#33AF85"   # green (good)
SOL     = "#DC8000"   # amber
BAER    = "#E44244"   # red (alert)
NATT    = "#001032"   # near-black
KOKS    = "#323232"   # text grey
GRAA    = "#ADADAD"

st.set_page_config(
    page_title="STP & Human Touches — SB1 Forvaltning",
    page_icon="📊",
    layout="wide",
)

# ---------- GLOBAL CSS (brand alignment) ----------
st.markdown(f"""
<style>
    .stApp {{ background-color: #FFFFFF; }}
    h1, h2, h3 {{ color: {FJELL}; font-weight: 600; letter-spacing: -0.01em; }}
    .stMetric {{
        background-color: {SAND};
        padding: 16px 20px;
        border-radius: 16px;
        border: 1px solid {SYRIN};
    }}
    [data-testid="stMetricValue"] {{ color: {VANN}; font-weight: 700; }}
    [data-testid="stMetricLabel"] {{ color: {KOKS}; }}
    .stTabs [data-baseweb="tab-list"] {{ gap: 8px; }}
    .stTabs [data-baseweb="tab"] {{
        background-color: {SAND};
        border-radius: 12px 12px 0 0;
        padding: 10px 20px;
        color: {FJELL};
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {VANN} !important;
        color: white !important;
    }}
    .block-container {{ padding-top: 2rem; }}
</style>
""", unsafe_allow_html=True)


# ---------- SEED DATA ----------
def seed_transactions():
    """Realistic-looking starter data so Tab 1 isn't empty on first load."""
    rng = pd.date_range(end=date.today(), periods=13, freq="W-FRI")
    rows = []
    counterparties = ["Custodian A", "Custodian B", "TA Nordic", "TA Europe",
                      "Distributor X", "Distributor Y"]
    instruments    = ["UCITS Equity", "UCITS Bond", "AIF", "ETF", "Money Market"]
    break_reasons  = ["Missing SSI", "Late confirmation", "Settlement mismatch",
                      "Cash funding", "Reference data", "Manual booking",
                      "Counterparty error", "Other"]
    import random
    random.seed(42)
    for w in rng:
        for cp in counterparties:
            for inst in instruments:
                n = random.randint(20, 90)
                # base STP rate varies by cp and instrument
                base = 0.96 if "Custodian" in cp else 0.92
                if inst == "AIF":      base -= 0.05
                if inst == "ETF":      base += 0.02
                if cp == "TA Europe":  base -= 0.04
                stp_n = int(n * max(0.7, min(0.995, base + random.uniform(-0.04, 0.04))))
                touches = (n - stp_n) + random.randint(0, 3)
                reason  = random.choice(break_reasons) if (n - stp_n) > 0 else None
                rows.append({
                    "week_end":      w.date(),
                    "counterparty":  cp,
                    "instrument":    inst,
                    "transactions":  n,
                    "stp":           stp_n,
                    "manual_touches": touches,
                    "top_break_reason": reason or "—",
                })
    return pd.DataFrame(rows)


def seed_labels():
    """Default labels — editable in Tab 2."""
    return {
        "dashboard_title":   "STP & Fund Settlement Dashboard",
        "subtitle":          "SpareBank 1 Forvaltning — Operations & Administration",
        "kpi_overall":       "Overall STP-Rate",
        "kpi_touches":       "Manual Touches (period)",
        "kpi_volume":        "Transactions (period)",
        "kpi_touches_per":   "Touches per 100 trades",
        "trend_title":       "STP-Rate Trend (weekly)",
        "waterfall_title":   "Where STP is Lost — by Break Reason",
        "pareto_title":      "Pareto: Break Causes",
        "heatmap_title":     "STP-Rate Heatmap — Counterparty × Instrument",
        "touches_title":     "Manual Touches by Counterparty",
        "funnel_title":      "Order → Settled Funnel",
        "sla_lower":         0.95,
        "sla_upper":         0.98,
    }


# ---------- SESSION STATE INIT ----------
if "tx_data" not in st.session_state:
    st.session_state.tx_data = seed_transactions()
if "labels" not in st.session_state:
    st.session_state.labels = seed_labels()


# ---------- HELPERS ----------
def kpi_card(label, value, delta=None, delta_color="normal"):
    st.metric(label=label, value=value, delta=delta, delta_color=delta_color)


def compute_aggregates(df):
    total_tx       = int(df["transactions"].sum())
    total_stp      = int(df["stp"].sum())
    total_touches  = int(df["manual_touches"].sum())
    stp_rate       = total_stp / total_tx if total_tx else 0
    touches_per100 = (total_touches / total_tx * 100) if total_tx else 0
    return total_tx, total_stp, total_touches, stp_rate, touches_per100


# ============================================================
# LAYOUT
# ============================================================
labels = st.session_state.labels

st.markdown(f"<h1 style='margin-bottom:0'>{labels['dashboard_title']}</h1>",
            unsafe_allow_html=True)
st.markdown(f"<p style='color:{KOKS};margin-top:0;font-size:1.05rem'>"
            f"{labels['subtitle']}</p>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📊  Overview", "⚙️  Data & Labels"])

# ============================================================
# TAB 1 — VISUAL OVERVIEW
# ============================================================
with tab1:
    df = st.session_state.tx_data.copy()

    if df.empty:
        st.warning("No data yet. Go to **Data & Labels** tab to add transactions.")
        st.stop()

    # ----- Slicers -----
    st.markdown("##### Filters")
    f1, f2, f3 = st.columns([2, 2, 2])
    with f1:
        cps = st.multiselect("Counterparty", sorted(df["counterparty"].unique()),
                             default=sorted(df["counterparty"].unique()))
    with f2:
        insts = st.multiselect("Instrument", sorted(df["instrument"].unique()),
                               default=sorted(df["instrument"].unique()))
    with f3:
        weeks = sorted(df["week_end"].unique())
        date_range = st.select_slider("Period (week ending)",
                                       options=weeks,
                                       value=(weeks[0], weeks[-1]))

    mask = (df["counterparty"].isin(cps)
            & df["instrument"].isin(insts)
            & (df["week_end"] >= date_range[0])
            & (df["week_end"] <= date_range[1]))
    f = df[mask]

    if f.empty:
        st.info("No data matches the current filters.")
        st.stop()

    # ----- KPI ROW -----
    st.markdown("### Key indicators")
    total_tx, total_stp, total_touches, stp_rate, touches_per100 = compute_aggregates(f)

    # delta vs first half of selected period
    half_point = date_range[0] + (date_range[1] - date_range[0]) / 2
    prev = f[f["week_end"] <= half_point]
    curr = f[f["week_end"] >  half_point]
    if not prev.empty and not curr.empty:
        prev_rate = prev["stp"].sum() / prev["transactions"].sum()
        curr_rate = curr["stp"].sum() / curr["transactions"].sum()
        rate_delta = f"{(curr_rate - prev_rate)*100:+.2f} pp"
        prev_touch = prev["manual_touches"].sum()
        curr_touch = curr["manual_touches"].sum()
        touch_delta = f"{curr_touch - prev_touch:+,}"
    else:
        rate_delta = touch_delta = None

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        kpi_card(labels["kpi_overall"], f"{stp_rate*100:.1f} %",
                 delta=rate_delta,
                 delta_color="normal" if (rate_delta and "+" in rate_delta) else "inverse")
    with k2:
        kpi_card(labels["kpi_volume"], f"{total_tx:,}")
    with k3:
        kpi_card(labels["kpi_touches"], f"{total_touches:,}",
                 delta=touch_delta, delta_color="inverse")
    with k4:
        kpi_card(labels["kpi_touches_per"], f"{touches_per100:.1f}")

    st.markdown("---")

    # ----- ROW 1: Trend + Waterfall -----
    c1, c2 = st.columns([1.2, 1])

    with c1:
        st.markdown(f"#### {labels['trend_title']}")
        trend = (f.groupby("week_end")
                  .agg(tx=("transactions", "sum"), stp=("stp", "sum"))
                  .assign(rate=lambda x: x["stp"] / x["tx"])
                  .reset_index())

        fig = go.Figure()
        # SLA band
        fig.add_hrect(y0=labels["sla_lower"]*100, y1=labels["sla_upper"]*100,
                      fillcolor=FROST, opacity=0.25, layer="below", line_width=0,
                      annotation_text="SLA band", annotation_position="top left",
                      annotation_font_color=FJELL)
        # Trend line
        colors = [BAER if r < labels["sla_lower"] else NORDLYS if r >= labels["sla_upper"]
                  else VANN for r in trend["rate"]]
        fig.add_trace(go.Scatter(
            x=trend["week_end"], y=trend["rate"]*100,
            mode="lines+markers",
            line=dict(color=VANN, width=3),
            marker=dict(size=10, color=colors, line=dict(color=FJELL, width=1)),
            name="STP-Rate",
            hovertemplate="Week %{x}<br>STP-Rate: %{y:.2f}%<extra></extra>",
        ))
        fig.update_layout(
            height=340, margin=dict(l=10, r=10, t=10, b=10),
            yaxis=dict(title="STP-Rate (%)", range=[max(70, trend['rate'].min()*100-3), 100],
                       gridcolor="#EFEFEF"),
            xaxis=dict(title=None, gridcolor="#FAFAFA"),
            plot_bgcolor="white", paper_bgcolor="white",
            font=dict(color=KOKS),
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown(f"#### {labels['waterfall_title']}")
        # Build waterfall: total tx -> minus each reason's losses -> STP
        breaks = (f[f["top_break_reason"] != "—"]
                  .assign(non_stp=lambda d: d["transactions"] - d["stp"])
                  .groupby("top_break_reason")["non_stp"].sum()
                  .sort_values(ascending=False))
        # Top 5 reasons, rest as "Other"
        top  = breaks.head(5)
        rest = breaks.iloc[5:].sum() if len(breaks) > 5 else 0
        items = list(top.items())
        if rest > 0:
            items.append(("Other reasons", rest))

        x_labels = ["Total transactions"] + [r for r, _ in items] + ["STP transactions"]
        y_vals   = [total_tx] + [-int(v) for _, v in items] + [total_stp]
        measures = ["absolute"] + ["relative"] * len(items) + ["total"]

        fig = go.Figure(go.Waterfall(
            x=x_labels, y=y_vals, measure=measures,
            connector=dict(line=dict(color=GRAA)),
            increasing=dict(marker=dict(color=NORDLYS)),
            decreasing=dict(marker=dict(color=BAER)),
            totals=dict(marker=dict(color=VANN)),
            textposition="outside",
            text=[f"{v:,}" if v != 0 else "" for v in y_vals],
        ))
        fig.update_layout(
            height=340, margin=dict(l=10, r=10, t=10, b=10),
            plot_bgcolor="white", paper_bgcolor="white",
            yaxis=dict(gridcolor="#EFEFEF"), xaxis=dict(tickangle=-20),
            font=dict(color=KOKS),
        )
        st.plotly_chart(fig, use_container_width=True)

    # ----- ROW 2: Heatmap + Pareto -----
    c3, c4 = st.columns([1.2, 1])

    with c3:
        st.markdown(f"#### {labels['heatmap_title']}")
        pivot = (f.groupby(["counterparty", "instrument"])
                  .agg(tx=("transactions", "sum"), stp=("stp", "sum"))
                  .assign(rate=lambda x: x["stp"] / x["tx"] * 100)
                  .reset_index()
                  .pivot(index="counterparty", columns="instrument", values="rate"))

        fig = go.Figure(go.Heatmap(
            z=pivot.values, x=pivot.columns, y=pivot.index,
            colorscale=[[0, BAER], [0.5, SOL], [0.8, FROST], [1.0, VANN]],
            zmin=80, zmax=100,
            text=[[f"{v:.1f}%" if pd.notna(v) else "" for v in row] for row in pivot.values],
            texttemplate="%{text}", textfont=dict(color="white", size=12),
            colorbar=dict(title="STP-Rate %"),
            hovertemplate="%{y} × %{x}<br>STP-Rate: %{z:.2f}%<extra></extra>",
        ))
        fig.update_layout(
            height=360, margin=dict(l=10, r=10, t=10, b=10),
            plot_bgcolor="white", paper_bgcolor="white",
            font=dict(color=KOKS),
        )
        st.plotly_chart(fig, use_container_width=True)

    with c4:
        st.markdown(f"#### {labels['pareto_title']}")
        pareto = (f[f["top_break_reason"] != "—"]
                  .assign(non_stp=lambda d: d["transactions"] - d["stp"])
                  .groupby("top_break_reason")["non_stp"].sum()
                  .sort_values(ascending=False)
                  .reset_index())
        pareto["cum_pct"] = pareto["non_stp"].cumsum() / pareto["non_stp"].sum() * 100

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=pareto["top_break_reason"], y=pareto["non_stp"],
            marker=dict(color=VANN), name="Breaks",
            hovertemplate="%{x}<br>Breaks: %{y:,}<extra></extra>",
        ))
        fig.add_trace(go.Scatter(
            x=pareto["top_break_reason"], y=pareto["cum_pct"],
            mode="lines+markers", name="Cumulative %",
            line=dict(color=BAER, width=2), marker=dict(size=8),
            yaxis="y2",
            hovertemplate="%{x}<br>Cumulative: %{y:.1f}%<extra></extra>",
        ))
        fig.add_hline(y=80, line=dict(color=GRAA, dash="dash"), yref="y2",
                      annotation_text="80%", annotation_position="right")
        fig.update_layout(
            height=360, margin=dict(l=10, r=10, t=10, b=10),
            yaxis=dict(title="Breaks", gridcolor="#EFEFEF"),
            yaxis2=dict(title="Cumulative %", overlaying="y", side="right",
                        range=[0, 105], showgrid=False),
            xaxis=dict(tickangle=-25),
            plot_bgcolor="white", paper_bgcolor="white",
            font=dict(color=KOKS),
            legend=dict(orientation="h", y=1.1),
        )
        st.plotly_chart(fig, use_container_width=True)

    # ----- ROW 3: Manual touches + Funnel -----
    c5, c6 = st.columns([1.2, 1])

    with c5:
        st.markdown(f"#### {labels['touches_title']}")
        touches_by_cp = (f.groupby("counterparty")
                          .agg(touches=("manual_touches", "sum"),
                               tx=("transactions", "sum"))
                          .assign(per100=lambda x: x["touches"] / x["tx"] * 100)
                          .reset_index()
                          .sort_values("touches", ascending=True))
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=touches_by_cp["counterparty"], x=touches_by_cp["touches"],
            orientation="h",
            marker=dict(color=FJELL),
            text=[f"{t:,} ({p:.1f}/100)" for t, p in
                  zip(touches_by_cp["touches"], touches_by_cp["per100"])],
            textposition="outside",
            hovertemplate="%{y}<br>Touches: %{x:,}<extra></extra>",
        ))
        fig.update_layout(
            height=360, margin=dict(l=10, r=80, t=10, b=10),
            xaxis=dict(title="Manual touches", gridcolor="#EFEFEF"),
            plot_bgcolor="white", paper_bgcolor="white",
            font=dict(color=KOKS),
        )
        st.plotly_chart(fig, use_container_width=True)

    with c6:
        st.markdown(f"#### {labels['funnel_title']}")
        # Synthetic funnel from the data — illustrative drop-off per stage
        order      = total_tx
        matched    = int(total_tx * 0.985)
        instructed = int(total_tx * 0.972)
        settled    = total_stp
        registered = int(total_stp * 0.995)

        fig = go.Figure(go.Funnel(
            y=["Order", "Matched", "Instructed", "Settled", "Registered"],
            x=[order, matched, instructed, settled, registered],
            textinfo="value+percent initial",
            marker=dict(color=[VANN, FJELL, FROST, NORDLYS, SYRIN]),
            connector=dict(line=dict(color=GRAA)),
        ))
        fig.update_layout(
            height=360, margin=dict(l=10, r=10, t=10, b=10),
            plot_bgcolor="white", paper_bgcolor="white",
            font=dict(color=KOKS),
        )
        st.plotly_chart(fig, use_container_width=True)


# ============================================================
# TAB 2 — DATA & LABELS
# ============================================================
with tab2:
    st.markdown("### Data & Labels")
    st.caption("Edit transactions and labels here — Tab 1 updates automatically.")

    sub1, sub2, sub3 = st.tabs(["📋 Transactions", "🏷️ Labels", "⚙️ SLA & Reset"])

    # ----- 2.1 Transactions editor -----
    with sub1:
        st.markdown("#### Transactions data")
        st.caption(
            "Each row = one (week × counterparty × instrument) bucket. "
            "`stp` should be ≤ `transactions`. `manual_touches` is the count of "
            "human interventions in that bucket."
        )

        edited = st.data_editor(
            st.session_state.tx_data,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "week_end":         st.column_config.DateColumn("Week end", format="YYYY-MM-DD"),
                "counterparty":     st.column_config.TextColumn("Counterparty"),
                "instrument":       st.column_config.TextColumn("Instrument"),
                "transactions":     st.column_config.NumberColumn("Transactions", min_value=0, step=1),
                "stp":              st.column_config.NumberColumn("STP", min_value=0, step=1),
                "manual_touches":   st.column_config.NumberColumn("Manual touches", min_value=0, step=1),
                "top_break_reason": st.column_config.SelectboxColumn(
                    "Top break reason",
                    options=["—", "Missing SSI", "Late confirmation", "Settlement mismatch",
                             "Cash funding", "Reference data", "Manual booking",
                             "Counterparty error", "Other"],
                ),
            },
            key="data_editor",
        )

        col_save, col_csv_up, col_csv_down = st.columns([1, 1, 1])
        with col_save:
            if st.button("💾 Save changes", type="primary", use_container_width=True):
                # Validate
                bad = edited[edited["stp"] > edited["transactions"]]
                if not bad.empty:
                    st.error(f"{len(bad)} row(s) have STP > transactions — please fix.")
                else:
                    st.session_state.tx_data = edited.copy()
                    st.success("Saved. Switch to Overview tab to see the update.")

        with col_csv_up:
            uploaded = st.file_uploader("Upload CSV", type=["csv"],
                                         label_visibility="collapsed")
            if uploaded is not None:
                try:
                    new_df = pd.read_csv(uploaded, parse_dates=["week_end"])
                    new_df["week_end"] = pd.to_datetime(new_df["week_end"]).dt.date
                    required = {"week_end", "counterparty", "instrument",
                                "transactions", "stp", "manual_touches", "top_break_reason"}
                    if not required.issubset(new_df.columns):
                        st.error(f"CSV missing columns: {required - set(new_df.columns)}")
                    else:
                        st.session_state.tx_data = new_df
                        st.success(f"Loaded {len(new_df)} rows.")
                        st.rerun()
                except Exception as e:
                    st.error(f"Could not read CSV: {e}")

        with col_csv_down:
            csv_bytes = st.session_state.tx_data.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Download CSV", data=csv_bytes,
                               file_name="stp_transactions.csv",
                               mime="text/csv", use_container_width=True)

    # ----- 2.2 Labels editor -----
    with sub2:
        st.markdown("#### Dashboard labels")
        st.caption("Headers, titles, and KPI labels shown in the Overview tab.")

        l = st.session_state.labels
        cA, cB = st.columns(2)
        with cA:
            l["dashboard_title"] = st.text_input("Dashboard title",   l["dashboard_title"])
            l["subtitle"]        = st.text_input("Subtitle",          l["subtitle"])
            l["kpi_overall"]     = st.text_input("KPI — Overall STP", l["kpi_overall"])
            l["kpi_volume"]      = st.text_input("KPI — Volume",      l["kpi_volume"])
            l["kpi_touches"]     = st.text_input("KPI — Touches",     l["kpi_touches"])
            l["kpi_touches_per"] = st.text_input("KPI — Touches/100", l["kpi_touches_per"])
        with cB:
            l["trend_title"]     = st.text_input("Trend chart title",     l["trend_title"])
            l["waterfall_title"] = st.text_input("Waterfall chart title", l["waterfall_title"])
            l["pareto_title"]    = st.text_input("Pareto chart title",    l["pareto_title"])
            l["heatmap_title"]   = st.text_input("Heatmap title",         l["heatmap_title"])
            l["touches_title"]   = st.text_input("Touches chart title",   l["touches_title"])
            l["funnel_title"]    = st.text_input("Funnel chart title",    l["funnel_title"])

        if st.button("💾 Save labels", type="primary"):
            st.session_state.labels = l
            st.success("Labels saved.")

    # ----- 2.3 SLA + reset -----
    with sub3:
        st.markdown("#### SLA band (used in trend chart)")
        c1, c2 = st.columns(2)
        with c1:
            st.session_state.labels["sla_lower"] = st.slider(
                "Lower SLA threshold", 0.80, 1.00,
                float(st.session_state.labels["sla_lower"]), 0.005,
                format="%.3f")
        with c2:
            st.session_state.labels["sla_upper"] = st.slider(
                "Upper SLA threshold", 0.80, 1.00,
                float(st.session_state.labels["sla_upper"]), 0.005,
                format="%.3f")

        st.markdown("---")
        st.markdown("#### Reset")
        if st.button("🔄 Reset to seed data", type="secondary"):
            st.session_state.tx_data = seed_transactions()
            st.session_state.labels  = seed_labels()
            st.success("Reset done.")
            st.rerun()


# ---------- FOOTER ----------
st.markdown(
    f"<hr style='margin-top:3rem;border:none;border-top:1px solid {SYRIN}'>"
    f"<p style='color:{GRAA};font-size:0.85rem;text-align:right'>"
    f"SpareBank 1 Forvaltning · Operations & Administration"
    f"</p>",
    unsafe_allow_html=True,
)
