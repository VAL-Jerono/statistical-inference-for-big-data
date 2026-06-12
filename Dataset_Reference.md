# Kenya Housing Survey (KHS) 2023/24 — Dataset Reference Card
*KNBS | 14 files loaded via SurveySolutions export*

---

## File Inventory

| File | Rows | Cols | Unit of Observation | Join Key |
|------|-----:|-----:|---------------------|----------|
| `HOUSEHOLD` | 21,347 | 392 | One row per household | `interview__key` |
| `INDIVIDUAL` | 80,889 | 97 | One row per household member | `interview__key` |
| `DWELLING` | 25,116 | 25 | One row per dwelling unit | `interview__key` |
| `COUNTY` | 47 | 116 | One row per county (official respondent) | `interview__key` |
| `MORTGAGE` | 1,644 | 13 | One row per mortgage product/institution | `interview__key` |
| `LOAN` | 946 | 10 | One row per housing loan product | `interview__key` |
| `LAND_PARCELS` | 11,136 | 34 | One row per land parcel (repeating roster) | `interview__key` |
| `NEMA` | 48 | 45 | One row per NEMA regional office | `interview__key` |
| `WATER_SVC` | 153 | 96 | One row per water service provider | `interview__key` |
| `REAL_ESTATE` | 7,236 | 300 | One row per real estate establishment | `interview__key` (absent — use `interview__id`) |
| `FINANCIERS` | 351 | 63 | One row per housing financier/bank | `interview__key` |
| `INSTITUTIONAL` | 348 | 194 | One row per real estate institution/developer | `interview__key` |
| `PROJECT_INFO` | 71 | 211 | One row per housing project (repeating within institution) | `interview__key` |
| `HOUSING_TYPES` | 131 | 17 | One row per housing type within a project | `interview__key` |

> **Note:** `REAL_ESTATE` is the only file missing `interview__key`; joins must use `interview__id`.  
> `PROJECT_INFO` and `HOUSING_TYPES` are nested under `INSTITUTIONAL` via `interview__key` + `c3_2__id`.

---

## Column Naming Conventions

SurveySolutions exports use a systematic prefix/suffix scheme. Learning the pattern decodes most column names without a codebook.

| Pattern | Meaning | Examples |
|---------|---------|---------|
| `a01`, `a07_1` | Module A — survey administration (county code, urban/rural) | `a01` = county code; `a07_1` = urban(1)/rural(2) |
| `b##` | Module B — individual roster (demographics, education, migration) | `b04` = sex; `b05_years` = age in years; `b07` = marital status |
| `c01_*` – `c14_*` | Module C — household utilities & assets | `c01_1` = main water source; `c04` = toilet type; `c10` = lighting fuel; `c11` = cooking fuel; `c12` = primary cooking fuel; `c14_1/2/3` = monthly expenditure (water/electricity/other energy) |
| `d01`, `d03`–`d19` | Module D — dwelling characteristics | `d01` = tenure type; `d03` = dwelling type; `d08` = wall material; `d09` = roof material; `d10` = floor material; `d12` = number of rooms; `d14` = outer wall material; `d15` = roof material (dwelling file); `d16` = floor material (dwelling file) |
| `e01`–`e09` | Module E — waste & environment | `e01` = solid waste disposal; `e03` = waste collection; `e05` = flood risk; `e08` = distance to health facility |
| `g01a`–`g01k` | Module G — household income/expenditure components | Food (a), clothing (b), education (c), health (d), transport (e), communication (f), recreation (g), housing costs (h), energy (i), other (j), remittances (k) |
| `g02`, `g03`, `g04` | Module G — rent & housing cost | `g02` = rent payment status; `g02_1` = monthly rent (KES); `g03` = tenure type; `g04` = owns other property |
| `g05__*` | Module G — housing problems experienced | Binary indicators (0/1) for overcrowding, poor water, poor sanitation, etc. |
| `g06__*` | Module G — housing aspirations/plans | Binary indicators for planned improvements |
| `h01`–`h11` | Module H — household perceptions of housing adequacy | Likert-scale ratings (1–3 or 1–5) for various dwelling attributes |
| `i00`, `i01_3`–`i13` | Module I — land parcel characteristics | `i01_3` = land ownership type; `i05` = title deed status; `i06` = land use; `i08` = land dispute; `i10` = land registration |
| `j02`–`j22` | Module J — housing tenure & mobility | `j04_1` = current tenure; `j09/j10/j11` = housing cost burden indicators; `j12_1` = years in current dwelling; `j13` = satisfied with tenure; `j17` = willing to relocate |
| `k01`–`k39` | Module K — rental market (renters only, ~32.5% of HHs) | `k05` = monthly rent; `k09` = lease type; `k21` = rent arrears; `k25` = desired purchase price |
| `l01`–`l32` | Module L — owned/self-built dwelling details | `l07/l08` = year dwelling built/surveyed; `l13` = estimated dwelling value; `l14` = land value; `l15` = monthly mortgage; `l19` = plot size; `l21` = renovation done; `l28` = year last renovated |
| `__#` suffix | Multi-select (checkbox) sub-item | e.g., `c13__2` = owns a mobile phone; `e09__9` = uses improved sanitation |
| `_other` / `_Other` | Free-text "other" response | Always paired with a categorical column |
| `_1`, `_2`, `_1_1` | Follow-up/conditional sub-questions | e.g., `c11_2_1` = monthly LPG spend if LPG used |

---

## Key Identifier & Weight Columns

| Column | File(s) | Description |
|--------|---------|-------------|
| `interview__key` | All (except REAL_ESTATE) | Household/establishment unique key — primary join key |
| `interview__id` | All | UUID from SurveySolutions — secondary identifier |
| `a01` / `countycode` | HOUSEHOLD | County code (01–47); `countycode` is string-padded version |
| `a07_1` | HOUSEHOLD, DWELLING | Urban (1) / Rural (2) |
| `serial` | HOUSEHOLD | KNBS household serial number |
| `hhid__id` | INDIVIDUAL | Member sequence number within household |
| `hhweight` | HOUSEHOLD | Household survey weight — use for all weighted estimates |
| `inw` | INDIVIDUAL | Individual survey weight |
| `land_parcels__id` | LAND_PARCELS | Parcel sequence number within household |
| `est_code` | MORTGAGE, LOAN, FINANCIERS, WATER_SVC | Establishment code for institutional surveys |

---

## Derived / Computed Columns (present in HOUSEHOLD)

These were computed by KNBS or during data processing and are ready to use:

| Column | Description |
|--------|-------------|
| `min_rent` | Minimum rent in the PSU (proxy for local rental market floor) |
| `utilities` | Binary: whether household pays for utilities (1=yes) |
| `ctymin_ut` | County-level minimum utility cost |
| `prop_util` | Proportion of income spent on utilities |
| `med_prop` | Median utility-to-income proportion (county level) |
| `med_brms` | Median number of bedrooms (county level) |
| `internet` | Whether household has internet access |
| `year_occ` | Years of occupancy category |
| `pln` | Planning status of settlement |
| `sf` | Slum/informal settlement flag |
| `duration` | Duration of tenancy category |
| `bf` | Building floor category |

---

## Derived / Computed Columns (present in INDIVIDUAL)

| Column | Description |
|--------|-------------|
| `age_cur` | Current age (computed) |
| `hhsize` | Household size (merged from household roster count) |
| `size` | Household size category |
| `sex` | Sex: 1=Male, 2=Female |
| `resid` | Residence: 1=Urban, 2=Rural |
| `wap` / `wap_1` | Working-age population flag |
| `any_disability` | Binary disability indicator |
| `dsb_aggregate` | Disability severity aggregate |
| `ken_edu_isced11` | Education level (ISCED-11 classification) |
| `ken_edu_attendance` | Current school attendance status |
| `age_dep` | Age dependency category (0=child, 15=working age, 65=elderly) |
| `age_cat_10yrbands` | 10-year age band |
| `youth_age_k` | Kenya definition of youth (18–35) |
| `hhh_sex` | Sex of household head (merged onto all members) |

---

## HOUSEHOLD Module Quick Reference

### Water & Sanitation (c01–c07)
- `c01_1` / `c02_1` — main / secondary water source (categorical: piped=1, borehole=4, river=10, etc.)
- `c01_2` / `c02_2` — water collection method
- `c01_3` / `c02_3` — water treatment (0=no, 1=yes)
- `c01_4` / `c02_4` — distance to water source (minutes)
- `c03` — number of toilet facilities
- `c04` — toilet type (flush=1, VIP latrine=6, open defecation=7, none=8)
- `c05` — hand-washing facility available (0=no, 1=yes)
- `c07` — hand-washing materials (soap+water=4)

### Energy (c10–c12)
- `c10` — main lighting source (electricity-grid=1, solar=4, kerosene=5)
- `c10_2` — hours of electricity per day
- `c10_4` — electricity connection type (prepaid=0, postpaid=1)
- `c11` — main cooking fuel (firewood=7, charcoal=9, LPG=11)
- `c12` — primary stove type (3-stone=1, improved=6, gas=10)

### Assets (c13–c14)
- `c13__1` through `c13__7` — asset ownership flags (radio, mobile, TV, computer, motorcycle, car, fridge)
- `c14_1` — monthly water expenditure (KES)
- `c14_2` — monthly electricity expenditure (KES)
- `c14_3` — monthly other energy expenditure (KES)

### Housing Perception (h01–h11)
All rated 1=Good / 2=Fair / 3=Poor (or similar 3-point scale):
- `h01` — structural quality
- `h02` — roof quality
- `h03` — wall quality
- `h04` — floor quality
- `h05` — ventilation
- `h06` — lighting
- `h07` — water supply
- `h08` — sanitation
- `h09` — waste disposal
- `h10` — neighbourhood security
- `h11` — overall satisfaction

---

## DWELLING File Quick Reference

Covers physical characteristics of the dwelling unit (separate roster allowing multiple dwellings per household):

| Column | Likely Meaning |
|--------|---------------|
| `d03` | Dwelling type (conventional=1, flat=4, traditional=7) |
| `d04` | Ownership status of dwelling |
| `d05` | Dwelling in approved building (1=yes, 0=no) |
| `d06` | Structure has planning approval |
| `d07` | Dwelling in hazard-prone area |
| `d08` | Wall material outer (stone/brick=1, block=2, timber=3, mud=5) |
| `d09` | Roof material (iron sheet=1, tiles=2, grass=3) |
| `d10` | Floor material (cement=1, tiles=2, earth=3) |
| `d11` | Number of rooms |
| `d11_1` | Floor area (sq m) |
| `d11_2` | Number of bedrooms |
| `d12` | Number of rooms used for sleeping |
| `d14` | Foundation/base material |
| `d15` | Roof material (dwelling file version) |
| `d16` | Floor material (dwelling file version) |

---

## Institutional Survey Files (COUNTY, NEMA, WATER_SVC, MORTGAGE, LOAN, FINANCIERS, INSTITUTIONAL)

These are supply-side / administrative surveys — not household-level. They do not join to the household file by key (different instruments). Use them for contextual variables or separate analyses.

| File | Respondent | Key variables |
|------|-----------|---------------|
| `COUNTY` | County housing officer | `cg1a/b` = housing units needed/delivered; `cg3` = housing backlog; `cg6__*` = services available; `cg8/9` = planning challenges; `cg13` = land tenure challenges |
| `NEMA` | NEMA regional office | `nema1a/b` = EIA applications; `nema4__*` = EIA requirements enforced; `nema5__*` = EIA challenges |
| `WATER_SVC` | Water service provider | `wssp1a/b` = connections (water/sewer); `wssp7` = tariff; `wssp9` = service area population; `wssp11a/b` = investment needs |
| `MORTGAGE` | Mortgage provider | `se1` = institution type; `se6b` = average interest rate; `se8a` = LTV ratio; `se9b` = average loan term (years) |
| `LOAN` | Housing loan provider | `se1` = institution type; `se3c` = average loan size; `se3d` = loans outstanding |
| `FINANCIERS` | Housing financier | `se4a` = total housing loan portfolio; `se5a` = products offered; `se7` = average loan tenure (months); `se12` = main collateral type |
| `INSTITUTIONAL` | Real estate developer/institution | `b2_3` = years in operation; `b2_4a` = scale of operations; `b2_17*` = challenges; `e5_1a__*` = services offered; `e5_3` = Nairobi County presence; `e5_12` = affordable housing engagement |

---

## PROJECT_INFO + HOUSING_TYPES (Nested Under INSTITUTIONAL)

`PROJECT_INFO` (71 rows) is a repeating roster of housing projects within institutional respondents:

| Column | Likely Meaning |
|--------|---------------|
| `c3_1a` | Project name |
| `c3_2a` / `c3_2b` / `c3_2c` | Location: county / sub-county / estate name |
| `c3_3a` | Project status (ongoing=1, completed=2) |
| `c3_3b` | % completion |
| `c3_4` | Project type (residential=1, mixed=2) |
| `c3_5a` | Tenure type offered (freehold=1, leasehold=2) |
| `c3_6a` | Funding source (private=1, government=96) |
| `c3_8a` | Number of blocks/phases |
| `c3_11` | % units sold/allocated |
| `c3_13` | Construction standard met (1=yes, 2=no) |
| `c3_14` | Main wall material |
| `c3_15` | Roof material |
| `c3_16` | Floor material |
| `c3_17` | Number of floors |
| `c3_20a__*` | Amenities provided (water, electricity, road, etc.) |
| `c3_21__*` | Approvals obtained |
| `c3_23__*` | Challenges faced |
| `c3_30b1`–`c3_30b6` | Unit mix percentages (studio, 1BR, 2BR, 3BR, 4BR+, commercial) |

`HOUSING_TYPES` (131 rows) further breaks down each project by unit type:

| Column | Likely Meaning |
|--------|---------------|
| `c3_32r__id` | Housing type code (10=studio, 11=1BR, 12=2BR, 13=3BR, etc.) |
| `c3_33` | Number of units of this type |
| `c3_34` | Units sold/occupied |
| `c3_35` | Units remaining |
| `c3_36a` / `c3_36a_1` | Floor area: min / max (sq m) |
| `c3_36b` / `c3_36b_1` | Plinth area: min / max (sq m) |
| `c3_37` / `c3_37_1` | Asking price: min / max (KES) |
| `c3_38` | Payment terms (outright=1, mortgage=2, installment=3) |
| `c3_39` | Monthly service charge (KES) |
| `c3_40` | Monthly rent (KES, if rental) |

---

## Common Coded Values (Likely Across Files)

| Value | Typical Meaning |
|-------|----------------|
| `-1` | Not applicable / skipped |
| `98` / `998` | Don't know |
| `99` / `999` | Refused / missing |
| `96` | "Other (specify)" — always paired with an `_other` text column |
| `0` | No / absent |
| `1` | Yes / present / first option |

---

*Generated from KHS 2023/24 SurveySolutions export schema. Column interpretations are inferred from variable names, response distributions, and survey module structure — validate against the official KNBS questionnaire for any column used in final analysis.*