# Aberporth Climate Analysis — Python

A time-series exploratory data analysis of 84 years of monthly weather observations (1941–2025) from the Aberporth weather station in Wales, using Python. The project covers data cleaning, missing-value treatment, exploratory analysis, and visual storytelling across temperature, rainfall, sunshine, and air frost.

**Tools:** Python · pandas · NumPy · Matplotlib · Seaborn
**Domain:** Climate / Meteorology · **Dataset:** UK Met Office MIDAS-style monthly records (1,020 observations)

---

## Business / Analytical Question

Long-term station weather data is messy: different instruments, estimated values, and decades of partial records. The goal of this project was to turn raw monthly observations into a clean, analysis-ready dataset and answer:

1. How do temperature, rainfall, sunshine, and frost vary **seasonally**?
2. Are there **long-term trends** (e.g. warming) across the 84-year record?
3. How should **missing values** be handled responsibly for each variable?
4. What **data-quality limitations** should temper the conclusions?

---

## Dataset

| Variable | Description | Type |
|----------|-------------|------|
| `Year`, `Month` | Calendar year and month of observation | Integer |
| `Max_Temperature(DegC)` | Average monthly maximum temperature | Float |
| `Min_Temperature(DegC)` | Average monthly minimum temperature | Float |
| `Rainfall(mm)` | Total monthly rainfall | Float |
| `Sunshine_hours` | Total monthly sunshine hours | Float |
| `Air_Frost_Days` | Days in the month with air frost (min temp ≤ 0°C) | Integer |

Source: Aberporth station data, aligned with UK Met Office MIDAS monthly climate record conventions.

---

## Approach

### 1. Data Cleaning & Missing-Value Strategy
A key focus of the project — each variable was treated according to its statistical nature rather than applying one blanket method:

- **Temperature** (smooth, autocorrelated): time-based interpolation combined with backward-fill, since early records had no preceding values to interpolate from.
- **Sunshine** (continuous, seasonal): converted from object to numeric (removing instrument markers), then imputed using **monthly median** to respect seasonal patterns.
- **Air Frost Days** (threshold-based count): **deliberately left missing**. Imputing zeros would have biased trends downward and made early years appear warmer than they were — a factually misleading result. Missing values were retained to preserve data integrity.

### 2. Exploratory Data Analysis
- Distribution analysis of all variables
- Pearson correlation heatmap with full interpretation (e.g. max/min temp r ≈ 0.98; temperature vs frost r ≈ −0.62 to −0.64)

### 3. Visual Analysis
Annotated time-series and seasonal charts for:
- Monthly maximum & minimum temperature (with hottest/coldest points marked)
- Average sunshine by month and total sunshine per year
- Average rainfall by month and total rainfall per year
- Air frost days by month and per year

---

## Key Findings

| Theme | Finding |
|-------|---------|
| **Seasonality** | All variables show strong, consistent seasonal cycles — warm/sunny summers, cold/frosty winters |
| **Temperature trend** | Gradual long-term warming: higher summer peaks and milder winter lows in recent decades |
| **Coldest / warmest** | Coldest min temp −3.5°C (early 1960s); warmest max temp 22.4°C (late 1990s) |
| **Sunshine** | Peaks in May (~210 hrs); lowest in December (~48 hrs); no clear long-term trend |
| **Rainfall** | Wettest in November (~108 mm); driest in April (~54 mm); no long-term trend |
| **Air frost** | Concentrated in Jan–Feb; highest single year 26 days (1963); fewer frost days in recent decades |

---

## Data-Quality Notes (Intellectual Honesty)

The analysis explicitly flags limitations rather than over-interpreting:
- Apparent stability in recent sunshine totals may partly reflect how missing values were handled, not a true climatic signal.
- Air frost missingness is structural (incomplete early daily observations), so frost trends are interpreted with caution.

This careful, limitation-aware interpretation is a core part of the project.

---

## Repository Structure

```
01_python_climate_analysis/
├── aberporth_climate_analysis.ipynb   # Main analysis notebook
├── data/
│   ├── DataOnly.csv                   # Raw monthly observations
│   └── data_dictionary.md             # Variable definitions & station metadata
├── outputs/                           # Exported charts (optional)
└── README.md
```

---

## How to Run

```bash
# 1. Install dependencies
pip install pandas numpy matplotlib seaborn

# 2. Launch Jupyter
jupyter notebook aberporth_climate_analysis.ipynb

# 3. Run all cells (Cell → Run All)
```

---

## What This Project Demonstrates

- Thoughtful, variable-specific missing-value treatment (knowing when *not* to impute)
- Time-series data preparation with a proper datetime index
- Clear exploratory analysis and correlation interpretation
- Well-annotated, communicative visualisations
- Honest acknowledgement of data limitations — analysis you can defend in an interview

---

## Reference

UK Meteorological seasons used throughout:
**Spring** (Mar–May) · **Summer** (Jun–Aug) · **Autumn** (Sep–Nov) · **Winter** (Dec–Feb)
