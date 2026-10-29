
from pathlib import Path
import xarray as xr

data_dir = Path("data/raw")
files = sorted(data_dir.glob("*.nc"))

print(f"Number of NetCDF files: {len(files)}")

if not files:
    raise FileNotFoundError("No .nc files found in data/raw/")

sample_file = files[0]
print(f"\nInspecting: {sample_file.name}")

with xr.open_dataset(sample_file) as ds:
    print("\nDataset details:")
    print(ds)

    print("\nData variables:")
    print(list(ds.data_vars))

    print("\nCoordinates:")
    print(list(ds.coords))

    print("\nAttributes:")
    print(ds.attrs)
