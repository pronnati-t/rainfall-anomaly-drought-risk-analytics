
from pathlib import Path

import numpy as np
import pandas as pd

INPUT_FILE = Path("data/processed/gujarat_monsoon_rainfall.csv")
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Use at least 5 historical years to calibrate each contract.
MIN_TRAIN_YEARS = 5

# Contract assumptions remain fixed across all folds.
TRIGGER_RATIO = 0.80
EXHAUSTION_RATIO = 0.50
MAX_PAYOUT_INR = 10_000

df = pd.read_csv(INPUT_FILE).sort_values("year").copy()
df["year"] = pd.to_numeric(df["year"], errors="raise")
df["monsoon_rainfall_mm"] = pd.to_numeric(
    df["monsoon_rainfall_mm"], errors="raise"
)

if df["year"].duplicated().any():
    raise ValueError("Duplicate years found.")

if df["monsoon_rainfall_mm"].isna().any():
    raise ValueError("Missing rainfall values found.")

df = df.reset_index(drop=True)

if len(df) <= MIN_TRAIN_YEARS:
    raise ValueError("Not enough years for rolling-origin backtesting.")

records = []

# Each fold trains only on past years and tests on the next year.
for test_index in range(MIN_TRAIN_YEARS, len(df)):
    train = df.iloc[:test_index]
    test = df.iloc[test_index]

    reference = train["monsoon_rainfall_mm"].mean()
    trigger = TRIGGER_RATIO * reference
    exhaustion = EXHAUSTION_RATIO * reference

    if trigger <= exhaustion:
        raise ValueError("Trigger must exceed exhaustion threshold.")

    rainfall = float(test["monsoon_rainfall_mm"])

    payout_fraction = float(
        np.clip(
            (trigger - rainfall) / (trigger - exhaustion),
            0,
            1,
        )
    )

    payout = round(payout_fraction * MAX_PAYOUT_INR, 2)

    records.append({
        "test_year": int(test["year"]),
        "training_start_year": int(train["year"].min()),
        "training_end_year": int(train["year"].max()),
        "training_years": len(train),
        "training_reference_mm": round(reference, 2),
        "trigger_ratio": TRIGGER_RATIO,
        "trigger_mm": round(trigger, 2),
        "exhaustion_mm": round(exhaustion, 2),
        "test_rainfall_mm": round(rainfall, 2),
        "payout_fraction": round(payout_fraction, 6),
        "simulated_payout_inr": payout,
        "trigger_activated": payout > 0,
    })

results = pd.DataFrame(records)

results_file = OUTPUT_DIR / "rolling_origin_backtest.csv"
results.to_csv(results_file, index=False)

n_test = len(results)
n_payout = int(results["trigger_activated"].sum())

summary = pd.DataFrame([{
    "minimum_training_years": MIN_TRAIN_YEARS,
    "first_test_year": int(results["test_year"].min()),
    "last_test_year": int(results["test_year"].max()),
    "test_observations": n_test,
    "payout_years": n_payout,
    "payout_frequency_pct": round(100 * n_payout / n_test, 2),
    "average_annual_payout_inr": round(
        results["simulated_payout_inr"].mean(), 2
    ),
    "total_simulated_payout_inr": round(
        results["simulated_payout_inr"].sum(), 2
    ),
    "maximum_annual_payout_inr": round(
        results["simulated_payout_inr"].max(), 2
    ),
}])

summary_file = OUTPUT_DIR / "rolling_origin_summary.csv"
summary.to_csv(summary_file, index=False)

print("ROLLING-ORIGIN PARAMETRIC INSURANCE BACKTEST")
print("-" * 52)
print(f"Minimum training window: {MIN_TRAIN_YEARS} years")
print(f"Test years: {results['test_year'].min()}-{results['test_year'].max()}")
print(f"Test observations: {n_test}")
print(f"Payout years: {n_payout}/{n_test}")
print(f"Payout frequency: {100 * n_payout / n_test:.2f}%")
print(
    "Average annual payout: "
    f"₹{results['simulated_payout_inr'].mean():,.2f}"
)
print(
    "Total simulated payouts: "
    f"₹{results['simulated_payout_inr'].sum():,.2f}"
)
print(
    "Maximum annual payout: "
    f"₹{results['simulated_payout_inr'].max():,.2f}"
)

print("\nYear-by-year results:")
print(
    results[
        [
            "test_year",
            "training_years",
            "training_reference_mm",
            "trigger_mm",
            "test_rainfall_mm",
            "simulated_payout_inr",
        ]
    ].to_string(index=False)
)

print(f"\nSaved detailed results: {results_file}")
print(f"Saved summary: {summary_file}")
