
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

INPUT_FILE = Path("data/processed/gujarat_dry_spell_metrics.csv")
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(INPUT_FILE).sort_values("year")

# Plot 1: Maximum consecutive dry spell by year.
plt.figure(figsize=(11, 5))
plt.bar(
    df["year"].astype(str),
    df["maximum_consecutive_dry_days"],
)
plt.xlabel("Year")
plt.ylabel("Maximum consecutive dry days")
plt.title("Gujarat Monsoon: Maximum Dry-Spell Duration")
plt.xticks(rotation=45)
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "maximum_dry_spell_by_year.png", dpi=200)
plt.close()

# Plot 2: Dry days and seasonal rainfall.
fig, ax1 = plt.subplots(figsize=(11, 5))

ax1.bar(
    df["year"].astype(str),
    df["dry_days"],
    alpha=0.8,
    label="Dry days",
)
ax1.set_xlabel("Year")
ax1.set_ylabel("Number of dry days")
ax1.tick_params(axis="x", rotation=45)

ax2 = ax1.twinx()
ax2.plot(
    df["year"].astype(str),
    df["monsoon_rainfall_mm"],
    marker="o",
    label="Seasonal rainfall",
)
ax2.set_ylabel("Monsoon rainfall (mm)")

ax1.set_title("Gujarat Monsoon: Dry Days vs Seasonal Rainfall")
fig.tight_layout()
fig.savefig(OUTPUT_DIR / "dry_days_vs_seasonal_rainfall.png", dpi=200)
plt.close(fig)

# Plot 3: Frequency of longer dry spells.
spell_columns = [
    "spells_at_least_5_days",
    "spells_at_least_7_days",
    "spells_at_least_10_days",
    "spells_at_least_14_days",
]

plt.figure(figsize=(11, 5))

for column in spell_columns:
    plt.plot(
        df["year"],
        df[column],
        marker="o",
        label=column.replace("spells_at_least_", "At least ")
                    .replace("_days", " days"),
    )

plt.xlabel("Year")
plt.ylabel("Number of dry spells")
plt.title("Frequency of Extended Dry Spells")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "dry_spell_frequency_by_year.png", dpi=200)
plt.close()

print("Dry-spell visualizations saved:")
print(OUTPUT_DIR / "maximum_dry_spell_by_year.png")
print(OUTPUT_DIR / "dry_days_vs_seasonal_rainfall.png")
print(OUTPUT_DIR / "dry_spell_frequency_by_year.png")
