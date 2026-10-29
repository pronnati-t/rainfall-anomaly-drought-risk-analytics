
from pathlib import Path

import numpy as np
import pandas as pd

INPUT_FILE = Path("data/processed/gujarat_monsoon_rainfall.csv")
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Illustrative policy assumptions
TRIGGER_RATIO = 0.80
EXHAUSTION_RATIO = 0.50
MAX_PAYOUT_INR = 10_000

df = pd.read_csv(INPUT_FILE).sort_values("year")

# Reference based on the study-period mean
reference_rainfall = df["monsoon_rainfall_mm"].mean()
trigger_mm = TRIGGER_RATIO * reference_rainfall
exhaustion_mm = EXHAUSTION_RATIO * reference_rainfall

if trigger_mm <= exhaustion_mm:
    raise ValueError("Trigger must exceed the maximum-payout threshold.")

# Payout is zero above the trigger, rises linearly below it,
# and is capped at the maximum payout at the exhaustion threshold.
df["trigger_mm"] = trigger_mm
df["exhaustion_mm"] = exhaustion_mm

df["payout_fraction"] = np.clip(
    (trigger_mm - df["monsoon_rainfall_mm"])
    / (trigger_mm - exhaustion_mm),
    0,
    1,
)

df["simulated_payout_inr"] = (
    df["payout_fraction"] * MAX_PAYOUT_INR
).round(2)

df["trigger_activated"] = df["simulated_payout_inr"] > 0

output_file = OUTPUT_DIR / "insurance_backtest.csv"
df.to_csv(output_file, index=False)

trigger_count = int(df["trigger_activated"].sum())
years = len(df)
total_payout = df["simulated_payout_inr"].sum()
average_payout = df["simulated_payout_inr"].mean()

print("PARAMETRIC RAINFALL INSURANCE — HISTORICAL BACKTEST")
print("-" * 55)
print(f"Years analysed: {years}")
print(f"Reference rainfall: {reference_rainfall:.2f} mm")
print(f"Payout trigger: {trigger_mm:.2f} mm")
print(f"Maximum-payout threshold: {exhaustion_mm:.2f} mm")
print(f"Maximum payout per policy: ₹{MAX_PAYOUT_INR:,.0f}")
print(f"Years with a payout: {trigger_count}/{years}")
print(f"Historical trigger frequency: {trigger_count / years:.1%}")
print(f"Average annual payout: ₹{average_payout:,.2f}")
print(f"Total simulated payouts: ₹{total_payout:,.2f}")
print(f"Maximum annual payout: ₹{df['simulated_payout_inr'].max():,.2f}")
print(f"\nSaved results to: {output_file}")

print("\nYear-by-year results:")
print(
    df[
        [
            "year",
            "monsoon_rainfall_mm",
            "payout_fraction",
            "simulated_payout_inr",
        ]
    ].round(2).to_string(index=False)
)
