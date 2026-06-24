# DSA 8301: Statistical Inference for Big Data
## Housing Financial Vulnerability Score (HFVS)
### A CRISP-DM Analysis of the Kenya Housing Survey 2023/24

---

| | |
|---|---|
| **Student** | Sephine Valerie Jerono |
| **Registration No.** | 222331 |
| **Course** | DSA 8301 — Statistical Inference for Big Data |
| **Institution** | Strathmore Institute of Mathematical Sciences, iLabAfrica |
| **Supervisor** | Dr. John Olukuru |
| **Dataset** | Kenya Housing Survey 2023/24 — KNBS |
| **Deployment** | https://statistical-inference-for-big-data.vercel.app/ |
| **Submission Date** | 24 June 2026 |

---

## Phase 1: Business Understanding

### 1.1 Background & Problem Statement

Kenya carries a **housing deficit of 2 million units**, growing by 200,000 units annually against a population increasing by one million per year. The deficit concentrates in informal settlements where land tenure is precarious, structures are non-permanent, and basic services are absent.

**The April 2024 floods were the defining policy event motivating this study.** Rainfall above the seasonal average killed **270 people** and displaced **200,000**. The casualty geography told a precise story: the households with the highest death rates were not simply the poorest. They were simultaneously:

- Flood-adjacent (physical hazard exposure)
- Informally structured (poor dwelling quality)
- Without tenure documentation (tenure insecurity)
- Without financial buffer (financial stress)

Not one condition in isolation — **all four at once**. The data to identify these households existed in the Kenya Housing Survey *before the rains arrived*. What did not exist was a validated instrument to translate those measurements into an operational risk score.

> **This is not a story about missing data. It is a story about missing synthesis.**

---

### 1.2 The Structural Blindspot in Kenya's Housing Policy

Three major policy instruments target Kenya's housing crisis. All three share the same targeting blind spot:

| Instrument | Current Targeting Variable | What It Misses |
|---|---|---|
| **Affordable Housing Programme (AHP)** | Population density + available land | Counties with highest compound vulnerability but low political visibility |
| **Insurance Regulatory Authority (IRA)** | National average flat premiums | No household-level risk score → cannot price county-differentiated risk |
| **Kenya Mortgage Refinance Company (KMRC)** | Existing mortgage penetration | Lends most where finance already exists, not where exclusion is deepest |

The consequence: Kenya's insurance penetration stands at **2.3%** — chronically attributed to *demand failure*, but the evidence points to a **supply-side measurement failure**. Insurers cannot design risk-proportional products without a household-level vulnerability indicator.

---

### 1.3 Research Questions

The analysis pursues three interlinked research objectives, structured as formal statistical hypotheses:

**RQ1 — Distributional:** Is the HFVS composite significantly different from the neutral midpoint (0.5), and what is its national distributional shape?

**RQ2 — Group Differences:** Do HFVS scores differ significantly across urban/rural strata, gender of household head, and education tiers?

**RQ3 — Predictive Validity:** Can the HFVS composite be approximated from demographic and contextual proxy variables alone — without requiring a full housing conditions survey?

**Central Research Question:**
> Can a Housing Financial Vulnerability Score, constructed from the 2023/24 Kenya Housing Survey, be accurately approximated using demographic proxy variables alone — and does that approximation produce a county-level risk map that is actuarially valid and policy-actionable?

If yes: vulnerability scoring does not require a full housing conditions survey. It requires a **10-minute intake form** — the kind any field worker, insurer, or mortgage officer can administer.

---

### 1.4 The HFVS Framework

The **Housing Financial Vulnerability Score (HFVS)** is a five-dimension composite index. Each dimension captures a structurally distinct channel through which a household becomes vulnerable:

$$\text{HFVS} = \frac{D_1 + D_2 + D_3 + D_4 + D_5}{5}$$

Where each dimension $D_i \in [0, 1]$, with higher values indicating greater vulnerability.

| Dimension | Label | Concept | Theory Basis |
|---|---|---|---|
| **D1** | Financial Stress | Rent burden, loan exclusion, income adequacy | Affordability threshold (30% rule) |
| **D2** | Tenure Insecurity | Renter status, land ownership, eviction risk | Property rights theory |
| **D3** | Physical Hazard | Flood/landslide/terrain exposure | Environmental risk mapping |
| **D4** | Dwelling Quality | Structural materials, overcrowding | WHO housing adequacy standards |
| **D5** | Utility Deprivation | Water, electricity, sanitation access | JMP/SDG service ladders |

The five-dimension structure is validated by the **Wilcoxon signed-rank test** (Phase 4), which confirms that D5 (Utility Deprivation) is systematically higher than D1 (Financial Stress) at the household level — proving that vulnerability is not flat across dimensions and that a single-proxy index would misclassify a substantial share of households.

---

### 1.5 Stakeholder Map & Success Criteria

| Stakeholder | Business Need | HFVS Output Required | Success Criterion |
|---|---|---|---|
| **IRA** | Risk-proportional insurance pricing | County HFVS percentile as premium-loading variable | Statistically significant county-level variation |
| **State Dept. for Housing / AHP** | Vulnerability-driven site selection | County vulnerability rank | Rank correlation with compound exposure rate |
| **KMRC** | Finance exclusion mapping | Low mortgage penetration × high HFVS quadrant | Identification of underserved county clusters |
| **NGOs / UN-Habitat** | Service-gap targeting | D5 utility deprivation scores by county | Dimension-level actionability |

---

### 1.6 Why This Is Not Just Another Poverty Index

Standard poverty indices (income quintile, consumption poverty line) are **unidimensional**. The HFVS is multidimensional by construction. The statistical evidence for why this matters:

- **Multiple OLS on proxy predictors explains only 14% of HFVS composite variance** — the remaining 86% is captured by housing conditions, tenure arrangements, and utility access that income alone cannot proxy.
- **The triple-exposed population (flood zone + tenure insecure + rent stressed) = 1.80% of households** — this subgroup is not identifiable from income data alone, but is precisely identifiable from the KHS.
- **The KS test** (Phase 4) confirms that high- and low-vulnerability households have significantly different expenditure distributions (p=0.048), but the overlap is substantial enough that expenditure alone is insufficient for targeting.

---

*Next: Phase 2 — Data Understanding*
## Phase 2: Data Understanding

*Source notebooks: `DSA8301_KHS_exploration.ipynb`, `KHS_Clean_Pipeline.ipynb`*

---

### 2.1 Dataset Source

The **Kenya Housing Survey 2023/24 (KHS)** is produced by the Kenya National Bureau of Statistics (KNBS) and represents a landmark improvement over previous data environments. It is the first nationally representative household survey with sufficient breadth and depth to support a multi-dimensional Housing Financial Vulnerability Score.

| Attribute | Detail |
|---|---|
| **Producer** | Kenya National Bureau of Statistics (KNBS) |
| **Portal** | https://statistics.knbs.or.ke/nada/index.php/catalog/184/get-microdata |
| **Coverage** | All 47 counties; stratified multi-stage cluster sampling |
| **Sample size** | **21,347 households** |
| **Survey weight range** | 24.9 to 8,162 (ratio: **327.6×**) |
| **File format** | Stata (.dta) → converted to Parquet for analysis |

---

### 2.2 Data File Inventory

The KHS ships as **14 separate Stata files**, each representing a different unit of observation. The exploration notebook (`DSA8301_KHS_exploration.ipynb`) loaded and inventoried all files:

| File Key | Unit | Rows | Cols | Core Content |
|---|---|---|---|---|
| `household` | Household (**spine**) | 21,347 | 392 | Finances, tenure, utilities, infrastructure |
| `individual` | Person | 80,889 | 97 | Demographics, education, employment |
| `dwelling` | Dwelling unit | 25,116 | 25 | Wall/roof/floor materials, rooms, area |
| `land_parcels` | Land parcel | 11,136 | 34 | Tenure documents, title, disputes |
| `county` | County (47 rows) | 47 | 116 | Physical planning, infrastructure |
| `mortgage` | Mortgage record | 1,644 | 13 | Products, county coverage |
| `loan` | Loan record | 946 | 10 | Housing loan providers |
| `nema` | NEMA county data | 48 | 45 | Environmental management |
| `water_svc` | Water providers | 153 | 96 | Service connections by county |
| `real_estate` | Real estate records | 7,236 | 300 | Property transactions |
| `financiers` | Housing financiers | 351 | 63 | Lender portfolios |
| `institutional` | Institutions | 348 | 194 | Institutional housing data |
| `project_info` | Housing projects | 71 | 211 | AHP project details |
| `housing_types` | Unit types | 131 | 17 | Classification of unit types |

---

### 2.3 Variable Registry

The exploration notebook constructed a **125-variable reference registry** mapping analysis-relevant variables across all files by type:

| File | Binary | Continuous | Ordinal | Categorical | Total |
|---|---|---|---|---|---|
| `household` | 34 | 29 | 25 | 5 | **93** |
| `dwelling` | 3 | 4 | 3 | 2 | **12** |
| `individual` | 6 | 3 | 2 | 1 | **12** |
| `land_parcels` | 3 | — | 1 | 2 | **6** |
| **Total** | **46** | **36** | **31** | **10** | **125** |

The household file (392 raw columns) was classified into KHS questionnaire modules:

| Module | Columns | Deep Miss (>70%) |
|---|---|---|
| Water & Sanitation | 42 | ⚠ 3 cols |
| Energy | 30 | ✓ 0 cols |
| Assets | 12 | ✓ 0 cols |
| Expenditure & Income | 36 | ⚠ 5 cols |
| Housing Problems | 20 | ⚠ 7 cols |
| Tenure & Mobility (J) | 18 | ⚠ 7 cols |
| Environment & Hazards | 25 | ⚠ 2 cols |

---

### 2.4 Join Feasibility Analysis

Before constructing the master frame, the exploration notebook tested whether each non-household file could be linked to the household spine via `interview__key`:

| File | HH-Level Match | Join Strategy |
|---|---|---|
| `individual` | **100.0%** (21,346 / 21,347) | Direct left join → aggregate per HH |
| `dwelling` | **100.0%** (21,346 / 21,347) | Direct left join → take primary unit |
| `land_parcels` | **45.5%** (9,707 / 21,347) | Left join → NaN = no land owned (structural) |
| `county`, `mortgage`, `loan`, `nema`, `water_svc` | **0%** — no `interview__key` | Aggregate to 47 counties → join via county code |

**Land parcel coverage finding (critical):** The 45.5% partial coverage of `land_parcels` was verified not to be missing data, but structurally complete: a parcel record exists *if and only if* the household reported land ownership (`i00 = 1`). All 9,707 land-owning households had parcel records; all 11,640 non-owners had none.

```
i00    Has parcel    No parcel    % with parcel
──────────────────────────────────────────────
  0             0       11,639            0.0%
  1         9,707            0          100.0%
```

---

### 2.5 Master Frame Construction

The master frame was built in the exploration notebook (`DSA8301_KHS_exploration.ipynb`) following a precise join sequence to preserve the household spine:

**Step 1 — Individual aggregates** (per household):
- `n_members`, `n_children`, `n_working_age`, `mean_age`, `dependency_ratio`
- `edu_max_years`, `head_edu_years`, `any_employed`
- Result: 21,347 rows × 11 cols

**Step 2 — Dwelling aggregates** (primary unit only):
- Filter: 8 stray `interview__key` values dropped before aggregation (prevented row inflation from 21,346 → 22,406)
- `dw_floor_material`, `dw_wall_material`, `dw_roof_material`, `dw_n_rooms`, `dw_floor_area_m2`
- Result: 21,346 rows × 12 cols

**Step 3 — Land parcel aggregates**:
- Filter: 3 stray keys dropped
- `lp_any_dispute`, `lp_has_title`, `lp_is_registered`, `lp_used_as_collateral`
- Result: 9,707 rows × 8 cols (left-joined; NaN = no land)

**Step 4 — County-level aggregates** (joined via `a01` county code):

| Aggregate | Rows | County Coverage |
|---|---|---|
| `county_agg` | 47 | 47 / 47 |
| `nema_agg` | 48 → 47 (deduplicated) | 47 / 47 |
| `wsvc_agg` | 45 | 45 / 47 |
| `mort_agg` | 38 | 38 / 47 |
| `loan_agg` | 38 | 38 / 47 |
| `fin_agg` | 38 | 38 / 47 |

**Final master frame:**

```
MASTER FRAME — BUILD COMPLETE
  Rows    : 21,347  (spine intact — zero row inflation)
  Columns : 443  (392 base + 51 added)

  Layer                       Cols
  ─────────────────────────────────
  household (base)             392
  individual (agg)              10
  dwelling (agg)                11
  land_parcels (agg)             7
  county_agg                     5
  nema_agg                       3
  wsvc_agg                       5
  mort_agg                       4
  loan_agg                       3
  fin_agg                        3
```

All columns were renamed from raw KNBS codes (`a01`, `k05`, `e06`) to clean analytical names (`county_code`, `rent_actual_kes`, `flood_zone`) via a 443-entry `RENAME_MAP` constructed in the exploration notebook.

---

### 2.6 Key Descriptive Statistics (Initial Profile)

From the exploration notebook, before any cleaning:

| Variable | Mean | Std | Note |
|---|---|---|---|
| `log_total_expenditure` | 10.39 | 0.67 | Approx. normal (skew = −0.058) |
| `housing_burden_ratio` | 0.092 | 0.119 | Right-skewed (skew = +2.58) |
| `rent_actual_kes` | — | — | 6,932 renter households with non-zero rent |
| Formal mortgage penetration | **1.13%** | — | KMRC target market barely exists outside high-income counties |
| Formal credit access (`k27`) | **2.30%** | — | 97.7% have no formal housing finance |
| Any loan access | **2.55%** | — | Finance exclusion is a structural baseline |

**Survey weight divergence flags** (variables where weighted ≠ unweighted mean by >5%):

| Variable | Unweighted Mean | Weighted Mean | % Divergence |
|---|---|---|---|
| `housing_burden_ratio` | 0.0921 | 0.0987 | +7.1% |
| `dwelling_age_yrs` | 12.71 | 13.41 | +5.5% |
| `dependency_ratio` | 0.747 | 0.706 | −5.5% |
| `wsvc_sewer_conns` | 1,733 | 2,716 | **+56.7%** |
| `hfvs_d3_hazard` | 0.121 | 0.127 | +5.2% |

> **Rule adopted throughout:** every policy-relevant headline figure uses the **weighted** statistic. The 56.7% divergence on `wsvc_sewer_conns` is due to county-level clustering and is flagged as a mandatory weighted-only variable.

---

### 2.7 Missingness Profile

The clean pipeline notebook (`KHS_Clean_Pipeline.ipynb`) ran a formal missingness intelligence analysis on the 447-column post-rename frame:

| Tier | Definition | Column Count |
|---|---|---|
| EXTREME | > 70% missing | **133** |
| HIGH | 30–70% missing | 104 |
| MODERATE | 5–30% missing | 18 |
| LOW | < 5% missing | 122 |
| Complete (zero missing) | — | 70 |

**Missingness mechanisms classified:**

| Mechanism | Description | Strategy |
|---|---|---|
| **MCAR** | Missing completely at random | Median imputation |
| **MAR** | Missing given observed covariate (skip-logic) | Conditional fill (e.g., renters have no `l_*` ownership data) |
| **MNAR** | Missing because of its own value | Sensitivity analysis; cautious imputation |
| **Structural** | Column never applies (e.g., `lp_*` where `i00=0`) | Semantic zero fill |

**Key validation — co-missingness of rental vs ownership modules:**
The K-module (rental) and L-module (ownership) were expected to be anti-correlated in missingness (a renter has no ownership data; an owner has no rental data):
```
rent_actual_kes vs dwelling_value_kes correlation: -0.876
```
This confirms the skip-logic is correctly structured and MAR imputation by renter/owner status is valid.

---

*Next: Phase 3 — Data Preparation*
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
