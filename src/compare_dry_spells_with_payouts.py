
from pathlib import Path

import pandas as pd

DRY_FILE = Path("data/processed/gujarat_dry_spell_metrics.csv")
PAYOUT_FILE = Path("outputs/rolling_origin_backtest.csv")
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

dry = pd.read_csv(DRY_FILE)
payouts = pd.read_csv(PAYOUT_FILE)

dry["year"] = pd.to_numeric(dry["year"], errors="raise")
payouts["test_year"] = pd.to_numeric(
    payouts["test_year"], errors="raise"
)

comparison = dry.merge(
    payouts,
    left_on="year",
    right_on="test_year",
    how="inner",
    validate="one_to_one",
)

comparison["payout_triggered"] = (
    comparison["simulated_payout_inr"] > 0
)

columns = [
    "year",
    "monsoon_rainfall_mm",
    "dry_days",
    "maximum_consecutive_dry_days",
    "spells_at_least_7_days",
    "spells_at_least_14_days",
    "training_reference_mm",
    "trigger_mm",
    "simulated_payout_inr",
    "payout_triggered",
]

result = comparison[columns].sort_values("year")

output_file = OUTPUT_DIR / "dry_spells_vs_insurance_payouts.csv"
result.to_csv(output_file, index=False)

print("DRY SPELLS VS INSURANCE PAYOUTS")
print("-" * 50)
print(result.to_string(index=False))

print("\nYears with the longest dry spells:")
print(
    result.nlargest(5, "maximum_consecutive_dry_days")[
        [
            "year",
            "maximum_consecutive_dry_days",
            "monsoon_rainfall_mm",
            "simulated_payout_inr",
        ]
    ].to_string(index=False)
)

print(f"\nSaved comparison to: {output_file}")
print(
    "\nInterpretation: this compares regional dry-spell indicators "
    "with a seasonal-rainfall insurance contract. It does not "
    "measure actual crop losses or establish basis risk."
)
