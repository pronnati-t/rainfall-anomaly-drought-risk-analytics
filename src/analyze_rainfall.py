
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr
import geopandas as gpd

DATA_DIR = Path("data/raw")
OUTPUT_DIR = Path("data/processed")
BOUNDARY_FILE = Path("data/boundaries/india_states.geojson")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

records = []

# Load Gujarat's state boundary.
states = gpd.read_file(BOUNDARY_FILE)
gujarat = states.loc[states["shapeISO"] == "IN-GJ"]

if gujarat.empty:
    raise ValueError("Gujarat boundary (IN-GJ) not found.")

gujarat_geometry = gujarat.geometry.union_all()

files = sorted(DATA_DIR.glob("RF25_ind*_rfp25.nc"))
if len(files) != 16:
    raise ValueError(f"Expected 16 yearly files, found {len(files)}")

for file in files:
    print(f"Processing {file.name}...")

    with xr.open_dataset(file) as ds:
        rainfall = ds["RAINFALL"]

        latitudes = rainfall["LATITUDE"].values
        longitudes = rainfall["LONGITUDE"].values

        lon_grid, lat_grid = np.meshgrid(longitudes, latitudes)

        # Select grid-cell centres inside Gujarat.
        points = gpd.GeoSeries(
            gpd.points_from_xy(
                lon_grid.ravel(),
                lat_grid.ravel(),
            ),
            crs="EPSG:4326",
        )

        spatial_mask = points.within(gujarat_geometry).to_numpy()
        spatial_mask = spatial_mask.reshape(
            len(latitudes), len(longitudes)
        )

        mask = xr.DataArray(
            spatial_mask,
            coords={
                "LATITUDE": rainfall["LATITUDE"],
                "LONGITUDE": rainfall["LONGITUDE"],
            },
            dims=("LATITUDE", "LONGITUDE"),
        )

        region = rainfall.where(mask, drop=False)

        valid_cells = int(
            np.isfinite(region.isel(TIME=0).values).sum()
        )

        if valid_cells == 0:
            raise ValueError(
                f"No valid Gujarat rainfall cells in {file.name}"
            )

        # Average rainfall across Gujarat grid-cell centres.
        daily_mean = region.mean(
            dim=("LATITUDE", "LONGITUDE"),
            skipna=True,
        )

        monsoon = daily_mean.where(
            daily_mean["TIME"].dt.month.isin([6, 7, 8, 9]),
            drop=True,
        )

        valid_days = int(np.isfinite(monsoon.values).sum())

        if valid_days != 122:
            raise ValueError(
                f"Expected 122 valid monsoon days in {file.name}, "
                f"found {valid_days}"
            )

        annual_total = float(monsoon.sum(skipna=True).values)

        records.append({
            "year": int(monsoon["TIME"].dt.year.values[0]),
            "monsoon_rainfall_mm": annual_total,
            "valid_monsoon_days": valid_days,
            "valid_grid_cells_first_day": valid_cells,
        })

results = pd.DataFrame(records).sort_values("year")

# Calculate anomalies relative to the 2010–2025 study-period mean.
baseline = results["monsoon_rainfall_mm"].mean()
results["anomaly_mm"] = results["monsoon_rainfall_mm"] - baseline
results["anomaly_percent"] = results["anomaly_mm"] / baseline * 100

# Illustrative threshold, not an official drought classification.
results["rainfall_deficit_flag"] = (
    results["monsoon_rainfall_mm"] < 0.80 * baseline
)

output_file = OUTPUT_DIR / "gujarat_monsoon_rainfall.csv"
results.to_csv(output_file, index=False)

print("\nMonsoon rainfall results:")
print(results.round(2).to_string(index=False))
print(f"\nGujarat grid cells on first day: "
      f"{results['valid_grid_cells_first_day'].iloc[0]}")
print(f"Study-period mean: {baseline:.2f} mm")
print(f"Rainfall-deficit years: "
      f"{results['rainfall_deficit_flag'].sum()}")
print(f"Saved results to: {output_file}")
