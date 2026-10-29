
from pathlib import Path

import numpy as np
import pandas as pd

INPUT_FILE = Path("data/processed/gujarat_monsoon_rainfall.csv")
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MIN_TRAIN_YEARS = 5
MAX_PAYOUT_INR = 10_000
EXHAUSTION_RATIO = 0.50
TRIGGER_RATIOS = [0.70, 0.75, 0.80, 0.85, 0.90, 0.95, 1.00]

df = pd.read_csv(INPUT_FILE).sort_values("year").copy()
df["year"] = pd.to_numeric(df["year"], errors="raise")
df["monsoon_rainfall_mm"] = pd.to_numeric(
    df["monsoon_rainfall_mm"], errors="raise"
)

if df["year"].duplicated().any():
    raise ValueError("Duplicate years found.")

if df["monsoon_rainfall_mm"].isna().any():
    raise ValueError("Missing rainfall values found.")

if len(df) <= MIN_TRAIN_YEARS:
    raise ValueError("Not enough observations for rolling-origin testing.")

records = []

for test_index in range(MIN_TRAIN_YEARS, len(df)):
    train = df.iloc[:test_index]
    test = df.iloc[test_index]

    reference = train["monsoon_rainfall_mm"].mean()
    exhaustion = EXHAUSTION_RATIO * reference
    rainfall = float(test["monsoon_rainfall_mm"])

    for ratio in TRIGGER_RATIOS:
        trigger = ratio * reference

        if trigger <= exhaustion:
            raise ValueError("Trigger must exceed exhaustion threshold.")

        fraction = float(
            np.clip(
                (trigger - rainfall) / (trigger - exhaustion),
                0,
                1,
            )
        )

        records.append({
            "test_year": int(test["year"]),
            "training_years": len(train),
            "training_reference_mm": round(reference, 2),
            "trigger_ratio_pct": round(ratio * 100, 2),
            "trigger_mm": round(trigger, 2),
            "exhaustion_mm": round(exhaustion, 2),
            "rainfall_mm": round(rainfall, 2),
            "payout_fraction": round(fraction, 6),
            "simulated_payout_inr": round(
                fraction * MAX_PAYOUT_INR, 2
            ),
        })

details = pd.DataFrame(records)
details["payout_triggered"] = details["simulated_payout_inr"] > 0

summary = (
    details.groupby("trigger_ratio_pct")
    .agg(
        test_observations=("test_year", "count"),
        payout_years=("payout_triggered", "sum"),
        average_annual_payout_inr=("simulated_payout_inr", "mean"),
        total_simulated_payout_inr=("simulated_payout_inr", "sum"),
        maximum_annual_payout_inr=("simulated_payout_inr", "max"),
    )
    .reset_index()
)

summary["payout_frequency_pct"] = (
    100 * summary["payout_years"] / summary["test_observations"]
).round(2)

for column in [
    "average_annual_payout_inr",
    "total_simulated_payout_inr",
    "maximum_annual_payout_inr",
]:
    summary[column] = summary[column].round(2)

details.to_csv(OUTPUT_DIR / "sensitivity_rolling_origin_by_year.csv", index=False)
summary.to_csv(OUTPUT_DIR / "sensitivity_rolling_origin_summary.csv", index=False)

print("ROLLING-ORIGIN TRIGGER SENSITIVITY")
print(f"Minimum training window: {MIN_TRAIN_YEARS} years")
print(f"Test period: {details['test_year'].min()}-{details['test_year'].max()}")
print()
print(summary.to_string(index=False))
print("\nSaved results in outputs/")
