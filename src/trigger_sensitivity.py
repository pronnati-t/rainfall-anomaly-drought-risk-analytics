
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

INPUT_FILE = Path("data/processed/gujarat_monsoon_rainfall.csv")
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MAX_PAYOUT_INR = 10_000
EXHAUSTION_RATIO = 0.50
TRIGGER_RATIOS = [0.70, 0.75, 0.80, 0.85, 0.90]

df = pd.read_csv(INPUT_FILE).sort_values("year")
reference = df["monsoon_rainfall_mm"].mean()
rainfall = df["monsoon_rainfall_mm"]
years = len(df)

summary = []
payout_columns = {}

for trigger_ratio in TRIGGER_RATIOS:
    trigger = trigger_ratio * reference
    exhaustion = EXHAUSTION_RATIO * reference

    fraction = (
        (trigger - rainfall) / (trigger - exhaustion)
    ).clip(lower=0, upper=1)

    payouts = fraction * MAX_PAYOUT_INR
    label = f"trigger_{int(trigger_ratio * 100)}pct"
    payout_columns[label] = payouts.round(2)

    summary.append({
        "trigger_ratio": trigger_ratio,
        "trigger_mm": round(trigger, 2),
        "years_with_payout": int((payouts > 0).sum()),
        "trigger_frequency_pct": round((payouts > 0).mean() * 100, 2),
        "average_annual_payout_inr": round(payouts.mean(), 2),
        "total_historical_payout_inr": round(payouts.sum(), 2),
        "maximum_annual_payout_inr": round(payouts.max(), 2),
    })

results = pd.DataFrame(summary)
results.to_csv(OUTPUT_DIR / "trigger_sensitivity.csv", index=False)

yearly = pd.DataFrame({"year": df["year"]})
for label, payouts in payout_columns.items():
    yearly[label] = payouts.values

yearly.to_csv(OUTPUT_DIR / "payout_sensitivity_by_year.csv", index=False)

print("TRIGGER SENSITIVITY ANALYSIS")
print(f"Reference rainfall: {reference:.2f} mm")
print(f"Maximum payout: ₹{MAX_PAYOUT_INR:,}")
print()
print(results.to_string(index=False))

# Plot: how trigger choice changes payout frequency
plt.figure(figsize=(9, 5))
plt.plot(
    results["trigger_ratio"] * 100,
    results["trigger_frequency_pct"],
    marker="o",
)
plt.xlabel("Payout trigger (% of reference rainfall)")
plt.ylabel("Years with payout (%)")
plt.title("Sensitivity of Payout Frequency to Trigger Design")
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "trigger_sensitivity.png", dpi=200)
plt.close()

# Plot: annual payouts for the alternative trigger designs
plt.figure(figsize=(11, 6))
for label in payout_columns:
    plt.plot(yearly["year"], yearly[label], marker="o", label=label)

plt.xlabel("Year")
plt.ylabel("Simulated payout (₹ per policy)")
plt.title("Historical Payouts Under Alternative Trigger Designs")
plt.xticks(yearly["year"], rotation=45)
plt.grid(alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "payout_sensitivity_by_year.png", dpi=200)
plt.close()

print("\nSaved sensitivity tables and charts in outputs/")
