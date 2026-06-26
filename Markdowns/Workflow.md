# DSA 8301 — Statistical Inference for Big Data
## Project Workflow & Analysis Guide
**Strathmore University | MSc Data Science & Analytics**

---

> **How to use this guide:** Work through each phase in order. Each phase has a *goal*, a checklist of tasks, the Python tools to use, and the output you must produce for your report. Do not move to Phase C until Phase B is complete — your normality results in Phase B directly determine your test selection in Phases C and D.

---

## PHASE 0 — Dataset Selection & Problem Framing
**Goal:** Lock in your dataset and define your analytical story before writing a single line of code.

### Tasks
- [ ] Select a dataset meeting minimum requirements (≥100 observations, ≥4 variables, mixed types)
- [ ] Confirm the source is reputable (UCI, Kaggle, World Bank, WHO, government portal)
- [ ] Write a 3-sentence problem statement: *what is the domain, what question are you asking, why does it matter?*
- [ ] List your variables and hypothesize which ones are related — this is your analytical backbone

### Output for Report
- Title page details (finalize these now, not at the end)
- Introduction section draft (~1 page): background, motivation, objectives, statistical questions

---

## PHASE 1 — Environment & Data Loading
**Goal:** Clean, reproducible setup before any analysis.

### Tasks
- [ ] Set up your notebook with a clear header cell (title, date, author, dataset)
- [ ] Import all libraries upfront

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf
from sklearn.linear_model import LinearRegression
import warnings
warnings.filterwarnings('ignore')

# Notebook display settings
pd.set_option('display.float_format', '{:.4f}'.format)
plt.rcParams['figure.figsize'] = (10, 6)
sns.set_style('whitegrid')
```

- [ ] Load data: `df = pd.read_csv('your_data.csv')`
- [ ] First-look inspection:

```python
df.shape          # (n_rows, n_cols)
df.dtypes         # variable types
df.head()         # first 5 rows
df.info()         # full column summary
```

### Output for Report
- Dataset description table: variable name, type, description, units

---

## PHASE 2 — Data Preprocessing
**Goal:** Produce a clean, analysis-ready dataset and document every decision.

### 2.1 Missing Values
```python
# Count and percentage of missing per column
missing = pd.DataFrame({
    'count': df.isnull().sum(),
    'pct': (df.isnull().sum() / len(df) * 100).round(2)
}).query('count > 0')
print(missing)
```
- [ ] Decide per variable: **drop row / impute (mean, median, mode) / flag as separate category**
- [ ] Document your decision and justification for each variable with missingness

### 2.2 Outlier Detection
```python
# IQR method
Q1 = df[col].quantile(0.25)
Q3 = df[col].quantile(0.75)
IQR = Q3 - Q1
outliers = df[(df[col] < Q1 - 1.5*IQR) | (df[col] > Q3 + 1.5*IQR)]

# Z-score method
from scipy.stats import zscore
df['z'] = np.abs(zscore(df[col]))
outliers_z = df[df['z'] > 3]
```
- [ ] Decide: **remove / cap (Winsorize) / retain with note**
- [ ] Never silently drop outliers — justify each decision

### 2.3 Consistency Checks
```python
df.duplicated().sum()           # duplicate rows
df[col].value_counts()          # frequency of categoricals
df.describe()                   # impossible ranges (negative ages, etc.)
```

### Output for Report
- Preprocessing summary table: issue found → treatment applied → rows/values affected

---

## PHASE 3 — Exploratory Data Analysis (EDA)
**Goal:** Understand distributions, relationships, and normality. Results here gate Phase C/D choices.

### 3.1 Descriptive Statistics Table
```python
# For continuous variables
desc = df.select_dtypes(include=np.number).agg([
    'mean', 'median', 'std', 'var',
    lambda x: x.max() - x.min(),           # range
    lambda x: x.quantile(0.75) - x.quantile(0.25)  # IQR
]).T
desc.columns = ['Mean', 'Median', 'Std Dev', 'Variance', 'Range', 'IQR']
```

### 3.2 Graphical Summaries

**Histograms + KDE (one per continuous variable)**
```python
for col in num_cols:
    fig, ax = plt.subplots()
    sns.histplot(df[col], kde=True, ax=ax)
    ax.set_title(f'Distribution of {col}')
    plt.tight_layout()
    plt.savefig(f'hist_{col}.png', dpi=150)
```

**Boxplots (continuous split by categorical group)**
```python
sns.boxplot(x='categorical_var', y='continuous_var', data=df)
```

**Scatterplots (key pairs)**
```python
sns.scatterplot(x='var1', y='var2', hue='group', data=df)
# Or pairplot for overview:
sns.pairplot(df[num_cols + ['group']], hue='group')
```

**Correlation Heatmap**
```python
corr = df[num_cols].corr()
sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm', center=0)
plt.title('Pearson Correlation Heatmap')
```

### 3.3 Normality Assessment ← **CRITICAL DECISION GATE**
```python
# Q-Q plots
from scipy.stats import probplot
for col in num_cols:
    fig, ax = plt.subplots()
    probplot(df[col].dropna(), plot=ax)
    ax.set_title(f'Q-Q Plot: {col}')

# Shapiro-Wilk test
from scipy.stats import shapiro
normality_results = {}
for col in num_cols:
    stat, p = shapiro(df[col].dropna().sample(min(5000, len(df))))  # max 5000 for Shapiro
    normality_results[col] = {'W-statistic': stat, 'p-value': p,
                               'Normal (α=0.05)': 'Yes' if p > 0.05 else 'No'}
pd.DataFrame(normality_results).T
```

> **Decision rule:**
> - p > 0.05 → fail to reject normality → **eligible for parametric tests**
> - p ≤ 0.05 → normality rejected → **use nonparametric equivalents**
> - Record this table — reference it explicitly when justifying test choices in Phases C & D

### Output for Report
- Descriptive statistics table
- All figures (histograms, boxplots, scatterplots, heatmap, Q-Q plots) with captions and interpretations
- Normality summary table with conclusions

---

## PHASE 4 — Parametric Statistical Analysis
**Goal:** Apply ≥3 parametric methods. Use variables confirmed (or assumed) normal.

> For every single test, use this exact reporting structure:
> 1. Research question
> 2. H₀ and H₁
> 3. Assumptions checked
> 4. Test statistic + degrees of freedom
> 5. p-value
> 6. Decision (reject / fail to reject H₀ at α = 0.05)
> 7. Plain-English interpretation

---

### Method C1 — One-Sample t-Test
**Use when:** Testing if the mean of a variable equals a specific known value.

```python
from scipy.stats import ttest_1samp
stat, p = ttest_1samp(df['variable'], popmean=EXPECTED_VALUE)
print(f't = {stat:.4f}, p = {p:.4f}')
```
Assumption check: normality (from Phase 3), no extreme outliers

---

### Method C2 — Two-Sample Independent t-Test
**Use when:** Comparing means of one continuous variable between two groups.

```python
from scipy.stats import ttest_ind, levene
group_a = df[df['group'] == 'A']['variable']
group_b = df[df['group'] == 'B']['variable']

# Check equal variance assumption first
lev_stat, lev_p = levene(group_a, group_b)
equal_var = lev_p > 0.05  # True = equal variances

stat, p = ttest_ind(group_a, group_b, equal_var=equal_var)
print(f't = {stat:.4f}, p = {p:.4f}')
```

---

### Method C3 — One-Way ANOVA
**Use when:** Comparing means across 3 or more groups.

```python
from scipy.stats import f_oneway
groups = [df[df['group'] == g]['variable'] for g in df['group'].unique()]
stat, p = f_oneway(*groups)
print(f'F = {stat:.4f}, p = {p:.4f}')

# Post-hoc if significant (Tukey HSD)
from statsmodels.stats.multicomp import pairwise_tukeyhsd
tukey = pairwise_tukeyhsd(df['variable'], df['group'])
print(tukey.summary())
```

---

### Method C4 — Simple/Multiple Linear Regression
**Use when:** Modelling the relationship between continuous predictors and a continuous outcome.

```python
import statsmodels.formula.api as smf

# Simple: one predictor
model = smf.ols('outcome ~ predictor', data=df).fit()
print(model.summary())

# Multiple: several predictors
model = smf.ols('outcome ~ pred1 + pred2 + C(categorical)', data=df).fit()
print(model.summary())

# Residual diagnostics
residuals = model.resid
sm.qqplot(residuals, line='s')            # residuals normal?
plt.scatter(model.fittedvalues, residuals) # homoscedasticity?
```
Report: R², adjusted R², F-statistic, coefficients, p-values, confidence intervals

---

### Method C5 — Confidence Intervals
**Use when:** Estimating a population parameter with uncertainty bounds.

```python
import scipy.stats as stats

# 95% CI for a mean
n = len(df['variable'].dropna())
mean = df['variable'].mean()
se = stats.sem(df['variable'].dropna())
ci = stats.t.interval(0.95, df=n-1, loc=mean, scale=se)
print(f'95% CI: ({ci[0]:.4f}, {ci[1]:.4f})')
```

---

## PHASE 5 — Nonparametric Statistical Analysis
**Goal:** Apply ≥3 nonparametric methods. Use these for variables that failed normality in Phase 3.

> Same reporting structure as Phase 4, **plus** an explicit sentence explaining why the nonparametric approach is appropriate for this variable/question.

---

### Method D1 — Wilcoxon Signed-Rank Test
**Use when:** Nonparametric equivalent of the one-sample or paired t-test.

```python
from scipy.stats import wilcoxon
stat, p = wilcoxon(df['variable'] - EXPECTED_VALUE)
print(f'W = {stat:.4f}, p = {p:.4f}')
```

---

### Method D2 — Mann-Whitney U Test
**Use when:** Nonparametric equivalent of the two-sample t-test.

```python
from scipy.stats import mannwhitneyu
stat, p = mannwhitneyu(group_a, group_b, alternative='two-sided')
print(f'U = {stat:.4f}, p = {p:.4f}')
```

---

### Method D3 — Kruskal-Wallis Test
**Use when:** Nonparametric equivalent of one-way ANOVA (3+ groups).

```python
from scipy.stats import kruskal
stat, p = kruskal(*groups)
print(f'H = {stat:.4f}, p = {p:.4f}')
```

---

### Method D4 — Spearman Rank Correlation
**Use when:** Measuring monotonic association between two variables without normality assumption.

```python
from scipy.stats import spearmanr
rho, p = spearmanr(df['var1'], df['var2'])
print(f'ρ = {rho:.4f}, p = {p:.4f}')
```
Compare to Pearson from your heatmap — note any differences and explain.

---

### Method D5 — Bootstrap Confidence Intervals
**Use when:** Estimating a CI for any statistic without distributional assumptions.

```python
import numpy as np

def bootstrap_ci(data, stat_func=np.mean, n_boot=10000, ci=95):
    boot_stats = [stat_func(np.random.choice(data, size=len(data), replace=True))
                  for _ in range(n_boot)]
    lower = np.percentile(boot_stats, (100-ci)/2)
    upper = np.percentile(boot_stats, 100 - (100-ci)/2)
    return lower, upper

lower, upper = bootstrap_ci(df['variable'].dropna().values)
print(f'Bootstrap 95% CI: ({lower:.4f}, {upper:.4f})')
```

---

### Method D6 — Kolmogorov-Smirnov Test (optional 6th method)
**Use when:** Testing whether a variable follows a specific distribution, or comparing two samples.

```python
from scipy.stats import kstest, ks_2samp

# Test against normal distribution
stat, p = kstest(df['variable'], 'norm',
                  args=(df['variable'].mean(), df['variable'].std()))
print(f'KS = {stat:.4f}, p = {p:.4f}')
```

---

## PHASE 6 — Report Writing
**Goal:** Translate your code outputs into a clean, structured academic report.

### Section Checklist

| Section | Key Content | Length |
|---|---|---|
| Title Page | Title, name, reg no., course, lecturer, institution, date | — |
| Introduction | Background, motivation, objectives, statistical questions | ~1 page |
| Dataset Description | Source, n, variables, types, preprocessing decisions | ~1 page |
| Methodology | Methods used, assumptions, packages, justifications | ~1 page |
| Results | All tables, figures, test outputs — organized by phase | ~3–4 pages |
| Discussion | Interpret findings, compare parametric vs nonparametric, flag surprises | ~1 page |
| Conclusions | Key findings, limitations, recommendations | ~0.5 page |
| References | Dataset, Python docs, textbooks — APA or IEEE style | — |

### Results Presentation Standard
Every hypothesis test result must appear in a table like this:

| Test | Variable(s) | Statistic | df | p-value | Decision |
|---|---|---|---|---|---|
| One-sample t | var_name | t = 2.34 | 149 | 0.021 | Reject H₀ |
| Mann-Whitney U | var1 vs var2 | U = 1842 | — | 0.008 | Reject H₀ |

---

## PHASE 7 — Submission Checklist
- [ ] PDF report (5–10 pages, properly formatted)
- [ ] Jupyter Notebook (.ipynb) — all cells run, outputs visible, code commented
- [ ] Dataset file (.csv or equivalent)
- [ ] All figures embedded in report with figure numbers and captions
- [ ] All references cited consistently (APA/IEEE)
- [ ] Title page complete
- [ ] Due date: **17th June 2026**

---

## Quick Reference — Test Selection Decision Tree

```
Is the variable approximately normal? (Shapiro-Wilk p > 0.05)
│
├── YES (normal)
│   ├── One group, test against known value  → One-sample t-test
│   ├── Two independent groups               → Two-sample t-test
│   ├── Two paired/related groups            → Paired t-test
│   ├── Three or more groups                 → ANOVA (+Tukey post-hoc)
│   ├── Relationship between variables       → Pearson correlation / Linear regression
│   └── Estimate with uncertainty            → t-based Confidence Interval
│
└── NO (non-normal)
    ├── One group, test against known value  → Wilcoxon signed-rank
    ├── Two independent groups               → Mann-Whitney U
    ├── Two paired/related groups            → Wilcoxon signed-rank (paired)
    ├── Three or more groups                 → Kruskal-Wallis
    ├── Relationship between variables       → Spearman correlation
    └── Estimate with uncertainty            → Bootstrap CI
```

---

