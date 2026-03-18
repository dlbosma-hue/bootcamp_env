# LAB7.04 — Evaluation Score Distribution Dashboard

**Author:** Dina Bosma-Buczynska
**Tool used:** Tableau Public (web)


## Overview

This lab builds an interactive stakeholder dashboard visualising LLM evaluation scores across five categories and four model versions over a 90-day period. The goal is to demonstrate the communication layer — translating analysis outputs into a format accessible to non-technical decision-makers.

## Dashboard Contents

The published Tableau Public dashboard contains four worksheets arranged in a single dashboard view:

| Sheet | Purpose |
|---|---|
| Score Distribution | Histogram of all scores (bin size 10) — shows overall performance spread |
| Scores by Category | Horizontal bar chart of average score per category, sorted descending, with overall average reference line |
| Box Plot by Category | Box-and-whisker plot showing score spread and outliers per category |
| Model Heatmap | Colour-coded matrix of average score per model × category combination |

## Note: 

This dashboard does not use separate filter widgets on the canvas; instead, clicking a bar in the Score Distribution histogram filters all other views to that score range.
Interactive filters allow drill-down by model version, category, and date range.



## Files

| File | Description |
|---|---|
| `evaluation_data.csv` | Source dataset (4,489 rows, 90 days, 5 categories, 4 models) |
| `generate_evaluation_data.py` | Script used to generate the dataset |
| `data_source.md` | Data source documentation |
| `reflection.md` | Reflection on communication layer principles |
| `dashboard_screenshot.png` | Screenshot of the final dashboard (add after publishing) |

## Data Source

See `data_source.md`. Generated synthetic data using beta distributions per category to simulate realistic evaluation score patterns.

## Notes

- Dashboard published to Tableau Public — (https://public.tableau.com/app/profile/dina.bosma/viz/LAB7_04/Dashboard1)
- No statistical jargon (p-values, confidence intervals) appears in the dashboard
- All chart titles and labels use business language
