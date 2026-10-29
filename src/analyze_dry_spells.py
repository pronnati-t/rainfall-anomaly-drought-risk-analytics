
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr
import geopandas as gpd

DATA_DIR = Path("data/raw")
OUTPUT_DIR = Path("data/processed")
BOUNDARY_FILE = Path("data/boundaries/india_states.geojson")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

DRY_DAY_THRESHOLD_MM = 2.5
MONSOON_MONTHS = [6, 7, 8, 9]
SPELL_LENGTHS = [5, 7, 10, 14]

# Load Gujarat boundary.
states = gpd.read_file(BOUNDARY_FILE)
gujarat = states.loc[states["shapeISO"] == "IN-GJ"]

if gujarat.empty:
    raise ValueError("Gujarat boundary (IN-GJ) not found.")

gujarat_geometry = gujarat.geometry.union_all()

files = sorted(DATA_DIR.glob("RF25_ind*_rfp25.nc"))

if len(files) != 16:
    raise ValueError(f"Expected 16 yearly files, found {len(files)}")

records = []

for file in files:
    print(f"Processing {file.name}...")

    with xr.open_dataset(file) as ds:
        rainfall = ds["RAINFALL"]

        latitudes = rainfall["LATITUDE"].values
        longitudes = rainfall["LONGITUDE"].values

        lon_grid, lat_grid = np.meshgrid(longitudes, latitudes)

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

        # Spatially averaged daily rainfall over Gujarat.
        daily_mean = region.mean(
            dim=("LATITUDE", "LONGITUDE"),
            skipna=True,
        )

        monsoon = daily_mean.where(
            daily_mean["TIME"].dt.month.isin(MONSOON_MONTHS),
            drop=True,
        ).sortby("TIME")

        daily = pd.DataFrame({
            "date": pd.to_datetime(monsoon["TIME"].values),
            "rainfall_mm": np.asarray(monsoon.values, dtype=float),
        })

        daily = daily.sort_values("date").reset_index(drop=True)

        if len(daily) != 122:
            raise ValueError(
                f"Expected 122 monsoon days in {file.name}; "
                f"found {len(daily)}"
            )

        if daily["rainfall_mm"].isna().any():
            raise ValueError(
                f"Missing daily rainfall values in {file.name}"
            )

        dry = daily["rainfall_mm"] < DRY_DAY_THRESHOLD_MM

        # Identify consecutive runs of dry days.
        run_id = dry.ne(dry.shift(fill_value=False)).cumsum()
        dry_runs = daily.loc[dry].groupby(run_id[dry]).size()

        maximum_spell = int(dry_runs.max()) if not dry_runs.empty else 0

        row = {
            "year": int(daily["date"].dt.year.iloc[0]),
            "monsoon_rainfall_mm": round(
                float(daily["rainfall_mm"].sum()), 2
            ),
            "dry_day_threshold_mm": DRY_DAY_THRESHOLD_MM,
            "dry_days": int(dry.sum()),
            "maximum_consecutive_dry_days": maximum_spell,
        }

        for length in SPELL_LENGTHS:
            row[f"spells_at_least_{length}_days"] = int(
                (dry_runs >= length).sum()
            )

        records.append(row)

results = pd.DataFrame(records).sort_values("year")

output_file = OUTPUT_DIR / "gujarat_dry_spell_metrics.csv"
results.to_csv(output_file, index=False)

print("\nGUJARAT MONSOON DRY-SPELL ANALYSIS")
print("-" * 45)
print(f"Dry-day threshold: < {DRY_DAY_THRESHOLD_MM} mm/day")
print(results.to_string(index=False))
print(f"\nSaved results to: {output_file}")
