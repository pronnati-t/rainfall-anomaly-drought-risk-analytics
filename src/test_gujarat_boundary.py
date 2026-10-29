
import geopandas as gpd
import xarray as xr
import numpy as np

BOUNDARY_FILE = "data/boundaries/india_states.geojson"
RAINFALL_FILE = "data/raw/RF25_ind2010_rfp25.nc"

# Load Gujarat's official boundary geometry from the GeoJSON.
states = gpd.read_file(BOUNDARY_FILE)
gujarat = states.loc[states["shapeISO"] == "IN-GJ"]

if gujarat.empty:
    raise ValueError("Gujarat boundary (IN-GJ) was not found.")

geometry = gujarat.geometry.union_all()

# Read the rainfall grid.
ds = xr.open_dataset(RAINFALL_FILE)
rainfall = ds["RAINFALL"]

latitudes = rainfall["LATITUDE"].values
longitudes = rainfall["LONGITUDE"].values

lon_grid, lat_grid = np.meshgrid(longitudes, latitudes)

# Build a GeoDataFrame of rainfall grid-cell centres.
grid = gpd.GeoDataFrame(
    geometry=gpd.points_from_xy(
        lon_grid.ravel(),
        lat_grid.ravel()
    ),
    crs="EPSG:4326",
)

# Select cells whose centres lie within Gujarat.
inside = grid.geometry.within(geometry).to_numpy()
mask = inside.reshape(len(latitudes), len(longitudes))

print("Gujarat boundary loaded:", not gujarat.empty)
print("Rainfall grid dimensions:", rainfall.sizes)
print("Grid-cell centres inside Gujarat:", int(mask.sum()))

# Compare with the old rectangular region.
rectangular = (
    (lat_grid >= 20) & (lat_grid <= 24.75)
    & (lon_grid >= 68) & (lon_grid <= 74.5)
)

print("Cells in old rectangular region:", int(rectangular.sum()))
print("Cells selected by both methods:", int((inside.reshape(lat_grid.shape) & rectangular).sum()))

ds.close()
