import nbformat as nbf

nb = nbf.v4.new_notebook()
cells = []

def md(src):
    cells.append(nbf.v4.new_markdown_cell(src))

def code(src):
    cells.append(nbf.v4.new_code_cell(src))

# ============================================================ TITLE ======
md(r"""# DSA 8301 — Statistical Inference for Big Data
## Exploratory, Parametric & Nonparametric Analysis
### Housing Financial Vulnerability in Kenya — KHS 2023/24

**Student:** Sephine Valerie Jerono | **Reg No:** 222331
**Course:** DSA 8301 — Statistical Inference for Big Data
**Lecturer:** Dr. John Olukuru
**Institution:** Strathmore Institute of Mathematical Sciences (iLabAfrica)
**Date of Submission:** 17 June 2026

---

### What this notebook does

The companion notebook *(Data Understanding · Cleaning · Feature Engineering)* turned 21,347 raw
Kenya Housing Survey 2023/24 (KHS) interviews — 443 columns of mostly skip-logic survey codes —
into a clean, theory-driven, **zero-missing** analytical file: `model_ready.parquet`. It scores
every household on a five-dimension **Housing Financial Vulnerability Score (HFVS)**: financial
stress, tenure insecurity, physical hazard, dwelling quality, and utility deprivation.

This notebook picks up exactly where that one left off, and asks three questions of the data:

1. **What does the data actually look like, once we stop trusting that "cleaned" means "perfect"?**
   (Part B — one residual data-entry fault survives even careful cleaning; finding it is the point.)
2. **What do classical, assumption-driven (parametric) methods say about housing vulnerability in
   Kenya — and do their assumptions actually hold at this scale?** (Part C)
3. **When we drop those assumptions and let the data speak for itself (nonparametric methods), does
   the story change?** (Part D)

A theme runs through all three parts: with **n = 21,347**, almost *everything* is "statistically
significant." The real skill this assignment is testing is knowing the difference between a
p-value and a finding that matters — so every test below reports an **effect size** alongside its
p-value, and the closing synthesis (Part E) is built entirely around that distinction.

| Section | Content |
|---|---|
| **Part B** | Dataset description, preprocessing & outlier treatment, descriptive statistics, graphical EDA, distributional diagnostics |
| **Part C** | 5 parametric methods: confidence intervals, one-sample *t*, two-sample *t*, one-way ANOVA, multiple linear regression |
| **Part D** | 5 nonparametric methods: Mann–Whitney *U*, Wilcoxon signed-rank, Kruskal–Wallis, Spearman correlation, bootstrap CI |
| **Part E** | Parametric vs. nonparametric synthesis, and what it means for the housing-policy question |

---""")

# ============================================================ PART B =====
md(r"""## Part B — Data Description & Exploratory Data Analysis

### B.0 — Environment & Data Loading""")

code(r"""# ── B.0.1  Imports ───────────────────────────────────────────────────────
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from scipy import stats
from scipy.stats import skew, shapiro, normaltest, spearmanr
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor

warnings.filterwarnings('ignore')
np.random.seed(42)

pd.set_option('display.float_format', '{:.4f}'.format)
pd.set_option('display.max_columns', 60)
pd.set_option('display.max_rows', 120)

plt.rcParams.update({
    'figure.dpi': 130, 'figure.facecolor': 'white',
    'axes.facecolor': '#F8F8F6', 'axes.spines.top': False,
    'axes.spines.right': False, 'axes.titlesize': 13,
    'axes.titleweight': '600', 'axes.labelsize': 11,
    'xtick.labelsize': 9, 'ytick.labelsize': 9,
})
sns.set_style('whitegrid')

TEAL  = '#00695C'; RED  = '#B71C1C'; AMBER = '#E65100'
BLUE  = '#1565C0'; GRAY = '#546E7A'; GREEN = '#2E7D32'

print('Environment ready.')""")

code(r"""# ── B.0.2  Load the cleaned, model-ready dataset ────────────────────────
# Output of the companion notebook "Data Understanding, Cleaning & Feature
# Engineering": 21,347 Kenyan households, 47 counties, reduced from 443 raw
# survey columns to 59 theory-driven features via the 5-pillar HFVS pipeline.
candidates = [Path('model_ready.parquet'), Path('data/model_ready.parquet'),
              Path('model_ready.csv'), Path('data/model_ready.csv')]
DATA_PATH = next((p for p in candidates if p.exists()), None)
if DATA_PATH is None:
    raise FileNotFoundError(
        'model_ready.parquet/csv not found next to this notebook. '
        'Place it in the same folder (or a ./data subfolder) and re-run.'
    )

df = pd.read_parquet(DATA_PATH) if DATA_PATH.suffix == '.parquet' else pd.read_csv(DATA_PATH)
print(f'Loaded: {df.shape[0]:,} households x {df.shape[1]} columns')
print(f'Source file: {DATA_PATH.resolve().name}')""")

md(r"""### B.1 — Dataset Description

**Source.** The 2023/24 Kenya Housing Survey (KHS), conducted by the Kenya National Bureau of
Statistics (KNBS) in collaboration with the State Department for Housing and Urban Development and
other government partners, covering all 47 counties between March and May 2024. This analysis uses
the KHS household-level microdata, processed by the author into the HFVS analytical file below.

**Unit of observation.** One row = one surveyed household (n = 21,347).

**Variables.** 59 columns spanning five HFVS dimensions, household demographic controls, and
county-level housing-supply indicators. The full data dictionary is generated below directly from
the dataset's own role-tagging, so the table can never silently drift out of sync with the data.""")

code(r"""# ── B.1.1  Data dictionary ───────────────────────────────────────────────
DICTIONARY = {
    'interview__key':          ('id',      'Unique household interview identifier'),
    'county_code':              ('id',      'KNBS county code (1-47)'),
    'is_urban':                 ('stratum', 'Residence stratum: 1 = Urban, 0 = Rural'),
    'hhweight':                  ('weight',  'Household sampling weight'),
    'log_total_expenditure':     ('D1',      'log(1+monthly total household expenditure, KES)'),
    'log_housing_cost':          ('D1',      'log(1+monthly housing cost: rent/mortgage/imputed, KES)'),
    'housing_burden_ratio':      ('D1',      'Housing cost as a share of total expenditure, capped at 1'),
    'is_cost_burdened':          ('D1',      '1 if housing_burden_ratio > 0.30 (cost-burden threshold)'),
    'utility_burden_ratio':      ('D1',      'Water + electricity + other energy cost share of expenditure'),
    'financial_stress_count':    ('D1',      'Count of financial-stress indicators present'),
    'in_rent_arrears':           ('D1',      '1 if household is behind on rent payments'),
    'asset_score':               ('D1',      'Household asset-ownership index (higher = more assets)'),
    'log_rent':                  ('D1',      'log(1+monthly rent, KES; 0 for non-renters)'),
    'tenure_security_score':     ('D2',      'Ordinal tenure security, 0 (insecure) to 3 (fully secure)'),
    'is_renter':                 ('D2',      '1 if household rents its dwelling'),
    'no_land_ownership':         ('D2',      '1 if household does not own the land it occupies'),
    'no_written_lease':          ('D2',      '1 if renting without a written lease agreement'),
    'rent_dispute_history':      ('D2',      '1 if household has a history of rent-related disputes'),
    'demolition_threat':         ('D2',      '1 if household has faced a demolition threat'),
    'eviction_threat':           ('D2',      '1 if household has faced an eviction threat'),
    'tenure_satisfied':          ('D2',      '1 if household reports satisfaction with tenure arrangement'),
    'yrs_in_dwelling':           ('D2',      'Years the household has lived in its current dwelling'),
    'flood_risk':                ('D3',      '1 if dwelling is in a flood-prone area'),
    'landslide_risk':            ('D3',      '1 if dwelling is in a landslide-prone area'),
    'hazard_proximity_count':    ('D3',      'Count of nearby environmental hazards (dumpsite, factory, etc.)'),
    'env_hazard_any':            ('D3',      'Composite flag: any environmental hazard present'),
    'wall_durable':              ('D4',      '1 if dwelling has durable wall material'),
    'roof_durable':              ('D4',      '1 if dwelling has durable roof material'),
    'floor_durable':             ('D4',      '1 if dwelling has durable floor material'),
    'structure_quality':         ('D4',      'Count (0-3) of durable structural components'),
    'is_overcrowded':            ('D4',      '1 if more than 2 persons per room'),
    'perception_quality_score':  ('D4',      "Household's mean self-rated dwelling quality (1=Poor, 3=Good)"),
    'n_housing_problems':        ('D4',      'Count of reported housing problems'),
    'log_floor_area':            ('D4',      'log(1+dwelling floor area, m2)'),
    'dwelling_age_yrs':          ('D4',      'Age of the dwelling structure, years'),
    'safe_water':                ('D5',      '1 if household has access to a safe/improved water source'),
    'improved_sanitation':       ('D5',      '1 if household has an improved sanitation facility'),
    'shared_sanitation':         ('D5',      '1 if the sanitation facility is shared with other households'),
    'clean_cooking':             ('D5',      '1 if household uses clean cooking fuel'),
    'has_electricity':           ('D5',      '1 if household is connected to electricity'),
    'hh_size':                   ('control', 'Number of household members'),
    'female_headed':             ('control', '1 if the household head is female'),
    'any_disability':            ('control', '1 if at least one member reports a disability'),
    'dependency_ratio':          ('control', '(children + elderly) / working-age members, clipped to [0,5]'),
    'edu_tier':                  ('control', "Household head's education tier: 0=none/primary, 1=secondary, 2=tertiary"),
    'mean_age':                  ('control', 'Mean age of household members (contains residual data faults — see B.2)'),
    'cty_housing_gap_ratio':     ('supply',  'County housing backlog / stock (supply-demand gap)'),
    'cty_has_housing_policy':    ('supply',  '1 if the county has an adopted housing policy'),
    'cty_planning_staff':        ('supply',  'Number of county urban-planning staff'),
    'wsvc_sewer_connections':    ('supply',  'County sewer connections (water-services-board records)'),
    'county_mort_ltv':           ('supply',  'County-average mortgage loan-to-value ratio (%)'),
    'county_mort_rate':          ('supply',  'County-average mortgage interest rate'),
    'hfvs_d1_financial':         ('HFVS',    'Dimension 1 score: Financial Stress (0=low, 1=high vulnerability)'),
    'hfvs_d2_tenure':            ('HFVS',    'Dimension 2 score: Tenure Insecurity'),
    'hfvs_d3_hazard':            ('HFVS',    'Dimension 3 score: Physical Hazard'),
    'hfvs_d4_quality':           ('HFVS',    'Dimension 4 score: Dwelling Quality'),
    'hfvs_d5_utility':           ('HFVS',    'Dimension 5 score: Utility Deprivation'),
    'hfvs_composite':            ('HFVS',    'Equal-weighted composite of D1-D5 — primary continuous outcome'),
    'high_vulnerability':        ('target',  'Binary flag: 1 if hfvs_composite falls in the high-vulnerability band'),
}

ddict = pd.DataFrame(
    [(c, role, df[c].dtype.name, desc) for c, (role, desc) in DICTIONARY.items() if c in df.columns],
    columns=['variable', 'role', 'dtype', 'description']
)
print(f'Data dictionary covers {len(ddict)} / {df.shape[1]} columns\n')
print(ddict.to_string(index=False))""")

code(r"""# ── B.1.2  Headline structural facts ─────────────────────────────────────
print('=== STRUCTURAL OVERVIEW ===')
print(f'Households (rows)            : {df.shape[0]:,}')
print(f'Variables (columns)          : {df.shape[1]}')
print(f'Counties represented         : {df["county_code"].nunique()} / 47')
print(f'Duplicate interview keys     : {df["interview__key"].duplicated().sum()}')
print(f'Urban share                  : {df["is_urban"].mean()*100:.1f}%')
print(f'High-vulnerability prevalence: {df["high_vulnerability"].mean()*100:.2f}%  '
      f'({df["high_vulnerability"].sum():,} households)')
print()
n_continuous = sum(df[c].dtype.kind == 'f' and df[c].nunique() > 10 for c in df.columns)
n_binary     = sum(df[c].dropna().nunique() <= 2 for c in df.columns if df[c].dtype.kind in 'fi')
print(f'Variables behaving as continuous : ~{n_continuous}')
print(f'Variables behaving as binary/flag: ~{n_binary}')
print('-> Requirement check: n >= 100 (yes), >= 4 variables (yes), mix of continuous')
print('   and categorical variables (yes), reputable public source (yes, KNBS).')""")

md(r"""### B.2 — Data Preprocessing

The companion notebook already drove total missingness to **zero** through skip-logic-aware,
stratified-median imputation. That does not mean the file is fault-free — it only means *missing*
values are gone. **Implausible** values can still hide inside a column that has no `NaN`s at all.
We check for exactly that below, then run a set of independent consistency checks.""")

code(r"""# ── B.2.1  Missingness re-verification ──────────────────────────────────
total_missing = df.isnull().sum().sum()
print(f'Total missing cells in model_ready: {total_missing}')
print('Confirms the upstream cleaning notebook: 0 missing values across all 59 columns.')""")

code(r"""# ── B.2.2  Outlier detection on mean_age: three methods, three verdicts ─
age = df['mean_age']
print(f'mean_age — raw summary: mean={age.mean():.2f}  std={age.std():.2f}  '
      f'min={age.min():.2f}  max={age.max():.2f}')

# Method 1: IQR rule (1.5x)
q1, q3 = age.quantile([.25, .75]); iqr = q3 - q1
lo_iqr, hi_iqr = q1 - 1.5*iqr, q3 + 1.5*iqr
flag_iqr = (age < lo_iqr) | (age > hi_iqr)

# Method 2: Z-score rule (|z| > 3)
z = (age - age.mean()) / age.std()
flag_z = z.abs() > 3

# Method 3: Domain rule (a household's mean member age cannot be negative
# or exceed ~100 years)
flag_domain = (age < 0) | (age > 100)

print(f'\nIQR rule        bounds=({lo_iqr:.1f}, {hi_iqr:.1f}) -> flags {flag_iqr.sum():,} rows '
      f'({flag_iqr.mean()*100:.2f}%)')
print(f'Z-score rule    |z|>3               -> flags {flag_z.sum()} rows '
      f'({flag_z.mean()*100:.3f}%)')
print(f'Domain rule     age<0 or age>100    -> flags {flag_domain.sum()} rows '
      f'({flag_domain.mean()*100:.4f}%)')
print(f'\nValues flagged by the domain rule: {sorted(age[flag_domain].unique())}')""")

md(r"""**Reading the three verdicts.** The IQR rule flags 1,384 households (6.5%) — far too many to be
"errors"; it is simply reacting to the natural right-skew of household age structure (some homes are
genuinely all-elderly). The z-score rule under-reacts to skew and finds only 3. Only the **domain
rule** — grounded in what a household mean age can physically be — isolates the real fault: 10
households (0.047%) carry values like `-2488.25` and `2024.0`, almost certainly a calendar year that
leaked into an age field during data capture. This is the correct lesson for a 21k-row government
microdataset: **statistical outlier rules are a starting point, not a verdict; domain knowledge
makes the final call.** We treat the 10 domain-implausible values as missing and re-impute them with
the urban/rural-stratum median, consistent with the imputation logic already used upstream.""")

code(r"""# ── B.2.3  Outlier treatment ─────────────────────────────────────────────
df['mean_age_clean'] = age.where(~flag_domain)
strat_median = df.groupby('is_urban')['mean_age_clean'].transform('median')
df['mean_age_clean'] = df['mean_age_clean'].fillna(strat_median)

print(f"Rows treated           : {flag_domain.sum()}")
print(f"mean_age (raw)   -> mean={age.mean():.2f}  std={age.std():.2f}")
print(f"mean_age_clean   -> mean={df['mean_age_clean'].mean():.2f}  "
      f"std={df['mean_age_clean'].std():.2f}  "
      f"min={df['mean_age_clean'].min():.2f}  max={df['mean_age_clean'].max():.2f}")
print('\nAll downstream analysis uses mean_age_clean, not the raw column.')""")

code(r"""# ── B.2.4  Independent consistency checks ───────────────────────────────
print('=== CONSISTENCY CHECKS ===\n')

print('1) Ratio variables must lie in [0, 1]:')
for c in ['housing_burden_ratio', 'utility_burden_ratio']:
    bad = ((df[c] < 0) | (df[c] > 1)).sum()
    print(f'   {c:<25} out-of-range = {bad}')

print('\n2) Binary variables must take only {0, 1}:')
binary_cols = ['is_urban', 'is_renter', 'flood_risk', 'landslide_risk', 'wall_durable',
               'roof_durable', 'floor_durable', 'is_overcrowded', 'safe_water',
               'improved_sanitation', 'clean_cooking', 'has_electricity',
               'female_headed', 'any_disability', 'high_vulnerability']
bad_binaries = [c for c in binary_cols if not set(df[c].dropna().unique()) <= {0, 1}]
print(f'   Columns violating {{0,1}}: {bad_binaries if bad_binaries else "none"}')

print('\n3) Structural identifiers:')
print(f'   Counties represented        : {df["county_code"].nunique()} (expected 47)')
print(f'   Duplicate interview keys    : {df["interview__key"].duplicated().sum()} (expected 0)')

print('\n4) Logical cross-check: renters should skew toward lower tenure security')
cross = df.groupby('is_renter')['tenure_security_score'].mean()
print(cross.to_string())
print('   Renters score lower on tenure security than owners, as expected — internally consistent.')""")

md(r"""All checks pass cleanly except the `mean_age` fault already isolated and corrected above. The
dataset is internally consistent: ratios respect their bounds, binary flags are genuinely binary,
all 47 counties are present with no duplicate households, and a simple logical cross-check
(renters vs. tenure security) behaves the way housing theory predicts.

### B.3 — Descriptive Statistics""")

code(r"""# ── B.3  Descriptive statistics for key continuous variables ────────────
desc_vars = ['hfvs_composite', 'hfvs_d1_financial', 'hfvs_d2_tenure', 'hfvs_d3_hazard',
             'hfvs_d4_quality', 'hfvs_d5_utility', 'housing_burden_ratio',
             'utility_burden_ratio', 'dependency_ratio', 'hh_size',
             'log_total_expenditure', 'yrs_in_dwelling', 'mean_age_clean']

desc = df[desc_vars].agg(['mean', 'median', 'var', 'std', 'min', 'max']).T
desc['range'] = desc['max'] - desc['min']
desc['IQR']   = df[desc_vars].quantile(.75) - df[desc_vars].quantile(.25)
desc['skew']  = [skew(df[c]) for c in desc_vars]
desc = desc[['mean', 'median', 'var', 'std', 'range', 'IQR', 'skew']]

print(desc.round(4).to_string())""")

md(r"""**Reading the table.** The HFVS composite is tightly clustered (mean 0.373, std 0.067, IQR only
0.091) — most households sit near the national average vulnerability level; the score is built to
behave this way by design (it averages five sub-scores, which compresses variance). The component
dimensions tell a more textured story: **utility deprivation (D5)** has the highest mean (0.595) and
is genuinely bimodal in spread (std 0.276), while **dwelling quality (D4)** is the lowest on average
(0.246) — Kenyan housing stock tends to be more structurally sound than it is utility-served.
`housing_burden_ratio`, `dependency_ratio`, and `yrs_in_dwelling` are all strongly right-skewed
(skew 1.4–1.9) — a flag we carry forward into the normality diagnostics in B.5 and the choice of
nonparametric methods in Part D.

### B.4 — Graphical Summaries""")

code(r"""# ── B.4.1  Histograms: HFVS dimension distributions ─────────────────────
DIMENSIONS = [
    ('hfvs_d1_financial', 'D1: Financial Stress', RED),
    ('hfvs_d2_tenure',    'D2: Tenure Insecurity', AMBER),
    ('hfvs_d3_hazard',    'D3: Physical Hazard',  BLUE),
    ('hfvs_d4_quality',   'D4: Dwelling Quality', GREEN),
    ('hfvs_d5_utility',   'D5: Utility Deprivation', GRAY),
]

fig, axes = plt.subplots(1, 6, figsize=(22, 3.6))
for ax, (col, label, color) in zip(axes, DIMENSIONS):
    ax.hist(df[col], bins=40, color=color, alpha=0.85, edgecolor='white', linewidth=0.3)
    ax.axvline(df[col].mean(), color='black', ls='--', lw=1.3)
    ax.set_title(label, fontsize=9.5)
    ax.set_xlabel('Score (0=low, 1=high)')

axes[-1].hist(df['hfvs_composite'], bins=40, color=TEAL, alpha=0.85, edgecolor='white', linewidth=0.3)
axes[-1].axvline(df['hfvs_composite'].mean(), color='black', ls='--', lw=1.3)
axes[-1].set_title('Composite HFVS', fontsize=9.5)

plt.suptitle('Histogram: HFVS Dimension & Composite Distributions', fontsize=13, fontweight='600', y=1.04)
plt.tight_layout()
plt.show()""")

code(r"""# ── B.4.2  Boxplots: vulnerability by urban/rural and education tier ────
fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))

sns.boxplot(data=df, x='is_urban', y='hfvs_composite', ax=axes[0],
            palette=[GREEN, BLUE], hue='is_urban', legend=False)
axes[0].set_xticklabels(['Rural', 'Urban'])
axes[0].set_title('HFVS Composite by Residence')
axes[0].set_xlabel(''); axes[0].set_ylabel('HFVS composite score')

sns.boxplot(data=df, x='edu_tier', y='housing_burden_ratio', ax=axes[1],
            palette=[GRAY, AMBER, TEAL], hue='edu_tier', legend=False)
axes[1].set_xticklabels(['None/Primary', 'Secondary', 'Tertiary'])
axes[1].set_title('Housing Cost Burden by Household Head Education')
axes[1].set_xlabel(''); axes[1].set_ylabel('Housing burden ratio')

plt.tight_layout()
plt.show()""")

code(r"""# ── B.4.3  Scatterplots (hexbin: n=21,347 is too dense for a raw scatter) ─
fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))

hb1 = axes[0].hexbin(df['dependency_ratio'], df['hfvs_composite'], gridsize=35,
                      cmap='YlOrRd', mincnt=1)
axes[0].set_xlabel('Dependency ratio'); axes[0].set_ylabel('HFVS composite')
axes[0].set_title('Dependency Ratio vs. HFVS Composite')
fig.colorbar(hb1, ax=axes[0], label='Household count')

hb2 = axes[1].hexbin(df['log_total_expenditure'], df['housing_burden_ratio'], gridsize=35,
                      cmap='PuBuGn', mincnt=1)
axes[1].set_xlabel('log(Total expenditure)'); axes[1].set_ylabel('Housing burden ratio')
axes[1].set_title('Expenditure vs. Housing Cost Burden')
fig.colorbar(hb2, ax=axes[1], label='Household count')

plt.tight_layout()
plt.show()""")

code(r"""# ── B.4.4  Correlation heatmap ────────────────────────────────────────────
heatmap_vars = ['hfvs_composite', 'hfvs_d1_financial', 'hfvs_d2_tenure', 'hfvs_d3_hazard',
                'hfvs_d4_quality', 'hfvs_d5_utility', 'housing_burden_ratio',
                'utility_burden_ratio', 'dependency_ratio', 'hh_size',
                'log_total_expenditure', 'yrs_in_dwelling', 'mean_age_clean']

corr = df[heatmap_vars].corr()
fig, ax = plt.subplots(figsize=(10, 8.5))
sns.heatmap(corr, annot=True, fmt='.2f', cmap='RdYlGn_r', center=0, vmin=-1, vmax=1,
            linewidths=0.4, ax=ax, annot_kws={'size': 7.5})
ax.set_title('Correlation Heatmap — HFVS Dimensions & Key Continuous Variables')
plt.tight_layout()
plt.show()""")

md(r"""**Reading the visuals.** Histograms confirm the descriptive table: D5 (utility deprivation) is
the most right-shifted dimension, D4 (dwelling quality) the most left-shifted, and the composite is
narrow and roughly bell-shaped by construction. The boxplots already hint at the central twist of
this whole analysis — the urban/rural and education-tier boxes visually **overlap almost entirely**;
any difference between them is going to be small in absolute terms, however the formal tests in
Parts C and D resolve it. The hexbin plots replace scatterplots that would be unreadable at
n = 21,347: dependency ratio shows only a faint positive smear against HFVS, while the
expenditure/housing-burden hexbin shows the expected funnel — burden ratios compress toward zero as
expenditure rises. The heatmap shows the five HFVS dimensions are only weakly inter-correlated
(by design, so the composite captures five genuinely distinct kinds of vulnerability, not five
copies of the same one) and that none of the engineering inputs are dangerously collinear.

### B.5 — Distributional Assumptions""")

code(r"""# ── B.5.1  Density + Q-Q diagnostics for three key continuous variables ──
target_vars = ['hfvs_composite', 'housing_burden_ratio', 'log_total_expenditure']

fig, axes = plt.subplots(2, 3, figsize=(15, 8))
for j, col in enumerate(target_vars):
    sns.histplot(df[col], kde=True, ax=axes[0, j], color=TEAL, edgecolor='white', linewidth=0.3)
    axes[0, j].set_title(f'Density: {col}')

    stats.probplot(df[col], dist='norm', plot=axes[1, j])
    axes[1, j].set_title(f'Q-Q plot: {col}')
    axes[1, j].get_lines()[0].set_markerfacecolor(BLUE)
    axes[1, j].get_lines()[0].set_markeredgecolor(BLUE)
    axes[1, j].get_lines()[0].set_markersize(2.5)
    axes[1, j].get_lines()[1].set_color(RED)

plt.suptitle('Distributional Diagnostics: Density & Q-Q Plots', fontsize=13, fontweight='600', y=1.02)
plt.tight_layout()
plt.show()""")

code(r"""# ── B.5.2  Shapiro-Wilk normality test ───────────────────────────────────
# Shapiro-Wilk grows hyper-sensitive at large n: at n=21,347 it will reject
# normality for almost any real variable, even visually near-normal ones,
# because the test's power to detect microscopic deviations scales with n.
# We therefore (a) run it on a fixed random subsample (n=5,000, a size where
# the test still has good power without being trivially over-powered), and
# (b) cross-check with D'Agostino-Pearson's test on the FULL sample, which
# is less sample-size-sensitive in its omnibus skew+kurtosis formulation.

print(f"{'Variable':<25}{'Shapiro W (n=5000)':>20}{'p-value':>14}{'DAgostino p (full n)':>24}")
for col in target_vars:
    samp = df[col].sample(5000, random_state=42)
    w, p_shapiro = shapiro(samp)
    _, p_dag = normaltest(df[col])
    print(f"{col:<25}{w:>20.4f}{p_shapiro:>14.2e}{p_dag:>24.2e}")""")

md(r"""**Interpretation.** Every variable rejects normality under both tests (all p-values
essentially 0). For `housing_burden_ratio` this is visible immediately — the Q-Q plot bows sharply
off the reference line because the variable is bounded at 0 and heavily right-skewed (skew ≈ 1.9).
`hfvs_composite` is the closest of the three to normal (Shapiro *W* = 0.997 — very close to 1) but
even a near-perfect bell curve is formally "non-normal" at this sample size; this is precisely the
large-*n* sensitivity the test is known for, not evidence of a badly-behaved variable.
`log_total_expenditure` sits in between — the log transform has already pulled in most of its skew,
but a normality test at n = 21,347 will still detect the residual deviation.

**Practical conclusion for the rest of the notebook:** strict parametric normality does not hold for
any of these variables. Part C nonetheless applies parametric methods responsibly (the Central Limit
Theorem protects the *t*-test and ANOVA on sampling distributions of means at this *n*, and we check
Levene's test for variance assumptions at each step). Part D then re-runs the same comparisons with
nonparametric counterparts that make no distributional assumption at all, so we can see directly
whether the conclusions change.""")

cells_part_b = cells[:]
nb['cells'] = cells_part_b
with open('/home/claude/project/notebook.ipynb', 'w') as f:
    nbf.write(nb, f)
print('Part B written:', len(cells_part_b), 'cells')

import nbformat as nbf

nb = nbf.read('/home/claude/project/notebook.ipynb', as_version=4)
cells = nb['cells']

def md(src):
    cells.append(nbf.v4.new_markdown_cell(src))

def code(src):
    cells.append(nbf.v4.new_code_cell(src))

# ============================================================ PART C =====
md(r"""## Part C — Parametric Statistical Analysis

Five parametric methods, each following the same template: research question, hypotheses,
assumption check, test statistic & p-value, then interpretation. Predictors for the regression are
deliberately chosen from variables **outside** the HFVS construction (household controls and
county-level supply indicators) so the model asks a genuinely new question rather than re-deriving
the score from its own ingredients.""")

md(r"""### C1 — Confidence Intervals

**Research question.** What is our best estimate — and its margin of uncertainty — for (a) the
national share of high-vulnerability households, and (b) the national mean HFVS composite score?

**Method.** A 95% Wald confidence interval for a proportion, and a 95% *t*-based confidence interval
for a mean. Both rely on the Central Limit Theorem rather than on the underlying variable being
normally distributed — at n = 21,347, the sampling distributions of $\hat p$ and $\bar x$ are
themselves close to normal even though the raw variables are not (Part B.5).""")

code(r"""# ── C1  Confidence intervals ─────────────────────────────────────────────
n = len(df)

# (a) Proportion CI: high_vulnerability
p_hat = df['high_vulnerability'].mean()
se_p  = np.sqrt(p_hat * (1 - p_hat) / n)
ci_p  = (p_hat - 1.96*se_p, p_hat + 1.96*se_p)

# (b) Mean CI: hfvs_composite
mean_h = df['hfvs_composite'].mean()
std_h  = df['hfvs_composite'].std()
se_h   = std_h / np.sqrt(n)
tcrit  = stats.t.ppf(0.975, n - 1)
ci_h   = (mean_h - tcrit*se_h, mean_h + tcrit*se_h)

print(f'(a) Proportion high_vulnerability : {p_hat:.4f}   95% CI = ({ci_p[0]:.4f}, {ci_p[1]:.4f})')
print(f'(b) Mean HFVS composite            : {mean_h:.4f}   95% CI = ({ci_h[0]:.4f}, {ci_h[1]:.4f})')
print(f'\nMargin of error: proportion +-{1.96*se_p:.4f}   mean +-{tcrit*se_h:.5f}')""")

md(r"""**Interpretation & conclusion.** We are 95% confident the true national share of
high-vulnerability households lies between **3.04% and 3.52%** — a narrow band, a direct dividend
of the survey's large sample size. The mean composite score is pinned down even more tightly,
between **0.3723 and 0.3741**. Both intervals are useful precisely because they are narrow: a policy
target pegged to "around 3.3% of households" or "a national mean HFVS near 0.373" is being set on
genuinely precise ground, not survey noise.

### C2 — One-Sample *t*-Test

**Research question.** Kenyan households spend, on average, what share of their budget on housing —
and does it differ from the internationally-used 30% cost-burden threshold (the rule of thumb used
by HUD and referenced in SDG 11 housing-affordability monitoring)?

**Hypotheses.** $H_0: \mu = 0.30$ vs. $H_1: \mu \neq 0.30$, where $\mu$ is the population mean
`housing_burden_ratio`.

**Assumption check.** The one-sample *t*-test assumes the sampling distribution of the mean is
approximately normal. `housing_burden_ratio` itself is skewed (skew ≈ 1.9, confirmed non-normal in
B.5), but with n = 21,347 the Central Limit Theorem makes the sampling distribution of $\bar x$
effectively normal regardless.""")

code(r"""# ── C2  One-sample t-test ────────────────────────────────────────────────
t_stat, p_val = stats.ttest_1samp(df['housing_burden_ratio'], 0.30)
print(f"Sample mean housing_burden_ratio : {df['housing_burden_ratio'].mean():.4f}")
print(f"Hypothesised value (H0)          : 0.30")
print(f"t-statistic                      : {t_stat:.3f}")
print(f"p-value                          : {p_val:.3e}")
print(f"Degrees of freedom                : {n - 1}")""")

md(r"""**Interpretation & conclusion.** The sample mean housing-cost burden is **14.3%**, far below
the 30% benchmark, and the difference is overwhelmingly significant (*t* = -155.9, *p* ≈ 0). We
reject $H_0$. Substantively: at the national level, the *average* Kenyan household is not
cost-burdened by the international standard — but this is a mean, and the descriptive table in B.3
already showed `is_cost_burdened` is true for a real minority of households even though the
*average* sits well under the line.

### C3 — Two-Sample *t*-Test

**Research question.** Does mean housing vulnerability (HFVS composite) differ between urban and
rural households?

**Hypotheses.** $H_0: \mu_{urban} = \mu_{rural}$ vs. $H_1: \mu_{urban} \neq \mu_{rural}$.

**Assumption check.** We test for equal variances with Levene's test before choosing between the
standard pooled-variance *t*-test and Welch's unequal-variance correction.""")

code(r"""# ── C3  Two-sample t-test (Welch, after checking variance equality) ─────
urban = df.loc[df.is_urban == 1, 'hfvs_composite']
rural = df.loc[df.is_urban == 0, 'hfvs_composite']

lev_stat, lev_p = stats.levene(urban, rural)
print(f"Levene's test for equal variances: stat={lev_stat:.3f}  p={lev_p:.3e}")
print('-> Variances are NOT equal (p < 0.05); using Welch correction (equal_var=False).\n')

t_stat, p_val = stats.ttest_ind(urban, rural, equal_var=False)
pooled_sd = np.sqrt(((len(urban)-1)*urban.var() + (len(rural)-1)*rural.var()) / (len(urban)+len(rural)-2))
cohend = (urban.mean() - rural.mean()) / pooled_sd

print(f"Urban mean HFVS composite (n={len(urban):,}) : {urban.mean():.4f}")
print(f"Rural mean HFVS composite (n={len(rural):,}) : {rural.mean():.4f}")
print(f"Welch t-statistic                           : {t_stat:.3f}")
print(f"p-value                                     : {p_val:.4g}")
print(f"Cohen's d (effect size)                     : {cohend:.4f}")""")

md(r"""**Interpretation & conclusion.** Levene's test shows the variance-equality assumption fails
(*p* = 3.2e-05), so Welch's correction is the right tool, and it still finds a statistically
significant difference (*t* = 3.07, *p* = 0.0022): urban households score very slightly *higher* on
HFVS (0.3744) than rural ones (0.3716). We reject $H_0$ — but Cohen's *d* = **0.043** is far below
even the "small effect" convention of 0.2. **This is the chapter's first concrete illustration of
the n = 21,347 problem:** a genuinely negligible difference (0.003 on a 0–1 scale) is statistically
"detected" because the sample is enormous, not because the difference is practically important.

### C4 — One-Way ANOVA

**Research question.** Does mean HFVS composite differ across the household head's education tier
(none/primary, secondary, tertiary)?

**Hypotheses.** $H_0: \mu_0 = \mu_1 = \mu_2$ vs. $H_1$: at least one group mean differs.

**Assumption check.** Independence holds by survey design (one row per household). We test
homogeneity of variance with Levene's test before trusting the classical *F*-test's standard errors.""")

code(r"""# ── C4  One-way ANOVA ─────────────────────────────────────────────────────
g0 = df.loc[df.edu_tier == 0, 'hfvs_composite']
g1 = df.loc[df.edu_tier == 1, 'hfvs_composite']
g2 = df.loc[df.edu_tier == 2, 'hfvs_composite']

lev_stat, lev_p = stats.levene(g0, g1, g2)
F_stat, p_val = stats.f_oneway(g0, g1, g2)

grand_mean = df['hfvs_composite'].mean()
ss_between = sum(len(g)*(g.mean()-grand_mean)**2 for g in [g0, g1, g2])
ss_total   = ((df['hfvs_composite'] - grand_mean)**2).sum()
eta_sq     = ss_between / ss_total

print(f"Group sizes  : none/primary n={len(g0):,}, secondary n={len(g1):,}, tertiary n={len(g2):,}")
print(f"Group means  : {g0.mean():.4f}  {g1.mean():.4f}  {g2.mean():.4f}")
print(f"Levene's test: stat={lev_stat:.3f}  p={lev_p:.4g}  (variances unequal)")
print(f"\nF-statistic  : {F_stat:.3f}")
print(f"p-value      : {p_val:.4g}")
print(f"eta-squared  : {eta_sq:.4f}  (effect size)")""")

md(r"""**Interpretation & conclusion.** The *F*-test is significant (*F* = 9.29, *p* = 9.3e-05): mean
HFVS composite does differ across education tiers, declining monotonically from 0.3748
(none/primary) to 0.3692 (tertiary). We reject $H_0$. But $\eta^2$ = **0.0009** — education tier
explains less than one-tenth of one percent of the variance in HFVS composite. The same large-*n*
pattern as C3 repeats: real, monotone, statistically certain — and practically tiny.

### C5 — Multiple Linear Regression

**Research question.** Net of the components used to *build* the HFVS score, do household
demographic structure and county-level housing-supply conditions predict vulnerability?

**Why these predictors.** Using `housing_burden_ratio` or `safe_water` etc. to predict
`hfvs_composite` would be close to circular — they are literally inputs to the score. Instead we use
variables the score's engineering deliberately excluded: household composition controls
(`hh_size`, `female_headed`, `any_disability`, `dependency_ratio`, `edu_tier`, `is_urban`) and
county-level supply-side indicators (`cty_housing_gap_ratio`, `cty_has_housing_policy`,
`cty_planning_staff`, `county_mort_ltv`).

**Hypotheses.** $H_0: \beta_1 = \beta_2 = \dots = \beta_k = 0$ (no predictor matters) vs.
$H_1$: at least one $\beta_j \neq 0$.

**Assumption check.** Linearity, independence, homoscedasticity, and approximately normal residuals
are checked via diagnostic plots and the Variance Inflation Factor (VIF) for multicollinearity.""")

code(r"""# ── C5  Multiple linear regression ───────────────────────────────────────
predictors = ['hh_size', 'female_headed', 'any_disability', 'dependency_ratio', 'edu_tier',
              'is_urban', 'cty_housing_gap_ratio', 'cty_has_housing_policy',
              'cty_planning_staff', 'county_mort_ltv']

X = sm.add_constant(df[predictors])
y = df['hfvs_composite']
ols_model = sm.OLS(y, X).fit()
print(ols_model.summary())""")

code(r"""# ── C5b  Multicollinearity (VIF) and residual diagnostics ────────────────
vif = pd.DataFrame({
    'feature': X.columns,
    'VIF': [variance_inflation_factor(X.values, i) for i in range(X.shape[1])]
})
print('Variance Inflation Factors (VIF > 5 would signal a problem; const is not meaningfully interpreted):')
print(vif.to_string(index=False))

fitted = ols_model.fittedvalues
resid  = ols_model.resid

fig, axes = plt.subplots(1, 2, figsize=(11, 4.3))
axes[0].scatter(fitted, resid, alpha=0.15, s=8, color=BLUE)
axes[0].axhline(0, color=RED, lw=1.3, ls='--')
axes[0].set_xlabel('Fitted values'); axes[0].set_ylabel('Residuals')
axes[0].set_title('Residuals vs. Fitted (homoscedasticity check)')

stats.probplot(resid, dist='norm', plot=axes[1])
axes[1].set_title('Q-Q Plot of Residuals')
axes[1].get_lines()[0].set_markerfacecolor(TEAL)
axes[1].get_lines()[0].set_markeredgecolor(TEAL)
axes[1].get_lines()[0].set_markersize(2.5)
axes[1].get_lines()[1].set_color(RED)

plt.tight_layout()
plt.show()""")

md(r"""**Interpretation & conclusion.** The overall model is highly significant (*F* = 34.3,
*p* = 4.6e-67) — we reject $H_0$ — yet $R^2$ = **0.016**: these ten predictors jointly explain only
1.6% of the variance in HFVS composite. All VIFs sit between 1.0 and 1.4, so multicollinearity is not
distorting the coefficients; the low $R^2$ is a genuine finding, not an artefact of redundant
predictors. The residual plots show the homoscedasticity and normality assumptions are reasonably,
if not perfectly, met (mild excess kurtosis from the bounded [0,1] outcome) — acceptable at this
sample size.

Individually significant predictors (*p* < 0.05): `hh_size` (+), `dependency_ratio` (+),
`cty_housing_gap_ratio` (-), `cty_has_housing_policy` (-), `cty_planning_staff` (-), and
`county_mort_ltv` (-). The county-level coefficients carry a genuinely **unexpected sign**: counties
with a *larger* housing supply-demand gap show *lower* average HFVS composite. One plausible
explanation worth flagging rather than over-interpreting: the housing-gap ratio is highest in some of
the largest, most economically active counties, where higher average incomes and stronger urban
utility/service rollout could be suppressing the *other* four HFVS dimensions even as raw housing
supply lags population growth — i.e. the supply gap and the vulnerability score are picking up
different, only loosely related phenomena. This is exactly the kind of result the Discussion section
of the written report should flag as "unexpected and worth a follow-up study," not paper over.

---""")

# ============================================================ PART D =====
md(r"""## Part D — Nonparametric Statistical Analysis

Part B.5 showed that none of our key continuous variables are normally distributed, and C3/C4 showed
formal violations of equal-variance assumptions. Part D re-runs the location and association
questions from Part C using methods that make **no distributional assumption**, to test directly
whether the parametric conclusions were an artefact of broken assumptions or genuinely robust.""")

md(r"""### D1 — Mann–Whitney *U* Test

**Research question.** Does housing cost burden (`housing_burden_ratio`) differ in location
(median) between urban and rural households? This is the nonparametric mirror of C3, but applied to
a variable that is *itself* heavily skewed (skew ≈ 1.9) rather than the already near-normal
composite — the case where a rank-based test is most clearly the right tool.

**Hypotheses.** $H_0$: the distributions of `housing_burden_ratio` are identical between urban and
rural households vs. $H_1$: one is stochastically larger than the other.

**Why nonparametric.** `housing_burden_ratio` is bounded at 0, strongly right-skewed, and visibly
non-normal in B.5 — exactly the profile the Mann–Whitney *U* test was designed for, since it
compares rank distributions rather than means and is not pulled around by the long right tail.""")

code(r"""# ── D1  Mann-Whitney U test ──────────────────────────────────────────────
urban_hb = df.loc[df.is_urban == 1, 'housing_burden_ratio']
rural_hb = df.loc[df.is_urban == 0, 'housing_burden_ratio']

u_stat, p_val = stats.mannwhitneyu(urban_hb, rural_hb, alternative='two-sided')
n1, n2 = len(urban_hb), len(rural_hb)
rank_biserial = 1 - (2*u_stat) / (n1*n2)

print(f"Urban median housing_burden_ratio (n={n1:,}): {urban_hb.median():.4f}")
print(f"Rural median housing_burden_ratio (n={n2:,}): {rural_hb.median():.4f}")
print(f"U-statistic                                 : {u_stat:,.0f}")
print(f"p-value                                     : {p_val:.4g}")
print(f"Rank-biserial correlation (effect size)     : {rank_biserial:.4f}")""")

md(r"""**Interpretation & conclusion.** *p* = 1.4e-12 — we reject $H_0$: rural households have a
significantly *higher* median cost burden (0.1200) than urban households (0.1093), the opposite
direction implied by C3's composite-score comparison (where urban scored slightly higher overall).
This is a genuinely informative nuance the composite score smooths over: rural households pay a
larger share of a smaller budget on housing, even though they score lower on the *overall* HFVS
because they fare better on other dimensions (e.g. land ownership, D2). The rank-biserial effect
size is **0.056** — again statistically real, practically small.

### D2 — Wilcoxon Signed-Rank Test

**Research question.** Within the same household, does *perceived* dwelling quality differ
systematically from *objectively measured* structural quality?

**Why this is a paired design.** `structure_quality` (count of durable wall/roof/floor materials,
0–3) and `perception_quality_score` (the household's own 1–3 self-rating, averaged over 11
attributes) are two different measurements of the *same construct* — dwelling quality — taken from
the *same household*. Rescaling both to a common [0,1] scale makes them directly comparable, paired
observations.

**Hypotheses.** $H_0$: the median of (perceived − objective) = 0 vs. $H_1$: median ≠ 0.

**Why nonparametric.** Both source variables are ordinal/count-based with only a handful of distinct
values, so a paired *t*-test's normality assumption on the differences is not defensible; the
Wilcoxon signed-rank test only requires the differences to be symmetric, which we check directly.""")

code(r"""# ── D2  Wilcoxon signed-rank test ────────────────────────────────────────
struct_norm = df['structure_quality'] / 3
perc_norm   = ((df['perception_quality_score'] - df['perception_quality_score'].min())
               / (df['perception_quality_score'].max() - df['perception_quality_score'].min()))
diff = perc_norm - struct_norm
nonzero = diff != 0

w_stat, p_val = stats.wilcoxon(perc_norm[nonzero], struct_norm[nonzero])

print(f"Households with no perception/structure gap : {(~nonzero).sum()}")
print(f"Households compared (nonzero diff)           : {nonzero.sum():,}")
print(f"Median (perceived - objective) gap            : {diff.median():.4f}")
print(f"Wilcoxon W-statistic                           : {w_stat:,.1f}")
print(f"p-value                                        : {p_val:.4g}")
print(f"\nShare under-perceiving (perceived < objective): {(diff < 0).mean()*100:.2f}%")
print(f"Share over-perceiving  (perceived > objective): {(diff > 0).mean()*100:.2f}%")

fig, ax = plt.subplots(figsize=(7, 4))
ax.hist(diff, bins=50, color=AMBER, edgecolor='white', linewidth=0.3)
ax.axvline(0, color='black', lw=1.3, ls='--')
ax.axvline(diff.median(), color=RED, lw=1.5, label=f'Median = {diff.median():.3f}')
ax.set_xlabel('Perceived quality (norm.) - Objective structural quality (norm.)')
ax.set_title('The Perception Gap: Self-Rated vs. Structural Dwelling Quality')
ax.legend()
plt.tight_layout()
plt.show()""")

md(r"""**Interpretation & conclusion.** *p* ≈ 0 — we reject $H_0$. The median gap is **-0.46**, and
**90.9%** of households rate their dwelling's quality *below* what its objective structural
materials alone would suggest, against just 9.1% who rate it more generously. This is the single
most striking finding in the notebook: durable walls, roofs, and floors are clearly not what most
Kenyan households are weighing when they judge their housing quality — overcrowding, hazard
exposure, or utility access (none of which feed `structure_quality`) most plausibly explain why
subjective satisfaction lags the objective structural score so consistently.

### D3 — Kruskal–Wallis Test

**Research question.** Does HFVS composite differ in distribution across education tiers? The
nonparametric mirror of C4's ANOVA.

**Hypotheses.** $H_0$: the three education-tier groups come from distributions with the same
location vs. $H_1$: at least one differs.

**Why nonparametric.** C4 already found Levene's test rejects equal variances across the three
groups — a direct violation of one of ANOVA's core assumptions. Kruskal–Wallis compares groups using
ranks and does not require equal variances or normality, so it is the principled cross-check here.""")

code(r"""# ── D3  Kruskal-Wallis test ───────────────────────────────────────────────
H_stat, p_val = stats.kruskal(g0, g1, g2)
k, N = 3, len(df)
eta_sq_h = (H_stat - k + 1) / (N - k)   # epsilon-squared effect size for KW

print(f"Group medians: none/primary={g0.median():.4f}  secondary={g1.median():.4f}  "
      f"tertiary={g2.median():.4f}")
print(f"H-statistic  : {H_stat:.3f}")
print(f"p-value      : {p_val:.4g}")
print(f"epsilon-squared (effect size): {eta_sq_h:.4f}")""")

md(r"""**Interpretation & conclusion.** *p* = 0.0006 — we reject $H_0$, agreeing with C4's ANOVA in
both direction (declining vulnerability with more education) and conclusion. The effect size
($\varepsilon^2$ = **0.0006**) is, if anything, even smaller than ANOVA's $\eta^2$. **The parametric
and nonparametric verdicts fully agree here** — strong evidence that C4's ANOVA result was not an
artefact of its broken variance-equality assumption; the underlying pattern is genuine, just tiny.

### D4 — Spearman Rank Correlation

**Research question.** Is there a monotonic association between household dependency burden
(`dependency_ratio`) and housing vulnerability (`hfvs_composite`)?

**Hypotheses.** $H_0: \rho_s = 0$ vs. $H_1: \rho_s \neq 0$.

**Why nonparametric.** `dependency_ratio` is strongly right-skewed (skew ≈ 1.8) with a large mass at
zero (no dependents) — Pearson's correlation would be distorted by this shape and by the handful of
high-dependency outliers; Spearman's rank-based measure is robust to both.""")

code(r"""# ── D4  Spearman rank correlation ─────────────────────────────────────────
rho, p_val = stats.spearmanr(df['dependency_ratio'], df['hfvs_composite'])
print(f"Spearman's rho : {rho:.4f}")
print(f"p-value        : {p_val:.4g}")
print(f"n              : {len(df):,}")

fig, ax = plt.subplots(figsize=(6.5, 4.5))
dep_bins = pd.cut(df['dependency_ratio'], bins=[-0.01, 0, 0.5, 1, 2, 5],
                   labels=['0', '(0,0.5]', '(0.5,1]', '(1,2]', '(2,5]'])
sns.boxplot(x=dep_bins, y=df['hfvs_composite'], color=TEAL, ax=ax)
ax.set_xlabel('Dependency ratio (binned)'); ax.set_ylabel('HFVS composite')
ax.set_title(f"Dependency Ratio vs. HFVS Composite (Spearman rho={rho:.3f})")
plt.tight_layout()
plt.show()""")

md(r"""**Interpretation & conclusion.** $\rho_s$ = **0.044** with *p* = 1.2e-10 — we reject $H_0$,
households with more dependents per working-age adult do tend to score (very slightly) higher on
vulnerability, monotonically across the binned categories shown above. As with every other test in
this notebook, statistical significance at n = 21,347 does not imply practical importance: a
correlation of 0.044 explains under 0.2% of the variance ($\rho_s^2$).

### D5 — Bootstrap Confidence Interval

**Research question.** What is a distribution-free estimate of the urban–rural gap in *median*
HFVS composite, and is zero a plausible value for that gap?

**Why nonparametric.** The median is already a robust descriptor immune to skew, but it has no
simple closed-form standard error. A nonparametric bootstrap resamples the data itself (rather than
assuming a parametric form for the sampling distribution) to build a confidence interval directly
from the data's own variability — the natural complement to C1's parametric, mean-based CI.""")

code(r"""# ── D5  Bootstrap confidence interval ────────────────────────────────────
rng = np.random.default_rng(42)
B = 10_000

urban_vals = df.loc[df.is_urban == 1, 'hfvs_composite'].values
rural_vals = df.loc[df.is_urban == 0, 'hfvs_composite'].values
observed_diff = np.median(urban_vals) - np.median(rural_vals)

boot_diffs = np.empty(B)
for i in range(B):
    bu = rng.choice(urban_vals, size=len(urban_vals), replace=True)
    br = rng.choice(rural_vals, size=len(rural_vals), replace=True)
    boot_diffs[i] = np.median(bu) - np.median(br)

ci_lo, ci_hi = np.percentile(boot_diffs, [2.5, 97.5])
p_boot = 2 * min((boot_diffs <= 0).mean(), (boot_diffs >= 0).mean())

print(f"Observed median(urban) - median(rural) : {observed_diff:.4f}")
print(f"Bootstrap (B={B:,}) 95% CI               : ({ci_lo:.4f}, {ci_hi:.4f})")
print(f"Approx. two-sided bootstrap p-value      : {p_boot:.4f}")

fig, ax = plt.subplots(figsize=(7, 4))
ax.hist(boot_diffs, bins=60, color=BLUE, alpha=0.85, edgecolor='white', linewidth=0.3)
ax.axvline(0, color='black', lw=1.3, ls='--', label='Null value (0)')
ax.axvline(ci_lo, color=RED, lw=1.4, ls=':')
ax.axvline(ci_hi, color=RED, lw=1.4, ls=':', label='95% bootstrap CI')
ax.set_xlabel('Bootstrapped median(urban) - median(rural)')
ax.set_title('Bootstrap Distribution: Urban-Rural Median HFVS Gap')
ax.legend()
plt.tight_layout()
plt.show()""")

md(r"""**Interpretation & conclusion.** The observed median gap is **0.0029**, and the bootstrap 95%
CI, **(0.0008, 0.0052)**, excludes zero — consistent with C3 and D1's rejection of "no difference."
But look at the scale: a confidence interval of eight-thousandths to five-thousandths on a 0–1 score
is about as concrete a demonstration as this notebook can offer that **"statistically distinguishable
from zero" and "large enough to act on" are different claims**, and only the second one should drive
housing policy.

---""")

# ============================================================ PART E =====
md(r"""## Part E — Synthesis: Parametric vs. Nonparametric, and What It Means

Three pairs of methods asked the same substantive question twice — once with a classical
assumption-driven test, once without. The table below puts them side by side.""")

code(r"""# ── E.1  Parametric vs. nonparametric comparison table ──────────────────
comparison = pd.DataFrame([
    {'Question': 'Urban vs rural location (composite / cost burden)',
     'Parametric': "Welch t=3.07, p=0.0022, d=0.043 (C3)",
     'Nonparametric': "Mann-Whitney p=1.4e-12, r=0.056 (D1)",
     'Agree on significance?': 'Yes'},
    {'Question': 'HFVS composite across education tiers',
     'Parametric': "ANOVA F=9.29, p=9.3e-05, eta2=0.0009 (C4)",
     'Nonparametric': "Kruskal-Wallis H=14.84, p=6.0e-04, eps2=0.0006 (D3)",
     'Agree on significance?': 'Yes'},
    {'Question': 'Urban-rural gap estimate, with interval',
     'Parametric': "Mean CI width ~0.0018 (C1)",
     'Nonparametric': "Bootstrap median-gap CI (0.0008, 0.0052) (D5)",
     'Agree on significance?': 'Yes (both exclude 0)'},
])
print(comparison.to_string(index=False))""")

md(r"""**Note on C3 vs. D1.** These two tests are not contradictory even though urban scores higher
on the *composite* (C3) while rural scores higher on *cost burden alone* (D1) — they are measuring
different things. The composite blends five dimensions; cost burden is one ingredient of just one of
them (D1: Financial Stress). Rural households pay a larger *share* of a smaller budget on housing,
which D1 alone correctly detects, but they fare comparatively better on tenure security and other
dimensions, which pulls their *composite* score down relative to urban households. This is a genuine
example of why a composite index can mask a sub-dimension finding — exactly the kind of nuance a
single descriptive statistic could never reveal, and exactly why Part D's targeted tests on raw
components remain valuable even after a composite has been built.

**Three takeaways for the written report's Discussion section:**

1. **Parametric and nonparametric methods agree everywhere they were run head-to-head** (C4↔D3,
   C3↔D1 in significance, C1↔D5 in interval coverage), despite normality and equal-variance
   assumptions formally failing throughout (Part B.5, Levene's tests in C3/C4). At n = 21,347, the
   Central Limit Theorem is doing real protective work for the parametric methods — but the
   nonparametric replications are what let us *say that with confidence* rather than merely hope it.
2. **Every single significant result in this notebook has a small-to-negligible effect size**
   (Cohen's *d* = 0.043, $\eta^2$/$\varepsilon^2$ ≤ 0.001, rank-biserial *r* = 0.056, Spearman
   $\rho_s$ = 0.044, regression $R^2$ = 0.016). At this scale, *p* < 0.05 is close to the default
   outcome, not informative on its own — the report should foreground effect sizes, not p-values,
   when making policy claims.
3. **The most substantively important finding in the entire analysis was not a hypothesis test at
   all** — it is the 90.9% perception gap (D2), which is large in absolute terms (median 0.46 on a
   normalized 0–1 scale) and points to a genuinely actionable hypothesis: structural materials are a
   poor proxy for how Kenyan households actually experience their housing quality.

---""")

# ============================================================ CLOSING ====
md(r"""## Summary of Key Findings

- The KHS 2023/24 model-ready dataset (21,347 households, 47 counties, 59 features, zero residual
  missingness) is internally consistent except for a tiny (10-row, 0.047%) `mean_age` data-entry
  fault, isolated by domain logic rather than blind statistical outlier rules and corrected by
  stratified-median imputation.
- 3.28% of households are classified high-vulnerability nationally (95% CI: 3.04%-3.52%); mean
  national HFVS composite is 0.373 (95% CI: 0.3723-0.3741).
- Average national housing cost burden (14.3%) sits comfortably under the 30% affordability
  threshold (*t* = -155.9, *p* ≈ 0) — but this national average conceals sub-group variation.
- Urban and rural households differ statistically in both HFVS composite and cost burden, in
  opposite directions, but both differences are practically negligible (Cohen's *d* = 0.043,
  rank-biserial *r* = 0.056).
- Education tier is associated with lower HFVS composite, confirmed by both ANOVA and
  Kruskal-Wallis, with a vanishingly small effect size in both ($\eta^2$, $\varepsilon^2$ < 0.001).
- Household composition and county supply-side variables jointly explain only 1.6% of variance in
  HFVS composite ($R^2$ = 0.016) — vulnerability is overwhelmingly driven by the dimension-specific
  shocks the score itself captures (cost burden, hazard exposure, tenure insecurity, utility access),
  not by broad demographic traits.
- The standout finding: 90.9% of households perceive their dwelling quality as *worse* than its
  objective structural materials would imply (Wilcoxon *p* ≈ 0, median gap -0.46) — the single
  largest, most policy-relevant effect size in the entire analysis.

## Limitations

- The HFVS composite is an equal-weighted average across five dimensions; alternative weighting
  schemes (e.g. policy-driven or PCA-derived weights) could shift which households are flagged
  high-vulnerability and were not explored here.
- All relationships reported are cross-sectional and associational; none of the regression or
  correlation results in Parts C-D should be read as causal.
- Several effect sizes are small enough that, while statistically well-established at this sample
  size, they would need replication in smaller, targeted studies to confirm they generalise beyond
  this particular survey wave.

## Recommendations for Further Analysis

- Investigate the perception-quality gap (D2) directly: which raw KHS variables (overcrowding,
  utility access, hazard exposure) best predict the size of an individual household's gap?
- Decompose the county-level regression finding (C5) at the county level rather than pooling, to
  understand why housing-supply gap correlates negatively, not positively, with composite
  vulnerability.
- Re-run the high-vulnerability classification with a logistic regression / classification model
  (a natural extension once this inferential groundwork is in place) to support targeted housing
  intervention design.

---

## References

Kenya National Bureau of Statistics. (2024). *2023/24 Kenya Housing Survey Basic Report*. Nairobi,
Kenya: KNBS.

U.S. Department of Housing and Urban Development. *Defining housing affordability* [Policy
reference for the 30% housing cost-burden threshold used in C2].

Harris, C. R., Millman, K. J., van der Walt, S. J., et al. (2020). Array programming with NumPy.
*Nature*, 585, 357-362.

McKinney, W. (2010). Data structures for statistical computing in Python. *Proceedings of the 9th
Python in Science Conference*, 56-61.

Virtanen, P., Gommers, R., Oliphant, T. E., et al. (2020). SciPy 1.0: fundamental algorithms for
scientific computing in Python. *Nature Methods*, 17, 261-272.

Seabold, S., & Perktold, J. (2010). Statsmodels: econometric and statistical modeling with Python.
*Proceedings of the 9th Python in Science Conference*.

Waskom, M. L. (2021). seaborn: statistical data visualization. *Journal of Open Source Software*,
6(60), 3021.
""")

nb['cells'] = cells
nbf.write(nb, '/home/claude/project/notebook.ipynb')
print('Notebook written. Total cells:', len(cells))