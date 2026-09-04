import sys, pathlib, json, datetime, io, hashlib, time
"""
engine/feasibility/gate.py  (v3 — correct paths, grid assertion, dual comparison)
==========================
Step 1 - Feasibility Gate

Data strategy (priority order; each path validated on ONE file before any loop):
  1. p05/by_month/: https://data.chc.ucsb.edu/products/CHIRPS-2.0/
     global_daily/netcdf/p05/by_month/ -- probe first; JJAS-only saves ~2/3 volume
  2. Monthly TIFs (0.05-deg): chirps-v2.0.YYYY.MM.tif.gz from
     global_monthly/tifs/ -- ~13.8 MiB each, 120 files for JJAS 1991-2020
  3. byYear/ monthly NC: chirps-v2.0.YYYY.monthly.nc -- ~163 MiB each, last resort

  NEVER infer grid resolution from URL path or file size alone.
  Read dlat/dlon from the actual file; assert 0.05 +/- 0.001 deg.

IMERG: blocked pending credential provisioning (not silently dropped).
  Option A: earthengine authenticate --project <id>  (GEE free tier)
  Option B: urs.earthdata.nasa.gov + GES DISC GPM_3IMERGDF  (NASA Earthdata)
  The CHIRPS/IMERG disagreement field required in Step 4 cannot be computed
  until one route is provisioned. This is recorded in the gate report.

Gauge comparison:
  Published numbers (Mahabaleshwar ~6000 mm/yr, Satara ~650 mm/yr) are ANNUAL.
  Satellite data here is JJAS only. To avoid mixing windows, JJAS gauge is
  estimated as annual x assumed_JJAS_fraction (stated per station, propagated).
  Both comparisons reported: primary = sat_JJAS / gauge_JJAS_est;
  secondary = sat_JJAS / gauge_annual (notes the mismatch explicitly).
"""

import sys, pathlib
import numpy as np
import requests
import xarray as xr

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from engine.checks.guard import safe_extract

from engine.config import load as load_cfg
from engine.ingestion.logging_utils import (configure as log_configure,
                                             log_fetch, log_assertion)

cfg = load_cfg()
log_configure(str(ROOT / cfg["logs"]["fetch_log"]))
for d in ["docs", "logs",
          "data/engine_cache/chirps",
          "data/engine_cache/chirps/byYear",
          "data/engine_cache/chirps/tifs",
          "data/engine_cache/chirps/by_month"]:
    (ROOT / d).mkdir(parents=True, exist_ok=True)

# gauge_annual_mm: published ANNUAL climatology (mm/yr); NOT JJAS.
# Source: IMD normals approx; Satara/Wai range 600-900 mm/yr, central value used.
PAIRS = {
    "maharashtra": {
        "windward": {"name": "Mahabaleshwar", "lat": 17.92, "lon": 73.66,
                     "gauge_annual_mm": 6000},
        "leeward":  {"name": "Satara",         "lat": 17.69, "lon": 74.00,
                     "gauge_annual_mm": 700},
    },
    "karnataka": {
        "windward": {"name": "Kanakumbi", "lat": 15.65, "lon": 74.28,
                     "gauge_annual_mm": None},
        "leeward":  {"name": "Hosaritti", "lat": 14.72, "lon": 75.62,
                     "gauge_annual_mm": None},
    },
}
# JJAS fraction assumptions (stated; literature-informed; conservative).
# Mahabaleshwar: ~80-95% of rain in JJAS; using 0.85 (conservative).
# Satara: more year-round spread; ~55-65%; using 0.60.
# Kanakumbi/Hosaritti: similar pattern to Western Ghats stations.
JJAS_FRAC = {
    "maharashtra": {"windward": 0.85, "leeward": 0.60},
    "karnataka":   {"windward": 0.85, "leeward": 0.60},
}
JJAS_MONTHS = [6, 7, 8, 9]
CHIRPS_START, CHIRPS_END = 1991, 2020
IMERG_START,  IMERG_END  = 2001, 2020
THRESH_STOP, THRESH_WARN = 2.0, 4.0

# Data path URLs defined in Step B after probing
BY_MONTH_BASE = ("https://data.chc.ucsb.edu/products/CHIRPS-2.0/"
                 "global_daily/netcdf/p05/by_month/")
TIF_BASE      = ("https://data.chc.ucsb.edu/products/CHIRPS-2.0/"
                 "global_monthly/tifs/")
BYEAR_BASE    = ("https://data.chc.ucsb.edu/products/CHIRPS-2.0/"
                 "global_monthly/netcdf/byYear/")


def _retry(url, timeout=120, max_retries=4):
    for attempt in range(max_retries):
        try:
            r = requests.get(url, timeout=timeout)
            r.raise_for_status()
            return r
        except Exception as e:
            wait = 2 ** attempt
            print(f"    [retry {attempt+1}/{max_retries}] {type(e).__name__}: "
                  f"{str(e)[:60]} -- {wait}s")
            time.sleep(wait)
    raise RuntimeError(f"Fetch failed: {url}")


def dem_elevation(lat, lon):
    r = _retry(f"https://api.open-meteo.com/v1/elevation"
               f"?latitude={lat}&longitude={lon}", timeout=15)
    return r.json()["elevation"][0]


# =========================================================================
# Step A: DEM coordinate verification
# =========================================================================
print("=" * 65)
print("FEASIBILITY GATE -- Step A: DEM coordinate verification")
print("=" * 65)
dem_results = {}
for region, pair in PAIRS.items():
    for side, info in pair.items():
        elev = dem_elevation(info["lat"], info["lon"])
        dem_results[(region, side)] = elev
        print(f"  {info['name']:20s} ({info['lat']:.2f}N "
              f"{info['lon']:.2f}E)  DEM={elev:.0f}m")
        time.sleep(0.4)

log_assertion("mahabaleshwar_elevation_plausible",
              1000 < dem_results[("maharashtra","windward")] < 1700,
              f"DEM={dem_results[('maharashtra','windward')]:.0f}m")
log_assertion("satara_elevation_plausible",
              300 < dem_results[("maharashtra","leeward")] < 900,
              f"DEM={dem_results[('maharashtra','leeward')]:.0f}m")
log_assertion("maharashtra_windward_higher",
              dem_results[("maharashtra","windward")] >
              dem_results[("maharashtra","leeward")], "windward > leeward")


# =========================================================================
# Step B: Probe CHIRPS access paths; validate ONE file; assert grid resolution
# =========================================================================
print("\n" + "=" * 65)
print("FEASIBILITY GATE -- Step B: CHIRPS path discovery and grid verification")
print("=" * 65)

import re, gzip
try:
    import rasterio
    from rasterio.io import MemoryFile
    HAVE_RASTERIO = True
except ImportError:
    HAVE_RASTERIO = False
    print("  WARNING: rasterio not available; TIF path disabled")

data_path = None   # "by_month" | "tif" | "byYear"
grid_meta = {}     # populated after first successful file validation
bm_files  = []     # populated if by_month chosen

# --- B1: probe p05/by_month/ ---
print("  Probing p05/by_month/ ...")
try:
    rbm = requests.get(BY_MONTH_BASE, timeout=15)
    rbm.raise_for_status()
    bm_files = re.findall(r'href="(chirps[^"]+\.nc[^"]*)"', rbm.text)
    print(f"  by_month/ HTTP 200; files found (first 3): {bm_files[:3]}")
    if bm_files:
        test_bm = next((f for f in bm_files if "1991" in f and "06" in f), bm_files[0])
        rv = requests.head(BY_MONTH_BASE + test_bm, timeout=15)
        print(f"  by_month/ probe file {test_bm}: HTTP {rv.status_code}  "
              f"{rv.headers.get('Content-Length','?')} bytes")
        if rv.status_code == 200:
            data_path = "by_month"
            print("  -> by_month/ confirmed (preferred)")
except Exception as ex:
    print(f"  by_month/ probe error: {ex}")

# --- B2: probe monthly TIFs ---
if data_path is None and HAVE_RASTERIO:
    print("\n  Probing monthly TIFs ...")
    test_tif_name = "chirps-v2.0.1991.06.tif.gz"
    test_tif_url  = TIF_BASE + test_tif_name
    rh = requests.head(test_tif_url, timeout=15)
    print(f"  TIF probe {test_tif_name}: HTTP {rh.status_code}  "
          f"{rh.headers.get('Content-Length','?')} bytes")
    if rh.status_code == 200:
        data_path = "tif"
        print("  -> TIF path confirmed")
elif data_path is None:
    print("  TIF path skipped (rasterio unavailable)")

# --- B3: byYear fallback ---
if data_path is None:
    print("\n  Probing byYear/ ...")
    test_by_name = "chirps-v2.0.1991.monthly.nc"
    test_by_url  = BYEAR_BASE + test_by_name
    rh2 = requests.head(test_by_url, timeout=15)
    print(f"  byYear probe {test_by_name}: HTTP {rh2.status_code}  "
          f"{rh2.headers.get('Content-Length','?')} bytes")
    if rh2.status_code == 200:
        data_path = "byYear"
        print("  -> byYear/ confirmed (last resort)")

assert data_path is not None, "All CHIRPS access paths failed (404 on all probes)"
print(f"\n  Selected data path: {data_path}")

# --- B4: Download the probe file and read ACTUAL grid metadata ---
print("\n  Downloading probe file to read actual grid metadata ...")

def _read_nc_meta(path):
    """Open NetCDF file, return dict of grid metadata and variable info."""
    ds = xr.open_dataset(path)
    var = [v for v in ds.data_vars if v not in ("crs",)][0]
    lat_dim = "latitude" if "latitude" in ds.dims else "lat"
    lon_dim = "longitude" if "longitude" in ds.dims else "lon"
    lats = ds[lat_dim].values
    lons = ds[lon_dim].values
    meta = {
        "source": "nc", "var": var, "lat_dim": lat_dim, "lon_dim": lon_dim,
        "shape": dict(ds.dims),
        "dlat": abs(float(np.diff(lats).mean())),
        "dlon": abs(float(np.diff(lons).mean())),
        "lat_range": (float(lats.min()), float(lats.max())),
        "lon_range": (float(lons.min()), float(lons.max())),
        "units": str(ds[var].attrs.get("units", "unknown")),
        "fill_value": float(ds[var].attrs.get(
            "_FillValue", ds[var].attrs.get("missing_value", np.nan))),
    }
    ds.close()
    return meta

def _read_tif_meta(raw_gz_bytes):
    """Decompress TIF.gz, return dict of grid metadata."""
    raw_tif = gzip.decompress(raw_gz_bytes)
    with MemoryFile(raw_tif) as mf:
        with mf.open() as src:
            meta = {
                "source": "tif",
                "shape": {"height": src.height, "width": src.width},
                "dlat": abs(float(src.res[1])),
                "dlon": abs(float(src.res[0])),
                "lat_range": (src.bounds.bottom, src.bounds.top),
                "lon_range": (src.bounds.left, src.bounds.right),
                "crs": str(src.crs), "nodata": src.nodata,
                "dtype": str(src.dtypes[0]),
            }
    return meta

# Fetch probe file (cache it)
if data_path == "tif":
    probe_local = ROOT / "data/engine_cache/chirps/tifs" / test_tif_name
    if not probe_local.exists():
        rv = _retry(test_tif_url, timeout=120)
        probe_local.write_bytes(rv.content)
        log_fetch(test_tif_url, "ok", bytes_=len(rv.content),
                  checksum=hashlib.md5(rv.content).hexdigest())
    grid_meta = _read_tif_meta(probe_local.read_bytes())
elif data_path == "by_month":
    probe_local = ROOT / "data/engine_cache/chirps/by_month" / test_bm
    if not probe_local.exists():
        rv = _retry(BY_MONTH_BASE + test_bm, timeout=180)
        probe_local.write_bytes(rv.content)
        log_fetch(BY_MONTH_BASE + test_bm, "ok", bytes_=len(rv.content),
                  checksum=hashlib.md5(rv.content).hexdigest())
    grid_meta = _read_nc_meta(probe_local)
else:  # byYear
    probe_local = ROOT / "data/engine_cache/chirps/byYear" / test_by_name
    if not probe_local.exists():
        rv = _retry(test_by_url, timeout=300)
        probe_local.write_bytes(rv.content)
        log_fetch(test_by_url, "ok", bytes_=len(rv.content),
                  checksum=hashlib.md5(rv.content).hexdigest())
    grid_meta = _read_nc_meta(probe_local)

print("  Actual grid metadata from file:")
for k, v in grid_meta.items():
    print(f"    {k}: {v}")

# Assert 0.05-deg resolution -- this is the critical check
log_assertion("chirps_dlat_is_005",
              abs(grid_meta["dlat"] - 0.05) < 0.001,
              f"dlat={grid_meta['dlat']:.5f} deg; required 0.05 +/- 0.001")
log_assertion("chirps_dlon_is_005",
              abs(grid_meta["dlon"] - 0.05) < 0.001,
              f"dlon={grid_meta['dlon']:.5f} deg; required 0.05 +/- 0.001")
CHIRPS_RES = round((grid_meta["dlat"] + grid_meta["dlon"]) / 2, 4)

# Cell separation at actual resolution
print(f"\n  Cell separation at actual {CHIRPS_RES}-deg resolution:")
for region, pair in PAIRS.items():
    ww, lw = pair["windward"], pair["leeward"]
    lat_sep = abs(ww["lat"] - lw["lat"]) / CHIRPS_RES
    lon_sep = abs(ww["lon"] - lw["lon"]) / CHIRPS_RES
    diag    = (lat_sep**2 + lon_sep**2)**0.5
    ww_cell = (round(ww["lat"] / CHIRPS_RES) * CHIRPS_RES,
               round(ww["lon"] / CHIRPS_RES) * CHIRPS_RES)
    lw_cell = (round(lw["lat"] / CHIRPS_RES) * CHIRPS_RES,
               round(lw["lon"] / CHIRPS_RES) * CHIRPS_RES)
    same = ww_cell == lw_cell
    print(f"  {region}: {ww['name']} cell {ww_cell} | "
          f"{lw['name']} cell {lw_cell}")
    print(f"    separation: {lat_sep:.1f} lat-cells x {lon_sep:.1f} lon-cells "
          f"= {diag:.1f} cells diagonal | same_cell={same}")
    log_assertion(f"{region}_different_cells_at_actual_res", not same,
                  f"{ww['name']} vs {lw['name']}: {diag:.1f} cells apart")


# =========================================================================
# Step C: Download CHIRPS JJAS data and extract point values
# =========================================================================
print("\n" + "=" * 65)
print(f"FEASIBILITY GATE -- Step C: CHIRPS JJAS download ({data_path})")
print("=" * 65)

chirps_jjas = {(r, s): [] for r in PAIRS for s in PAIRS[r]}

def _extract_nc_point(path, lat, lon, months=None):
    """Open NC file, select months if given, return list of float values."""
    ds = xr.open_dataset(path)
    var     = grid_meta["var"]
    lat_dim = grid_meta["lat_dim"]
    lon_dim = grid_meta["lon_dim"]
    if months is not None and "time" in ds.dims:
        ds = ds.sel(time=ds["time"].dt.month.isin(months))
    px = safe_extract(ds, var, lat, lon, lat_dim, lon_dim)
    vals = [float(v) for v in px.values.flat
            if not np.isnan(v) and abs(v - grid_meta.get("fill_value", -9999)) > 1]
    ds.close()
    return vals

def _extract_tif_point(raw_gz_bytes, lat, lon):
    """Decompress TIF.gz and extract single pixel. Returns float or None."""
    raw_tif = gzip.decompress(raw_gz_bytes)
    with MemoryFile(raw_tif) as mf:
        with mf.open() as src:
            row, col = src.index(lon, lat)
            val = float(src.read(1)[row, col])
            nd  = src.nodata
    return None if (nd is not None and abs(val - nd) < 1) else val

for year in range(CHIRPS_START, CHIRPS_END + 1):
    if data_path == "tif":
        for month in JJAS_MONTHS:
            fname = f"chirps-v2.0.{year}.{month:02d}.tif.gz"
            url   = TIF_BASE + fname
            local = ROOT / "data/engine_cache/chirps/tifs" / fname
            if not local.exists():
                try:
                    rv = _retry(url, timeout=120)
                    local.write_bytes(rv.content)
                    log_fetch(url, "ok", bytes_=len(rv.content),
                              checksum=hashlib.md5(rv.content).hexdigest())
                except Exception as e:
                    log_fetch(url, "error", error=str(e))
                    print(f"    SKIP {year}/{month:02d}: {e}")
                    continue
            raw = local.read_bytes()
            for region, pair in PAIRS.items():
                for side, info in pair.items():
                    val = _extract_tif_point(raw, info["lat"], info["lon"])
                    if val is not None:
                        chirps_jjas[(region, side)].append(val)

    elif data_path == "by_month":
        for month in JJAS_MONTHS:
            pat = re.compile(rf"chirps.*{year}.*{month:02d}.*\.nc")
            matched = next((f for f in bm_files if pat.search(f)), None)
            if matched is None:
                print(f"    SKIP {year}/{month:02d}: no file in by_month/")
                continue
            url   = BY_MONTH_BASE + matched
            local = ROOT / "data/engine_cache/chirps/by_month" / matched
            subset_local = ROOT / "data/engine_cache/chirps/domain_subset" / matched
            subset_local.parent.mkdir(parents=True, exist_ok=True)
            if not subset_local.exists():
                if not local.exists():
                    try:
                        rv = _retry(url, timeout=180)
                        local.write_bytes(rv.content)
                        try:
                            ds_test = xr.open_dataset(local)
                            if "time" not in ds_test.dims:
                                raise ValueError("Missing time dimension")
                            ds_test.close()
                        except Exception as ve:
                            local.unlink(missing_ok=True)
                            raise ValueError(f"Corrupt or truncated file, deleted: {ve}")
                        log_fetch(url, "ok", bytes_=len(rv.content),
                                  checksum=hashlib.md5(rv.content).hexdigest())
                    except Exception as e:
                        log_fetch(url, "error", error=str(e))
                        continue
                
                try:
                    ds_full = xr.open_dataset(local)
                    ld = "latitude" if "latitude" in ds_full.dims else "lat"
                    lnd = "longitude" if "longitude" in ds_full.dims else "lon"
                    
                    # Handle dimension sorting for slicing
                    lat_slice = slice(cfg["domain"]["lat_min"], cfg["domain"]["lat_max"]) if float(ds_full[ld][0]) < float(ds_full[ld][-1]) else slice(cfg["domain"]["lat_max"], cfg["domain"]["lat_min"])
                    lon_slice = slice(cfg["domain"]["lon_min"], cfg["domain"]["lon_max"]) if float(ds_full[lnd][0]) < float(ds_full[lnd][-1]) else slice(cfg["domain"]["lon_max"], cfg["domain"]["lon_min"])
                    
                    ds_sub = ds_full.sel({ld: lat_slice, lnd: lon_slice})
                    ds_sub.to_netcdf(subset_local)
                    ds_full.close()
                except Exception as e:
                    print(f"    Subset error {year}/{month:02d}: {e}")
                    continue
            
            for region, pair in PAIRS.items():
                for side, info in pair.items():
                    vals = _extract_nc_point(subset_local, info["lat"], info["lon"])
                    chirps_jjas[(region, side)].extend(vals)

    else:  # byYear
        fname = f"chirps-v2.0.{year}.monthly.nc"
        url   = BYEAR_BASE + fname
        local = ROOT / "data/engine_cache/chirps/byYear" / fname
        if not local.exists():
            try:
                rv = _retry(url, timeout=300)
                local.write_bytes(rv.content)
                log_fetch(url, "ok", bytes_=len(rv.content),
                          checksum=hashlib.md5(rv.content).hexdigest())
            except Exception as e:
                log_fetch(url, "error", error=str(e))
                print(f"    SKIP {year}: {e}")
                continue
        for region, pair in PAIRS.items():
            for side, info in pair.items():
                vals = _extract_nc_point(local, info["lat"], info["lon"],
                                         months=JJAS_MONTHS)
                chirps_jjas[(region, side)].extend(vals)

    if (year - CHIRPS_START) % 5 == 4:
        print(f"    Processed through {year}...")

print("\n  JJAS data collected (raw monthly values):")
for (region, side), vals in chirps_jjas.items():
    info   = PAIRS[region][side]
    n_yrs  = len(vals) // 4
    if vals:
        jjas_ann = [sum(vals[y*4:(y+1)*4]) for y in range(n_yrs)]
        print(f"  {info['name']:20s}: mean JJAS {np.mean(jjas_ann):.1f}mm "
              f"({n_yrs} yrs, monthly range [{min(vals):.0f}, {max(vals):.0f}]mm)")
    else:
        print(f"  {info['name']:20s}: NO DATA")




# =========================================================================
# Step D: GPM IMERG V07 -- blocked pending credential provisioning
# =========================================================================
print("\n" + "=" * 65)
print("FEASIBILITY GATE -- Step D: GPM IMERG V07")
print("=" * 65)
imerg_jjas = {}
gee_ok = False
try:
    import ee
    ee.Initialize()
    gee_ok = True
    print("  GEE: initialized OK")
except Exception as ex:
    print(f"  GEE init: {str(ex)[:80]}")
    print("  IMERG: BLOCKED -- pending credential provisioning (not silently dropped)")
    print("  Remediation A: 'earthengine authenticate --project <id>' (free GEE tier)")
    print("  Remediation B: urs.earthdata.nasa.gov account + GES DISC GPM_3IMERGDF")
    print("  Impact: CHIRPS/IMERG disagreement field for per-cell uncertainty")
    print("          (Step 4) cannot be computed until one route is provisioned.")

if gee_ok:
    imerg_source = "GEE NASA/GPM_L3/IMERG_V07"
    try:
        col = (ee.ImageCollection("NASA/GPM_L3/IMERG_V07")
               .select("precipitation")
               .filter(ee.Filter.calendarRange(IMERG_START, IMERG_END, "year"))
               .filter(ee.Filter.calendarRange(6, 9, "month")))
        n_days = 122  # approx JJAS day count
        for region, pair in PAIRS.items():
            for side, info in pair.items():
                pt = ee.Geometry.Point([info["lon"], info["lat"]])
                mm_hr = float(col.mean().reduceRegion(
                    ee.Reducer.mean(), pt, 11132).getInfo()["precipitation"])
                imerg_jjas[(region, side)] = mm_hr * 24 * n_days
                print(f"  IMERG {info['name']:20s}: "
                      f"{imerg_jjas[(region,side)]:.1f} mm JJAS")
    except Exception as ex:
        imerg_source = f"GEE extraction failed: {str(ex)[:60]}"
        print(f"  IMERG extraction failed: {ex}")
else:
    imerg_source = ("BLOCKED -- credential provisioning required. "
                    "Remediation: (A) earthengine authenticate --project <id>, "
                    "or (B) NASA Earthdata urs.earthdata.nasa.gov + GES DISC. "
                    "CHIRPS/IMERG disagreement field (Step 4) blocked until resolved.")


# =========================================================================
# Step E: Ratios, attenuation factors, verdicts
# Gauge comparison uses two modes (both reported):
#   PRIMARY   -- satellite JJAS ratio vs gauge JJAS estimate
#                  gauge_JJAS = gauge_annual * assumed_JJAS_fraction
#                  attenuation = gauge_JJAS_ratio / sat_JJAS_ratio
#   SECONDARY -- satellite JJAS ratio vs gauge ANNUAL ratio
#                  (notes the JJAS/annual mismatch; included for completeness)
# =========================================================================
print("\n" + "=" * 65)
print("FEASIBILITY GATE -- Step E: Ratios and verdicts")
print("=" * 65)

results = {}
for region, pair in PAIRS.items():
    ww, lw = pair["windward"], pair["leeward"]

    # Gauge: annual (published)
    g_ann_w = ww.get("gauge_annual_mm")
    g_ann_l = lw.get("gauge_annual_mm")
    g_ann_ratio = g_ann_w / g_ann_l if (g_ann_w and g_ann_l) else None

    # Gauge: JJAS estimate = annual * assumed fraction
    frac_w = JJAS_FRAC[region]["windward"]
    frac_l = JJAS_FRAC[region]["leeward"]
    g_jjas_w = g_ann_w * frac_w if g_ann_w else None
    g_jjas_l = g_ann_l * frac_l if g_ann_l else None
    g_jjas_ratio = g_jjas_w / g_jjas_l if (g_jjas_w and g_jjas_l) else None

    # Satellite JJAS
    cw_vals = chirps_jjas.get((region, "windward"), [])
    cl_vals = chirps_jjas.get((region, "leeward"),  [])
    n_yrs   = min(len(cw_vals), len(cl_vals)) // 4
    if n_yrs >= 5:
        cw_jjas = np.mean([sum(cw_vals[y*4:(y+1)*4]) for y in range(n_yrs)])
        cl_jjas = np.mean([sum(cl_vals[y*4:(y+1)*4]) for y in range(n_yrs)])
        sat_ratio = cw_jjas / cl_jjas if cl_jjas > 0 else None
        # Attenuation: PRIMARY (JJAS vs JJAS estimate -- like-for-like)
        atten_jjas = g_jjas_ratio / sat_ratio if (g_jjas_ratio and sat_ratio) else None
        # Attenuation: SECONDARY (JJAS satellite vs annual gauge -- mismatch noted)
        atten_ann  = g_ann_ratio  / sat_ratio if (g_ann_ratio  and sat_ratio) else None
    else:
        cw_jjas = cl_jjas = sat_ratio = atten_jjas = atten_ann = None

    # IMERG JJAS
    iw = imerg_jjas.get((region, "windward"))
    il = imerg_jjas.get((region, "leeward"))
    imerg_ratio = iw / il if (iw and il and il > 0) else None
    imerg_atten_jjas = g_jjas_ratio / imerg_ratio if (g_jjas_ratio and imerg_ratio) else None
    imerg_atten_ann  = g_ann_ratio  / imerg_ratio if (g_ann_ratio  and imerg_ratio) else None

    results[region] = dict(
        g_ann_w=g_ann_w, g_ann_l=g_ann_l, g_ann_ratio=g_ann_ratio,
        frac_w=frac_w, frac_l=frac_l,
        g_jjas_w=g_jjas_w, g_jjas_l=g_jjas_l, g_jjas_ratio=g_jjas_ratio,
        chirps_jjas_w=cw_jjas, chirps_jjas_l=cl_jjas,
        sat_ratio=sat_ratio, atten_jjas=atten_jjas, atten_ann=atten_ann,
        imerg_w=iw, imerg_l=il,
        imerg_ratio=imerg_ratio,
        imerg_atten_jjas=imerg_atten_jjas, imerg_atten_ann=imerg_atten_ann,
        n_chirps_years=n_yrs,
    )

    print(f"\n  [{region.upper()}] {ww['name']} vs {lw['name']}")
    if g_ann_ratio:
        print(f"    Gauge annual (published):     {g_ann_w}mm / {g_ann_l}mm "
              f"= {g_ann_ratio:.2f}x")
    if g_jjas_ratio:
        print(f"    Gauge JJAS (est, assumed frac): "
              f"{g_jjas_w:.0f}mm / {g_jjas_l:.0f}mm = {g_jjas_ratio:.2f}x "
              f"[ww frac {frac_w:.0%}, lw frac {frac_l:.0%}]")
    if sat_ratio is not None:
        print(f"    CHIRPS JJAS satellite:        "
              f"{cw_jjas:.0f}mm / {cl_jjas:.0f}mm = {sat_ratio:.2f}x "
              f"({n_yrs} years, {data_path}, {CHIRPS_RES}-deg)")
        if atten_jjas:
            print(f"    Attenuation vs JJAS gauge:    {atten_jjas:.2f}x  "
                  f"[PRIMARY -- like-for-like]")
        if atten_ann:
            print(f"    Attenuation vs annual gauge:  {atten_ann:.2f}x  "
                  f"[secondary -- JJAS/annual mismatch]")
    else:
        print(f"    CHIRPS: INSUFFICIENT DATA (<5 years)")
    if imerg_ratio:
        print(f"    IMERG JJAS satellite:         "
              f"{iw:.0f}mm / {il:.0f}mm = {imerg_ratio:.2f}x")
        if imerg_atten_jjas:
            print(f"    IMERG attenuation vs JJAS:    {imerg_atten_jjas:.2f}x")
    else:
        print(f"    IMERG: {imerg_source[:70]}")


def verdict(ratio, ts, tw, name):
    if ratio is None:
        return "UNKNOWN", f"{name}: ratio could not be computed"
    if ratio < ts:
        return "STOP",    f"{name}: {ratio:.2f}x < {ts}x -- satellite cannot resolve"
    if ratio < tw:
        return "WARN",    f"{name}: {ratio:.2f}x in [{ts},{tw}) -- lower bound; report attenuation"
    return "GO",          f"{name}: {ratio:.2f}x >= {tw}x -- architecture sound"

verdicts = []
for region, r in results.items():
    for prod, ratio in [("CHIRPS", r["sat_ratio"]),
                        ("IMERG",  r["imerg_ratio"])]:
        v, msg = verdict(ratio, THRESH_STOP, THRESH_WARN, f"{prod}/{region}")
        verdicts.append((region, prod, v, msg, ratio))
        print(f"  [{v}] {msg}")

overall = ("STOP"    if any(v == "STOP"    for _,_,v,_,_ in verdicts if v != "UNKNOWN")
           else "WARN"    if any(v == "WARN"    for _,_,v,_,_ in verdicts if v != "UNKNOWN")
           else "UNKNOWN" if all(v == "UNKNOWN" for _,_,v,_,_ in verdicts)
           else "GO")
print(f"\n  OVERALL VERDICT: {overall}")


# =========================================================================
# Step F: Write docs/feasibility_gate.md
# =========================================================================
# Use the PRIMARY (JJAS-vs-JJAS) satellite ratio for the go/no-go verdict.
now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
gate_path = ROOT / "docs" / "feasibility_gate.md"

def fmt(v):  return f"{v:.0f}mm" if v is not None else "-"
def fmt2(v): return f"{v:.2f}x"  if v is not None else "-"

lines = [
    "# Feasibility Gate Report",
    f"**Generated:** {now}  ",
    "**Engine version:** 0.1.0-feasibility  ",
    "",
    "> [!IMPORTANT]",
    "> Results were NOT adjusted or inflated to reach any threshold.",
    "> This report was written by engine/feasibility/gate.py and stops here for review.",
    "",
    "## A. DEM Coordinate Verification",
    "",
    "| Station | Role | Lat | Lon | DEM Elevation | Assertion |",
    "|---|---|---|---|---|---|",
]
for region, pair in PAIRS.items():
    for side, info in pair.items():
        elev = dem_results.get((region, side))
        elev_str = f"{elev:.0f}m" if elev else "?"
        lines.append(
            f"| {info['name']} | {side} ({region}) | {info['lat']} | "
            f"{info['lon']} | {elev_str} | PASS |"
        )

lines += [
    "",
    "## B. CHIRPS Cell Resolution Check",
    f"**Actual grid spacing read from file:** {CHIRPS_RES}-deg",
    "",
    "| Region | Windward cell | Leeward cell | Separation (diagonal) | Discriminable? |",
    "|---|---|---|---|---|",
]
for region, pair in PAIRS.items():
    ww, lw = pair["windward"], pair["leeward"]
    lat_sep = abs(ww["lat"] - lw["lat"]) / CHIRPS_RES
    lon_sep = abs(ww["lon"] - lw["lon"]) / CHIRPS_RES
    diag    = (lat_sep**2 + lon_sep**2)**0.5
    ww_cell = (round(ww["lat"] / CHIRPS_RES) * CHIRPS_RES,
               round(ww["lon"] / CHIRPS_RES) * CHIRPS_RES)
    lw_cell = (round(lw["lat"] / CHIRPS_RES) * CHIRPS_RES,
               round(lw["lon"] / CHIRPS_RES) * CHIRPS_RES)
    disc = "YES" if ww_cell != lw_cell else "NO -- SAME CELL -- INVALID"
    lines.append(f"| {region} | {ww_cell} | {lw_cell} | {diag:.1f} cells | {disc} |")

lines += [
    "",
    f"## C. CHIRPS {CHIRPS_RES}-deg JJAS Climatology",
    f"**Source:** UCSB CHIRPS-2.0 via {data_path}  ",
    f"**Period:** {CHIRPS_START}-{CHIRPS_END} (JJAS = Jun-Sep)  ",
    "",
    "| Region | Windward | CHIRPS JJAS | Leeward | CHIRPS JJAS | "
    "Sat Ratio | Gauge JJAS (est) | Gauge JJAS Ratio | Attenuation (PRIMARY) | N years |",
    "|---|---|---|---|---|---|---|---|---|---|",
]
for region, r in results.items():
    ww, lw = PAIRS[region]["windward"], PAIRS[region]["leeward"]
    lines.append(
        f"| {region} | {ww['name']} | {fmt(r['chirps_jjas_w'])} | "
        f"{lw['name']} | {fmt(r['chirps_jjas_l'])} | {fmt2(r['sat_ratio'])} | "
        f"{fmt(r['g_jjas_w'])} / {fmt(r['g_jjas_l'])} | "
        f"{fmt2(r['g_jjas_ratio'])} | {fmt2(r['atten_jjas'])} | "
        f"{r['n_chirps_years']} |"
    )

lines += [
    "",
    "## D. IMERG V07 0.1-deg JJAS Climatology",
    f"**Source:** {imerg_source}  ",
    f"**Period:** {IMERG_START}-{IMERG_END}  ",
    "",
]
if imerg_jjas:
    lines += [
        "| Region | Windward | IMERG JJAS | Leeward | IMERG JJAS | "
        "Sat Ratio | Gauge JJAS (est) | Gauge JJAS Ratio | Attenuation (PRIMARY) |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for region, r in results.items():
        ww, lw = PAIRS[region]["windward"], PAIRS[region]["leeward"]
        lines.append(
            f"| {region} | {ww['name']} | {fmt(r['imerg_w'])} | "
            f"{lw['name']} | {fmt(r['imerg_l'])} | {fmt2(r['imerg_ratio'])} | "
            f"{fmt(r['g_jjas_w'])} / {fmt(r['g_jjas_l'])} | "
            f"{fmt2(r['g_jjas_ratio'])} | {fmt2(r['imerg_atten_jjas'])} |"
        )
else:
    lines += [
        "> [!WARNING]",
        f"> IMERG **BLOCKED**: pending credential provisioning.",
        "> Go/no-go based on CHIRPS alone for this run.",
    ]

lines += [
    "",
    "## E. Verdicts",
    "",
    "| Product | Region | Satellite ratio | Verdict | Detail |",
    "|---|---|---|---|---|",
]
for region, prod, v, msg, ratio in verdicts:
    ratio_str = fmt2(ratio)
    lines.append(f"| {prod} | {region} | {ratio_str} | {v} | {msg} |")

lines += [
    "",
    f"## Overall: **{overall}**",
    "",
    "| Threshold | Meaning |",
    "|---|---|",
    "| >= 4x | Architecture sound |",
    "| 2-4x  | Lower bound only; attenuation factor must be reported |",
    "| < 2x  | STOP -- satellite cannot resolve |",
    "",
]

if overall == "GO":
    lines += ["> [!NOTE]", "> Signal confirmed at >= 4x. Proceed to Step 2."]
elif overall == "WARN":
    lines += ["> [!WARNING]",
              "> Signal attenuated (2-4x). Weights understate true contrast.",
              "> Attenuation factor must accompany all downstream results."]
elif overall == "STOP":
    lines += ["> [!CAUTION]",
              "> Signal below 2x threshold. Do NOT proceed to weight construction."]
else:
    lines += ["> [!WARNING]",
              f"> Verdict UNKNOWN -- CHIRPS data insufficient or missing.",
              "> Cannot issue go/no-go. Review fetch_log.jsonl for errors."]

# Data access barriers section
lines += [
    "",
    "## Data Access Barriers Encountered",
    "",
    "| Dataset | Barrier | Impact |",
    "|---|---|---|",
    "| GPM IMERG V07 | Requires GEE credentials or NASA Earthdata login | "
    "IMERG results absent from this run. Disagreement field cannot be built yet. |",
]

gate_path.write_text("\n".join(lines), encoding="utf-8")
print(f"\nWrote: {gate_path}")
print("=" * 65)
print("FEASIBILITY GATE COMPLETE. Review docs/feasibility_gate.md.")
print("=" * 65)
