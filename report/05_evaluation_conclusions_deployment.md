## Phase 5: Evaluation

*Source notebooks: `HFVS_CRISP_DM_Final.ipynb`, `222331_HVFS_Housing.ipynb`, `HFVS_Report_Notebook.ipynb`*

---

### 5.1 Consolidated Hypothesis Test Results

All 12 hypothesis tests resolved — both parametric and nonparametric — with decisions, effect sizes, and policy implications:

| Test | Type | RQ | Decision | Effect Size | Agreement |
|---|---|---|---|---|---|
| **T1** One-sample t (HFVS vs 0.50) | Parametric | Distributional | REJECT H₀ | — | N/A |
| **T2** Two-sample t (urban vs rural) | Parametric | Group diff | REJECT H₀ | d=0.137 (small) | ✓ with N1 |
| **T3** One-way ANOVA (education tier) | Parametric | Group diff | REJECT H₀ | η²=0.013 (small) | ✓ with N2 |
| **T4** Simple OLS (log_expend → D1) | Parametric | Predictive | REJECT H₀ | R²=0.153 | — |
| **T5** Multiple OLS (composite) | Parametric | Predictive | REJECT H₀ | R²=0.14 | — |
| **T6** CIs for dimension means | Parametric | Descriptive | All ≠ 0.5 | Narrow CIs | — |
| **M1** MLE Beta fit | Parametric | Distributional | Fit good | AIC −62,192 | — |
| **N1** Mann-Whitney U (urban vs rural) | Nonparametric | Group diff | REJECT H₀ | r=0.067 (small) | ✓ with T2 |
| **N2** Kruskal-Wallis (education) | Nonparametric | Group diff | REJECT H₀ | ε²=0.013 (small) | ✓ with T3 |
| **N3** Spearman correlation (D1 vs composite) | Nonparametric | Construct | REJECT H₀ | ρ=0.200*** | — |
| **N4** KS normality (all dimensions) | Nonparametric | Assumption | All non-normal | — | Justifies dual approach |
| **N5** Wilcoxon signed-rank (D1 vs D5) | Nonparametric | Construct | REJECT H₀ | r=0.053 (small) | — |
| **N6** Bootstrap CI (gap ratio) | Nonparametric | Predictive | Fail to reject | CI overlap | — |

**Key evaluation finding:** All six substantive comparisons (urban/rural, education tier, D1 vs D5) yield **identical decisions** under both parametric and nonparametric methods. This convergence confirms that findings are robust and not artefacts of distributional assumptions.

---

### 5.2 Interpretation of Key Findings

**HFVS Construct Validity**

The composite mean of 0.480 (SD=0.041) is tightly distributed around the lower half of the [0,1] scale, as expected given z-score standardisation. The top-quartile high-vulnerability threshold (≥75th percentile) captures approximately **5,337 households** — a pragmatically significant population for policy targeting.

**Parametric-Nonparametric Agreement**

Effect sizes are consistently *small* across all tests (Cohen's d < 0.2; ε² < 0.02; r < 0.13 for Mann-Whitney). This is the most important substantive finding:

> **The HFVS is not primarily driven by observable demographic proxies (gender, education, urban stratum) but by a multi-dimensional configuration of dwelling characteristics, tenure arrangements, and utility access.** This is precisely what the index was designed to capture — and the small effect sizes of demographic predictors confirm that the composite is not reducible to a simple income or education proxy.

**Urban-Rural Paradox**

Urban households score higher on HFVS despite generally higher incomes. Dimension-level analysis reveals:
- D2 Tenure Insecurity and D1 Financial Stress drive the urban premium (informal settlement tenure, higher rent burdens)
- D5 Utility Deprivation is considerably worse in rural areas

The offsetting effect compresses the overall composite difference, yielding small effect sizes even though specific dimensions show larger urban-rural gaps.

**Education Gradient**

The monotone education gradient (no education > primary/secondary > post-secondary) is statistically robust, but η²=0.013 indicates education explains only **1.3% of HFVS variance**. Education improves income → reduces D1 Financial Stress, but does not insulate households from D3 Physical Hazard or D4 Dwelling Quality, which depend on location and housing stock.

**Regression Findings**

- Simple OLS (log_expenditure → D1): R²=0.153 → 84.7% of D1 variance is non-income
- Multiple OLS (all proxies → composite): R²=0.14 → **86% of composite variance requires the full five-dimension measurement instrument**

---

### 5.3 Model Performance Summary

The LightGBM/XGBoost gradient boosting ensemble is recommended as the production proxy model:

| Metric | LightGBM | XGBoost | Blend |
|---|---|---|---|
| Test AUC (classification) | 0.7779 | 0.7777 | **0.7820** |
| Test R² (regression) | 0.3674 | 0.3681 | **0.3716** |
| Spatial CV AUC | 0.6503 | 0.6538 | ~0.65 |
| Spatial correction | −0.127 | −0.124 | — |
| Brier score | 0.1872 | 0.1870 | **0.1857** |

**Spatial correction interpretation:** The ~0.127 AUC drop from standard CV to spatial CV is not a model failure — it is an honest correction for within-county learning. The spatially-corrected AUC of ~0.65 is the figure relevant to deployment on new counties.

**TabNet and MLP underperform** (R² ~0.21–0.23 vs 0.37 for gradient boosting), confirming that deep learning adds no benefit over gradient boosting on this structured, tabular feature set.

---

### 5.4 Limitations

| Code | Limitation | Impact on Results |
|---|---|---|
| **L1** | `yrs_in_dwelling` excluded (70.7% sentinel contamination) | D2 loses one input (~2.9% composite weight) |
| **L2** | `is_slum_binary` failed NZV (0.9% prevalence after re-derivation) | D1 loses slum-settlement signal for urban analysis |
| **L3** | `eviction_risk_flag` / `in_rent_arrears` implausibly high (45.4% / 44.0%) | D2/D1 may be inflated; retained as WATCH items |
| **L4** | County-level supply features are constants within county | Between-county variance only; no within-county signal |
| **L5** | Survey weight ratio 327.6× | Unweighted national statistics are unrepresentative |
| **L6** | Single cross-section (2023/24) | Causal claims impossible; HFVS is correlational |
| **L7** | D3 proximity sub-columns absent from extract | D3 effective weight ~21% rather than full theoretical 20% |
| **L8** | k25 (willingness-to-spend) median = KES 1,000,000 | Inconsistent with monthly figure; excluded from D1 |

---

## Phase 6: Conclusions

### 6.1 Answers to Research Questions

**RQ1 — Distributional:**
The national HFVS composite mean is **0.480** (SD=0.041), significantly below the neutral midpoint of 0.5 (p<0.001). All five dimension scores are significantly non-normal. The Beta(28.67, 44.97) distribution provides a good parametric approximation (AIC=−62,192). The distribution is right-skewed in burden components — aggregate affordability is moderate, but a severe vulnerable tail exists.

**RQ2 — Group Differences:**
All group differences are statistically highly significant (all p<0.001) but **uniformly small in effect size**:
- Urban > rural HFVS (d=0.137)
- No education > post-secondary (η²=0.013)
- Female-headed > male-headed (d=0.07)
- D5 > D1 at household level (Wilcoxon p<10⁻¹⁴)

The small effect sizes confirm the composite is not reducible to demographic proxies.

**RQ3 — Predictive Validity:**
The HFVS can be approximated from proxy variables at **Test AUC ~0.778** (LightGBM/XGBoost) and **spatial CV AUC ~0.65**. The spatially-corrected figure is the honest external validity estimate. Proxy approximation is viable for operational screening — a 10-minute intake form can identify high-vulnerability households with meaningful accuracy.

---

### 6.2 Major Findings Summary

1. **Multidimensionality is real and necessary:** Demographic proxies explain only 14% of composite variance. The remaining 86% requires the full five-dimension measurement.

2. **Utility deprivation dominates:** D5 is systematically higher than D1 at household level (Wilcoxon p<10⁻¹⁴), challenging the conventional framing that financial stress is the primary housing vulnerability driver.

3. **The triple-exposed population = 1.80%:** This is the exact household profile — flood-adjacent, tenure-insecure, rent-stressed — that experienced the highest casualty rates in April 2024. Every one was identifiable in KHS data before the disaster.

4. **Urban households are more vulnerable than rural** on the composite, despite higher incomes, due to informal tenure and rent burden overwhelming utility access advantages.

5. **County-level instruments are most efficient where vulnerability is highest** (negative Gini-HFVS correlation ρ=−0.368), because highly vulnerable counties are internally more homogeneous.

6. **Finance exclusion is structural:** 99.4% of households have zero accessible loan amount; 97.7% have no formal housing finance of any kind. This is a supply-side failure, not demand failure.

---

## Phase 7: Recommendations

### 7.1 Stakeholder-Specific Policy Recommendations

| Stakeholder | Recommendation | Evidence | Priority |
|---|---|---|---|
| **IRA** | Use county HFVS percentile as premium-loading variable in property microinsurance. Load above Fire Domestic 28.4% baseline proportionally to county HFVS decile. | N5 Wilcoxon + KS test + county ranking | **Immediate** |
| **State Dept. Housing / AHP** | Use HFVS county rank as mandatory input in site selection. Prioritise top-missed counties from the alignment table. | County vulnerability ranking | **Immediate** |
| **KMRC** | Expand concessional lending to counties in bottom-quartile mortgage penetration AND top-quartile HFVS — the finance exclusion quadrant. | Phase 2 finance exclusion data | **Short-term** |
| **NGOs / UN-Habitat** | Target D5 utility interventions (rural electrification, WASH) in ASAL counties with highest utility deprivation dimension scores. | D5 dimension scores by county | **Short-term** |
| **Insurance underwriters** | Develop parametric flood-trigger products in counties where triple-exposed households exceed 15% of population. | Triple-exposure analysis | **Medium-term** |
| **KNBS** | Expand next KHS round to include: asset values, formal insurance coverage, claims history, explicit monthly housing budget question (replace k25). | Limitations L1–L8 | **Long-term** |

---

### 7.2 Research Next Steps

1. **Longitudinal validation** (2026/27): Panel survey re-interviewing KHS households matched against insurance claims records — the definitive actuarial test of HFVS predictive validity.

2. **Actuarially calibrated dimension weights:** When household-level claims records are linked via regulatory data-sharing (IRA × KNBS), dimension weights should be re-estimated via Poisson regression of claim frequency on dimension scores.

3. **Sub-county spatial CV:** Current spatial grouping is at county level. Ward-level grouping would strengthen internal validity and enable more granular targeting.

4. **Confirmatory Factor Analysis (CFA):** A principled test of the five-factor structure assumed by the HFVS composite.

5. **East African generalisation:** The five-dimension structure, WHO/JMP-aligned material codes, and CRISP-DM pipeline are directly transferable to Uganda's NHSurvey and Tanzania's National Panel Survey.

---

## Phase 8: Deployment

### 8.1 Production Architecture

**Deployment URL:** https://statistical-inference-for-big-data.vercel.app/

The deployment is a static web application (`index.html`) hosted on Vercel, providing a public-facing interactive interface to the HFVS analysis. The deployment represents the operationalisation end-point of the CRISP-DM pipeline.

**Primary product — Continuous HFVS Score:**
- Produced per household from observable demographic, dwelling, and county features
- Accompanied by county and national percentile rank for non-technical interpretation
- Example output: *"This household scores 0.42 on the HFVS — 67th national percentile; above-average vulnerability driven primarily by D2 Tenure Insecurity and D5 Utility Deprivation"*

**Secondary product — Configurable binary high-vulnerability flag:**

| Stakeholder | Recommended Threshold | Rationale |
|---|---|---|
| IRA (insurance targeting) | 90th percentile (≥0.533) | High-precision targeting |
| State Dept. for Housing | 80th percentile (≥ ~0.520) | Broader programme eligibility |
| KMRC (mortgage supplement) | 75th percentile | Widest eligible pool |

> **The threshold is NOT baked into the model.** It is applied post-scoring, allowing stakeholders to adjust as budgets and policy objectives change.

**Production model recommendation:** LightGBM/XGBoost calibrated blend
- Handles missing values natively
- Survey-weighted via `sample_weight`
- Spatially validated (county-grouped CV)
- Calibrated probability outputs suitable for actuarial use
- Deployable as a lightweight API endpoint

---

### 8.2 Open Science Commitment

The full pipeline is available at: **github.com/VAL-Jerono/statistical-inference-for-big-data**

All figures, CSV output tables, and the master parquet file (`master_hfvs_v4_corrected.parquet`) are reproducible from a single top-to-bottom run on Google Colab Pro+. The repository is structured for reuse:

- Utility functions in importable modules
- Data directory documents expected parquet file structure
- Codebook JSON files provide column-label mappings for future KHS rounds
- CRISP-DM pipeline is directly adaptable to other East African country surveys

---

### 8.3 Closing Statement

The Housing Financial Vulnerability Score is not a solution to Kenya's two-million-unit housing deficit. **It is the evidence layer that every other solution has been operating without.**

- The AHP can now select sites by vulnerability rank, not land availability.
- The IRA can load premiums by county HFVS, not geographic intuition.
- The KMRC can target concessional lending by the finance-exclusion quadrant, not by existing customer relationships.

The April 2024 floods demonstrated, catastrophically, what the absence of this measurement instrument costs. The measurement gap does not close by itself — it closes when this framework is operationalised, linked to real IRA loss data, and embedded in the policy instruments designed to reach Kenya's most vulnerable housing market participants.

---

## References

1. Cohen, J. (1988). *Statistical Power Analysis for the Behavioral Sciences* (2nd ed.). Lawrence Erlbaum Associates.
2. Efron, B. (1979). Bootstrap methods: Another look at the jackknife. *Annals of Statistics*, 7(1), 1–26.
3. Hodges, J. L., & Lehmann, E. L. (1963). Estimates of location based on rank tests. *Annals of Mathematical Statistics*, 34(2), 598–611.
4. Kenya National Bureau of Statistics (KNBS). (2024). *Kenya Housing Survey 2023/24: Survey Methodology and Results*. KNBS, Nairobi.
5. Kruskal, W. H., & Wallis, W. A. (1952). Use of ranks in one-criterion variance analysis. *Journal of the American Statistical Association*, 47(260), 583–621.
6. Levene, H. (1960). Robust tests for equality of variances. In I. Olkin (Ed.), *Contributions to Probability and Statistics* (pp. 278–292). Stanford University Press.
7. Mann, H. B., & Whitney, D. R. (1947). On a test of whether one of two random variables is stochastically larger than the other. *Annals of Mathematical Statistics*, 18(1), 50–60.
8. Pedregosa, F., et al. (2011). Scikit-learn: Machine learning in Python. *Journal of Machine Learning Research*, 12, 2825–2830.
9. Seabold, S., & Perktold, J. (2010). Statsmodels: Econometric and statistical modeling with Python. *Proceedings of the 9th Python in Science Conference*.
10. Shapiro, S. S., & Wilk, M. B. (1965). An analysis of variance test for normality (complete samples). *Biometrika*, 52(3–4), 591–611.
11. Spearman, C. (1904). The proof and measurement of association between two things. *American Journal of Psychology*, 15(1), 72–101.
12. Tukey, J. W. (1949). Comparing individual means in the analysis of variance. *Biometrics*, 5(2), 99–114.
13. Virtanen, P., et al. (2020). SciPy 1.0: Fundamental algorithms for scientific computing in Python. *Nature Methods*, 17, 261–272.
14. Wilcoxon, F. (1945). Individual comparisons by ranking methods. *Biometrics Bulletin*, 1(6), 80–83.
15. World Bank Open Data. (2024). Kenya housing and urban development indicators. https://data.worldbank.org
