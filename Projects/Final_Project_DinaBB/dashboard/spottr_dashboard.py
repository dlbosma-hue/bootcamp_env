"""
spottr_dashboard.py
--------------------
Spottr — Member Retention Dashboard
Two views: risk overview (bar chart) + priority member list (table).

Run from project root:
    python dashboard/spottr_dashboard.py

Opens at http://127.0.0.1:8050
"""

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dash_table, dcc, html

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent.parent
MEMBERS  = BASE_DIR / "data" / "demo_members.csv"

# ── Load ───────────────────────────────────────────────────────────────────────
df = pd.read_csv(MEMBERS)
df["churn_risk_tier"] = df["churn_risk_tier"].str.upper()

# ── Colours ────────────────────────────────────────────────────────────────────
RED    = "#E63946"
AMBER  = "#F4A261"
GREEN  = "#2A9D8F"
BG     = "#FAFAFA"
TEXT   = "#222222"
SUBTLE = "#888888"

TIER_COLOUR = {"HIGH": RED, "MEDIUM": AMBER, "LOW": GREEN}

# ── Summary numbers ────────────────────────────────────────────────────────────
total           = len(df)
high_n          = int((df["churn_risk_tier"] == "HIGH").sum())
medium_n        = int((df["churn_risk_tier"] == "MEDIUM").sum())
low_n           = int((df["churn_risk_tier"] == "LOW").sum())
revenue_at_risk = int(df["revenue_at_risk_eur"].sum())

# ══════════════════════════════════════════════════════════════════════════════
# CHART — Risk overview bar
# ══════════════════════════════════════════════════════════════════════════════
tier_order  = ["HIGH", "MEDIUM", "LOW"]
tier_labels = ["High risk", "Medium risk", "Low risk"]
tier_counts = [high_n, medium_n, low_n]
tier_pct    = [f"{round(n / total * 100)}%" for n in tier_counts]

fig = go.Figure()

fig.add_trace(go.Bar(
    x=tier_labels,
    y=tier_counts,
    marker_color=[TIER_COLOUR[t] for t in tier_order],
    text=[f"{n} members ({p})" for n, p in zip(tier_counts, tier_pct)],
    textposition="outside",
    textfont=dict(size=14, color=TEXT),
    name="Members",
    yaxis="y1",
    hovertemplate="<b>%{x}</b><br>%{y} members<extra></extra>",
))

fig.update_layout(
    title=dict(
        text=f"{total} members total — €{revenue_at_risk:,} revenue at risk",
        font=dict(size=17, color=TEXT),
        x=0,
    ),
    yaxis=dict(
        title="Members",
        range=[0, max(tier_counts) * 1.4],
        showgrid=True,
        gridcolor="#eeeeee",
    ),
    showlegend=False,
    plot_bgcolor=BG,
    paper_bgcolor=BG,
    margin=dict(l=20, r=20, t=60, b=40),
    font=dict(family="Arial", color=TEXT),
)

# ══════════════════════════════════════════════════════════════════════════════
# TABLE — Priority member list (HIGH + MEDIUM only, sorted by probability)
# ══════════════════════════════════════════════════════════════════════════════
priority = (
    df[df["churn_risk_tier"].isin(["HIGH", "MEDIUM"])]
    .sort_values("churn_probability", ascending=False)
    .reset_index(drop=True)
)

priority["Rank"]              = priority.index + 1
priority["Member"]            = priority["user_id"].astype(str)
priority["Risk"]              = priority["churn_risk_tier"]
priority["Churn probability"] = (priority["churn_probability"] * 100).round(1).astype(str) + "%"
priority["Days since visit"]  = priority["days_since_last_workout"].astype(int)
priority["Sessions / week"]   = priority["avg_sessions_per_week"].round(1)
priority["Revenue at risk"]   = priority["revenue_at_risk_eur"].apply(
    lambda v: f"€{int(v):,}" if v > 0 else "—"
)

table_cols = ["Rank", "Member", "Risk", "Churn probability", "Days since visit", "Sessions / week", "Revenue at risk"]
table_df   = priority[table_cols]

def row_style(tier):
    if tier == "HIGH":
        return {"backgroundColor": "#fff0f0"}
    return {"backgroundColor": "#fff8f0"}

table = dash_table.DataTable(
    data=table_df.to_dict("records"),
    columns=[{"name": c, "id": c} for c in table_cols],
    style_table={"overflowX": "auto"},
    style_header={
        "backgroundColor": "#f0f0f0",
        "fontWeight": "bold",
        "fontSize": "13px",
        "color": TEXT,
        "border": "none",
        "padding": "10px 12px",
    },
    style_cell={
        "fontSize": "13px",
        "color": TEXT,
        "padding": "9px 12px",
        "border": "none",
        "borderBottom": "1px solid #eeeeee",
        "fontFamily": "Arial",
        "textAlign": "left",
    },
    style_data_conditional=[
        {
            "if": {"filter_query": '{Risk} = "HIGH"'},
            "backgroundColor": "#fff5f5",
        },
        {
            "if": {"filter_query": '{Risk} = "MEDIUM"'},
            "backgroundColor": "#fffaf4",
        },
        {
            "if": {"column_id": "Risk", "filter_query": '{Risk} = "HIGH"'},
            "color": RED,
            "fontWeight": "bold",
        },
        {
            "if": {"column_id": "Risk", "filter_query": '{Risk} = "MEDIUM"'},
            "color": "#c97a2a",
            "fontWeight": "bold",
        },
        {
            "if": {"column_id": "Churn probability", "filter_query": '{Risk} = "HIGH"'},
            "fontWeight": "bold",
        },
    ],
    page_size=20,
    sort_action="native",
)

# ══════════════════════════════════════════════════════════════════════════════
# Layout
# ══════════════════════════════════════════════════════════════════════════════
def _kpi(label, value, colour):
    return html.Div([
        html.P(label, style={"margin": "0 0 4px 0", "fontSize": "12px", "color": SUBTLE, "textTransform": "uppercase", "letterSpacing": "0.5px"}),
        html.P(value, style={"margin": "0", "fontSize": "28px", "fontWeight": "700", "color": colour}),
    ], style={
        "backgroundColor": "white",
        "border": "1px solid #eeeeee",
        "borderRadius": "8px",
        "padding": "16px 20px",
        "flex": "1",
    })


app = Dash(__name__)
app.title = "Spottr"

app.layout = html.Div(
    style={"fontFamily": "Arial", "backgroundColor": BG, "padding": "32px 40px", "maxWidth": "1100px", "margin": "0 auto"},
    children=[
        # Header
        html.Div([
            html.H1("Spottr", style={"margin": "0", "fontSize": "32px", "color": TEXT, "letterSpacing": "-0.5px"}),
            html.P(
                "Member retention dashboard — demo data (150 members, boutique studio scale)",
                style={"margin": "4px 0 0 0", "color": SUBTLE, "fontSize": "13px"},
            ),
        ], style={"marginBottom": "32px"}),

        # KPI row
        html.Div([
            _kpi("High risk", str(high_n), RED),
            _kpi("Medium risk", str(medium_n), AMBER),
            _kpi("Low risk", str(low_n), GREEN),
            _kpi("Revenue at risk", f"€{revenue_at_risk:,}", RED),
        ], style={"display": "flex", "gap": "16px", "marginBottom": "32px"}),

        # Bar chart
        dcc.Graph(figure=fig, style={"marginBottom": "40px"}),

        # Priority list
        html.H2(
            f"Priority list — {high_n + medium_n} members need attention this week",
            style={"fontSize": "16px", "color": TEXT, "fontWeight": "600", "marginBottom": "12px"},
        ),
        html.P(
            "Sorted by churn probability. Reach out to HIGH risk members within 48 hours.",
            style={"color": SUBTLE, "fontSize": "13px", "marginBottom": "16px", "marginTop": "-8px"},
        ),
        table,

        html.P(
            "Model: logistic regression trained on 4,000 labelled gym members — 92.5% accuracy, 0.977 ROC-AUC. "
            "Demo data derived from Endomondo workout sessions. Replaced with real studio export at go-live.",
            style={"color": "#bbbbbb", "fontSize": "11px", "marginTop": "24px"},
        ),
    ],
)


if __name__ == "__main__":
    app.run(debug=False, port=8050)
