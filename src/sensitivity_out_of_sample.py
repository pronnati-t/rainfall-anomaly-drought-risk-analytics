
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
TRIGGER_RATIOS = [0.70, 0.75, 0.80, 0.85, 0.90]

df = pd.read_csv(INPUT_FILE).sort_values("year")

train = df[df["year"].between(TRAIN_START, TRAIN_END)].copy()
test = df[df["year"].between(TEST_START, TEST_END)].copy()

if train.empty or test.empty:
    raise ValueError("Training or testing period has no data.")

# Calculate the benchmark from training years ONLY.
reference = train["monsoon_rainfall_mm"].mean()
rainfall = test["monsoon_rainfall_mm"]
years = len(test)

summary = []
payout_columns = {}
yearly = pd.DataFrame({"year": test["year"].values})

for trigger_ratio in TRIGGER_RATIOS:
    trigger = trigger_ratio * reference
    exhaustion = EXHAUSTION_RATIO * reference

    if trigger <= exhaustion:
        raise ValueError("Trigger must exceed the exhaustion threshold.")

    fraction = (
        (trigger - rainfall) / (trigger - exhaustion)
    ).clip(lower=0, upper=1)

    payouts = (fraction * MAX_PAYOUT_INR).round(2)
    label = f"trigger_{int(trigger_ratio * 100)}pct"
    payout_columns[label] = payouts.values
    yearly[label] = payouts.values

    payout_years = int((payouts > 0).sum())

    summary.append({
        "trigger_ratio": trigger_ratio,
        "training_reference_mm": round(reference, 2),
        "trigger_mm": round(trigger, 2),
        "exhaustion_mm": round(exhaustion, 2),
        "test_years": years,
        "test_years_with_payout": payout_years,
        "test_trigger_frequency_pct": round(
            payout_years / years * 100, 2
        ),
        "average_annual_payout_inr": round(payouts.mean(), 2),
        "total_test_payout_inr": round(payouts.sum(), 2),
        "maximum_annual_payout_inr": round(payouts.max(), 2),
    })

results = pd.DataFrame(summary)

summary_file = OUTPUT_DIR / "sensitivity_out_of_sample.csv"
yearly_file = OUTPUT_DIR / "payout_sensitivity_out_of_sample_by_year.csv"

results.to_csv(summary_file, index=False)
yearly.to_csv(yearly_file, index=False)

# Chart 1: test-period payout frequency by trigger.
plt.figure(figsize=(9, 5))
plt.plot(
    results["trigger_ratio"] * 100,
    results["test_trigger_frequency_pct"],
    marker="o",
)
plt.xlabel("Trigger (% of training-period reference)")
plt.ylabel("Test years with payout (%)")
plt.title("Out-of-Sample Payout Frequency by Trigger")
plt.xticks([70, 75, 80, 85, 90])
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(
    OUTPUT_DIR / "sensitivity_out_of_sample_frequency.png",
    dpi=200,
)
plt.close()

# Chart 2: test-period payouts by year.
plt.figure(figsize=(11, 6))
for label in payout_columns:
    plt.plot(yearly["year"], yearly[label], marker="o", label=label)

plt.xlabel("Test year")
plt.ylabel("Simulated payout (₹ per policy)")
plt.title("Out-of-Sample Payouts Under Alternative Triggers")
plt.xticks(yearly["year"], rotation=45)
plt.grid(alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig(
    OUTPUT_DIR / "sensitivity_out_of_sample_payouts.png",
    dpi=200,
)
plt.close()

print("OUT-OF-SAMPLE TRIGGER SENSITIVITY")
print("-" * 45)
print(f"Training years: {TRAIN_START}-{TRAIN_END}")
print(f"Test years: {int(test['year'].min())}-{int(test['year'].max())}")
print(f"Training reference rainfall: {reference:.2f} mm")
print(f"Exhaustion ratio: {EXHAUSTION_RATIO:.0%}")
print(f"Maximum payout: ₹{MAX_PAYOUT_INR:,.0f}\n")
print(results.to_string(index=False))

print("\nSaved files:")
print(summary_file)
print(yearly_file)
print(OUTPUT_DIR / "sensitivity_out_of_sample_frequency.png")
print(OUTPUT_DIR / "sensitivity_out_of_sample_payouts.png")
