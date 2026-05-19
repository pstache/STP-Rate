"""
STP & Human Touches — SpareBank 1 Forvaltning
Forenklet versjon: Arbeidsflyt → Steg → STP-grad + Human Touches
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ============================================================
# SB1 BRAND PALETTE
# ============================================================
VANN     = "#005AA4"
FJELL    = "#002776"
FROST    = "#7EB5D2"
SYRIN    = "#D3D3EA"
SAND     = "#F8E9DD"
NORDLYS  = "#33AF85"
SOL      = "#DC8000"
BAER     = "#E44244"
NATT     = "#001032"
KOKS     = "#323232"
GRAA     = "#ADADAD"
HVIT     = "#FFFFFF"

st.set_page_config(
    page_title="STP & Human Touches — SB1 Forvaltning",
    page_icon="📊",
    layout="wide",
)

# ============================================================
# SESSION STATE — theme + data
# ============================================================
if "theme" not in st.session_state:
    st.session_state.theme = "Lys"

def seed_data():
    """Default workflows with sub-steps."""
    return pd.DataFrame([
        # Tegning
        ("Tegning",      "Mottak ordre",        96.5,  12),
        ("Tegning",      "Validering",          98.2,   6),
        ("Tegning",      "Allokering",          99.1,   3),
        ("Tegning",      "Oppgjør",             94.8,  18),
        ("Tegning",      "Registrering VPS",    93.2,  22),
        # Innløsning
        ("Innløsning",   "Mottak ordre",        95.8,  14),
        ("Innløsning",   "Validering",          97.5,   8),
        ("Innløsning",   "Allokering",          98.7,   4),
        ("Innløsning",   "Oppgjør",             92.4,  26),
        ("Innløsning",   "Registrering VPS",    91.5,  29),
        # Bytte
        ("Bytte",        "Mottak ordre",        93.2,  21),
        ("Bytte",        "Validering",          95.6,  14),
        ("Bytte",        "Bekreftelse",         96.8,  10),
        ("Bytte",        "Oppgjør",             89.5,  34),
        # Overføring
        ("Overføring",   "Mottak forespørsel",  88.4,  38),
        ("Overføring",   "Verifisering",        85.2,  47),
        ("Overføring",   "Avstemming",          82.6,  56),
        ("Overføring",   "Bekreftelse",         91.3,  28),
        # Avstemming
        ("Avstemming",   "Daglig avstemming",   97.8,   7),
        ("Avstemming",   "Brudd-håndtering",    78.5,  62),
        ("Avstemming",   "Rapportering",        99.2,   2),
    ], columns=["arbeidsflyt", "steg", "stp_grad", "human_touches"])

if "data" not in st.session_state:
    st.session_state.data = seed_data()


# ============================================================
# THEME — palettes that work on both backgrounds
# ============================================================
def get_theme(mode):
    if mode == "Mørk":
        return {
            "bg":         NATT,
            "panel":      "#0A1F4A",
            "text":       HVIT,
            "text_muted": "#B8C4DC",
            "border":     "#1A3A6E",
            "grid":       "#1A3A6E",
            "primary":    FROST,
            "secondary":  SYRIN,
            "good":       NORDLYS,
            "warn":       SOL,
            "bad":        "#FF6B6D",
            "tab_inactive_bg":   "#0A1F4A",
            "tab_inactive_text": "#B8C4DC",
            "heatmap":    [[0, "#5A1A2D"], [0.4, "#873953"],
                           [0.7, FROST], [1.0, NORDLYS]],
        }
    # Light
    return {
        "bg":         HVIT,
        "panel":      SAND,
        "text":       NATT,
        "text_muted": KOKS,
        "border":     SYRIN,
        "grid":       "#EFEFEF",
        "primary":    VANN,
        "secondary":  FJELL,
        "good":       NORDLYS,
        "warn":       SOL,
        "bad":        BAER,
        "tab_inactive_bg":   SAND,
        "tab_inactive_text": FJELL,
        "heatmap":    [[0, BAER], [0.4, SOL], [0.7, FROST], [1.0, VANN]],
    }

T = get_theme(st.session_state.theme)


# ============================================================
# GLOBAL CSS
# ============================================================
st.markdown(f"""
<style>
    .stApp {{ background-color: {T['bg']}; color: {T['text']}; }}
    h1, h2, h3, h4 {{ color: {T['text']}; font-weight: 600; letter-spacing: -0.01em; }}
    p, label, span {{ color: {T['text']}; }}

    [data-testid="stMetric"] {{
        background-color: {T['panel']};
        padding: 16px 20px;
        border-radius: 16px;
        border: 1px solid {T['border']};
    }}
    [data-testid="stMetricValue"] {{ color: {T['primary']}; font-weight: 700; }}
    [data-testid="stMetricLabel"] {{ color: {T['text_muted']}; font-weight: 500; }}
    [data-testid="stMetricDelta"] {{ color: {T['text_muted']}; }}

    .stTabs [data-baseweb="tab-list"] {{ gap: 8px; }}
    .stTabs [data-baseweb="tab"] {{
        background-color: {T['tab_inactive_bg']};
        color: {T['tab_inactive_text']};
        border-radius: 12px 12px 0 0;
        padding: 10px 24px;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {T['primary']} !important;
        color: {HVIT} !important;
    }}

    hr {{ border-color: {T['border']}; }}
    .block-container {{ padding-top: 1.5rem; }}
</style>
""", unsafe_allow_html=True)


# ============================================================
# HEADER
# ============================================================
header_l, header_r = st.columns([4, 1])
with header_l:
    st.markdown(
        f"<h1 style='margin-bottom:0'>STP & Human Touches</h1>"
        f"<p style='color:{T['text_muted']};margin-top:0;font-size:1.05rem'>"
        f"SpareBank 1 Forvaltning · Operations & Administration</p>",
        unsafe_allow_html=True,
    )
with header_r:
    st.markdown("<br>", unsafe_allow_html=True)
    new_theme = st.radio(
        "Tema",
        ["Lys", "Mørk"],
        horizontal=True,
        index=0 if st.session_state.theme == "Lys" else 1,
        label_visibility="collapsed",
    )
    if new_theme != st.session_state.theme:
        st.session_state.theme = new_theme
        st.rerun()


# ============================================================
# TABS
# ============================================================
tab_overview, tab_data = st.tabs(["📊  Oversikt", "⚙️  Data"])


# ============================================================
# TAB 1 — OVERSIKT
# ============================================================
with tab_overview:
    df = st.session_state.data.copy()

    if df.empty:
        st.warning("Ingen data ennå. Gå til **Data**-fanen for å legge til arbeidsflyter.")
        st.stop()

    # Aggregates — likt vektet snitt per steg innen arbeidsflyt
    overall_stp   = df["stp_grad"].mean()
    total_touches = int(df["human_touches"].sum())
    by_workflow = (df.groupby("arbeidsflyt")
                     .agg(stp_grad=("stp_grad", "mean"),
                          touches =("human_touches", "sum"),
                          n_steg  =("steg", "count"))
                     .reset_index()
                     .sort_values("stp_grad", ascending=False))

    # ---- KPI ROW ----
    k1, k2, k3 = st.columns(3)
    with k1:
        st.metric("Overall STP-grad", f"{overall_stp:.1f} %")
    with k2:
        st.metric("Samlet Human Touches",
                  f"{total_touches:,}".replace(",", " "))
    with k3:
        worst = by_workflow.iloc[-1]
        st.metric("Svakeste arbeidsflyt",
                  worst["arbeidsflyt"],
                  delta=f"{worst['stp_grad']:.1f} %",
                  delta_color="off")

    st.markdown("<br>", unsafe_allow_html=True)

    # ---- ROW 1: STP per arbeidsflyt + Human touches per arbeidsflyt ----
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("#### STP-grad per arbeidsflyt")
        wf_sorted = by_workflow.sort_values("stp_grad", ascending=True)
        bar_colors = [
            T["bad"]  if r < 90 else
            T["warn"] if r < 95 else
            T["good"] if r >= 98 else
            T["primary"]
            for r in wf_sorted["stp_grad"]
        ]
        fig = go.Figure(go.Bar(
            x=wf_sorted["stp_grad"],
            y=wf_sorted["arbeidsflyt"],
            orientation="h",
            marker=dict(color=bar_colors,
                         line=dict(color=T["border"], width=1)),
            text=[f"{v:.1f} %" for v in wf_sorted["stp_grad"]],
            textposition="outside",
            textfont=dict(color=T["text"], size=12),
            hovertemplate="<b>%{y}</b><br>STP-grad: %{x:.2f} %<extra></extra>",
        ))
        fig.update_layout(
            height=340,
            margin=dict(l=10, r=70, t=10, b=10),
            xaxis=dict(
                title="STP-grad (%)",
                range=[max(70, wf_sorted["stp_grad"].min() - 5), 102],
                gridcolor=T["grid"], color=T["text"],
            ),
            yaxis=dict(color=T["text"]),
            plot_bgcolor=T["bg"], paper_bgcolor=T["bg"],
            font=dict(color=T["text"], family="Arial, sans-serif"),
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown("#### Human Touches per arbeidsflyt")
        wf_touches = by_workflow.sort_values("touches", ascending=True)
        max_t = wf_touches["touches"].max() if wf_touches["touches"].max() > 0 else 1
        touch_colors = [
            T["bad"]  if (v / max_t) > 0.75 else
            T["warn"] if (v / max_t) > 0.45 else
            T["primary"]
            for v in wf_touches["touches"]
        ]
        fig = go.Figure(go.Bar(
            x=wf_touches["touches"],
            y=wf_touches["arbeidsflyt"],
            orientation="h",
            marker=dict(color=touch_colors,
                         line=dict(color=T["border"], width=1)),
            text=[f"{v:,}".replace(",", " ") for v in wf_touches["touches"]],
            textposition="outside",
            textfont=dict(color=T["text"], size=12),
            hovertemplate="<b>%{y}</b><br>Human touches: %{x}<extra></extra>",
        ))
        fig.update_layout(
            height=340,
            margin=dict(l=10, r=70, t=10, b=10),
            xaxis=dict(title="Antall human touches",
                       gridcolor=T["grid"], color=T["text"]),
            yaxis=dict(color=T["text"]),
            plot_bgcolor=T["bg"], paper_bgcolor=T["bg"],
            font=dict(color=T["text"], family="Arial, sans-serif"),
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ---- ROW 2: Heatmap (full bredde) ----
    st.markdown("#### Heatmap — STP-grad per arbeidsflyt × steg")
    st.caption("Tomme celler betyr at steget ikke finnes i den arbeidsflyten.")

    pivot = df.pivot_table(index="arbeidsflyt", columns="steg",
                            values="stp_grad", aggfunc="mean")
    text_matrix = [[f"{v:.1f} %" if pd.notna(v) else "" for v in row]
                   for row in pivot.values]

    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=pivot.columns,
        y=pivot.index,
        colorscale=T["heatmap"],
        zmin=75, zmax=100,
        text=text_matrix,
        texttemplate="%{text}",
        textfont=dict(color=HVIT, size=12, family="Arial, sans-serif"),
        colorbar=dict(
            title=dict(text="STP-grad %", font=dict(color=T["text"])),
            tickfont=dict(color=T["text"]),
            outlinecolor=T["border"],
        ),
        hovertemplate="<b>%{y}</b><br>Steg: %{x}<br>STP-grad: %{z:.2f} %<extra></extra>",
        xgap=2, ygap=2,
    ))
    fig.update_layout(
        height=400,
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(side="top", color=T["text"], tickangle=-20),
        yaxis=dict(color=T["text"]),
        plot_bgcolor=T["bg"], paper_bgcolor=T["bg"],
        font=dict(color=T["text"], family="Arial, sans-serif"),
    )
    st.plotly_chart(fig, use_container_width=True)


# ============================================================
# TAB 2 — DATA
# ============================================================
with tab_data:
    st.markdown("### Data")
    st.caption(
        "Definer arbeidsflyter, steg, STP-grad og human touches her. "
        "Endringer reflekteres i **Oversikt**-fanen når du lagrer."
    )

    st.markdown(
        f"<ul style='color:{T['text_muted']}'>"
        "<li><b>Arbeidsflyt (navn)</b> — overordnet prosess, f.eks. Tegning, Innløsning</li>"
        "<li><b>Navn på steg i arbeidsflyt</b> — delsteg innenfor arbeidsflyten</li>"
        "<li><b>STP-grad</b> — prosent (0–100) gjennomført uten manuell inngripen</li>"
        "<li><b>Human Touch</b> — antall manuelle inngrep i perioden</li>"
        "</ul>",
        unsafe_allow_html=True,
    )

    edited = st.data_editor(
        st.session_state.data,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        column_config={
            "arbeidsflyt": st.column_config.TextColumn(
                "Arbeidsflyt (navn)",
                help="Overordnet prosess",
                required=True,
            ),
            "steg": st.column_config.TextColumn(
                "Navn på steg i arbeidsflyt",
                help="Delsteg i arbeidsflyten",
                required=True,
            ),
            "stp_grad": st.column_config.NumberColumn(
                "STP-grad (%)",
                help="Andel som går straight-through, 0–100",
                min_value=0.0, max_value=100.0, step=0.1, format="%.1f",
                required=True,
            ),
            "human_touches": st.column_config.NumberColumn(
                "Human Touch (antall)",
                help="Antall manuelle inngrep",
                min_value=0, step=1, format="%d",
                required=True,
            ),
        },
        key="data_editor",
    )

    col_save, col_reset, col_dl = st.columns([1, 1, 1])

    with col_save:
        if st.button("💾 Lagre endringer", type="primary",
                      use_container_width=True):
            invalid = edited[
                edited["arbeidsflyt"].isna() | (edited["arbeidsflyt"] == "")
                | edited["steg"].isna()        | (edited["steg"] == "")
            ]
            if not invalid.empty:
                st.error(f"{len(invalid)} rad(er) mangler arbeidsflyt eller steg-navn.")
            elif (edited["stp_grad"] < 0).any() or (edited["stp_grad"] > 100).any():
                st.error("STP-grad må være mellom 0 og 100.")
            else:
                st.session_state.data = edited.copy()
                st.success("Lagret. Bytt til **Oversikt** for å se oppdateringen.")

    with col_reset:
        if st.button("🔄 Tilbakestill", use_container_width=True):
            st.session_state.data = seed_data()
            st.success("Tilbakestilt til standard.")
            st.rerun()

    with col_dl:
        csv = st.session_state.data.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Last ned CSV",
            data=csv,
            file_name="stp_arbeidsflyt.csv",
            mime="text/csv",
            use_container_width=True,
        )


# ============================================================
# FOOTER
# ============================================================
st.markdown(
    f"<hr style='margin-top:3rem'>"
    f"<p style='color:{T['text_muted']};font-size:0.85rem;text-align:right'>"
    f"SpareBank 1 Forvaltning · Operations & Administration</p>",
    unsafe_allow_html=True,
)
