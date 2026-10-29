# Rainfall Risk Analytics & Parametric Insurance Backtesting

A Python-based climate-risk analytics project that studies historical monsoon rainfall across Gujarat using daily gridded rainfall data from the India Meteorological Department (IMD). The project analyzes rainfall anomalies, identifies rainfall-deficit years, simulates hypothetical parametric insurance payouts, and evaluates alternative contract designs using historical backtesting, out-of-sample validation, rolling-origin evaluation, and dry-spell analysis.

The goal is to explore how rainfall-based indices can be used to model weather risk and how different trigger designs affect simulated insurance payouts.

## Project Objectives

- Analyze June–September monsoon rainfall across Gujarat using a state-boundary mask.
- Quantify annual rainfall anomalies relative to the 2010–2025 study-period mean.
- Identify rainfall-deficit years using an illustrative threshold.
- Simulate hypothetical parametric insurance payouts under configurable trigger assumptions.
- Compare payout frequency, average annual payout, cumulative simulated payouts, and maximum annual payout across alternative trigger designs.
- Evaluate insurance contract behaviour using chronological out-of-sample testing and rolling-origin backtesting.
- Examine the sensitivity of simulated payouts to different rainfall trigger thresholds.
- Analyze within-season rainfall distribution and consecutive dry spells.
- Compare seasonal-rainfall and dry-spell insurance payout mechanisms.

## Dataset

- **Source:** India Meteorological Department (IMD), daily gridded rainfall dataset.
- **Spatial resolution:** 0.25° × 0.25°.
- **Period analyzed:** 2010–2025.
- **Variable:** Daily rainfall, in millimetres.
- **Season:** June–September.
- **Geographic boundary:** Gujarat state boundary from the geoBoundaries India ADM1 dataset.

The analysis selects rainfall grid-cell centres located within the Gujarat polygon. Rainfall is averaged across the selected grid cells for each day and aggregated over the June–September monsoon season.

The geographic mask uses grid-cell centres rather than fractional-area weighting. Boundary cells may be only partially inside Gujarat, and the analysis does not currently apply area weighting.

The original IMD NetCDF files are stored locally under `data/raw/` and excluded from Git. Processed datasets are also excluded from Git to avoid committing large generated files.

## Methodology

### 1. Rainfall Analysis

Daily rainfall is averaged across the selected Gujarat grid cells. Daily regional means are summed over June–September to produce an annual monsoon rainfall indicator.

Anomalies are calculated relative to the mean annual monsoon rainfall across the 16-year study period:

`anomaly = annual monsoon rainfall - study-period mean`

Percentage anomalies express this difference as a percentage of the study-period mean.

### 2. Rainfall-Deficit Screening

Years with monsoon rainfall below 80% of the study-period mean are flagged for exploratory analysis.

This is an illustrative screening rule, not an official drought classification.

### 3. Parametric Insurance Simulation

The hypothetical seasonal-rainfall insurance model uses the following assumptions:

- **Reference rainfall:** Mean annual monsoon rainfall across the study period, or a reference calculated from prior years in the rolling-origin evaluation.
- **Payout trigger:** A selected percentage of reference rainfall.
- **Full-payout threshold:** 50% of the applicable reference rainfall.
- **Maximum payout:** ₹10,000 per hypothetical policy.
- **Payout structure:** Linear between the trigger and full-payout threshold.

The payout fraction is calculated as:

`clip((trigger - observed rainfall) / (trigger - full-payout threshold), 0, 1)`

The simulated payout equals the payout fraction multiplied by the maximum payout.

These parameters are illustrative and are not calibrated to actual insurance contracts, crop losses, premiums, insured values, or claims.

### 4. Trigger Sensitivity Analysis

The initial sensitivity analysis compares trigger levels of 70%, 75%, 80%, 85%, and 90% of reference rainfall while holding the full-payout threshold at 50% and the maximum payout at ₹10,000.

For each contract design, the analysis reports payout frequency, average annual payout, total simulated payouts, and maximum annual payout.

A separate rolling-origin sensitivity analysis evaluates trigger ratios from 70% to 100%, using only preceding years to calculate the reference rainfall for each test year.

### 5. Out-of-Sample Validation

Two backtesting approaches are used to examine how the hypothetical contract behaves when evaluated on rainfall observations not used to calculate its reference.

**Chronological holdout**

- Training period: 2010–2019.
- Test period: 2020–2025.
- The rainfall reference is calculated using training-period observations and held fixed during testing.

**Rolling-origin backtesting**

- Evaluation period: 2015–2025.
- At least five preceding years are used to calculate the reference for each test year.
- The reference is recalculated as additional historical observations become available.
- Each test year's reference uses only observations from preceding years.

The rolling-origin approach better represents a setting in which a contract benchmark is updated using historical information available before each season.

### 6. Fixed-Reference Versus Rolling-Reference Comparison

The project compares two approaches over the same 2015–2025 evaluation period:

- **Fixed reference:** A reference calibrated using 2010–2014 and held constant throughout the test period.
- **Rolling reference:** A reference recalculated from preceding years for each test year.

This comparison illustrates how the choice of reference-calibration method affects trigger thresholds and simulated payouts.

### 7. Dry-Spell Analysis

The project extends seasonal rainfall analysis by examining the distribution of rainfall within each June–September monsoon season.

A **dry day** is defined for this experiment as a day when the daily Gujarat spatial-average rainfall is below 2.5 mm.

For each year, the analysis calculates:

- Total number of dry days during the monsoon season.
- Maximum number of consecutive dry days.
- Number of dry spells lasting at least 5 days.
- Number of dry spells lasting at least 7 days.
- Number of dry spells lasting at least 10 days.
- Number of dry spells lasting at least 14 days.

The 2.5 mm threshold is an analytical choice for this experiment, not an official drought classification.

Dry-spell metrics are compared with seasonal-rainfall insurance payouts to investigate whether within-season rainfall distribution provides a different risk signal from total seasonal rainfall.

### 8. Experimental Dry-Spell Insurance Contract

A separate illustrative contract uses the maximum consecutive dry-spell duration:

- **Trigger:** 14 consecutive dry days.
- **Exhaustion threshold:** 30 consecutive dry days.
- **Maximum payout:** ₹10,000.
- **Payout structure:** Linear between the trigger and exhaustion thresholds.

The payout fraction is calculated as:

`clip((maximum dry-spell duration - 14) / (30 - 14), 0, 1)`

The simulated payout equals the resulting fraction multiplied by ₹10,000.

Under this implementation, a maximum dry spell of exactly 14 days produces no positive payout. The payout increases for longer spells and reaches the maximum at 30 days.

The dry-spell contract is an experimental comparison, not a calibrated or commercially priced insurance product.

## Results

### 1. Rainfall Analysis

Based on the Gujarat grid-cell-centre mask and the 2010–2025 study period:

| Metric | Result |
|---|---:|
| Mean monsoon rainfall | 827.33 mm |
| Driest year | 2018 |
| Rainfall in the driest year | 484.79 mm |
| Wettest year | 2020 |
| Rainfall in the wettest year | 1,085.09 mm |
| Rainfall-deficit years | 2012, 2014, 2015, 2016, 2018 |
| Grid cells with valid rainfall on the first day | 258 |

Rainfall-deficit years are identified using the illustrative threshold of 80% of the study-period mean. They should not be interpreted as official drought declarations.

### 2. Initial Insurance Sensitivity Analysis

Under the illustrative seasonal-rainfall payout model:

| Trigger | Years with payout | Average annual payout | Total simulated payouts | Maximum annual payout |
|---:|---:|---:|---:|---:|
| 70% | 3/16 (18.75%) | ₹471.55 | ₹7,544.80 | ₹5,701.37 |
| 75% | 5/16 (31.25%) | ₹805.24 | ₹12,883.81 | ₹6,561.09 |
| 80% | 5/16 (31.25%) | ₹1,191.86 | ₹19,069.84 | ₹7,134.24 |
| 85% | 6/16 (37.50%) | ₹1,482.12 | ₹23,713.90 | ₹7,543.64 |
| 90% | 6/16 (37.50%) | ₹1,765.60 | ₹28,249.66 | ₹7,850.68 |

Higher triggers generally increase historical payout frequency and simulated payouts. These are historical model outputs, not forecasts or measures of insurer profitability.

### 3. Fixed-Reference Versus Rolling-Reference Backtest

Both approaches were evaluated over the same 2015–2025 test period.

| Metric | Fixed reference | Rolling reference |
|---|---:|---:|
| Test years | 11 | 11 |
| Years with payout | 3 | 3 |
| Payout frequency | 27.27% | 27.27% |
| Average annual payout | ₹1,317.69 | ₹1,066.24 |
| Total simulated payouts | ₹14,494.56 | ₹11,728.64 |
| Maximum annual payout | ₹7,504.75 | ₹5,839.45 |

The rolling-origin backtest using an 80% trigger and a 50% exhaustion threshold produced payouts in 3 of 11 test years, with an average simulated payout of ₹1,066.24 per year.

The fixed-reference method generated approximately 23.6% more total simulated payouts than the rolling-reference method over the same test period. This reflects differences in contract thresholds, not evidence that either method is more profitable or provides better protection.

### 4. Rolling-Origin Trigger Sensitivity

Seven trigger ratios were evaluated using rolling-origin backtesting. The exhaustion threshold remained fixed at 50% of reference rainfall, and the maximum illustrative payout was ₹10,000.

| Trigger ratio | Payout years | Payout frequency | Average annual payout | Total simulated payouts |
|---:|---:|---:|---:|---:|
| 70% | 1/11 | 9.09% | ₹341.74 | ₹3,759.18 |
| 75% | 3/11 | 27.27% | ₹734.03 | ₹8,074.37 |
| 80% | 3/11 | 27.27% | ₹1,066.24 | ₹11,728.64 |
| 85% | 3/11 | 27.27% | ₹1,303.53 | ₹14,338.84 |
| 90% | 4/11 | 36.36% | ₹1,542.60 | ₹16,968.61 |
| 95% | 4/11 | 36.36% | ₹1,775.24 | ₹19,527.66 |
| 100% | 4/11 | 36.36% | ₹1,961.35 | ₹21,574.89 |

Increasing the trigger ratio increases simulated payouts and can increase payout frequency. Between 80% and 85%, the number of payout years remains three, but the average annual payout rises. At 90%, four of the eleven test years trigger payouts.

These results illustrate the trade-off between payout frequency and simulated payout amounts. They do not establish an optimal insurance contract because premiums, insurer expenses, and actual crop-loss observations are not included.

### 5. Dry-Spell Findings

The dry-spell analysis reveals patterns that seasonal rainfall totals alone can miss.

- **2015:** 89 dry days and a maximum consecutive dry spell of 25 days.
- **2018:** 484.79 mm of seasonal rainfall and a maximum dry spell of 23 days.
- **2023:** The longest maximum consecutive dry spell in the study period, at 36 days, despite seasonal rainfall of 842.35 mm.

These results demonstrate that total seasonal rainfall and the distribution of rainfall within the season can provide different signals.

A long dry spell does not by itself prove that crop damage occurred. Soil moisture, irrigation, crop type, planting dates, and other conditions can affect agricultural outcomes.

### 6. Dry-Spell Insurance Backtest

The experimental dry-spell contract was evaluated over the 2015–2025 rolling-origin test period.

| Metric | Result |
|---|---:|
| Test years | 11 |
| Years with a dry-spell payout | 5 |
| Dry-spell payout frequency | 45.45% |
| Average annual dry-spell payout | ₹2,670.45 |
| Total dry-spell payouts | ₹29,375.00 |
| Maximum annual dry-spell payout | ₹10,000.00 |
| Combined simulated payouts across both contracts | ₹41,103.64 |

For example, in 2023, the maximum dry spell was 36 days. The experimental dry-spell contract generated a simulated payout of ₹10,000, while the seasonal-rainfall contract generated no payout for that year.

This illustrates how a within-season dry-spell index can trigger in circumstances where a seasonal-total index does not.

The combined total of ₹41,103.64 adds payouts from the two hypothetical contracts. It is not a measure of insured agricultural losses, insurance value, or profitability. Overlapping payouts may reflect the same underlying weather event.

## Visualizations

The `outputs/` directory contains charts and analysis outputs covering:

- Historical Gujarat monsoon rainfall.
- Rainfall anomalies.
- Rainfall-deficit screening.
- Average annual payout by trigger design.
- Historical payout comparison across trigger designs.
- Rolling-origin trigger sensitivity.
- Maximum consecutive dry spell by year.
- Dry days versus seasonal rainfall.
- Dry-spell frequency by year.

Important generated figures include:

- `outputs/maximum_dry_spell_by_year.png`
- `outputs/dry_days_vs_seasonal_rainfall.png`
- `outputs/dry_spell_frequency_by_year.png`
- `outputs/sensitivity_rolling_origin_frequency.png`
- `outputs/sensitivity_rolling_origin_average_payout.png`

The outputs directory also contains CSV files with annual results, summary metrics, sensitivity analyses, and comparisons between rainfall indices and simulated insurance payouts.

## Tech Stack

- **Language:** Python
- **Data processing:** Pandas, NumPy
- **Scientific data:** xarray, netCDF4
- **Geospatial analysis:** GeoPandas, Shapely, PyProj
- **Visualization:** Matplotlib
- **Version control:** Git and GitHub

## Repository Structure

```text
rainfall-risk-analytics/
├── data/
│   ├── boundaries/
│   │   └── india_states.geojson
│   ├── raw/                         # Original IMD NetCDF files; excluded from Git
│   └── processed/                   # Derived rainfall and dry-spell data; excluded from Git
├── outputs/
│   ├── maximum_dry_spell_by_year.png
│   ├── dry_days_vs_seasonal_rainfall.png
│   ├── dry_spell_frequency_by_year.png
│   ├── dry_spell_insurance_backtest.csv
│   ├── dry_spell_insurance_summary.csv
│   ├── dry_spells_vs_insurance_payouts.csv
│   ├── rolling_origin_backtest.csv
│   ├── rolling_origin_summary.csv
│   ├── sensitivity_rolling_origin_by_year.csv
│   ├── sensitivity_rolling_origin_summary.csv
│   └── ...                          # Other generated charts and tables
├── src/
│   ├── inspect_data.py
│   ├── check_rainfall.py
│   ├── analyze_rainfall.py
│   ├── test_gujarat_boundary.py
│   ├── visualize_results.py
│   ├── plot_backtest.py
│   ├── backtest_insurance.py
│   ├── trigger_sensitivity.py
│   ├── backtest_out_of_sample.py
│   ├── sensitivity_out_of_sample.py
│   ├── sensitivity_extended_out_of_sample.py
│   ├── backtest_rolling_origin.py
│   ├── compare_backtest_methods.py
│   ├── sensitivity_rolling_origin.py
│   ├── evaluate_basis_risk.py
│   ├── analyze_dry_spells.py
│   ├── visualize_dry_spells.py
│   ├── compare_dry_spells_with_payouts.py
│   └── backtest_dry_spell_insurance.py
├── requirements.txt
├── .gitignore
└── README.md
```

The structure above documents the main scripts and representative outputs. Exact file availability may vary as the project evolves. Raw rainfall data, processed datasets, virtual environments, and local backup scripts are not intended to be committed to Git.

## Reproducibility

Create and activate a virtual environment, install the dependencies, and place the required IMD rainfall NetCDF files in `data/raw/`. Ensure that the Gujarat boundary file is available under `data/boundaries/`.

Example setup on macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run the analyses from the repository root so the scripts can resolve their relative file paths.

Examples:

```bash
python src/analyze_rainfall.py
python src/visualize_results.py
python src/backtest_rolling_origin.py
python src/sensitivity_rolling_origin.py
python src/analyze_dry_spells.py
python src/visualize_dry_spells.py
python src/compare_dry_spells_with_payouts.py
python src/backtest_dry_spell_insurance.py
```

Some scripts depend on outputs generated by earlier steps. Run the relevant upstream analyses first if their expected CSV files are missing.

The rolling-origin sensitivity script writes annual results to `outputs/sensitivity_rolling_origin_by_year.csv` and summary metrics to `outputs/sensitivity_rolling_origin_summary.csv`.

The dry-spell analysis generates processed metrics under `data/processed/`, while its visualizations and insurance backtest tables are written to `outputs/`.

## Limitations

- The study covers only 16 annual monsoon observations, with 11 years in the rolling-origin evaluation. Historical payout frequencies are therefore uncertain.
- The geographic mask uses grid-cell centres. Partial cell coverage and area weighting are not handled.
- The study-period mean used in the initial analysis includes all years in the study period. Those in-sample results are exploratory rather than out-of-sample estimates.
- Rolling-origin reference calculations use only preceding years, but the short evaluation period still limits the reliability of conclusions.
- The rainfall-deficit threshold, dry-day threshold, and insurance contract parameters are illustrative.
- Rainfall deficits and dry spells are not official drought classifications or direct measurements of agricultural damage.
- Crop-yield, crop-loss, soil-moisture, irrigation, and insured-value observations are not incorporated.
- The project does not establish whether simulated payouts align with actual agricultural losses.
- The project does not estimate commercially viable premiums or validate insurer profitability.
- Adding payouts from the two experimental contracts can count overlapping weather risks more than once.
- The results do not establish a long-term climate trend or reliable future payout probabilities.

## Future Improvements

- Add area-weighted rainfall aggregation and quantify sensitivity to the spatial mask.
- Compare alternative reference periods and assess how reference choices affect payouts.
- Extend the historical period where consistent data are available.
- Add automated data-quality checks and reproducible evaluation tests.
- Validate rainfall-index designs against reliable agricultural impact data if suitable data become available.
- Explore alternative dry-day thresholds and contract structures, with careful separation of calibration and evaluation periods.
- Improve the visualization and reporting workflow so the main findings can be reproduced consistently.

## Disclaimer

This project is an educational quantitative risk-modelling exercise. All simulated payouts are hypothetical and must not be interpreted as actual insurance claims, official drought assessments, actuarially validated prices, evidence of crop losses, or proof of commercial profitability.

The project illustrates the behaviour of rainfall-indexed contract designs under historical rainfall observations. Real-world insurance design would require agricultural loss data, contract calibration, premium modelling, assessment of basis risk, and appropriate actuarial and regulatory review.
