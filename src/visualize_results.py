
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

INPUT_FILE = Path("data/processed/gujarat_monsoon_rainfall.csv")
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(INPUT_FILE).sort_values("year")
mean_rainfall = df["monsoon_rainfall_mm"].mean()

# Chart 1: Monsoon rainfall over time
plt.figure(figsize=(11, 6))
plt.plot(
    df["year"],
    df["monsoon_rainfall_mm"],
    marker="o",
    linewidth=2,
    label="Monsoon rainfall",
)
plt.axhline(
    mean_rainfall,
    linestyle="--",
    label=f"Study-period mean ({mean_rainfall:.1f} mm)",
)
plt.title("Gujarat Region: Monsoon Rainfall (2010–2025)")
plt.xlabel("Year")
plt.ylabel("June–September rainfall (mm)")
plt.xticks(df["year"], rotation=45)
plt.grid(alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "monsoon_rainfall_trend.png", dpi=200)
plt.close()

# Chart 2: Percentage rainfall anomalies
plt.figure(figsize=(11, 6))
plt.bar(df["year"], df["anomaly_percent"])
plt.axhline(0, linewidth=1)
plt.axhline(-20, linestyle="--", label="-20% reference")
plt.title("Monsoon Rainfall Anomaly vs Study-Period Mean")
plt.xlabel("Year")
plt.ylabel("Rainfall anomaly (%)")
plt.xticks(df["year"], rotation=45)
plt.grid(axis="y", alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "rainfall_anomalies.png", dpi=200)
plt.close()

# Chart 3: Years flagged by the illustrative deficit threshold
plt.figure(figsize=(11, 6))
colors = [
    "red" if deficit else "steelblue"
    for deficit in df["rainfall_deficit_flag"]
]
plt.bar(df["year"], df["monsoon_rainfall_mm"], color=colors)
plt.axhline(
    0.8 * mean_rainfall,
    linestyle="--",
    label="80% of study-period mean",
)
plt.title("Rainfall-Deficit Screening (Illustrative Threshold)")
plt.xlabel("Year")
plt.ylabel("June–September rainfall (mm)")
plt.xticks(df["year"], rotation=45)
plt.grid(axis="y", alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "rainfall_deficit_years.png", dpi=200)
plt.close()

print("Charts saved:")
for path in sorted(OUTPUT_DIR.glob("*.png")):
    print(path)
