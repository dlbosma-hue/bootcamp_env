# Executive Memo: Marketing Channel ROI Analysis

**To:** Chief Marketing Officer
**From:** Dina Bosma-Buczynska, Marketing Analyst
**Date:** March 17, 2026
**Dataset:** Digital Marketing Performance Dataset (Kaggle, Synthetic Benchmark-Based)
**Source:** https://www.kaggle.com/datasets/alinaboulsi/digital-marketing-performance-dataset

---

## Executive Summary

This analysis evaluates six marketing platforms (Google Search, Meta, TikTok, Snapchat, Google Display, LinkedIn) using a 30,000-row dataset simulating real platform KPI benchmarks. Statistical tests (Welch t-tests, Fisher exact, Kruskal-Wallis) were applied to identify which performance differences are genuine versus noise. All results were corrected for multiple comparisons using Bonferroni and Benjamini-Hochberg FDR corrections. A $500,000 monthly budget allocation is proposed based on a composite ROAS and CPA efficiency score.

---

## Key Findings

### Top Performing Channels by Composite Score

Channels are ranked by a composite score (60% ROAS efficiency, 40% CPA efficiency):

| Platform | CPA ($) | Composite Score | Recommended Budget ($) |
|---|---|---|---|
| Google Search | 12.66 | 1.000 | 194,007 |
| Meta | 62.81 | 0.439 | 85,159 |
| Snapchat | 68.61 | 0.407 | 79,055 |
| TikTok | 73.95 | 0.405 | 78,556 |
| Google Display | 127.03 | 0.326 | 63,223 |
| LinkedIn | 457.47 | 0.000 | 0 |

### Statistically Significant CPA Differences (FDR-corrected)

9 of 15 platform pairs show statistically significant CPA differences. All 9 also survive the more conservative Bonferroni correction.

Key findings:

- **LinkedIn vs Google Search**: CPA gap of $154.85 (76.3% higher for LinkedIn). Cohen's d = -0.395 (small effect).
- **LinkedIn is the most expensive channel by CPA** across every comparison, significantly outpriced relative to all five other platforms.
- **Google Search has the lowest CPA** (~$202.95 aggregate) and is confirmed cheaper than LinkedIn and Google Display.
- **Meta, TikTok, and Snapchat are statistically indistinguishable from each other** in CPA (no significant differences at any correction level), forming a cluster that can be treated as equivalent for budget purposes.

### Conversion Rate Comparisons (Fisher Exact Test)

All 15 platform pairs show statistically significant conversion rate differences after both correction methods. Google Search has the highest conversion rate (1.882%), while Google Display has the lowest (0.503%).

### Data Adequacy (Power Analysis)

Simulation-based power analysis (1,000 iterations per cell, base CPA $248.89, std = 15%):

| Effect Size | Min Days for 80% Power | 90-Day Dataset Status |
|---|---|---|
| 5% CPA difference | >180 days | Insufficient |
| 10% CPA difference | ~120 days | Insufficient |
| 15% CPA difference | ~60 days | Sufficient |
| 20% CPA difference | ~30 days | Sufficient |

The 9 significant pairs in this dataset show CPA differences ranging from 18% to 76%, all above the 15% threshold where 90 days of data provides adequate power.

---

## Recommendations

### Budget Allocation ($500,000/month)

- **Google Search**: $194,007 (38.8%)
- **Meta**: $85,159 (17.0%)
- **Snapchat**: $79,055 (15.8%)
- **TikTok**: $78,556 (15.7%)
- **Google Display**: $63,223 (12.6%)
- **LinkedIn**: $0 (0.0%)

Note: LinkedIn scores 0.000 on the composite scale due to high CPA and near-zero ROAS in the sales-objective segment. A minimum floor of $10,000 is recommended for LinkedIn if B2B awareness objectives require it, funded by reducing the Google Search allocation by 2%.

### Strategic Actions

1. **Reallocate away from LinkedIn for performance objectives.** LinkedIn's CPA is statistically and practically higher than every other channel tested. Consider limiting LinkedIn to brand and awareness campaigns where CPM, not CPA, is the primary metric.
2. **Protect and grow Google Search.** Confirmed lowest CPA with the highest conversion rate. Additional budget here has the most reliable ROI evidence.
3. **Treat Meta, TikTok, Snapchat as a cluster.** No statistically significant CPA differences between them. Allocate proportionally and monitor weekly. Creative differentiation likely matters more than channel shifts within this group.
4. **Extend data collection to 120 days** before drawing conclusions on CPA differences smaller than 10%. The current dataset is adequate for large effects but underpowered for smaller ones.

---

## Statistical Caveats

- **Synthetic dataset**: This dataset was generated using benchmark KPI ranges and is not real advertiser data. Findings reflect the assumptions built into the simulation, not actual platform performance.
- **Multiple comparisons correction applied**: Both Bonferroni (very conservative) and Benjamini-Hochberg FDR (less conservative) corrections were used. All 9 significant CPA pairs survived both methods, strongly indicating these are not false positives.
- **Statistical vs practical significance**: Most Cohen's d values are in the negligible-to-small range. Large sample sizes (1,352 to 4,094 rows per platform) allow detection of very small effects. The LinkedIn finding has both statistical significance AND practical importance. Other pairs may be statistically significant but not worth acting on individually.
- **95% bootstrap confidence intervals**: Calculated for CPA per platform. LinkedIn CI does not overlap with any other platform, confirming the finding robustly.
- **Right-skewed CPA distributions**: CPA is not normally distributed. Kruskal-Wallis and Welch t-tests were used to accommodate this. Power simulations assume approximate normality, so actual power may be slightly lower than estimated for skewed data.
- **External factors not modeled**: Audience overlap, creative performance, bid competition, seasonality, and campaign objective mix all affect real-world CPA and are not captured in this dataset.

---

## Next Steps

1. Present the budget reallocation proposal to the CMO, focusing on the LinkedIn finding as the strongest statistical evidence with the largest dollar impact.
2. Implement the revised $500K allocation and run a prospective 90-day test with identical objectives per platform.
3. Build a weekly CPA monitoring dashboard to detect divergence within the Meta/TikTok/Snapchat cluster.
4. After 120 days of live data, re-run the full statistical analysis to validate findings with real platform behavior.