
from pathlib import Path

import numpy as np
import pandas as pd

INPUT_FILE = Path("data/processed/gujarat_monsoon_rainfall.csv")
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Chronological split: calibrate on earlier years, test on later years.
TRAIN_START = 2010
TRAIN_END = 2019
TEST_START = 2020
TEST_END = 2025

# Illustrative policy assumptions
TRIGGER_RATIO = 0.80
EXHAUSTION_RATIO = 0.50
MAX_PAYOUT_INR = 10_000

df = pd.read_csv(INPUT_FILE).sort_values("year").copy()

required_columns = {"year", "monsoon_rainfall_mm"}
missing = required_columns - set(df.columns)
if missing:
    raise ValueError(f"Missing required columns: {sorted(missing)}")

df["year"] = pd.to_numeric(df["year"], errors="raise")
df["monsoon_rainfall_mm"] = pd.to_numeric(
    df["monsoon_rainfall_mm"], errors="raise"
)

if df["year"].duplicated().any():
    raise ValueError("Duplicate years found in rainfall data.")

if df["monsoon_rainfall_mm"].isna().any():
    raise ValueError("Missing rainfall values found.")

train = df[df["year"].between(TRAIN_START, TRAIN_END)].copy()
test = df[df["year"].between(TEST_START, TEST_END)].copy()

if train.empty or test.empty:
    raise ValueError("Training or testing period has no data.")

if train["year"].max() >= test["year"].min():
    raise ValueError("Training years must precede test years.")

# Calibrate the contract using TRAINING data only.
reference_rainfall = train["monsoon_rainfall_mm"].mean()
trigger_mm = TRIGGER_RATIO * reference_rainfall
exhaustion_mm = EXHAUSTION_RATIO * reference_rainfall

if trigger_mm <= exhaustion_mm:
    raise ValueError("Trigger must exceed the exhaustion threshold.")

# Apply the frozen contract to the test period.
test["reference_rainfall_mm"] = reference_rainfall
test["trigger_mm"] = trigger_mm
test["exhaustion_mm"] = exhaustion_mm

test["payout_fraction"] = np.clip(
    (trigger_mm - test["monsoon_rainfall_mm"])
    / (trigger_mm - exhaustion_mm),
    0,
    1,
)

test["simulated_payout_inr"] = (
    test["payout_fraction"] * MAX_PAYOUT_INR
).round(2)

test["trigger_activated"] = test["simulated_payout_inr"] > 0

# Save year-by-year out-of-sample results.
output_file = OUTPUT_DIR / "insurance_out_of_sample.csv"
test.to_csv(output_file, index=False)

# Summarize results for the unseen test years.
test_years = len(test)
trigger_count = int(test["trigger_activated"].sum())
total_payout = test["simulated_payout_inr"].sum()
average_payout = test["simulated_payout_inr"].mean()

summary = pd.DataFrame(
    [
        {
            "train_start": TRAIN_START,
            "train_end": TRAIN_END,
            "test_start": int(test["year"].min()),
            "test_end": int(test["year"].max()),
            "training_reference_rainfall_mm": reference_rainfall,
            "trigger_ratio": TRIGGER_RATIO,
            "trigger_mm": trigger_mm,
            "exhaustion_ratio": EXHAUSTION_RATIO,
            "exhaustion_mm": exhaustion_mm,
            "max_payout_inr": MAX_PAYOUT_INR,
            "test_years": test_years,
            "payout_years": trigger_count,
            "payout_frequency": trigger_count / test_years,
            "average_annual_payout_inr": average_payout,
            "total_payout_inr": total_payout,
            "maximum_annual_payout_inr": test["simulated_payout_inr"].max(),
        }
    ]
)

summary_file = OUTPUT_DIR / "out_of_sample_summary.csv"
summary.to_csv(summary_file, index=False)

print("OUT-OF-SAMPLE PARAMETRIC INSURANCE BACKTEST")
print("-" * 52)
print(f"Training period: {TRAIN_START}-{TRAIN_END}")
print(f"Testing period: {test['year'].min()}-{test['year'].max()}")
print(f"Training reference rainfall: {reference_rainfall:.2f} mm")
print(f"Fixed payout trigger: {trigger_mm:.2f} mm")
print(f"Fixed exhaustion threshold: {exhaustion_mm:.2f} mm")
print(f"Maximum payout: ₹{MAX_PAYOUT_INR:,.0f}")
print(f"Test years with payout: {trigger_count}/{test_years}")
print(f"Test-period payout frequency: {trigger_count / test_years:.1%}")
print(f"Average annual payout: ₹{average_payout:,.2f}")
print(f"Total simulated payouts: ₹{total_payout:,.2f}")
print(
    "Maximum annual payout: "
    f"₹{test['simulated_payout_inr'].max():,.2f}"
)
print(f"\nSaved yearly results to: {output_file}")
print(f"Saved summary to: {summary_file}")

print("\nYear-by-year test results:")
print(
    test[
        [
            "year",
            "monsoon_rainfall_mm",
            "trigger_mm",
            "exhaustion_mm",
            "payout_fraction",
            "simulated_payout_inr",
        ]
    ].round(2).to_string(index=False)
)
