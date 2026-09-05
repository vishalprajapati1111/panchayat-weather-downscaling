import ee, json, pathlib
import numpy as np

ee.Initialize()

# 1. Construct node-centred projection: pixel center at (L_lon, L_lat)
node_proj = ee.Projection('EPSG:4326', [0.25, 0, -180.125, 0, -0.25, 90.125])

# SRTM reduced to 0.25 deg node-centred boxes
dem = ee.Image('USGS/SRTMGL1_003').select('elevation')
dem_900 = dem.reduceResolution(reducer=ee.Reducer.mean(), maxPixels=65535).reproject(crs='EPSG:4326', scale=900)
dem_node = dem_900.reduceResolution(reducer=ee.Reducer.mean(), maxPixels=65535).reproject(crs=node_proj)

# Load existing arrays
grids_old = np.load("data/cache/orography_grids.npz")
lats = grids_old['lats'] # 17.5 down to 13.0 (19 values)
lons = grids_old['lons'] # 73.5 up to 76.5 (13 values)
z_era5 = grids_old['z_era5'] # (19, 13)

# Build feature collection of all 247 nodes
node_features = []
for i, lat in enumerate(lats):
    for j, lon in enumerate(lons):
        pt = ee.Geometry.Point([float(lon), float(lat)])
        node_features.append(ee.Feature(pt, {'i': i, 'j': j, 'lat': float(lat), 'lon': float(lon)}))

fc_nodes = ee.FeatureCollection(node_features)
print("Reducing dem_node at all 247 ERA5 nodes on Earth Engine...")
sampled = dem_node.reduceRegions(collection=fc_nodes, reducer=ee.Reducer.first()).getInfo()

srtm_node_grid = np.full((len(lats), len(lons)), np.nan)
for f in sampled['features']:
    props = f['properties']
    i = props['i']
    j = props['j']
    val = props.get('first')
    if val is not None:
        srtm_node_grid[i, j] = float(val)

# Compute new differences: z_era5 - srtm_node_grid
diff_node = z_era5 - srtm_node_grid
valid_mask = ~np.isnan(srtm_node_grid)
valid_count = np.sum(valid_mask)
print(f"Valid land cells: {valid_count} / {len(lats)*len(lons)}")

valid_diffs = diff_node[valid_mask]
print("\n=== REBUILT 239-CELL OFFSET DISTRIBUTION (ERA5 node - SRTM node-box) ===")
print(f"Count: {len(valid_diffs)}")
print(f"Min:   {np.min(valid_diffs):.2f} m")
print(f"p1:    {np.percentile(valid_diffs, 1):.2f} m")
print(f"p25:   {np.percentile(valid_diffs, 25):.2f} m")
print(f"p50:   {np.median(valid_diffs):.2f} m")
print(f"Mean:  {np.mean(valid_diffs):.2f} m")
print(f"p75:   {np.percentile(valid_diffs, 75):.2f} m")
print(f"p99:   {np.percentile(valid_diffs, 99):.2f} m")
print(f"Max:   {np.max(valid_diffs):.2f} m")

# Save to data/cache/node_orography_grids.npz
np.savez(
    "data/cache/node_orography_grids.npz",
    lats=lats,
    lons=lons,
    z_era5=z_era5,
    srtm_node_grid=srtm_node_grid,
    diff_node=diff_node
)
print("Saved rebuilt grids to data/cache/node_orography_grids.npz successfully!")
