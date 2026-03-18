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

## Filters

The dashboard has one explicit filter control: **Score**.

### Active Filters

**Score filter (range / discrete values):** The filter is labeled "Score" and offers selectable values 7,751 · 10,000 · 12,000 · 14,000 · 16,000 · 17,116. This filter works as a range or subset filter on the numeric score field, limiting all views to rows whose total count of scores matches the selected value(s).

### How it affects each view

| View | Effect |
|---|---|
| Score Distribution | Bars are re-computed only for records in the filtered subset, changing both counts and the visible distribution of binned scores |
| Average Score by Category | The average score per category (code, instruction_following, knowledge, reasoning, tool_calling) is recalculated over filtered records only |
| Score Spread by Category | Plotted points (Avg. Score per category) update to reflect the filtered subset — spread and relative positions may shift |
| Model Performance by Category | Square sizes (Score) for each Model Version–Category combination are recalculated on filtered data only, so model comparisons reflect that subset |

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
