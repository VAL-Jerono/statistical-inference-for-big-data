# CRISP-DM Phase 1: Data Understanding
## Housing Financial Vulnerability Score (HFVS) | 2023/24 Kenya Housing Survey
### Valerie Jerono | Reg. No. 222331 | Strathmore University iLabAfrica

---

## 1. Why Data Understanding Comes Before Everything Else

The HFVS is a formula-constructed target. That means every variable used to build the score must be understood before any model is trained, because the boundary between formula ingredients and proxy features is not self-evident from column names alone. A variable misclassified as a proxy when it is actually a score ingredient is a leakage event: it inflates model performance artificially and produces a classifier that is useless in deployment because the "proxy" it relies on will not be available in an abbreviated intake instrument. CRISP-DM mandates explicit data understanding precisely because this class of error cannot be caught at the modelling stage. It must be prevented here.

This document therefore serves three functions simultaneously. It is the empirical foundation of the methodology chapter. It is the leakage-prevention audit that certifies the proxy feature matrix. And it is the evidence base from which every pillar construction decision is justified with reference to actual variable distributions rather than assumed column meanings.

---

## 2. Data Asset Overview

### 2.1 Primary Spine: The Master Frame

The analytical master frame is a household-level panel with the following structure:

| Dimension | Value |
|---|---|
| Unit of observation | Household |
| Total records | 21,347 |
| Total columns (final) | 443 |
| Spine key | `interview__key` |
| Geographic coverage | All 47 Kenyan counties |
| Survey reference period | 2023/24 |
| Source institution | Kenya National Bureau of Statistics (KNBS) |

The 443 columns are assembled from 10 distinct source files joined to the household spine, plus 51 engineered aggregation columns. This is not a single-file dataset. It is a relational survey architecture with a household as the joining atom.

### 2.2 Source Files and Join Architecture

| File | Rows | Cols | Join Rate | Join Type | Role in HFVS |
|---|---|---|---|---|---|
| `household` | 21,347 | 392 | 100% | Spine | All five pillars |
| `individual` | 80,889 | 97 | ~100% | Aggregated to HH | Household composition features, proxy features |
| `dwelling` | 25,116 | 25 | ~100% | Direct join | Pillar 2 (Physical Quality) |
| `land_parcels` | 11,136 | 34 | ~45.5% | Left join | Pillar 3 (Tenure Security) |
| `county` | 47 | 116 | 100% (via county code) | County merge | Pillar 3, policy chapter |
| `nema` | 48 | 45 | 100% (via county) | County merge | Policy chapter (regulatory friction) |
| `water_svc` | 153 | 96 | 100% (via county) | County merge | Pillar 2 (Utility Deprivation) |
| `mortgage` | 1,644 | 13 | 100% (via county) | County merge | Pillar 1 (Financial Stress), policy chapter |
| `loan` | 946 | 10 | 100% (via county) | County merge | Pillar 1 (Financial Stress), policy chapter |
| `financiers` | 351 | 63 | 100% (via county) | County merge | Policy chapter (credit desert) |
| `real_estate` | 7,236 | 300 | No `interview__key` | County-only merge | Policy chapter (supply side) |
| `project_info` | 71 | 211 | County-level | County merge | Policy chapter (pipeline) |
| `institutional` | 348 | 194 | County-level | County merge | Policy chapter |

**Critical join note:** The `land_parcels` file joins at approximately 45.5%, meaning 55% of households own no land (`i00 == 0`). This is not missing data. It is a structural feature of Kenya's housing market: the majority of urban and peri-urban households are renters or informal occupants with no land holding. These households receive a structurally-informed default score on Pillar 3 (Tenure Security) rather than being excluded from analysis. Dropping them would mean the model cannot score the most tenure-vulnerable population, which is precisely the population the HFVS is designed to identify.

**Real estate join note:** The `real_estate` file has no `interview__key` and joins only at county level. It represents the supply side of the market: developer activity, transaction prices, rental yields. It is not used in the household-level HFVS but is essential for the county-level policy chapter examining alignment between vulnerability demand and housing supply.

---

## 3. The Constructed Aggregation Columns

The 51 engineered columns appended to the household spine during master frame construction are documented here because their provenance must be understood before use. Derived columns from unknown construction logic are a leakage risk.

### 3.1 Individual-Level Aggregations (10 columns)
Aggregated from the 80,889-row individual roster to household level. These include household size, dependency ratios, age composition, and disability prevalence. These are **proxy features**, not HFVS ingredients. They describe who lives in the household without measuring housing conditions.

### 3.2 Dwelling Aggregations (11 columns)
Aggregated from the 25,116-row dwelling file. These include material quality indicators for wall (`d15`), roof (`d14`), and floor (`d12`), number of rooms, and dwelling type. These are **Pillar 2 (Physical Quality) ingredients**. They must not appear in the proxy feature matrix.

### 3.3 Land Parcel Aggregations (7 columns, 55% missing)

The following columns are present but have approximately 55% missingness because they are derived from the land_parcels join:

- `lp_has_title`: whether household holds a formal title on any parcel
- `lp_n_parcels`: number of land parcels owned
- `lp_any_registered`: whether any parcel is formally registered
- `lp_any_collateral`: whether any parcel is used as loan collateral
- `lp_any_dispute`: whether any parcel has an active tenure dispute
- `lp_primary_use`: primary use category of main parcel
- `lp_any_other` (and one further column)

These are **Pillar 3 (Tenure Security) ingredients**. The 55% missingness rate is interpretable: it corresponds almost exactly to `i00 == 0`, the households with no land. A null in these columns is not a data quality failure. It is a meaningful signal of tenure insecurity and must be encoded as such (zero score on land-related tenure indicators) rather than imputed or dropped.

### 3.4 County-Level Aggregations (5 + 3 + 5 + 4 + 3 + 3 = 23 columns)

These are contextual features merged at county level from institutional data files:

**County physical planning (`county_agg`, 5 cols):** Regulatory capacity indicators from the 47-row county file. These include planning approval rates and compliance infrastructure. Used in the policy chapter.

**NEMA aggregations (`nema_agg`, 3 cols):** Derived from the 48-row NEMA file:
- EIA application count (`nema1a`): volume of environmental impact applications received
- EIA approval count (`nema1b`): approvals issued; ratio `nema1b/nema1a` is the county approval rate
- Processing days (`nema6`): bureaucratic lag in days per application

These three columns represent regulatory friction at county level. No Kenyan housing study has used NEMA processing data as a predictor of supply-side housing market conditions. This is a novel analytical contribution of the policy chapter.

**Water service aggregations (`wsvc_agg`, 5 cols):** Derived from the 153-row water utility file. Include service coverage rates, tariff levels, and connection density by county. Used in Pillar 2 (Utility Deprivation) as contextual county-level complement to household-level water source (`c01_1`).

**Mortgage aggregations (`mort_agg`, 4 cols, 60-81% missing):**

| Column | Missingness | Meaning |
|---|---|---|
| `mort_interest_rate` | 81% | Average mortgage interest rate in county |
| `mort_ltv_ratio` | 64% | Average loan-to-value ratio offered |
| `mort_avg_term_years` | 60% | Average mortgage term in years |
| `mort_avg_products` | ~30% | Number of mortgage products available |

The high missingness in `mort_interest_rate` (81%) reflects the geographic concentration of formal mortgage products: the 1,644-row mortgage file is dominated by Nairobi City (44% of records) and Kiambu (6%). The 37 counties with sparse or absent mortgage institution presence return nulls. This missingness is itself a structural signal: a null `mort_interest_rate` at county level means the county has effectively no formal mortgage market. This column is used in Pillar 1 (Financial Stress) as a county-level market exclusion indicator rather than as a continuous interest rate variable.

**Loan aggregations (`loan_agg`, 3 cols):** Derived from the 946-row housing loan file. Average loan size, outstanding balance, and loan-to-income proxy. Nairobi (52% of records) heavily dominates.

**Financier aggregations (`fin_agg`, 3 cols):** Derived from the 351-row financiers file. Portfolio size (`se4a`), loan tenure (`se7`), and product diversity. Used to construct the county-level credit accessibility index for the policy chapter.

### 3.5 Pre-Computed Household Columns Requiring Verification

Three columns in the household base file appear to have been pre-computed by KNBS or a prior data preparation process. Their provenance is not documented in the KHS codebook and must be verified before use:

**`prop_util` (30.3% present, 69.7% missing):** The name suggests a proportion involving utilities. Top values are 0.20 and 0.10. The 69.7% missingness aligns closely with the renter subpopulation (`k05` is 67.5% missing, which is the non-renter group). Working hypothesis: `prop_util = utilities_cost / rent_paid` or `utilities / total_exp`. If confirmed as `utilities / k05`, this would be a utility-burden ratio for renters and would partially operationalise Pillar 1 without reconstruction. **Action required: verify construction before using in any formula.**

**`med_prop` (70.7% missing):** Top values are 0.171 and 0.167, which are consistent with county-level medians of `prop_util`. Likely the county median of `prop_util`. Usable as a contextual feature once `prop_util` is verified.

**`med_brms` (78.1% missing):** Top values are 3.0 and 2.0. Likely county or cluster median number of bedrooms. Usable as a crowding context feature for Pillar 2 once confirmed.

**`min_rent` (67.5% missing):** Minimum rent in the area, likely county or sub-county level. Complement to `k05` for constructing relative rent burden. Requires verification.

---

## 4. The Five Pillars: Variable-Level Detail

### Pillar 1: Financial Stress

**What it measures:** The degree to which housing costs threaten a household's financial stability, both through direct cost burden and through structural exclusion from formal finance.

**Core variable: Total Household Expenditure (constructed)**

The KHS does not collect income directly. The proxy is total household expenditure, constructed from the eleven monthly expenditure category variables:

```
g01a  Food and non-alcoholic beverages
g01b  Clothing and footwear
g01c  Education
g01d  Health
g01e  Transport
g01f  Communication
g01g  Recreation and culture
g01h  Housing (rent, mortgage, or imputed)
g01i  Energy (fuel, electricity)
g01j  Other goods and services
g01k  Remittances sent
```

All eleven columns show 0% missingness in the household file. This is the income proxy foundation of the entire index. The construction is: `total_exp = g01a + g01b + ... + g01k`.

This approach is consistent with the World Bank LSMS methodology and the KIHBS expenditure aggregation protocol. It is standard practice for East African household surveys where formal income reporting is unreliable due to informal employment.

**Rent burden ratio (renter subpopulation)**

The `k05` column records monthly rent paid. It has 67.5% missingness, which is structurally correct: it applies only to renter households. The renter identification variable is `g02` (tenure type; `g02 == 1` identifies renters, approximately 22% of households based on the household file distribution where `g02: 1.0 (22%)`).

Rent burden is constructed as:
```
rent_burden = k05 / (total_exp - g01h)
```

The denominator subtracts `g01h` to avoid double-counting rent in both numerator and denominator. `g01h` is the broader housing expenditure category which includes rent for renters; `k05` is the specific monthly rent amount. The 30% threshold for `rent_burdened` follows SDG 11 and KIHBS convention.

**Validation variables (not ingredients, not proxies — validators only):**
- `j09`: Binary; household reports housing cost is a financial burden (39% = yes). This is the stated-preference validation for the constructed `rent_burden` ratio.
- `j10`: Binary; household missed a housing payment in past 12 months (41% = yes). This is the revealed-behaviour validation for financial stress.
- `j11`: Binary; household at eviction risk (45% = yes). Cross-pillar: also informs Pillar 3.

The chi-square test between `rent_burden > 0.30` and `j09 == 1`, and between `rent_burden > 0.30` and `j10 == 1`, constitutes the primary validation of the Pillar 1 construction. If the constructed ratio is measuring real financial stress, households above the threshold should show significantly higher rates of stated burden and missed payments.

**County-level finance access indicators:**

The `mort_agg` and `loan_agg` columns encode structural access to formal housing finance at county level. High missingness in `mort_interest_rate` (81%) is not imputed away. Counties with no recorded mortgage products are assigned the maximum exclusion score on this dimension. The credit desert index for the policy chapter is the inverse of finance accessibility: counties with high mean HFVS and low `fin_agg` coverage are priority intervention targets.

**Aspirational housing variables (unmet demand, not stress indicators):**

The household file contains `k16` through `k22`, which capture housing improvement aspirations: whether the household intends to move, preferred dwelling type, estimated cost of desired dwelling, and financing preference. These variables describe unmet demand but not current financial stress. They are **proxy features** (describing aspiration and awareness) rather than Pillar 1 ingredients. They are candidates for the proxy feature matrix.

---

### Pillar 2: Physical Quality

**What it measures:** The structural and amenity adequacy of the physical dwelling, from materials quality through to basic service provision.

**Dwelling materials (from `dwelling` file):**

| Variable | Description | Distribution |
|---|---|---|
| `d12` | Floor material | 1=earth (66%), 2=cement/concrete (28%), 3=tiles/wood (5%) |
| `d14` | Roof material | 8=iron sheets (45%), 1=grass/thatch (33%), 7=concrete (12%) |
| `d15` | Wall material | 4=mud/wood (23%), 12=stone/cement (21%), 11=burnt brick (20%) |

Each is coded from worst to best material and normalised 0–1. Mud floor + grass roof + mud wall = maximum physical vulnerability. Tiles/concrete/stone = minimum.

**Basic services (from `household` file):**

| Variable | Description | Key values |
|---|---|---|
| `c01_1` | Primary water source | 1=piped indoor (27%), 10=borehole (18%), 4=surface water (12%) |
| `c04` | Toilet type | 7=pit latrine no slab (41%), 8=open defecation (20%), 6=pit with slab (10%) |
| `c11` | Primary cooking fuel | 9=firewood (54%), 7=charcoal (25%), 11=LPG (17%) |

**Subjective quality ratings (from `household` file):**

`h01` through `h11` record the household's own assessment of 11 housing dimensions on a scale including inadequate/adequate/more than adequate. The distribution heavily concentrates at `h01: 2 (37%)`, `h02: 2 (36%)`, consistent with a "satisfactory/adequate" modal response.

The **objective-subjective quality gap** is a constructed analytical feature: `gap = objective_quality_score - subjective_quality_score`. A large negative gap (household rates dwelling positively but objective indicators are poor) identifies households that are materially vulnerable but do not self-identify as such. These households are invisible to demand-side needs assessments and represent latent risk that the HFVS is specifically designed to surface.

**Dwelling type and density:**

`d01` (dwelling type: 85% permanent, 12% semi-permanent, 2% temporary) provides a top-level quality classification. `d08` through `d10` capture number of rooms, enabling construction of a persons-per-room crowding index when combined with household size from the individual aggregation.

**County-level water service context:**

The `wsvc_agg` columns provide county-level water coverage rates and tariff levels from the 153-row water utility file. These contextualise household `c01_1` responses: a household reporting piped water in a county where the water utility covers 20% of connections is in a different risk position than the same household in a 90%-coverage county.

---

### Pillar 3: Tenure Security

**What it measures:** The legal, documentary, and practical stability of a household's right to occupy its dwelling and, where applicable, its land.

**Household-level tenure indicators:**

| Variable | Description | Distribution |
|---|---|---|
| `j05` | Has formal title document | 1=yes (54%), 0=no (46%) |
| `j11` | Eviction risk | 1=yes (45%), 0=no (55%) |
| `i00` | Owns land | 1=yes (45%), 0=no (55%) |
| `j04_1` | Tenure type | 1=owner occupier (62%), 0=renter/other (27%), 2=employer-provided (11%) |
| `j02` | Has written agreement for current dwelling | 1=yes (88%), 0=no (12%) |

**Land parcel indicators (45.5% join, applicable only to `i00 == 1`):**

| Variable | Description | Distribution (among landowners) |
|---|---|---|
| `i06` | Title document type | 1=freehold (61%), 14=no document (19%), 12=leasehold (7%) |
| `i08` | Security of tenure on parcel | 1=secure (72%), 0=insecure (25%) |
| `i10` | Legal right to parcel | 1=yes (75%), 0=no (22%) |
| `i05` | Land use type | 1=residential (85%), 3=agricultural (9%) |

**The 55% with no land — scoring design decision:**

Households where `i00 == 0` (no land ownership) receive a Pillar 3 score that reflects their structural tenure condition rather than a null. The logic is as follows: a household that rents with no land holding and no formal title to any dwelling, but that has a written lease and has not experienced eviction, is in a different tenure position than a household with no land, no lease, and active eviction risk. The pillar construction handles this through the household-level variables (`j05`, `j11`, `j02`, `j04_1`) which are populated for all 21,347 households regardless of land ownership. Land parcel variables contribute a bonus or modifier to the score for the 45.5% with land; they are not the base of the pillar.

This design ensures the pillar is meaningful for the modal Kenyan housing condition (renter, no land) rather than only for the minority who own land. It is a methodological contribution of the study.

---

### Pillar 4: Physical Hazard Exposure (from proposal D3)

**What it measures:** The degree to which the household's location exposes it to climate and environmental hazards, principally flooding and landslide risk.

**Key variables from `household` file:**

| Variable | Description | Distribution |
|---|---|---|
| `e06` | Household experienced flooding | 0=no (81%), 2=yes severe (13%), 1=yes minor (7%) |
| `e07` | Household experienced landslide | 0=no (87%), 2=yes (9%), 1=yes minor (4%) |
| `e08` | Household experienced other hazard | 1=none (53%), 2=fire (35%), 3=drought (10%) |
| `e09__*` | Hazard impact indicators | 11 binary columns for flood/landslide consequences |

**The triple-exposure indicator:**

This is a constructed binary feature: `triple_exposed = (flood_exposed) AND (informal_structure) AND (absent_title)`. A household simultaneously in a flood zone, living in a non-permanent structure, and without formal tenure documentation occupies the highest-risk compound profile. This flag is used both in Pillar 4 scoring and as a standalone binary feature in the county-level risk atlas.

The triple-exposure rate is anticipated to be highest in Mombasa, Kisumu, and the Nairobi informal settlement cluster, consistent with the April 2024 flood casualty profile (ReliefWeb, 2024).

---

### Pillar 5: Utility Deprivation (from proposal D5)

**What it measures:** The degree to which the household lacks access to basic utility infrastructure, including electricity, clean water, and clean cooking energy.

**Key variables:**

| Variable | Description | High-vulnerability values |
|---|---|---|
| `c01_1` | Primary water source | 4=surface water, 10=borehole (depending on quality) |
| `c04` | Sanitation | 7=pit latrine no slab, 8=open defecation |
| `c11` | Cooking fuel | 9=firewood (54% of HHs), 7=charcoal |
| `c10` | Lighting source | 5=none/paraffin (32%), 4=other (7%) |
| `c08` | Has handwashing facility with soap | 1=yes (57%), 0=no (43%) |

**Note on overlap with Pillar 2:**

Utility deprivation and physical quality overlap at the variable level (both reference water source and sanitation). The differentiation in the composite score is intentional: Pillar 2 scores the material quality of the physical structure; Pillar 5 scores the service environment in which the household lives. A household in a permanent structure (high Pillar 2 score) in an area with no piped water or grid electricity (low Pillar 5 score) is a real and common profile in Kenya's rapidly formalising peri-urban areas. The two pillars capture this distinction.

---

## 5. The Proxy Feature Matrix

The proxy feature matrix contains 24 demographic and contextual variables that are conceptually upstream of the HFVS formula — variables an intake officer could collect without measuring housing conditions. These variables are used to train the five ML classifiers.

The strict rule: **no HFVS formula-ingredient variable may appear in the proxy matrix.** The banned-variable assertion is enforced in the pipeline.

**Proposed proxy features:**

| Feature | Source | Justification |
|---|---|---|
| Household head education (ISCED) | `individual` (agg) | Proxy for income-earning capacity |
| Age of household head | `individual` (agg) | Lifecycle stage affects housing choice |
| Sex of household head | `individual` (agg) | Gender dimension of financial exclusion |
| Household size | `individual` (agg) | Crowding proxy; also affects expenditure |
| Dependency ratio | `individual` (agg) | Financial stress indicator without measuring expenditure |
| Residence type (urban/rural) | `household: a07_1` | Context for all vulnerability dimensions |
| County code | `household: a01` | Spatial context |
| Sub-county/cluster | `household: a12` | Sub-county heterogeneity |
| Employment status of HH head | `individual` (agg) | Income stability proxy |
| Mobile phone ownership | `household: c13__2` | Financial inclusion proxy |
| Distance to nearest market | `household: e05` | Accessibility proxy |
| Number of rooms in dwelling | `dwelling: d11_1` | Crowding measure without quality scoring |
| Dwelling type (permanent/semi/temporary) | `dwelling: d01` | Structural type without material scoring |
| Years in current dwelling | `household: l08`, `l07` | Stability indicator |
| Migration in past 5 years | `household: b09_3` | Displacement risk |
| Housing aspiration (intends to move) | `household: k20` | Revealed preference on housing adequacy |
| Preferred tenure type | `household: k21` | Aspiration variable |
| Household has savings/financial account | `household: g04` | Financial resilience proxy |
| Access to mobile money | `household: g05__7` | Financial inclusion |
| Number of income sources | `household: g05__*` aggregated | Income diversification |
| Residence type × tenure status | Interaction term | Collinearity-informed interaction |
| Household size × utility access | Interaction term | Crowding-utility interaction |
| County mortgage penetration | `mort_agg` | Structural finance access context |
| County NEMA approval rate | `nema_agg` | Regulatory environment context |

---

## 6. Missingness Tier Classification

Following the protocol specified in the methodology, the 443 columns are classified into four missingness tiers:

| Tier | Missing% | Treatment |
|---|---|---|
| Complete | 0% | Use as-is |
| Low | 1–20% | Group-median imputation, stratified by tenure type |
| Moderate | 21–60% | Use with imputation where interpretable; flag as imputed |
| High | >60% | Exclude from HFVS formula construction; retain as contextual features where theoretically motivated |

**High-missingness columns retained with justification:**

- `mort_interest_rate` (81% missing): Retained as a county-level exclusion indicator. Null = no formal mortgage market in county. Not imputed; encoded as maximum exclusion.
- `k05` (67.5% missing): Retained; structural missingness. Applies only to renters. Not imputed; pillar sub-scores for rent burden apply only to renter subpopulation.
- `lp_*` columns (55% missing): Retained; structural missingness reflects `i00 == 0`. Encoded as zero-contribution to land-related tenure indicators for non-landowners.

---

## 7. Survey Weights

The `hhweight` column is present in the household file with 0% missingness. Top values show substantial variation (1,345.4, 206.9, 751.8), reflecting the stratified oversampling design of the KHS, which oversamples Nairobi and certain urban counties.

All county-level aggregates in the HFVS must use `hhweight` to produce nationally representative estimates. An unweighted county mean HFVS is not the same as a population-representative county vulnerability score. This is especially consequential for the policy outputs: the finance exclusion scatter plot and the AHP priority ranking must be based on weighted HFVS scores, or the targeting recommendations will be biased toward the oversampled counties.

The survey weight is **not** a feature variable and must not appear in the proxy matrix. It is an analytical weight applied to aggregate outputs.

---

## 8. The Supply-Side Data: What It Can and Cannot Do

The `real_estate` (7,236 rows, 300 cols), `project_info` (71 rows), `institutional` (348 rows), and `housing_types` (131 rows) files do not join to individual households. They operate at county level and describe the supply side of the housing market: developer activity, project completion rates, unit type distributions, and price points.

**What these files enable:**
- County-level housing gap model: units in pipeline vs. weighted demand
- Rental yield calculation (`rb13` rental income over `rc10b` capital value) by county
- NEMA compliance linkage: whether high-friction counties also have lower housing project completion rates
- Developer affordability targeting: whether projects in pipeline match the price points affordable to high-HFVS households

**What they cannot do:**
- Join directly to household vulnerability scores (no `interview__key`)
- Enter the HFVS formula or the proxy feature matrix
- Be used in any household-level model

The supply-side analysis is therefore a separate analytical chapter. It consumes county-level HFVS outputs (mean, quintile, triple-exposure rate) as inputs and asks whether supply responds to where vulnerability is highest. This is the policy chapter, not the model chapter.

---

## 9. Known Data Quality Issues

| Issue | Column(s) | Nature | Treatment |
|---|---|---|---|
| Survey weight not applied in raw EDA | `hhweight` | Analytical omission | All descriptive statistics must be weighted |
| Pre-computed derived columns | `prop_util`, `med_prop`, `med_brms`, `min_rent` | Provenance unverified | Inspect construction; do not use before confirmation |
| Structural missingness misclassified as data gap | `k05`, `lp_*`, `mort_interest_rate` | Missingness is informative | Encode, do not impute |
| Real estate file has no spine key | `real_estate` | Join limitation | County-level only |
| Nominal codes without codebook mapping | Multiple `d14`, `d15`, `c01_1` values | Requires KHS codebook for material labelling | Verify category ordering before normalisation |
| Nairobi overrepresentation in financial files | `mortgage`, `loan`, `financiers` | Sampling bias in institutional files | Survey-weight all county aggregates; flag Nairobi as outlier |

---

## 10. Summary: What This Data Can Definitively Support

Based on the complete data understanding, the following findings from the 2023/24 KHS data asset can be supported with high analytical confidence:

1. **A five-dimension composite HFVS** for all 21,347 households, with all five pillars constructable from variables with 0–20% missingness or with principled structural-missingness encoding.

2. **A validated rent burden ratio** for the renter subpopulation (~7,000 households), triangulated against stated (`j09`) and revealed (`j10`) financial stress behaviours.

3. **A county-level risk atlas** for all 47 counties, survey-weighted, with HFVS quintile classification and triple-exposure rate annotation.

4. **A proxy ML classifier** trained on the 24-feature proxy matrix, with leakage-controlled cross-validation using `StratifiedGroupKFold` by county.

5. **A supply-demand alignment analysis** at county level, comparing weighted HFVS scores against housing pipeline data (`project_info`), regulatory friction (`nema_agg`), and financier coverage (`fin_agg`, `mort_agg`).

6. **The objective-subjective quality gap** as an analytically novel finding: the population that is materially vulnerable but does not self-report as such, and therefore escapes demand-side needs assessments.

What the data cannot support without additional sources: longitudinal vulnerability tracking, satellite-augmented risk scoring, or direct income validation.

---

*This document satisfies CRISP-DM Phase 1: Data Understanding. All subsequent phases — data preparation, modelling, evaluation, and deployment — may proceed on the basis of the variable mappings, missingness classifications, and design decisions documented here.*