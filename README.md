# STP & Human Touches — Streamlit App

Two-tab Streamlit app for SpareBank 1 Forvaltning fund settlement operations.

## Run locally

```bash
pip install streamlit pandas plotly
streamlit run app.py
```

App opens at http://localhost:8501

## Tabs

**📊 Overview** — Visual dashboard
- KPI tiles: Overall STP-Rate, Volume, Manual Touches, Touches per 100 trades
- Trend line with editable SLA band (color-coded markers)
- Waterfall: where STP is lost by break reason
- Heatmap: STP-rate by counterparty × instrument
- Pareto of break causes (80% line)
- Manual touches by counterparty
- Funnel: Order → Matched → Instructed → Settled → Registered
- Global filters: counterparty, instrument, date range

**⚙️ Data & Labels** — Three sub-tabs:
1. **Transactions** — editable grid (add/edit/delete rows), CSV upload/download
2. **Labels** — rename every header, KPI label, and chart title
3. **SLA & Reset** — set SLA band thresholds, reset to seed data

## Data model

Each row = one (week × counterparty × instrument) bucket with:
`week_end · counterparty · instrument · transactions · stp · manual_touches · top_break_reason`

`stp` must be ≤ `transactions` (validated on save).

## Branding

SpareBank 1 palette: Vann (primary), Fjell (secondary), Frost, Syrin, Sand,
Nordlys (in-SLA), Sol (warning), Bær (breach).
