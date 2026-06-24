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
