# LAB 7.02 - Marketing Channel ROI Comparison
Dina Bosma-Buczynska

---

## Overview

This lab applies statistical analysis to a real-world style marketing dataset to produce
a defensible budget allocation recommendation across six advertising platforms.

The scenario: a CMO has asked how to allocate a $500,000 monthly budget across
Google Search, Meta, TikTok, Snapchat, Google Display, and LinkedIn, based on
channel performance data. The analysis must be statistically rigorous to avoid
shifting budget to underperforming channels based on false positives.

---

## Dataset

**Name:** Digital Marketing Performance Dataset (Synthetic, Benchmark-Based)
**Source:** Kaggle - https://www.kaggle.com/datasets/alinaboulsi/digital-marketing-performance-dataset
**Files used:**
- `digital_marketing_dataset_30k.csv` - 30,000 daily ad records across 6 platforms
- `data_dictionary.csv` - column definitions
- `README_DATASET.md` - original dataset documentation

The dataset is synthetically generated using real platform benchmark KPI ranges.
It is suitable for statistical analysis practice but should not be used for real budget decisions.

---

## How to Run

1. Place all CSV files in the same folder as the notebook
2. Open `data_exploration_final.ipynb` in Jupyter Notebook or JupyterLab
3. Run all cells top to bottom (Kernel > Restart and Run All)
4. Charts render inline; the Executive Report appears as the final cell

**Dependencies:** numpy, pandas, matplotlib, seaborn, scipy
Install with: `pip install numpy pandas matplotlib seaborn scipy`

---

## Key Findings

- **Google Search** has the lowest CPA ($12.66 aggregate) and highest conversion rate
  (1.882%) and is the clear top performer on every metric
- **LinkedIn** has significantly higher CPA than all other platforms
  (76.3% higher than Google Search, Cohen's d = 0.395, p < 1e-29 FDR-corrected)
- **Meta, TikTok, and Snapchat** are statistically indistinguishable from each other
  in CPA - no significant differences between them at any correction level
- **9 of 15 platform pairs** show statistically significant CPA differences;
  all 9 survive both Bonferroni and BH-FDR correction
- **Power analysis** confirms findings are reliable: all significant pairs show
  CPA gaps of 18% or more, above the 15% threshold where 90 days of data
  provides adequate power (power >= 0.999 at 90 days)

### Recommended $500K Budget Allocation

| Platform | Budget ($) | Share |
|---|---|---|
| Google Search | 194,007 | 38.8% |
| Meta | 85,159 | 17.0% |
| Snapchat | 79,055 | 15.8% |
| TikTok | 78,556 | 15.7% |
| Google Display | 63,223 | 12.6% |
| LinkedIn | 0 | 0.0% |

---

## Deliverables

| File | Contents |
|---|---|
| `data_exploration_final.ipynb` | Complete notebook: all 5 parts + Executive Report |
| `marketing_data_clean.csv` | Cleaned dataset saved during Part 1 |
| `executive_memo.md` | Standalone executive memo for CMO |
| `README.md` | This file |

Charts are generated and displayed inline when the notebook is run.

---

## Approach

**Part 1 - Data:** Loaded and cleaned 30,000 rows. Computed derived KPIs
(CPA, ROAS, CTR, conversion rate) from raw spend/clicks/conversions/revenue columns
using division-by-zero guards.

**Part 2 - Metrics:** Aggregated per platform. Visualised 6 key metrics as bar charts
and plotted per-row distributions as box plots and histograms.

**Part 3 - Statistical Tests:** Kruskal-Wallis H-test for overall CTR difference,
then pairwise Welch t-tests on CPA (15 pairs) with Cohen's d effect sizes.
Fisher's exact test for conversion rate comparisons. Applied both Bonferroni
and Benjamini-Hochberg FDR correction to all comparisons.

**Part 4 - Power Analysis:** Simulation-based empirical power function
(1,000 iterations per cell) across 4 effect sizes and 5 sample sizes.
Determined minimum data requirements for 80% power.

**Part 5 - Recommendations:** Bootstrap 95% confidence intervals for CPA per platform.
Composite ranking score (60% ROAS + 40% CPA efficiency). Budget allocation table.

---

## Assumptions and Notes

- CPA is used as the primary business metric for budget allocation because it
directly answers the CMO's question: how much does it cost to acquire one customer.
- Aggregate-level CPA (total spend / total conversions) differs from the per-row
  mean CPA used in statistical tests. The report uses per-row values for testing
  and aggregate values for the summary table - this is noted in the Executive Report.
- LinkedIn's composite score of 0.000 reflects near-zero ROAS in the
  sales-objective segment of this dataset. A minimum floor of $10,000 is
  recommended if B2B awareness objectives require LinkedIn presence.
- Power simulations assume approximately normal CPA distributions with std = 15%
  of the base CPA. Actual CPA distributions are right-skewed, so real power
  may be slightly lower than the simulation estimates.
- All findings are based on synthetic data and should not be applied to real
  platform budget decisions without validation on live data.
