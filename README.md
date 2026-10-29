# Rainfall Risk Analytics & Parametric Insurance Backtesting

A Python-based climate-risk analytics project that analyzes historical monsoon rainfall across Gujarat using daily gridded rainfall data from the India Meteorological Department (IMD). The project builds a hypothetical rainfall-indexed insurance payout model and evaluates alternative trigger designs through historical backtesting and sensitivity analysis.

## Project Objectives

- Analyze June–September monsoon rainfall across Gujarat using a state-boundary mask.
- Quantify annual rainfall anomalies relative to the 2010–2025 study-period mean.
- Screen for rainfall-deficit years using an illustrative threshold.
- Simulate hypothetical parametric insurance payouts under configurable trigger assumptions.
- Compare payout frequency, average annual payout, cumulative simulated payouts, and maximum annual payout across alternative trigger designs.

## Dataset

- **Source:** India Meteorological Department (IMD), daily gridded rainfall dataset
- **Spatial resolution:** 0.25° × 0.25°
- **Period analyzed:** 2010–2025
- **Variable:** Daily rainfall, in millimetres
- **Season:** June–September
- **Geographic boundary:** Gujarat state boundary from the geoBoundaries India ADM1 dataset

The analysis selects rainfall grid-cell centres that fall within the Gujarat polygon. It averages rainfall across the selected cells for each day and aggregates the daily regional mean over June–September.

This is a grid-cell-centre mask, not a fractional-area-weighted calculation. Boundary cells may be only partly inside Gujarat, and the analysis does not yet apply area weighting.

## Methodology

### 1. Rainfall analysis

For each year, daily rainfall is averaged across the selected Gujarat grid cells. Daily regional means are summed over June–September to produce an annual monsoon rainfall indicator.

Anomalies are calculated relative to the mean of the 16-year study period:

`anomaly = annual monsoon rainfall - study-period mean`

Percentage anomalies express this difference as a percentage of the study-period mean.

### 2. Rainfall-deficit screening

Years with monsoon rainfall below 80% of the study-period mean are flagged for exploratory analysis. This is an illustrative screening rule, not an official drought classification.

### 3. Parametric insurance simulation

The hypothetical policy uses the following assumptions:

- **Reference rainfall:** Mean annual monsoon rainfall across the study period
- **Payout trigger:** Selected percentage of reference rainfall
- **Full-payout threshold:** 50% of reference rainfall
- **Maximum payout:** ₹10,000 per policy
- **Payout structure:** Linear between the trigger and full-payout threshold

The payout fraction is:

`clip((trigger - observed rainfall) / (trigger - full-payout threshold), 0, 1)`

The simulated payout is the payout fraction multiplied by the maximum payout.

These parameters are illustrative and are not calibrated to actual insurance contracts, crop losses, premiums, or claims.

### 4. Trigger sensitivity analysis

The model compares trigger levels of 70%, 75%, 80%, 85%, and 90% of reference rainfall while holding the full-payout threshold at 50% and the maximum payout at ₹10,000.

For each design, it reports historical payout frequency, average annual payout, total simulated payouts, and maximum annual payout.

## Results

### Rainfall analysis

Based on the current Gujarat grid-cell-centre mask and 2010–2025 study period:

- **Mean monsoon rainfall:** 827.33 mm
- **Rainfall-deficit years:** 2012, 2014, 2015, 2016, and 2018
- **Driest year:** 2018, with 484.79 mm
- **Wettest year:** 2020, with 1,085.09 mm
- **Grid cells with valid rainfall on the first day:** 258

The rainfall-deficit flags use the illustrative 80%-of-mean threshold and should not be interpreted as official drought declarations.

### Insurance sensitivity analysis

Under the illustrative payout model:

| Trigger | Years with payout | Average annual payout | Total simulated payouts | Maximum annual payout |
|---:|---:|---:|---:|---:|
| 70% | 3/16 (18.75%) | ₹471.55 | ₹7,544.80 | ₹5,701.37 |
| 75% | 5/16 (31.25%) | ₹805.24 | ₹12,883.81 | ₹6,561.09 |
| 80% | 5/16 (31.25%) | ₹1,191.86 | ₹19,069.84 | ₹7,134.24 |
| 85% | 6/16 (37.50%) | ₹1,482.12 | ₹23,713.90 | ₹7,543.64 |
| 90% | 6/16 (37.50%) | ₹1,765.60 | ₹28,249.66 | ₹7,850.68 |

Higher triggers generally increase historical payout frequency and simulated payouts. These are historical model outputs, not forecasts or measures of insurer profitability.

## Visualizations

The `outputs/` directory contains visualizations of:

- Historical monsoon rainfall
- Rainfall anomalies
- Rainfall-deficit screening
- Average annual payout by trigger design
- Historical payout comparison across trigger designs
- Trigger sensitivity

## Tech Stack

Python, Pandas, NumPy, Matplotlib, xarray, netCDF4, GeoPandas, Shapely, PyProj, Git, and GitHub.

## Repository Structure

```text
rainfall-risk-analytics/
├── data/
│   ├── boundaries/   # Gujarat state-boundary dataset
│   ├── raw/          # Original IMD files; excluded from Git
│   └── processed/    # Derived tables; excluded from Git
├── outputs/          # Charts and backtest summaries
├── src/
│   ├── inspect_data.py
│   ├── check_rainfall.py
│   ├── analyze_rainfall.py
│   ├── test_gujarat_boundary.py
│   ├── visualize_results.py
│   ├── backtest_insurance.py
│   ├── trigger_sensitivity.py
│   └── plot_backtest.py
├── requirements.txt
└── README.md
```

## Limitations

- The analysis covers only 16 years, so historical payout frequencies are uncertain.
- Grid-cell centres are used to define the geographic mask; partial cell coverage and area weighting are not handled.
- The reference rainfall and trigger assumptions are evaluated on the same study period, so the results are exploratory rather than an out-of-sample assessment.
- The policy parameters are not calibrated against crop losses, claims, insured values, or actual contract terms.
- Rainfall deficits do not necessarily correspond to agricultural losses or official drought classifications.
- The analysis does not estimate a commercially viable premium or validate insurer profitability.

## Future Improvements

- Add area-weighted rainfall aggregation and quantify sensitivity to the spatial mask.
- Compare alternative reference periods and evaluate trigger designs on held-out years.
- Analyze dry spells and within-season rainfall distribution.
- Compare rainfall triggers against observed agricultural impacts and quantify basis risk where reliable data are available.
- Extend the historical period where consistent data are available.
- Add automated data-quality checks and reproducible evaluation tests.

## Disclaimer

This project is an educational quantitative risk-modelling exercise. Simulated payouts are hypothetical and must not be interpreted as actual insurance claims, official drought assessments, actuarially validated prices, or evidence of commercial profitability.

## Out-of-Sample Validation

To evaluate contract behaviour on unseen rainfall observations, the project implements chronological out-of-sample testing and rolling-origin backtesting.

### Validation design

- **Chronological holdout:** Calibrates the rainfall reference on 2010–2019 and evaluates the contract on 2020–2025.
- **Trigger sensitivity:** Compares multiple trigger ratios while keeping the training-period reference and exhaustion threshold fixed.
- **Rolling-origin backtest:** Uses at least five preceding years to calibrate the reference for each subsequent test year, evaluating 2015–2025.
- **Method comparison:** Compares a fixed reference calibrated on 2010–2014 with a rolling reference recalculated using only prior years, evaluated on the same 2015–2025 test period.

### Results

| Metric | Fixed reference | Rolling reference |
|---|---:|---:|
| Test years | 11 | 11 |
| Years with payout | 3 | 3 |
| Payout frequency | 27.27% | 27.27% |
| Average annual payout | ₹1,317.69 | ₹1,066.24 |
| Total simulated payouts | ₹14,494.56 | ₹11,728.64 |
| Maximum annual payout | ₹7,504.75 | ₹5,839.45 |

The rolling-origin backtest using an 80% trigger and 50% exhaustion threshold produced payouts in 3 of 11 test years, with an average simulated payout of ₹1,066.24 per year.

The fixed-reference method generated approximately 23.6% more total simulated payouts than the rolling-reference method over the same test period. This reflects differences in contract thresholds, not evidence that either method is more profitable or provides better protection.

### Limitations

- The analysis contains only 16 annual rainfall observations, with 11 observations in the rolling-origin evaluation.
- Simulated payouts are illustrative and are not actual insurance claims, premiums, or actuarial pricing estimates.
- Crop-loss data are not incorporated, so the analysis does not measure basis risk or establish whether payouts correspond to agricultural losses.
- The results do not establish a long-term climate trend or reliable future payout probabilities.
- The fixed and rolling approaches represent different benchmark designs and should be evaluated against crop losses, affordability, and insurer costs before making product recommendations.