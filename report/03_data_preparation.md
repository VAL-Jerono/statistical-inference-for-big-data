## Phase 3: Data Preparation

*Source notebooks: `KHS_Clean_Pipeline.ipynb`, `HFVS_Report_Notebook.ipynb`*

---

### 3.1 Overview

Data preparation spans seven documented pipeline stages (PL-01 through PL-07) in `KHS_Clean_Pipeline.ipynb`. Every drop, fix, and imputation decision is documented by reason — this phase constitutes the scientific record proving that the variables entering the HFVS formula are what the formula assumes them to be.

**Pipeline output shape:**

| Stage | Rows | Columns |
|---|---|---|
| Master frame (input) | 21,347 | 447 |
| After PL-03 drops | 21,347 | 277 |
| After PL-06 pruning | 21,347 | 68 |
| Final `model_ready` (output) | 21,347 | **64** |

---

### 3.2 PL-01 — Column Taxonomy

Every column in the 447-column master frame was classified by data type and role:

| Class | Count |
|---|---|
| Binary | 227 |
| Ordinal | 88 |
| Continuous | 87 |
| Free text | 25 |
| Categorical | 12 |
| Identifier | 4 |
| Zero-variance | 4 |
| **Total** | **447** |

**Zero-variance columns identified (4):** `other_savings_for_housing`, `finance_other`, `survey_tag`, `has_internet` — all had identical values across all 21,347 rows and carry no analytical signal.

**Free-text columns (25):** CAPI "other, specify" fields (e.g., `water_src_main_other`, `toilet_facility_other`) — contain empty strings and are uninformative at scale.

---

### 3.3 PL-02 — Missingness Intelligence

**Formal mechanism classification applied per column:**

| Mechanism | Count | Strategy |
|---|---|---|
| Structural | 4 | Semantic zero fill (`lp_*` → 0 where `i00=0`) |
| MAR (skip-logic) | Many | Conditional fill by renter/owner status |
| Unknown / MCAR | 373 | Stratified median (county × urban/rural) |

---

### 3.4 PL-03 — Targeted Cleaning

**Structured drop decisions (170 columns removed, all documented):**

| Drop Reason | Columns Dropped |
|---|---|
| Zero-variance | 3 |
| Free-text / unstructured | 25 |
| K-module deep missing (>85%) | 32 |
| L-module deep missing (>85%) | 22 |
| J-subitem deep missing | 20 |
| G06 aspiration subitems | 2 |
| L-finance subitems | 55 |
| D18–D20 subitems | 18 |
| Admin noise columns | 6 |
| Supply granular duplicates | 10 |
| **Total unique drops** | **170** |

**Result:** 447 → 277 columns, 21,347 rows unchanged.

**Sentinel code nullification** (SurveySolutions CAPI conventions):
Codes −1 (skipped), 98/998 (don't know), 99/999 (refused) were converted to NaN across 18 columns:

| Column | Cells Nullified |
|---|---|
| `dwelling_yr_last_renovated` | 9,507 |
| `electricity_hrs_day` | 4,644 |
| `spend_energy_other_kes` | 1,819 |
| `spend_electricity_kes` | 1,251 |
| `yrs_in_dwelling` | 783 |
| **All others** | 4,091 |
| **Total** | **20,095** |

**Physical outlier caps (P99 with justification):**

| Column | Cap Value | Rows Affected | Justification |
|---|---|---|---|
| `dwelling_yr_built` | 1920–2025 | 1 | Pre-1920 implausible for survey; >2025 future |
| `dw_area_m2` | 1,200 m² | 193 | Residential plausibility |
| `rent_actual_kes` | KES 30,000 | 57 | Monthly rent P99 cap |
| `dwelling_value_kes` | KES 20,000,000 | 111 | P99 cap |
| `water_dist_mins` | 180 mins | 71 | Extreme outliers |
| `electricity_hrs_day` | 24 hrs | 1,716 | Physical maximum |
| `spend_*` (all expenditure) | P99 per column | 2,574 total | Monthly spend realism |

**Five documented bug fixes applied:**

| Bug | Description | Fix |
|---|---|---|
| **BUG-1** | `urban_rural` coded 1=Urban, 2=Rural (KNBS convention) — analysts mistakenly used raw value | Created `is_urban` binary: Urban=1, Rural=0 |
| **BUG-2** | Hazard variables incorrectly mapped to sanitation columns (`e09__*`) | Remapped to correct enumerator-observed columns (`e02__*`, `e06`, `e07`) |
| **BUG-3** | `is_slum` averaged as continuous → mean = 243.4% | Re-derived as binary flag; subsequently failed NZV (0.9% prevalence) and excluded from D1 |
| **BUG-4** | D2 tenure source collision — `j13` and `l16b__9` both renamed `satisfied_tenure` | Resolved: `tenure_satisfied` = `j13`-derived (general tenure satisfaction) only |
| **BUG-5** | `dwelling_age_yrs` derived from wrong column (`dwelling_yr_surveyed`) | Corrected to `dwelling_yr_built` (actual construction year) |

---

### 3.5 PL-04 — Feature Engineering (Five HFVS Dimensions)

All 53 analytical features were engineered directly from `df_clean`. The leakage separation principle governs this phase: **all formula-ancestor variables are tagged in a banned-variable list** and excluded from the proxy feature set by assertion.

#### D1 — Financial Stress (12 features)

| Feature | Description | Value |
|---|---|---|
| `log_total_expenditure` | Log of total monthly HH expenditure (sum of 11 components) | Mean: 10.39 |
| `log_housing_cost` | Log of unified housing cost (rent for renters; imputed for owners) | Mean: 6.44 |
| `housing_burden_ratio` | Housing cost / total expenditure | Mean: 9.2% |
| `is_cost_burdened` | Binary: burden ratio > 30% | 6.2% of HHs |
| `utility_burden_ratio` | Utility spend / total expenditure | Mean: 41.1% |
| `any_financial_stress` | Composite flag: any D1 stress indicator active | 51.8% |
| `in_rent_arrears` | Behind on rent payments | 44.0% of renters |
| `asset_score` | Count of durable assets owned (0–15 scale) | Mean: 0.56 |
| `has_housing_insurance` | Formal housing insurance | **0.8%** |
| `owns_other_property` | Owns property beyond primary dwelling | 18.7% |
| `financial_stress_count` | Count of simultaneous stress indicators | — |
| `no_loan_access` | Zero accessible loan amount (`k27`) | **99.4%** |

> **Note on `k27`:** The corrected implementation using `k27` (accessible loan amount) — as opposed to the wrong column `k25` (willingness-to-spend, median KES 1,000,000, consistent with a lump-sum not monthly figure) — contributes genuine high-variance signal to D1.

#### D2 — Tenure Insecurity (9 features, bug-corrected)

| Feature | Rate | Weight in D2 |
|---|---|---|
| `is_renter` (from `hh_tenure_type`) | 38.1% | 25% |
| `no_land_ownership` (`i00 = 0`) | **54.5%** | 30% |
| `has_title_deed` (`lp_has_title`) | 85.1% | 10% |
| `land_dispute` (`lp_has_dispute`) | 75.4% | 5% |
| `land_registered` (`lp_is_registered`) | 78.4% | 5% |
| `no_written_lease` | 25.2% of renters | 20% |
| `rent_dispute` | 8.4% | — |
| `eviction_risk_flag` | **45.4%** (WATCH: implausibly high) | — |
| `tenure_satisfied` (`j13`) | — | — |

> **`yrs_in_dwelling` excluded (Ruling 1):** Raw values showed mean = 1,432 years — confirmed as a sentinel contamination issue (70.7% raw calendar years, 29.3% sentinel value 1.0). Correct repair requires the survey interview year which is not present in this extract.

#### D3 — Physical Hazard (8 features, expanded)

| Feature | Rate | Note |
|---|---|---|
| `flood_risk` | **19.1%** | Enumerator-observed flood zone |
| `flood_severe` | 6.5% | Severe flood zone subset |
| `landslide_risk` | **12.6%** | Enumerator-observed mudslide zone |
| `steep_terrain` | 12.4% | Terrain gradient |
| `near_waste_dump` | 99.8% | Failed NZV → excluded |
| `hazard_proximity_count` | Mean: 0.40 | Count of 11 proximity items |
| `dw_in_hazard_zone_flag` | 1.3% | Failed NZV → excluded |
| `env_hazard_any` | 99.9% | Failed NZV → excluded |

> D3 is structurally underweighted because proximity sub-columns (`e08__1` through `e08__6`) were absent from this data extract. D3 is therefore constructed from only flood and landslide zone variables, which explains its lower effective weight in the composite.

#### D4 — Dwelling Quality (10 features)

| Feature | Rate | Note |
|---|---|---|
| `floor_durable` | **62.2%** | Tiles, cement, terrazzo, marble |
| `wall_durable` | **68.3%** | Brick, stone, concrete, metal |
| `roof_durable` | **86.2%** | Iron sheets, concrete, tiles |
| `is_overcrowded` | **38.2%** | > 3 persons per room |
| `dw_n_rooms` | Mean: — | Continuous room count |
| `dw_floor_area_m2` | — | Capped at 1,200 m² |
| `structure_quality` | — | Composite of floor/wall/roof |
| `n_quality_problems` | Mean: 2.3 | Count of structural defects |
| `dwelling_age_yrs` | Mean: 13.4 (weighted) | From `dwelling_yr_built` |
| `persons_per_room` | — | Dropped (|r|=0.879 with `hh_size`) |

#### D5 — Utility Deprivation (9 features)

| Feature | Rate | Note |
|---|---|---|
| `has_electricity` | — | Grid/solar/generator connection |
| `improved_water` | — | Piped / protected well |
| `safe_water` | — | JMP improved source |
| `improved_sanitation` | — | Flush/VIP latrine |
| `no_internet` | — | No internet access |
| `has_handwash` | — | Handwashing facility (dropped: |r|=0.982 with `shared_sanitation`) |
| `cooking_fuel_clean` | — | LPG / electricity |
| `water_dist_mins` | — | Walking time to water source |
| `wsvc_sewer_conns` | Mean: 2,716 (weighted) | County sewer connections (weighted-only) |

---

### 3.6 PL-05 — Exploratory Data Analysis

**Normality assessment (size-robust verdict function):**

At n=21,347, raw Shapiro-Wilk always rejects normality (trivially significant due to statistical power). A size-robust verdict function was implemented:

- SW test run on a **fixed n=2,000 subsample**
- Effect-size criteria: |skew| < 0.5 AND |excess kurtosis| < 1.0
- When SW and effect-size disagree → labelled "approx. normal (SW rejects on power alone)"

| Variable | Skew | Excess Kurtosis | SW p (n=2000) | Verdict |
|---|---|---|---|---|
| `log_total_expenditure` | −0.058 | 0.409 | 0.0002 | **Approx. normal** |
| `log_housing_cost` | −1.132 | 0.235 | 0.000 | Non-normal |
| `housing_burden_ratio` | +2.576 | 8.967 | 0.000 | Non-normal |
| `hfvs_composite` | — | — | < 0.001 | Non-normal |
| All dimension scores D1–D5 | — | — | < 0.001 | Non-normal |

**Top-10 strongest correlates with vulnerability** (Spearman, from PL-05.5):

| Feature | Dimension | Correlation | Method |
|---|---|---|---|
| `is_cost_burdened` | D1 | +0.485 | Point-biserial |
| `financial_stress_count` | D1 | +0.385 | Spearman |
| `landslide_risk` | D3 | +0.374 | Point-biserial |
| `any_financial_stress` | D1 | +0.372 | Point-biserial |
| `eviction_risk_flag` | D2 | +0.372 | Point-biserial |
| `safe_water` | D5 | −0.372 | Point-biserial |
| `flood_risk` | D3 | +0.361 | Point-biserial |
| `has_electricity` | D5 | −0.360 | Point-biserial |
| `log_housing_cost` | D1 | +0.345 | Spearman |

**Urban vs Rural stratification** (top differences, Mann-Whitney):

| Feature | Urban Mean | Rural Mean | Difference |
|---|---|---|---|
| `wsvc_sewer_conns` | 1,536 | 1,982 | 446 connections |
| `mean_age` | 30.7 | 27.7 | 3.0 years |
| `n_quality_problems` | 1.61 | 2.95 | **−1.34 (rural worse)** |
| `hh_size` | 4.16 | 3.32 | 0.84 persons |

---

### 3.7 PL-06 — Dimensionality Control

**Mechanism-informed imputation:**
- Structural zeros: `lp_*` filled with 0 for 11,639 non-land-owning households
- MAR (owner rows): `in_rent_arrears`, `log_rent`, `no_written_lease` filled with 0 for ~9,100 owner-occupier rows
- Stratified median: 30 continuous columns imputed by county × urban/rural stratum

**NZV pruning (binary features with prevalence <3% or >97%):**
- `has_housing_insurance` (0.8%) → dropped
- `near_waste_dump` (99.8%) → dropped
- `dw_in_hazard_zone_flag` (1.3%) → dropped
- `env_hazard_any` (99.9%) → dropped

**Correlation pruning (|r| > 0.85):**

| Pair | Correlation | Kept | Dropped |
|---|---|---|---|
| `financial_stress_count` vs `any_financial_stress` | 0.901 | `financial_stress_count` | `any_financial_stress` |
| `financial_stress_count` vs `eviction_risk_flag` | 0.875 | `financial_stress_count` | `eviction_risk_flag` |
| `no_land_ownership` vs `has_title_deed` | 0.870 | `has_title_deed` | `no_land_ownership` |
| `persons_per_room` vs `hh_size` | 0.879 | `hh_size` | `persons_per_room` |
| `shared_sanitation` vs `has_handwash` | 0.982 | — | `shared_sanitation` |
| `hh_size` vs `log_hh_size` | 0.965 | `hh_size` | `log_hh_size` |

**VIF pruning (threshold = 10, iterative):**
- Final VIF check: 53 candidate features, **0 dropped**
- Maximum VIF in final set: **5.33** (`structure_quality`)
- `env_hazard_any` excluded from VIF computation (composite → VIF = ∞) but retained

**Final model_df:** 21,347 rows × 64 columns | **0 missing cells | 0 duplicate keys**

---

### 3.8 PL-07 — HFVS Construction

**Dimension scoring approach (z-score standardisation):**

Each input variable $x_{ij}$ within dimension $D_k$ is standardised:

$$z_{ij} = \frac{x_{ij} - \bar{x}_j}{\sigma_j} \times s_j$$

where $s_j \in \{+1, -1\}$ is the theoretical sign (higher value = higher vulnerability).

The raw dimension score is min-max rescaled to $[0,1]$:

$$D_k = \frac{\sum_j z_{ij} - \min}{\max - \min}$$

The composite is the equal-weight mean:

$$\text{HFVS} = \frac{D_1 + D_2 + D_3 + D_4 + D_5}{5}$$

**Effective weight validation** (confirms z-score resolves D3 suppression):

| Dimension | Std Dev | Effective Weight |
|---|---|---|
| D1 Financial Stress | 0.0789 | 14.6% |
| D2 Tenure Insecurity | 0.1004 | 18.6% |
| D3 Physical Hazard | 0.1161 | **21.5%** ← was 4.9% under min-max |
| D4 Dwelling Quality | 0.1141 | 21.1% |
| D5 Utility Deprivation | 0.1312 | 24.3% |

**Final composite statistics:**

| Metric | Value |
|---|---|
| National mean (HFVS) | **0.480** |
| Standard deviation | **0.041** |
| 90th percentile threshold | **0.533** |
| High-vulnerability (≥90th pct) | **2,154 households (10.1%)** |
| n/p ratio | **403** (rule of thumb ≥20: ✓) |

**Statistical inference readiness check:**
```
n (households)          : 21,347
p (features after VIF)  :     53
n/p ratio               :    403  ✓
Minority class (n)      :  2,154  (90th pct threshold)
MLE feasibility         : ✓  Logistic, Gaussian GLM, Fisher information all viable
```

---

*Next: Phase 4 — Modelling*
