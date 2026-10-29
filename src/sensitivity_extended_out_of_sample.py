
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

INPUT_FILE = Path("data/processed/gujarat_monsoon_rainfall.csv")
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TRAIN_START, TRAIN_END = 2010, 2019
TEST_START, TEST_END = 2020, 2025

MAX_PAYOUT_INR = 10_000
EXHAUSTION_RATIO = 0.50
TRIGGER_RATIOS = [
    0.90, 0.95, 1.00, 1.05, 1.10, 1.15, 1.20
]

df = pd.read_csv(INPUT_FILE).sort_values("year")
train = df[df["year"].between(TRAIN_START, TRAIN_END)]
test = df[df["year"].between(TEST_START, TEST_END)].copy()

if train.empty or test.empty:
    raise ValueError("Training or testing period has no data.")

reference = train["monsoon_rainfall_mm"].mean()
exhaustion = EXHAUSTION_RATIO * reference
rainfall = test["monsoon_rainfall_mm"]

summary = []
yearly = pd.DataFrame({"year": test["year"].values})

for ratio in TRIGGER_RATIOS:
    trigger = ratio * reference

    if trigger <= exhaustion:
        raise ValueError("Trigger must exceed exhaustion threshold.")

    fraction = (
        (trigger - rainfall) / (trigger - exhaustion)
    ).clip(lower=0, upper=1)

    payout = (fraction * MAX_PAYOUT_INR).round(2)
    label = f"trigger_{int(ratio * 100)}pct"
    yearly[label] = payout.values

    n_triggered = int((payout > 0).sum())

    summary.append({
        "trigger_ratio_pct": ratio * 100,
        "trigger_mm": round(trigger, 2),
        "exhaustion_mm": round(exhaustion, 2),
        "test_years": len(test),
        "years_with_payout": n_triggered,
        "payout_frequency_pct": round(
            100 * n_triggered / len(test), 2
        ),
        "average_annual_payout_inr": round(payout.mean(), 2),
        "total_test_payout_inr": round(payout.sum(), 2),
        "maximum_annual_payout_inr": round(payout.max(), 2),
    })

results = pd.DataFrame(summary)

results.to_csv(
    OUTPUT_DIR / "sensitivity_extended_out_of_sample.csv",
    index=False,
)
yearly.to_csv(
    OUTPUT_DIR / "payouts_extended_out_of_sample_by_year.csv",
    index=False,
)

plt.figure(figsize=(9, 5))
plt.plot(
    results["trigger_ratio_pct"],
    results["payout_frequency_pct"],
    marker="o",
)
plt.xlabel("Trigger (% of training reference)")
plt.ylabel("Test years with payout (%)")
plt.title("Out-of-Sample Trigger Frequency")
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(
    OUTPUT_DIR / "sensitivity_extended_frequency.png",
    dpi=200,
)
plt.close()

plt.figure(figsize=(9, 5))
plt.plot(
    results["trigger_ratio_pct"],
    results["average_annual_payout_inr"],
    marker="o",
)
plt.xlabel("Trigger (% of training reference)")
plt.ylabel("Average annual payout (₹)")
plt.title("Out-of-Sample Average Payout by Trigger")
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(
    OUTPUT_DIR / "sensitivity_extended_average_payout.png",
    dpi=200,
)
plt.close()

print("EXTENDED OUT-OF-SAMPLE SENSITIVITY")
print(f"Training reference: {reference:.2f} mm")
print(f"Fixed exhaustion threshold: {exhaustion:.2f} mm")
print(f"Test period: {int(test.year.min())}-{int(test.year.max())}")
print()
print(results.to_string(index=False))
print("\nSaved results and charts in outputs/")
