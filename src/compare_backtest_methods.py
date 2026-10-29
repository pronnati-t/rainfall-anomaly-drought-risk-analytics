
from pathlib import Path

import numpy as np
import pandas as pd

INPUT_FILE = Path("data/processed/gujarat_monsoon_rainfall.csv")
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MIN_TRAIN_YEARS = 5
TRIGGER_RATIO = 0.80
EXHAUSTION_RATIO = 0.50
MAX_PAYOUT_INR = 10_000

df = pd.read_csv(INPUT_FILE).sort_values("year").reset_index(drop=True)

records = []

# Fixed-reference contract: benchmark is frozen after the first five years.
initial_train = df.iloc[:MIN_TRAIN_YEARS]
fixed_reference = initial_train["monsoon_rainfall_mm"].mean()
fixed_trigger = TRIGGER_RATIO * fixed_reference
fixed_exhaustion = EXHAUSTION_RATIO * fixed_reference

for i in range(MIN_TRAIN_YEARS, len(df)):
    train = df.iloc[:i]
    test = df.iloc[i]

    rainfall = float(test["monsoon_rainfall_mm"])
    rolling_reference = train["monsoon_rainfall_mm"].mean()

    contracts = [
        (
            "rolling_reference",
            rolling_reference,
        ),
        (
            "fixed_reference",
            fixed_reference,
        ),
    ]

    for method, reference in contracts:
        trigger = TRIGGER_RATIO * reference
        exhaustion = EXHAUSTION_RATIO * reference

        fraction = np.clip(
            (trigger - rainfall) / (trigger - exhaustion),
            0,
            1,
        )
        payout = round(float(fraction) * MAX_PAYOUT_INR, 2)

        records.append({
            "year": int(test["year"]),
            "method": method,
            "training_reference_mm": round(reference, 2),
            "trigger_mm": round(trigger, 2),
            "exhaustion_mm": round(exhaustion, 2),
            "rainfall_mm": round(rainfall, 2),
            "payout_inr": payout,
            "trigger_activated": payout > 0,
        })

results = pd.DataFrame(records)
results.to_csv(OUTPUT_DIR / "backtest_method_comparison_by_year.csv", index=False)

summary = (
    results.groupby("method")
    .agg(
        test_years=("year", "nunique"),
        payout_years=("trigger_activated", "sum"),
        average_annual_payout_inr=("payout_inr", "mean"),
        total_payout_inr=("payout_inr", "sum"),
        maximum_annual_payout_inr=("payout_inr", "max"),
    )
    .reset_index()
)

summary["payout_frequency_pct"] = (
    100 * summary["payout_years"] / summary["test_years"]
)

summary.to_csv(OUTPUT_DIR / "backtest_method_comparison_summary.csv", index=False)

print("BACKTEST METHOD COMPARISON")
print(f"Test period: {df.iloc[MIN_TRAIN_YEARS]['year']}-{df['year'].max()}")
print(f"Fixed reference (2010-2014): {fixed_reference:.2f} mm\n")
print(summary.round(2).to_string(index=False))
print("\nSaved comparison files in outputs/")
