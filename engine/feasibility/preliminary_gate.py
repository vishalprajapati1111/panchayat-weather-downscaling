import sys, pathlib, json, datetime, io, hashlib, time
import os
import pathlib
import datetime
import numpy as np
import xarray as xr

ROOT = pathlib.Path(__file__).parent.parent.parent
CACHE_DIR = ROOT / "data/engine_cache/chirps/by_month"

PAIRS = {
    "maharashtra": {
        "windward": {"name": "Mahabaleshwar", "lat": 17.92, "lon": 73.66, "gauge_annual_mm": 6000},
        "leeward":  {"name": "Satara",         "lat": 17.69, "lon": 74.00, "gauge_annual_mm": 700},
    },
    "karnataka": {
        "windward": {"name": "Kanakumbi", "lat": 15.65, "lon": 74.28, "gauge_annual_mm": None},
        "leeward":  {"name": "Hosaritti", "lat": 14.72, "lon": 75.62, "gauge_annual_mm": None},
    },
}
JJAS_FRAC = {
    "maharashtra": {"windward": 0.85, "leeward": 0.60},
    "karnataka":   {"windward": 0.85, "leeward": 0.60},
}

files = sorted([f for f in CACHE_DIR.glob("*.nc")])
if not files:
    print("No cached files found yet.")
    exit(0)

# 1. Metadata check on first file
first_file = files[0]
print(f"=== METADATA CHECK (File: {first_file.name}) ===")
ds = xr.open_dataset(first_file)
var = [v for v in ds.data_vars if v not in ("crs",)][0]
lat_dim = "latitude" if "latitude" in ds.dims else "lat"
lon_dim = "longitude" if "longitude" in ds.dims else "lon"

lats = ds[lat_dim].values
lons = ds[lon_dim].values
dlat = abs(float(np.diff(lats).mean()))
dlon = abs(float(np.diff(lons).mean()))

print(f"Array shape: {ds.dims}")
print(f"Lat spacing: {dlat:.5f} deg")
print(f"Lon spacing: {dlon:.5f} deg")
print(f"Units attribute: {ds[var].attrs.get('units', 'unknown')}")
fill_val = ds[var].attrs.get('_FillValue', ds[var].attrs.get('missing_value', np.nan))
print(f"Fill/Missing value: {fill_val}")
if 'time' in ds.variables:
    print(f"Time encoding/attrs: {ds['time'].attrs}")

assert abs(dlat - 0.05) < 0.001, f"FATAL: dlat is {dlat}, expected 0.05"
assert abs(dlon - 0.05) < 0.001, f"FATAL: dlon is {dlon}, expected 0.05"
CHIRPS_RES = 0.05

print("\nNearest Cell Verification:")
for region, pair in PAIRS.items():
    ww, lw = pair["windward"], pair["leeward"]
    
    w_px = ds[var].sel({lat_dim: ww["lat"], lon_dim: ww["lon"]}, method="nearest")
    l_px = ds[var].sel({lat_dim: lw["lat"], lon_dim: lw["lon"]}, method="nearest")
    
    w_lat_c, w_lon_c = float(w_px[lat_dim].values), float(w_px[lon_dim].values)
    l_lat_c, l_lon_c = float(l_px[lat_dim].values), float(l_px[lon_dim].values)
    
    lat_cells = abs(w_lat_c - l_lat_c) / CHIRPS_RES
    lon_cells = abs(w_lon_c - l_lon_c) / CHIRPS_RES
    diag = (lat_cells**2 + lon_cells**2)**0.5
    
    print(f"  {ww['name']} -> cell center: {w_lat_c:.3f}N, {w_lon_c:.3f}E")
    print(f"  {lw['name']} -> cell center: {l_lat_c:.3f}N, {l_lon_c:.3f}E")
    print(f"  {region} separation: {lat_cells:.1f} lat-cells, {lon_cells:.1f} lon-cells -> {diag:.1f} cells diagonal")
ds.close()

# 2. Compute Preliminary Ratios
print(f"\n=== PRELIMINARY DATA EXTRACTION ({len(files)} files) ===")

annual_totals = {r: {"windward": {}, "leeward": {}} for r in PAIRS}

for f in files:
    try:
        # Extract year and month from filename
        # chirps-v2.0.1991.06.days_p05.nc
        parts = f.name.split('.')
        year = int(parts[2])
        ds = xr.open_dataset(f)
        for region, pair in PAIRS.items():
            for side, info in pair.items():
                px = ds[var].sel({lat_dim: info["lat"], lon_dim: info["lon"]}, method="nearest")
                # Filter out nans and fill values correctly
                valid_vals = []
                for v in px.values.flat:
                    if np.isnan(v):
                        continue
                    if not np.isnan(fill_val) and abs(v - fill_val) < 1e-5:
                        continue
                    valid_vals.append(float(v))
                if year not in annual_totals[region][side]:
                    annual_totals[region][side][year] = 0.0
                annual_totals[region][side][year] += sum(valid_vals)
        ds.close()
    except Exception as e:
        print(f"Error parsing {f.name}: {e}")

lines = [
    "# Preliminary Feasibility Gate Report",
    f"**Generated:** {datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%MZ')}  ",
    f"**Cached Files Used:** {len(files)}  ",
    "",
    "| Region | Windward | Mean JJAS | Leeward | Mean JJAS | Sat Ratio | Gauge JJAS (est) | Gauge JJAS Ratio | Attenuation | Years Analyzed |",
    "|---|---|---|---|---|---|---|---|---|---|",
]

for region, pair in PAIRS.items():
    ww, lw = pair["windward"], pair["leeward"]
    
    w_years = annual_totals[region]["windward"]
    l_years = annual_totals[region]["leeward"]
    
    valid_years = sorted(list(set(w_years.keys()).intersection(l_years.keys())))
    
    if not valid_years:
        continue
        
    w_vals = [w_years[y] for y in valid_years]
    l_vals = [l_years[y] for y in valid_years]
    
    w_mean = np.mean(w_vals)
    l_mean = np.mean(l_vals)
    sat_ratio = w_mean / l_mean if l_mean > 0 else None
    
    ratios = [w_years[y]/l_years[y] for y in valid_years if l_years[y] > 0]
    spread = np.std(ratios) if len(ratios) > 1 else 0.0
    
    print(f"\n[{region.upper()}] Preliminary {len(valid_years)} years:")
    print(f"  {ww['name']} JJAS: {w_mean:.1f} mm")
    print(f"  {lw['name']} JJAS: {l_mean:.1f} mm")
    sat_str = f"{sat_ratio:.2f}x" if sat_ratio is not None else "None"
    print(f"  Satellite Ratio: {sat_str} (std: +/- {spread:.2f})")
    
    g_ann_w = ww.get("gauge_annual_mm")
    g_ann_l = lw.get("gauge_annual_mm")
    frac_w = JJAS_FRAC[region]["windward"]
    frac_l = JJAS_FRAC[region]["leeward"]
    g_jjas_w = g_ann_w * frac_w if g_ann_w else None
    g_jjas_l = g_ann_l * frac_l if g_ann_l else None
    g_jjas_ratio = g_jjas_w / g_jjas_l if (g_jjas_w and g_jjas_l) else None
    
    atten = (g_jjas_ratio / sat_ratio) if g_jjas_ratio and sat_ratio else None
    g_w_str = f"{g_jjas_w:.0f}" if g_jjas_w is not None else "None"
    g_l_str = f"{g_jjas_l:.0f}" if g_jjas_l is not None else "None"
    g_rat_str = f"{g_jjas_ratio:.2f}x" if g_jjas_ratio is not None else "None"
    atten_str = f"{atten:.2f}x" if atten is not None else "None"
            
    lines.append(
        f"| {region} | {ww['name']} | {w_mean:.0f}mm | {lw['name']} | {l_mean:.0f}mm | "
        f"{sat_str} (±{spread:.2f}) | {g_w_str} / {g_l_str} | "
        f"{g_rat_str} | {atten_str} | {len(valid_years)} |"
    )

(ROOT / "docs" / "feasibility_gate_preliminary.md").write_text("\n".join(lines), encoding="utf-8")
print("\nWrote preliminary report.")
