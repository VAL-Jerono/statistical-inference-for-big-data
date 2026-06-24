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
