# Rainfall Risk Analytics & Parametric Insurance Backtesting

A Python-based climate-risk analytics project that analyzes historical rainfall variability and backtests hypothetical rainfall-indexed insurance payouts using daily gridded rainfall data from the India Meteorological Department (IMD).

## Project Objectives

- Analyze June–September monsoon rainfall across a geographic region approximating Gujarat.
- Calculate rainfall anomalies against the 2010–2025 study-period mean.
- Identify rainfall-deficit years using an illustrative threshold.
- Simulate hypothetical parametric insurance payouts based on rainfall triggers.
- Compare payout frequency and historical payout amounts under alternative trigger designs.

## Dataset

- **Source:** India Meteorological Department (IMD), daily gridded rainfall dataset
- **Spatial resolution:** 0.25° × 0.25°
- **Period analyzed:** 2010–2025
- **Variable:** Daily rainfall, in millimetres
- **Season:** June–September

The analysis initially uses a geographic bounding box as an approximation of Gujarat. It is not an exact state-boundary mask, so results should be interpreted as exploratory regional indicators.

## Methodology

### 1. Rainfall analysis

Daily rainfall is averaged across available grid cells within the selected region. June–September values are aggregated for each year, and anomalies are calculated relative to the mean across the 16-year study period.

### 2. Rainfall-deficit screening

Years with monsoon rainfall below 80% of the study-period mean are flagged for exploratory analysis. This is an illustrative threshold, not an official drought classification.

### 3. Parametric insurance simulation

A hypothetical policy uses the following assumptions:

- Reference rainfall: study-period mean
- Payout trigger: selected percentage of reference rainfall
- Maximum-payout threshold: 50% of reference rainfall
- Maximum payout: ₹10,000 per policy
- Payout structure: linear between the trigger and maximum-payout threshold

The payout fraction is calculated as:

`clip((trigger - observed rainfall) / (trigger - exhaustion threshold), 0, 1)`

The simulated payout is the payout fraction multiplied by the maximum payout.

### 4. Trigger sensitivity analysis

The model compares trigger levels of 70%, 75%, 80%, 85%, and 90% of reference rainfall, measuring historical payout frequency, average annual payout, total simulated payouts, and maximum annual payout.

## Preliminary Findings

Using the current regional approximation and illustrative policy assumptions:

- Study-period mean monsoon rainfall: **833.84 mm**
- Years flagged below 80% of the mean: **2012, 2014, 2015, 2016, and 2018**
- Driest monsoon in the study period: **2018**, at 514.20 mm
- Wettest monsoon in the study period: **2024**, at 1,070.23 mm

Under the current payout formula, the 80% trigger design produces payouts in 5 of 16 historical years. The sensitivity analysis shows that higher triggers generally increase historical payout frequency and average payout amounts.

## Visualizations

The `outputs/` directory contains charts for:

- Historical monsoon rainfall
- Rainfall anomalies
- Rainfall-deficit screening
- Average annual payout by trigger design
- Historical payout comparison across trigger designs
- Trigger sensitivity

## Tech Stack

Python, Pandas, NumPy, Matplotlib, xarray, netCDF4, Git, and GitHub.

## Repository Structure

```text
rainfall-risk-analytics/
├── data/
│   ├── raw/          # Original data, excluded from Git
│   └── processed/    # Processed tables, excluded from Git
├── outputs/          # Charts and backtest summaries
├── src/
│   ├── inspect_data.py
│   ├── check_rainfall.py
│   ├── analyze_rainfall.py
│   ├── visualize_results.py
│   ├── backtest_insurance.py
│   ├── trigger_sensitivity.py
│   └── plot_backtest.py
├── requirements.txt
└── README.md
```

## Limitations

- The study covers only 16 years, so estimates of payout frequency are uncertain.
- The geographic bounding box approximates Gujarat and may include grid cells outside the state.
- The policy parameters are illustrative and have not been calibrated against crop losses, claims, or insured values.
- The analysis does not estimate a commercially viable premium or validate insurer profitability.
- Historical rainfall deficits do not necessarily imply agricultural losses or official drought declarations.

## Future Improvements

- Replace the geographic bounding box with a state-boundary mask.
- Evaluate data quality and spatial weighting.
- Analyze dry spells and within-season rainfall distribution.
- Compare trigger designs against observed agricultural impacts, where reliable data are available.
- Extend the historical period and perform additional robustness checks.

## Disclaimer

This project is an educational quantitative risk modelling exercise. The simulated payouts are hypothetical and should not be interpreted as actual insurance claims, official drought assessments, or actuarially validated prices.