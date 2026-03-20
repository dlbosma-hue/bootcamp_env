"""
plotly_dashboard.py
--------------------
Fitness Chain Retention – Member Early Warning Dashboard
Built for Chleo, CEO of a European medium-sized fitness chain.

Run:
    cd Project5_dashboard_project
    python dashboard/plotly_dashboard.py

Opens in your browser at http://127.0.0.1:8050
"""

import pandas as pd
import numpy as np
from pathlib import Path

import dash
from dash import dcc, html
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).parent.parent
ENDOMONDO  = BASE_DIR / "data" / "processed" / "fitness_user_metrics.csv"
GYM_CHURN  = BASE_DIR / "data" / "raw" / "gym_churn_us.csv"

# ── Load data ──────────────────────────────────────────────────────────────────
endo = pd.read_csv(ENDOMONDO)
gym  = pd.read_csv(GYM_CHURN)

# ── Colour palette ─────────────────────────────────────────────────────────────
RED    = "#E63946"
AMBER  = "#F4A261"
GREEN  = "#2A9D8F"
DARK   = "#1D1D1D"
CARD   = "#F8F8F8"
TEXT   = "#333333"

RISK_COLOURS = {"high": RED, "medium": AMBER, "low": GREEN}

# ══════════════════════════════════════════════════════════════════════════════
# CHART 1 — Retention Funnel
# ══════════════════════════════════════════════════════════════════════════════
risk_counts = endo["churn_risk"].value_counts()
low_n    = int(risk_counts.get("low",    0))
medium_n = int(risk_counts.get("medium", 0))
high_n   = int(risk_counts.get("high",   0))
total    = low_n + medium_n + high_n
revenue_at_risk = int(endo["revenue_at_risk_eur"].sum())

fig_funnel = go.Figure(go.Funnel(
    y=["Active members", "At-risk members", "High-risk (act now)"],
    x=[low_n + medium_n + high_n, medium_n + high_n, high_n],
    textinfo="value+percent initial",
    marker=dict(color=[GREEN, AMBER, RED]),
    connector=dict(line=dict(color="#cccccc", width=1)),
    textfont=dict(size=14, color="white"),
))
fig_funnel.update_layout(
    title=dict(
        text=f"How many of your {total} members are heading for the exit?<br>"
             f"<sup style='color:{RED}'>€{revenue_at_risk:,} in membership revenue is currently at risk</sup>",
        font=dict(size=16, color=TEXT),
    ),
    plot_bgcolor=CARD, paper_bgcolor=CARD,
    margin=dict(l=20, r=20, t=80, b=20),
    font=dict(family="Arial", color=TEXT),
)

# ══════════════════════════════════════════════════════════════════════════════
# CHART 2 — Churn rate by contract type
# ══════════════════════════════════════════════════════════════════════════════
contract_churn = gym.groupby("Contract_period")["Churn"].mean().reset_index()
contract_churn["Churn_pct"] = (contract_churn["Churn"] * 100).round(1)
contract_churn["label"] = contract_churn["Contract_period"].map(
    {1: "Month-to-month", 6: "6-month", 12: "12-month"}
)
contract_churn["colour"] = contract_churn["Churn_pct"].apply(
    lambda x: RED if x > 30 else AMBER if x > 10 else GREEN
)
contract_counts = gym.groupby("Contract_period").size().reset_index(name="n")
contract_churn = contract_churn.merge(contract_counts, on="Contract_period")

fig_contract = go.Figure(go.Bar(
    x=contract_churn["label"],
    y=contract_churn["Churn_pct"],
    marker_color=contract_churn["colour"],
    text=[f"{v}%" for v in contract_churn["Churn_pct"]],
    textposition="outside",
    textfont=dict(size=13, color=TEXT),
    customdata=contract_churn["n"],
    hovertemplate="<b>%{x}</b><br>Churn rate: %{y}%<br>Members: %{customdata}<extra></extra>",
))
fig_contract.update_layout(
    title=dict(
        text="Month-to-month members are 18× more likely to churn than 12-month members<br>"
             "<sup>Upsell to longer contracts = biggest single lever to reduce churn</sup>",
        font=dict(size=15, color=TEXT),
    ),
    xaxis_title="Contract type",
    yaxis_title="Churn rate (%)",
    yaxis=dict(range=[0, 55]),
    plot_bgcolor=CARD, paper_bgcolor=CARD,
    margin=dict(l=20, r=20, t=90, b=40),
    font=dict(family="Arial", color=TEXT),
    showlegend=False,
)

# ══════════════════════════════════════════════════════════════════════════════
# CHART 3 — Class frequency vs churn
# ══════════════════════════════════════════════════════════════════════════════
gym["freq_bucket"] = pd.cut(
    gym["Avg_class_frequency_current_month"],
    bins=[-0.01, 0.5, 1.0, 2.0, 7.0],
    labels=["<0.5 / week", "0.5–1 / week", "1–2 / week", ">2 / week"],
)
freq_churn = gym.groupby("freq_bucket", observed=True)["Churn"].agg(["mean", "count"]).reset_index()
freq_churn.columns = ["bucket", "churn_rate", "count"]
freq_churn["churn_pct"] = (freq_churn["churn_rate"] * 100).round(1)
freq_churn["colour"] = freq_churn["churn_pct"].apply(
    lambda x: RED if x > 40 else AMBER if x > 20 else GREEN
)

fig_freq = go.Figure(go.Bar(
    x=freq_churn["bucket"],
    y=freq_churn["churn_pct"],
    marker_color=freq_churn["colour"],
    text=[f"{v}%" for v in freq_churn["churn_pct"]],
    textposition="outside",
    textfont=dict(size=13, color=TEXT),
    customdata=freq_churn["count"],
    hovertemplate="<b>%{x}</b><br>Churn rate: %{y}%<br>Members in group: %{customdata}<extra></extra>",
))
fig_freq.add_hline(
    y=20, line_dash="dot", line_color=AMBER,
    annotation_text="Intervention threshold", annotation_position="top left",
    annotation_font_color=AMBER,
)
fig_freq.update_layout(
    title=dict(
        text="Members attending less than once a week churn at 3–7× the rate of active members<br>"
             "<sup>Dropping below 1 class/week is the clearest early-warning signal for coaches to act on</sup>",
        font=dict(size=15, color=TEXT),
    ),
    xaxis_title="Class frequency (current month)",
    yaxis_title="Churn rate (%)",
    yaxis=dict(range=[0, 70]),
    plot_bgcolor=CARD, paper_bgcolor=CARD,
    margin=dict(l=20, r=20, t=90, b=40),
    font=dict(family="Arial", color=TEXT),
    showlegend=False,
)

# ══════════════════════════════════════════════════════════════════════════════
# CHART 4 — Social factors & retention
# ══════════════════════════════════════════════════════════════════════════════
social_data = {
    "Factor":      ["No group classes", "Group classes",
                    "No partner", "Joined with partner",
                    "No referral", "Referred by friend"],
    "Churn_pct":   [33.0, 17.3, 33.3, 19.4, 31.3, 15.8],
    "Group":       ["Group classes", "Group classes",
                    "Partner membership", "Partner membership",
                    "Referral (Promo)", "Referral (Promo)"],
    "Type":        ["baseline", "social",
                    "baseline", "social",
                    "baseline", "social"],
}
social_df = pd.DataFrame(social_data)
social_df["colour"] = social_df["Type"].map({"baseline": "#AAAAAA", "social": GREEN})

fig_social = go.Figure()
for group in ["Group classes", "Partner membership", "Referral (Promo)"]:
    sub = social_df[social_df["Group"] == group]
    fig_social.add_trace(go.Bar(
        x=sub["Factor"],
        y=sub["Churn_pct"],
        name=group,
        marker_color=sub["colour"].tolist(),
        text=[f"{v}%" for v in sub["Churn_pct"]],
        textposition="outside",
        textfont=dict(size=12, color=TEXT),
        hovertemplate="<b>%{x}</b><br>Churn rate: %{y}%<extra></extra>",
    ))

fig_social.update_layout(
    title=dict(
        text="Social members churn at roughly half the rate — connection is the best retention tool<br>"
             "<sup>Group classes, partner sign-ups, and friend referrals all cut churn by ~40–50%</sup>",
        font=dict(size=15, color=TEXT),
    ),
    xaxis_title=None,
    yaxis_title="Churn rate (%)",
    yaxis=dict(range=[0, 45]),
    barmode="group",
    plot_bgcolor=CARD, paper_bgcolor=CARD,
    margin=dict(l=20, r=20, t=90, b=80),
    font=dict(family="Arial", color=TEXT),
    legend=dict(orientation="h", y=-0.25),
    showlegend=True,
)

# ══════════════════════════════════════════════════════════════════════════════
# CHART 5 — Recency vs frequency scatter (early-warning zone)
# ══════════════════════════════════════════════════════════════════════════════
colour_map = endo["churn_risk"].map(RISK_COLOURS)

fig_scatter = go.Figure()
for risk, colour in RISK_COLOURS.items():
    sub = endo[endo["churn_risk"] == risk]
    fig_scatter.add_trace(go.Scatter(
        x=sub["avg_sessions_per_week"],
        y=sub["days_since_last_workout"],
        mode="markers",
        name=risk.capitalize() + " risk",
        marker=dict(color=colour, size=6, opacity=0.65,
                    line=dict(width=0.3, color="white")),
        customdata=sub[["user_id", "sport_variety", "avg_duration_min"]].values,
        hovertemplate=(
            "<b>Member #%{customdata[0]}</b><br>"
            "Sessions/week: %{x:.1f}<br>"
            "Days inactive: %{y}<br>"
            "Sport variety: %{customdata[1]}<br>"
            "Avg session: %{customdata[2]:.0f} min"
            "<extra></extra>"
        ),
    ))

# Early-warning zone shading
fig_scatter.add_shape(
    type="rect",
    x0=0, x1=2, y0=21, y1=185,
    fillcolor=RED, opacity=0.07,
    line=dict(color=RED, width=1, dash="dot"),
)
fig_scatter.add_annotation(
    x=1, y=170, text="⚠ Early-warning zone<br><2 sessions/week + >3 weeks inactive",
    showarrow=False, font=dict(color=RED, size=11),
    bgcolor="rgba(255,255,255,0.8)", bordercolor=RED, borderwidth=1,
)

fig_scatter.update_layout(
    title=dict(
        text="Every dot is a member — the red zone is where coaches need to act<br>"
             "<sup>Low session frequency + long inactivity = the dropout pattern, visible 4–6 weeks early</sup>",
        font=dict(size=15, color=TEXT),
    ),
    xaxis_title="Avg sessions per week",
    yaxis_title="Days since last workout",
    xaxis=dict(range=[-0.1, 9]),
    yaxis=dict(range=[-5, 190]),
    plot_bgcolor=CARD, paper_bgcolor=CARD,
    margin=dict(l=20, r=20, t=90, b=40),
    font=dict(family="Arial", color=TEXT),
    legend=dict(orientation="h", y=-0.15),
)

# ══════════════════════════════════════════════════════════════════════════════
# KPI CARDS — computed values
# ══════════════════════════════════════════════════════════════════════════════
total_members   = len(endo)
high_risk_n     = int((endo["churn_risk"] == "high").sum())
high_risk_pct   = round(high_risk_n / total_members * 100, 1)
revenue_risk    = int(endo["revenue_at_risk_eur"].sum())
month_churn_pct = round(gym[gym["Contract_period"] == 1]["Churn"].mean() * 100, 1)
low_freq_churn  = round(gym[gym["Avg_class_frequency_current_month"] < 1]["Churn"].mean() * 100, 1)


def kpi_card(value, label, colour=TEXT, bg=CARD):
    return html.Div([
        html.Div(value, style={
            "fontSize": "2.2rem", "fontWeight": "700",
            "color": colour, "lineHeight": "1.1",
        }),
        html.Div(label, style={
            "fontSize": "0.8rem", "color": "#666",
            "marginTop": "4px", "lineHeight": "1.3",
        }),
    ], style={
        "background": bg,
        "border": f"2px solid {colour}",
        "borderRadius": "10px",
        "padding": "18px 22px",
        "flex": "1",
        "minWidth": "140px",
        "boxShadow": "0 2px 8px rgba(0,0,0,0.06)",
    })


# ══════════════════════════════════════════════════════════════════════════════
# DASH APP LAYOUT
# ══════════════════════════════════════════════════════════════════════════════
app = dash.Dash(__name__, title="Member Retention Risk — Chleo Demo")

app.layout = html.Div([

    # Header
    html.Div([
        html.H1("Member Retention Risk — Early Warning System",
                style={"margin": "0", "fontSize": "1.6rem", "color": "white", "fontWeight": "700"}),
        html.P("Preliminary analysis · Fitness chain · 1,059 members (Endomondo) + 4,000 members (Model Fitness)",
               style={"margin": "4px 0 0 0", "fontSize": "0.85rem", "color": "#ddd"}),
    ], style={
        "background": DARK, "padding": "22px 32px",
        "borderBottom": f"4px solid {RED}",
    }),

    # KPI row
    html.Div([
        kpi_card(f"{high_risk_n}", f"Members at high risk\n({high_risk_pct}% of total)", RED),
        kpi_card(f"€{revenue_risk:,}", "Revenue at risk\n(high-risk LTV)", RED),
        kpi_card(f"{month_churn_pct}%", "Month-to-month\nchurn rate", AMBER),
        kpi_card(f"{low_freq_churn}%", "Churn rate: members\n<1 class/week", AMBER),
        kpi_card("4–6 weeks", "Average early-warning\nwindow before cancel", GREEN),
    ], style={
        "display": "flex", "gap": "16px",
        "padding": "24px 32px 8px 32px",
        "flexWrap": "wrap",
    }),

    # Charts row 1
    html.Div([
        html.Div(dcc.Graph(figure=fig_funnel,  config={"displayModeBar": False}),
                 style={"flex": "1", "minWidth": "300px"}),
        html.Div(dcc.Graph(figure=fig_scatter, config={"displayModeBar": False}),
                 style={"flex": "1.6", "minWidth": "400px"}),
    ], style={"display": "flex", "gap": "16px", "padding": "8px 32px"}),

    # Charts row 2
    html.Div([
        html.Div(dcc.Graph(figure=fig_contract, config={"displayModeBar": False}),
                 style={"flex": "1", "minWidth": "300px"}),
        html.Div(dcc.Graph(figure=fig_freq,     config={"displayModeBar": False}),
                 style={"flex": "1", "minWidth": "300px"}),
        html.Div(dcc.Graph(figure=fig_social,   config={"displayModeBar": False}),
                 style={"flex": "1.2", "minWidth": "380px"}),
    ], style={"display": "flex", "gap": "16px", "padding": "8px 32px 32px 32px"}),

    # Footer
    html.Div([
        html.Span("Data sources: ", style={"fontWeight": "600"}),
        html.Span("Endomondo Fitness Trajectories (Kaggle) · Gym Customer Churn — Model Fitness (Kaggle)  ·  "),
        html.A("Live Tableau version",
               href="https://public.tableau.com/authoring/MemberRetentionRiskEarlyWarningSystem/MemberRetentionRiskOverview#1",
               target="_blank",
               style={"color": GREEN}),
    ], style={
        "padding": "12px 32px",
        "fontSize": "0.78rem",
        "color": "#888",
        "borderTop": "1px solid #e0e0e0",
        "background": "#fafafa",
    }),

], style={"fontFamily": "Arial, sans-serif", "background": "#f0f0f0", "minHeight": "100vh"})


if __name__ == "__main__":
    app.run(debug=False, port=8050)
