
from pathlib import Path

import pandas as pd

INPUT_FILE = Path("outputs/rolling_origin_backtest.csv")
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(INPUT_FILE)

# A rainfall deficit is rainfall below 80% of the
# reference calculated using only preceding years.
df["rainfall_deficit"] = (
    df["test_rainfall_mm"] < df["trigger_mm"]
)

df["payout_triggered"] = df["simulated_payout_inr"] > 0

# Compare rainfall deficits with insurance payouts.
df["classification"] = "Neither"
df.loc[
    df["rainfall_deficit"] & df["payout_triggered"],
    "classification",
] = "Deficit and payout"
df.loc[
    df["rainfall_deficit"] & ~df["payout_triggered"],
    "classification",
] = "Deficit without payout"
df.loc[
    ~df["rainfall_deficit"] & df["payout_triggered"],
    "classification",
] = "Payout without deficit"

output_columns = [
    "test_year",
    "training_reference_mm",
    "trigger_mm",
    "test_rainfall_mm",
    "rainfall_deficit",
    "payout_triggered",
    "simulated_payout_inr",
    "classification",
]

results = df[output_columns].copy()

results_file = OUTPUT_DIR / "basis_risk_evaluation.csv"
results.to_csv(results_file, index=False)

print("RAINFALL DEFICIT VS INSURANCE PAYOUT")
print("-" * 45)
print(results.to_string(index=False))

print("\nClassification counts:")
print(results["classification"].value_counts().to_string())

print(f"\nSaved results to: {results_file}")
print(
    "\nNote: This is a rainfall-trigger alignment diagnostic, "
    "not a definitive measure of agricultural basis risk. "
    "Crop-loss observations are not included."
)
