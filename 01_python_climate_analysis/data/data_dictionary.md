# Data Dictionary — Aberporth Climate Dataset

**Station:** Aberporth
**Location:** 224100E 252100N · Lat 52.139, Lon −4.570 · 133 metres above mean sea level
**Records:** 1,020 monthly observations (1941–2025)

This dataset contains monthly climate observations for the Aberporth weather station. Each record represents aggregated weather measurements for a given month, spanning several decades.

## Data Conventions

- Estimated data is marked with a `*` after the value in the raw source.
- Missing data (more than 2 days missing in a month) is marked by `---`.
- Sunshine data from an automatic Kipp & Zonen sensor is marked with `#`; otherwise sunshine was recorded with a Campbell-Stokes recorder.

## Variables

| Variable | Description | Data Type | Unit |
|----------|-------------|-----------|------|
| `yyyy` (Year) | Calendar year of observation | Integer | year |
| `mm` (Month) | Month of observation (1–12) | Integer | month |
| `Date` | First day of each month, created for time-series analysis | Date | date |
| `tmax_degC` | Average monthly maximum temperature | Float | °C |
| `tmin_degC` | Average monthly minimum temperature | Float | °C |
| `rain_mm` | Total monthly rainfall | Float | mm |
| `sun_hours` | Total monthly sunshine hours | Float | hours |
| `af_days` | Number of days in month with air frost (min temp ≤ 0°C) | Integer | days |

## About the Dataset

The dataset contains a mix of continuous, seasonal, and count-based climate variables. Each attribute was treated according to its statistical properties and data-quality characteristics to ensure reliable and valid analysis.

Attribute definitions and data-quality notes are based on the accompanying Aberporth station data, supplemented by standard UK Met Office climate data conventions. The dataset structure and attribute meanings align with those used in UK Meteorological Office MIDAS monthly climate records.
