
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

OUTPUT_DIR = Path("outputs")

sensitivity = pd.read_csv(OUTPUT_DIR / "trigger_sensitivity.csv")
yearly = pd.read_csv(OUTPUT_DIR / "payout_sensitivity_by_year.csv")

# 1. Compare average annual payouts by trigger.
plt.figure(figsize=(9, 5))
plt.bar(
    (sensitivity["trigger_ratio"] * 100).astype(int).astype(str) + "%",
    sensitivity["average_annual_payout_inr"],
)
plt.title("Average Annual Payout by Trigger Design")
plt.xlabel("Trigger (% of reference rainfall)")
plt.ylabel("Average payout (₹ per policy per year)")
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "average_payout_by_trigger.png", dpi=200)
plt.close()

# 2. Compare yearly payouts for each trigger.
plt.figure(figsize=(11, 6))
for column in yearly.columns:
    if column.startswith("trigger_"):
        plt.plot(yearly["year"], yearly[column], marker="o", label=column)

plt.title("Historical Payout Comparison Across Trigger Designs")
plt.xlabel("Year")
plt.ylabel("Simulated payout (₹ per policy)")
plt.xticks(yearly["year"], rotation=45)
plt.grid(alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "historical_payout_comparison.png", dpi=200)
plt.close()

print("Saved:")
print(OUTPUT_DIR / "average_payout_by_trigger.png")
print(OUTPUT_DIR / "historical_payout_comparison.png")
