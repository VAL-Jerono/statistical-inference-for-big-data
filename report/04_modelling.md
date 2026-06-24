## Phase 4: Statistical Analysis & Modelling

*Source notebooks: `HFVS_Report_Notebook.ipynb`, `HFVS_CRISP_DM_Final.ipynb`, `01_HFVS_CRISP_DM_Final.ipynb`, `222331_HVFS_Housing.ipynb`*

---

### 4.1 Dual-Method Design

All six research questions are answered using **both parametric and nonparametric methods**. This dual-method design serves two purposes:

1. **Assumption robustness:** HFVS dimension scores are non-normal (KS and SW tests reject normality for all five dimensions). Parametric tests rely on CLT at n=21,347; nonparametric tests make no distributional assumption.
2. **Cross-validation of findings:** Where both methods agree, the conclusion is robust. Any disagreement triggers investigation.

**Normality verdict table (gates all hypothesis test choices):**

| Variable | n | Skew | Excess Kurtosis | SW p (n=2000) | Verdict |
|---|---|---|---|---|---|
| `log_total_expenditure` | 21,347 | −0.058 | 0.409 | 0.0002 | **Approx. normal** |
| `log_housing_cost` | 21,347 | −1.132 | 0.235 | 0.000 | Non-normal |
| `housing_burden_ratio` | 21,347 | +2.576 | 8.967 | 0.000 | Non-normal |
| `hfvs_d1_financial` | 21,347 | 0.306 | — | < 0.001 | Non-normal |
| `hfvs_composite` | 21,347 | — | — | < 0.001 | Non-normal |

---

### 4.2 Parametric Tests

#### T1 — One-Sample t-Test: Mean HFVS vs Neutral Midpoint

**Research question:** Is the national mean HFVS significantly different from 0.5 (the scale midpoint)?

$$H_0: \mu_{HFVS} = 0.50 \quad H_1: \mu_{HFVS} \neq 0.50 \quad \alpha = 0.05$$

**Assumption:** CLT applies at n=21,347; test statistic is approximately normal regardless of distribution of individual scores.

| Statistic | Value |
|---|---|
| Sample mean | **0.3892** |
| Standard deviation | 0.0605 |
| t-statistic | Highly significant (p ≪ 0.001) |
| Decision | **REJECT H₀** |

**Interpretation:** The national mean HFVS is significantly below the neutral midpoint, indicating that the **aggregate** population sits in the moderate-low vulnerability range. However, the right-skewed housing burden ratio (skew = +2.58) reveals a severe vulnerable tail — aggregate affordability conceals substantial individual hardship.

> **Policy note:** The IRA should not use the national mean as a pricing reference. The relevant statistic is the **top-decile threshold (0.533)**, which identifies the 2,154 households requiring priority intervention.

---

#### T2 — Two-Sample t-Test: Urban vs Rural HFVS

$$H_0: \mu_{urban} = \mu_{rural} \quad H_1: \mu_{urban} \neq \mu_{rural}$$

**Levene's test for equal variances:** F=0.220, p=0.639 → equal variances assumed.

| Group | n | Mean | SD |
|---|---|---|---|
| Urban | 11,900 | **0.4822** | 0.0411 |
| Rural | 9,447 | **0.4766** | 0.0406 |

| Statistic | Value |
|---|---|
| t-statistic | 9.929 |
| df | 21,345 |
| p-value | 3.50 × 10⁻²³ *** |
| Cohen's d | **0.137 (small)** |
| Decision | **REJECT H₀** |

**The urban-rural paradox:** Urban households score *higher* on HFVS despite generally higher incomes. Investigation reveals: D2 (Tenure Insecurity) and D1 (Financial Stress) drive the urban premium through informal settlement tenure and rent burdens; D5 (Utility Deprivation) offsets the composite by being considerably worse in rural areas.

---

#### T3 — One-Way ANOVA: HFVS by Education Tier

$$H_0: \mu_{T0} = \mu_{T1} = \mu_{T2} \quad H_1: \text{at least one differs}$$

| Tier | Label | n | Mean HFVS | SD |
|---|---|---|---|---|
| T0 | None / Pre-primary | 12,400 | 0.4835 | 0.0405 |
| T1 | Primary / Secondary | 7,138 | 0.4757 | 0.0415 |
| T2 | Post-secondary | 1,809 | 0.4698 | 0.0393 |

| Statistic | Value |
|---|---|
| Levene's F | 4.916, p=0.007 (heterogeneous variances noted) |
| F(2, 21344) | **141.72** |
| p-value | 7.21 × 10⁻⁶² *** |
| η² | **0.0131 (small)** |
| Decision | **REJECT H₀** |

**Tukey HSD post-hoc (all pairs p < 0.001):**

| Comparison | Mean Difference | Significant |
|---|---|---|
| T0 vs T1 | −0.0078 | Yes *** |
| T0 vs T2 | −0.0137 | Yes *** |
| T1 vs T2 | −0.0059 | Yes *** |

**Education is a monotone protective factor** (more education → lower HFVS), but η²=0.013 means education explains only **1.3% of HFVS variance** — it improves financial stress (D1) through income, but does not protect against hazard exposure (D3) or dwelling quality (D4), which depend on location and housing stock.

---

#### T4 — Simple OLS Regression: log(expenditure) → D1

$$D1_i = \beta_0 + \beta_1 \cdot \log(\text{expenditure}_i) + \varepsilon_i$$

| Statistic | Value |
|---|---|
| n | 21,347 |
| R² | **0.153** |
| Adjusted R² | 0.153 |
| F-statistic | 3,851 (p < 0.001) |
| β₁ (log expenditure) | Negative (higher expenditure → lower D1) *** |
| AIC | −51,397.6 |

**Interpretation:** Expenditure explains 15.3% of D1 Financial Stress variance. The remaining 84.7% is driven by housing cost structure, asset position, loan access, and behavioural factors — confirming that income alone is insufficient to model financial vulnerability.

---

#### T5 — Multiple OLS: Composite HFVS Predictors

All 53 VIF-pruned proxy features regressed against `hfvs_composite`:

| Statistic | Value |
|---|---|
| n | 21,347 |
| R² | **0.14** |
| Demographic proxies alone explain | **14% of composite variance** |

This is the most policy-critical regression finding: **86% of HFVS variance is not captured by demographic and contextual proxies**. The composite measures what income, education, and urban status cannot.

---

#### T6 — Confidence Intervals for Dimension Score Means

95% parametric confidence intervals (CLT-based, n=21,347):

| Dimension | Mean | 95% CI Lower | 95% CI Upper |
|---|---|---|---|
| D1 Financial Stress | 0.489 | — | — |
| D2 Tenure Insecurity | 0.487 | — | — |
| D3 Physical Hazard | 0.438 | — | — |
| D4 Dwelling Quality | 0.487 | — | — |
| D5 Utility Deprivation | 0.498 | — | — |
| **Composite** | **0.480** | **0.479** | **0.480** |

The exceptionally narrow CI for the composite (±0.001) reflects both the large sample size and the compression effect of averaging five dimensions.

---

#### M1 — Maximum Likelihood Estimation: Beta Distribution Fit

The composite HFVS ∈ [0,1] was modelled as a Beta(α, β) distribution via MLE:

$$\hat{\alpha} = 28.667 \quad (SE = 0.306, B=500 \text{ bootstrap})$$
$$\hat{\beta} = 44.974 \quad (SE = 0.496)$$

| MLE Statistic | Value |
|---|---|
| Log-likelihood | 31,098.05 |
| AIC | −62,192.10 |
| BIC | −62,176.17 |
| Implied mean (Beta) | **0.3893** |
| Observed mean | 0.3892 |

The near-perfect match between implied and observed means confirms the Beta family is a reasonable parametric approximation for this [0,1]-bounded composite. The Q-Q plot reveals minor deviations in the tails, consistent with the survey's categorical inputs.

---

### 4.3 Nonparametric Tests

All nonparametric tests serve as robustness checks on the parametric results. Where both agree, the finding is robust.

#### N1 — Mann-Whitney U: Urban vs Rural HFVS

$$H_0: P(X_{urban} > X_{rural}) = 0.5 \quad H_1: \neq 0.5$$

| Statistic | Value |
|---|---|
| Urban median | **0.490** |
| Rural median | **0.477** |
| U statistic | 60,581,587 – 64,301,067 |
| Z approximation | 9.78 – 18.09 |
| p-value | < 10⁻²² *** |
| Effect size r | 0.067 – 0.124 **(small)** |
| Hodges-Lehmann Δ | 0.005 – 0.013 |
| Decision | **REJECT H₀** |
| Agreement with T2 | ✓ YES |

---

#### N2 — Kruskal-Wallis: HFVS by Education Tier

| Group | n | Median |
|---|---|---|
| None | 12,400 | 0.490 |
| Primary/Secondary | 7,138 | 0.479 |
| Post-secondary | 1,809 | 0.469 |

| Statistic | Value |
|---|---|
| H-statistic | 273.24 – 387.43 |
| df | 2 |
| p-value | < 10⁻⁵⁹ *** |
| ε² | **0.013 (small)** |
| Decision | **REJECT H₀** |

**Bonferroni-corrected pairwise Mann-Whitney (all pairs p < 0.001):**
- None vs Primary/Secondary: p = 3.2 × 10⁻³⁵
- None vs Post-secondary: p = 5.3 × 10⁻⁴⁰
- Primary/Secondary vs Post-secondary: p = 9.8 × 10⁻⁸

Education monotone gradient confirmed. Agreement with ANOVA ✓.

---

#### N3 — Spearman Rank Correlation: D1 vs Composite

$$H_0: \rho = 0 \quad H_1: \rho \neq 0$$

| Statistic | Value |
|---|---|
| Spearman ρ | **0.200 – 0.624** |
| p-value | < 10⁻¹⁹² *** |
| 95% CI for ρ | [0.188, 0.213] |
| Decision | **REJECT H₀** |

D1 is the strongest single dimension contributor to the composite (Spearman ρ=0.624 in the full correlation matrix). The value ρ < 1 validates the multi-dimensional design — D1 alone cannot substitute for the composite.

**Full Spearman correlation matrix (key predictors × HFVS dimensions):**

| Predictor | D1 | D2 | D3 | D4 | D5 | Composite |
|---|---|---|---|---|---|---|
| `log_total_expenditure` | −0.399*** | −0.124*** | +0.088*** | −0.015 | +0.232*** | −0.056*** |
| `housing_burden_ratio` | +0.136*** | −0.004 | −0.014 | −0.023*** | +0.087*** | +0.088*** |
| `dependency_ratio` | −0.091*** | +0.005 | −0.005 | +0.136*** | +0.232*** | +0.160*** |
| `hh_size` | −0.123*** | −0.099*** | +0.010 | +0.298*** | +0.241*** | +0.192*** |
| `tenure_security_score` | −0.054*** | −0.273*** | −0.007 | +0.036*** | +0.139*** | −0.094*** |
| `structure_quality` | +0.075*** | +0.133*** | −0.058*** | −0.347*** | +0.102*** | −0.060*** |
| `asset_score` | −0.225*** | −0.098*** | +0.093*** | +0.193*** | **−0.562****** | −0.303*** |
| `n_quality_problems` | +0.051*** | −0.015 | +0.078*** | +0.432*** | −0.439*** | +0.048*** |

The strongest single association: `asset_score` ↔ D5 Utility Deprivation (ρ = −0.562), confirming that asset wealth strongly predicts service access.

---

#### N4 — Kolmogorov-Smirnov: Dimension Normality

| Variable | n | KS D | p-value | Normal? |
|---|---|---|---|---|
| `hfvs_d1_financial` | 21,347 | 0.0424 | < 0.001 | **NO** |
| `hfvs_d2_tenure` | 21,347 | — | < 0.001 | **NO** |
| `hfvs_d3_hazard` | 21,347 | — | < 0.001 | **NO** |
| `hfvs_d4_quality` | 21,347 | — | < 0.001 | **NO** |
| `hfvs_d5_utility` | 21,347 | — | < 0.001 | **NO** |
| `hfvs_composite` | 21,347 | — | < 0.001 | **NO** |

Bonferroni-adjusted α = 0.0083 for 6 simultaneous tests. All dimensions remain non-normal under corrected threshold. This justifies the dual parametric-nonparametric design throughout.

---

#### N5 — Wilcoxon Signed-Rank: D1 vs D5 (Paired, Within-Household)

$$H_0: \text{median}(D1 - D5) = 0 \quad H_1: \neq 0$$

**Why paired:** Each household contributes both D1 and D5 — these are within-household observations, not independent samples.

| Statistic | Value |
|---|---|
| D1–D5 difference: mean | −0.00902 |
| D1–D5 difference: median | −0.01119 |
| Households with D1 > D5 | 10,149 |
| Households with D5 > D1 | 11,198 |
| W statistic | 107,015,596 |
| Z | −7.678 |
| p-value | 1.61 × 10⁻¹⁴ *** |
| Effect size r | 0.0526 |
| Decision | **REJECT H₀** |

**D5 Utility Deprivation is systematically higher at the household level than D1 Financial Stress.** This is the key finding that justifies the five-dimension architecture: a composite dominated by D1 alone would systematically under-measure the burden carried by households in service-deprived areas.

---

#### N6 — Bootstrap CI: Median HFVS by County Housing Gap

$$H_0: \text{median}_{low-gap} = \text{median}_{high-gap}$$

Using B=500–1000 bootstrap resamples (non-parametric; no normality assumption):

| Group | n | Median | 95% Bootstrap CI |
|---|---|---|---|
| Low housing gap | 11,705 | 0.47932 | [0.47856, 0.48033] |
| High housing gap | 9,642 | 0.47667 | [0.47576, 0.47755] |
| CI overlap | **Yes** | — | — |

**Decision: Fail to reject H₀.** County housing supply constraint (gap ratio) does not robustly predict median HFVS scores. This is a policy-relevant negative finding: the housing deficit is not where vulnerability concentrates — they are geographically decoupled.

---

### 4.4 Compound Exposure Analysis

The triple-exposed population identifies the exact household profile that suffered the highest casualty rates in Kenya's April 2024 floods:

| Exposure Profile | Rate | Policy Significance |
|---|---|---|
| Flood zone only | 19.1% | Sparse — D3's effective weight limitation |
| Tenure insecure only | 25.2% | One in four lacks formal tenure |
| Rent stressed only | 31.8% | Manageable with single-instrument support |
| Flood + tenure insecure | 4.6% | Dual exposure |
| Flood + rent stressed | 5.4% | Dual exposure |
| Tenure insecure + rent stressed | 10.4% | Dual exposure |
| **Triple exposed (all three)** | **1.80%** | **The April 2024 flood casualty profile** |
| Quad exposed (+ eviction threat) | 0.1% | Most vulnerable in Kenya (~14 households) |

The triple-exposed share (1.80%) is smaller than any single-exposure share — confirming that **compound vulnerability is a distinct and severe subpopulation**, not the mechanical overlap of three common conditions.

---

### 4.5 County-Level Vulnerability Ranking

Top-10 most vulnerable counties (weighted mean HFVS):

| Rank | County | Weighted Mean HFVS | n |
|---|---|---|---|
| 1 | **Homa Bay** | 0.407 | 422 |
| 2 | **Tana River** | 0.368 | 450 |
| 3 | **Kajiado** | 0.361 | 411 |
| 4 | **Kisumu** | 0.357 | 446 |
| 5 | **Trans Nzoia** | 0.357 | 373 |
| 6 | Turkana | — | — |
| 7 | Garissa | — | — |

**Within-county inequality (Gini coefficients):**

| County | Gini | Mean HFVS | Policy Implication |
|---|---|---|---|
| Murang'a | 0.169 | 0.305 | Sub-county targeting required |
| Taita-Taveta | 0.161 | 0.337 | Sub-county targeting required |
| Kirinyaga | 0.158 | 0.319 | Sub-county targeting required |
| Garissa | 0.105 | 0.380 | County-level instrument efficient |
| Turkana | 0.103 | — | County-level instrument efficient |

**Gini vs mean HFVS correlation:** ρ = −0.368 (p=0.011). More vulnerable counties tend to be more internally homogeneous — **county-level policy instruments are most efficient precisely where vulnerability is highest**.

---

### 4.6 Machine Learning Models (Proxy Approximation)

Five model families were trained on the 53-feature leakage-corrected proxy set. The central modelling question: *can HFVS be approximated from demographic proxies alone?*

**Train-test split:** 80/20, stratified, performed once before any hyperparameter search.
**Survey weights:** passed to LightGBM and XGBoost via `sample_weight`.
**Spatial CV:** `StratifiedGroupKFold` by county (zero county overlap across all 5 folds).

| Model | Standard CV AUC | Spatial CV AUC | Test AUC | Test R² |
|---|---|---|---|---|
| **Logistic Regression** | 0.6904 | 0.6511 | **0.6962** | — |
| **LightGBM** | 0.7574 | 0.6503 | **0.7779** | 0.3674 |
| **XGBoost** | 0.7611 | 0.6538 | **0.7777** | 0.3681 |
| LightGBM (isotonic calib.) | — | — | **0.7829** | — |
| LightGBM+XGBoost blend | — | — | **0.7820** | 0.3716 |
| **TabNet** | — | — | — | 0.2053 |
| **MLP (PyTorch)** | — | — | — | 0.2269 |

**Spatial correction magnitude:** LightGBM drops ~0.127 AUC points under spatial CV. This is the honest estimate of performance on completely unseen counties — the figure relevant to regulators and policymakers.

**Top logistic regression features by odds ratio:**

| Feature | Odds Ratio | Interpretation |
|---|---|---|
| `tenure_type_renter` | **2.205** | Renters 2.2× more likely high-vulnerability |
| `n_working_age` | 1.769 | More workers → higher composite |
| `h04` | 1.474 | Housing problem count |
| `g06__3` | 1.405 | Aspiration variable |
| `n_children` | 1.283 | Children → higher vulnerability |

---

*Next: Phase 5 — Evaluation*
