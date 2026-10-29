
from pathlib import Path
import numpy as np
import xarray as xr

data_dir = Path("data/raw")
sample_file = sorted(data_dir.glob("*.nc"))[0]

with xr.open_dataset(sample_file) as ds:
    rainfall = ds["RAINFALL"]

    print("File:", sample_file.name)
    print("\nRainfall attributes:")
    print(rainfall.attrs)

    print("\nRainfall dimensions:", rainfall.dims)
    print("Rainfall shape:", rainfall.shape)

    values = rainfall.values
    finite_values = values[np.isfinite(values)]

    print("\nFinite value count:", finite_values.size)
    print("Minimum:", np.min(finite_values))
    print("Maximum:", np.max(finite_values))
    print("Mean:", np.mean(finite_values))
    print("Missing/NaN count:", np.isnan(values).sum())

    print("\nSample rainfall values:")
    print(finite_values[:20])
