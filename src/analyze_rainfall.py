
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr

DATA_DIR = Path("data/raw")
OUTPUT_DIR = Path("data/processed")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Approximate geographic bounding box for Gujarat.
LAT_MIN, LAT_MAX = 20.0, 24.75
LON_MIN, LON_MAX = 68.0, 74.5

records = []

files = sorted(DATA_DIR.glob("RF25_ind*_rfp25.nc"))
if len(files) != 16:
    raise ValueError(f"Expected 16 yearly files, found {len(files)}")

for file in files:
    print(f"Processing {file.name}...")

    with xr.open_dataset(file) as ds:
        rainfall = ds["RAINFALL"]

        # Select the approximate Gujarat region.
        region = rainfall.where(
            (ds["LATITUDE"] >= LAT_MIN)
            & (ds["LATITUDE"] <= LAT_MAX)
            & (ds["LONGITUDE"] >= LON_MIN)
            & (ds["LONGITUDE"] <= LON_MAX),
            drop=True,
        )

        # Check the selected region has usable data.
        valid_cells = int(
            np.isfinite(region.isel(TIME=0).values).sum()
        )

        if valid_cells == 0:
            raise ValueError(f"No valid rainfall cells in {file.name}")

        # Average across available grid cells each day.
        daily_mean = region.mean(
            dim=("LATITUDE", "LONGITUDE"),
            skipna=True,
        )

        # Sum daily rainfall during June–September.
        monsoon = daily_mean.where(
            daily_mean["TIME"].dt.month.isin([6, 7, 8, 9]),
            drop=True,
        )

        annual_total = float(monsoon.sum(skipna=True).values)
        valid_days = int(np.isfinite(monsoon.values).sum())

        records.append({
            "year": int(monsoon["TIME"].dt.year.values[0]),
            "monsoon_rainfall_mm": annual_total,
            "valid_monsoon_days": valid_days,
            "valid_grid_cells_first_day": valid_cells,
        })

results = pd.DataFrame(records).sort_values("year")

# Calculate anomalies relative to this study period.
baseline = results["monsoon_rainfall_mm"].mean()
results["anomaly_mm"] = results["monsoon_rainfall_mm"] - baseline
results["anomaly_percent"] = (
    results["anomaly_mm"] / baseline * 100
)

# Illustrative threshold, not an official drought classification.
results["rainfall_deficit_flag"] = (
    results["monsoon_rainfall_mm"] < 0.80 * baseline
)

output_file = OUTPUT_DIR / "gujarat_monsoon_rainfall.csv"
results.to_csv(output_file, index=False)

print("\nMonsoon rainfall results:")
print(results.round(2).to_string(index=False))
print(f"\nStudy-period mean: {baseline:.2f} mm")
print(f"Rainfall-deficit years: {results['rainfall_deficit_flag'].sum()}")
print(f"Saved results to: {output_file}")
