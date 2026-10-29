
from pathlib import Path

import numpy as np
import pandas as pd

INPUT_FILE = Path("outputs/dry_spells_vs_insurance_payouts.csv")
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Illustrative contract assumptions, not actuarially calibrated.
TRIGGER_DAYS = 14
EXHAUSTION_DAYS = 30
MAX_PAYOUT_INR = 10_000

df = pd.read_csv(INPUT_FILE).sort_values("year").copy()

if df["year"].duplicated().any():
    raise ValueError("Duplicate years found.")

if df["maximum_consecutive_dry_days"].isna().any():
    raise ValueError("Missing dry-spell observations.")

if TRIGGER_DAYS >= EXHAUSTION_DAYS:
    raise ValueError("Exhaustion days must exceed trigger days.")

# No payout at or below the trigger.
# Full payout at or above the exhaustion threshold.
fraction = (
    (df["maximum_consecutive_dry_days"] - TRIGGER_DAYS)
    / (EXHAUSTION_DAYS - TRIGGER_DAYS)
).clip(lower=0, upper=1)

df["dry_spell_payout_fraction"] = fraction
df["dry_spell_payout_inr"] = (
    fraction * MAX_PAYOUT_INR
).round(2)

df["dry_spell_payout_triggered"] = (
    df["dry_spell_payout_inr"] > 0
)

df["combined_payout_inr"] = (
    df["simulated_payout_inr"] + df["dry_spell_payout_inr"]
).round(2)

output_file = OUTPUT_DIR / "dry_spell_insurance_backtest.csv"
df.to_csv(output_file, index=False)

n = len(df)

summary = pd.DataFrame([{
    "test_years": n,
    "trigger_days": TRIGGER_DAYS,
    "exhaustion_days": EXHAUSTION_DAYS,
    "maximum_payout_inr": MAX_PAYOUT_INR,
    "dry_spell_payout_years": int(
        df["dry_spell_payout_triggered"].sum()
    ),
    "dry_spell_payout_frequency_pct": round(
        100 * df["dry_spell_payout_triggered"].sum() / n, 2
    ),
    "average_dry_spell_payout_inr": round(
        df["dry_spell_payout_inr"].mean(), 2
    ),
    "total_dry_spell_payout_inr": round(
        df["dry_spell_payout_inr"].sum(), 2
    ),
    "maximum_dry_spell_payout_inr": round(
        df["dry_spell_payout_inr"].max(), 2
    ),
    "combined_total_payout_inr": round(
        df["combined_payout_inr"].sum(), 2
    ),
}])

summary_file = OUTPUT_DIR / "dry_spell_insurance_summary.csv"
summary.to_csv(summary_file, index=False)

print("EXPERIMENTAL DRY-SPELL INSURANCE BACKTEST")
print("-" * 48)
print(f"Trigger: more than {TRIGGER_DAYS} consecutive dry days")
print(f"Exhaustion: {EXHAUSTION_DAYS} consecutive dry days")
print(f"Test years: {df['year'].min()}-{df['year'].max()}")
print()
print(df[[
    "year",
    "maximum_consecutive_dry_days",
    "simulated_payout_inr",
    "dry_spell_payout_inr",
    "combined_payout_inr",
]].to_string(index=False))
print()
print(summary.to_string(index=False))
print("\nSaved:")
print(output_file)
print(summary_file)
print(
    "\nThis is an illustrative scenario, not a priced insurance "
    "product. Combined payouts are additive and may overlap."
)
