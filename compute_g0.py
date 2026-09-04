import rasterio, time, os
import pandas as pd
import numpy as np
import xarray as xr

print('=== G0: 1. NATIVE 30M SRTM TPI & REPRESENTATION UNCERTAINTY ===')
t0 = time.time()
with rasterio.open('data/cache/srtm_domain_30m.tif') as src:
    dem = src.read(1)
    transform = src.transform
    inv_transform = ~transform
    res_x, res_y = src.res

print(f'Loaded 30m DEM in {time.time()-t0:.2f}s, shape: {dem.shape}')
df = pd.read_csv('outputs/village_corrections.csv', low_memory=False)
n_villages = len(df)
print(f'Loaded {n_villages} villages.')

xs = df['centroid_lon'].values
ys = df['centroid_lat'].values
cols, rows = inv_transform * (xs, ys)
cols = np.floor(cols).astype(int)
rows = np.floor(rows).astype(int)

# Extract 30m pixel elevation at centroid
z_30m_centroid = dem[rows, cols].astype(float)
df['srtm_30m_centroid'] = z_30m_centroid

# Representation discrepancy: 30m centroid pixel vs 30m polygon mean (fine_elev_m)
discrepancy = df['srtm_30m_centroid'] - df['fine_elev_m']
sigma_rep_30m = discrepancy.std()
mean_rep_30m = discrepancy.mean()

print(f'Recomputed 30m Representation Discrepancy: Mean = {mean_rep_30m:+.2f} m, Std = {sigma_rep_30m:.2f} m, Median = {discrepancy.median():+.2f} m')

pixel_m = res_y * 111000.0
radii = [500, 1000, 2000]

# Compute circular focal mean for each village at each radius
tpi_results = {}
edge_counts_domain = {}
edge_counts_dem = {}

# Domain bounds: [73.5, 13.0, 76.5, 17.5]
d_lon_min, d_lat_min, d_lon_max, d_lat_max = 73.5, 13.0, 76.5, 17.5
# DEM raster bounds
r_lon_min, r_lat_min, r_lon_max, r_lat_max = 73.40, 12.90, 76.60, 17.60

deg_m = 111000.0

for r_m in radii:
    r_pix = int(round(r_m / pixel_m))
    y, x = np.ogrid[-r_pix:r_pix+1, -r_pix:r_pix+1]
    mask = (x*x + y*y) <= r_pix*r_pix
    
    # Edge truncation check: distance to boundary in meters
    # Distance to domain bbox
    dist_domain_w = (xs - d_lon_min) * deg_m * np.cos(np.radians(ys))
    dist_domain_e = (d_lon_max - xs) * deg_m * np.cos(np.radians(ys))
    dist_domain_s = (ys - d_lat_min) * deg_m
    dist_domain_n = (d_lat_max - ys) * deg_m
    min_dist_domain = np.minimum(np.minimum(dist_domain_w, dist_domain_e), np.minimum(dist_domain_s, dist_domain_n))
    edge_counts_domain[r_m] = int((min_dist_domain < r_m).sum())
    
    # Distance to DEM bbox
    dist_dem_w = (xs - r_lon_min) * deg_m * np.cos(np.radians(ys))
    dist_dem_e = (r_lon_max - xs) * deg_m * np.cos(np.radians(ys))
    dist_dem_s = (ys - r_lat_min) * deg_m
    dist_dem_n = (r_lat_max - ys) * deg_m
    min_dist_dem = np.minimum(np.minimum(dist_dem_w, dist_dem_e), np.minimum(dist_dem_s, dist_dem_n))
    edge_counts_dem[r_m] = int((min_dist_dem < r_m).sum())
    
    t_start = time.time()
    tpi_vals = np.empty(n_villages, dtype=float)
    for i in range(n_villages):
        r, c = rows[i], cols[i]
        # Check boundary
        if r - r_pix < 0 or r + r_pix >= dem.shape[0] or c - r_pix < 0 or c + r_pix >= dem.shape[1]:
            tpi_vals[i] = np.nan
        else:
            sub = dem[r-r_pix:r+r_pix+1, c-r_pix:c+r_pix+1]
            tpi_vals[i] = z_30m_centroid[i] - np.mean(sub[mask])
            
    tpi_results[r_m] = tpi_vals
    df[f'tpi_{r_m}m'] = tpi_vals
    print(f'Radius {r_m} m computed in {time.time()-t_start:.2f}s.')

# Save candidate npz
np.savez('data/cache/village_tpi_30m_results.npz',
         village_id=df['village_id'].values,
         srtm_30m_centroid=z_30m_centroid,
         discrepancy_30m=discrepancy.values,
         tpi_500m=tpi_results[500],
         tpi_1000m=tpi_results[1000],
         tpi_2000m=tpi_results[2000])
print('Saved data/cache/village_tpi_30m_results.npz successfully!')

print('\n=== TPI DISTRIBUTIONS (NATIVE 30M SRTM) ===')
for r_m in radii:
    s = pd.Series(tpi_results[r_m]).dropna()
    print(f'\nRadius R = {r_m} m:')
    print(f'  Count:  {len(s)}')
    print(f'  Min:    {s.min():+7.2f} m')
    print(f'  P1:     {s.quantile(0.01):+7.2f} m')
    print(f'  P5:     {s.quantile(0.05):+7.2f} m')
    print(f'  P25:    {s.quantile(0.25):+7.2f} m')
    print(f'  Median: {s.median():+7.2f} m')
    print(f'  P75:    {s.quantile(0.75):+7.2f} m')
    print(f'  P95:    {s.quantile(0.95):+7.2f} m')
    print(f'  P99:    {s.quantile(0.99):+7.2f} m')
    print(f'  Max:    {s.max():+7.2f} m')
    print(f'  Mean:   {s.mean():+7.2f} m, Std: {s.std():.2f} m')
    print(f'  Domain Edge-Truncated (< {r_m}m to [73.5, 13.0, 76.5, 17.5]): {edge_counts_domain[r_m]} ({edge_counts_domain[r_m]/n_villages*100:.2f}%)')
    print(f'  DEM Edge-Truncated (< {r_m}m to raster edge):                 {edge_counts_dem[r_m]} ({edge_counts_dem[r_m]/n_villages*100:.2f}%)')

print('\n=== NOISE FLOOR RETESTING ===')
# Test against old 250m noise floor (27.14 m) and new 30m noise floor (sigma_rep_30m = 27.59 m)
for r_m in radii:
    s = pd.Series(tpi_results[r_m]).dropna()
    res_old = (s.abs() > 27.14).sum()
    pct_old = res_old / len(s) * 100.0
    res_new = (s.abs() > sigma_rep_30m).sum()
    pct_new = res_new / len(s) * 100.0
    print(f'Radius {r_m} m:')
    print(f'  |TPI| > 27.14 m: {res_old} / {len(s)} ({pct_old:.2f}%) resolvable | Below noise floor: {len(s)-res_old} ({100.0-pct_old:.2f}%)')
    print(f'  |TPI| > {sigma_rep_30m:.2f} m: {res_new} / {len(s)} ({pct_new:.2f}%) resolvable | Below noise floor: {len(s)-res_new} ({100.0-pct_new:.2f}%)')

print('\n=== G0: 2. PROVENANCE RESOLUTION (CHITRADURGA JUNE 2015, 720 HOURS) ===')
wb_url = 'gs://weatherbench2/datasets/era5/1959-2023_01_10-full_37-1h-0p25deg-chunk-1.zarr'
ds = xr.open_zarr(wb_url, consolidated=True, storage_options={'token': 'anon'})

ch_lat, ch_lon = 14.25, 76.50
time_month = slice('2015-06-01T00:00:00', '2015-06-30T23:00:00')
wb2_vars = ['10m_u_component_of_wind', '10m_v_component_of_wind', 'total_cloud_cover', '2m_temperature']
gee_vars = ['u_component_of_wind_10m', 'v_component_of_wind_10m', 'total_cloud_cover', 'temperature_2m']

sub_wb2 = ds[wb2_vars].sel(latitude=ch_lat, longitude=ch_lon).sel(time=time_month).compute()

df_gee = pd.read_csv('data/cache/station_hourly_era5.csv')
df_gee['datetime_utc'] = pd.to_datetime(df_gee['datetime_utc'])
df_ch_gee = df_gee[(df_gee['station_id'] == 'IN009070100') & 
                   (df_gee['datetime_utc'] >= '2015-06-01 00:00:00') & 
                   (df_gee['datetime_utc'] <= '2015-06-30 23:00:00')].sort_values('datetime_utc')

print(f'Chitradurga June 2015: WB2 records = {len(sub_wb2.time)}, GEE records = {len(df_ch_gee)}')

for wb_v, gee_v in zip(wb2_vars, gee_vars):
    v_wb = sub_wb2[wb_v].values
    v_gee = df_ch_gee[gee_v].values
    diff = v_wb - v_gee
    mad = np.mean(np.abs(diff))
    max_d = np.max(np.abs(diff))
    bias = np.mean(diff)
    print(f'Variable {wb_v}:')
    print(f'  MAD:     {mad:.8f}')
    print(f'  MaxDiff: {max_d:.8f}')
    print(f'  Bias:    {bias:+.8f}')
