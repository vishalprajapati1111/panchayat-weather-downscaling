import sys

raise SystemExit(
    "ERROR: update_village_corrections_final.py is SUPERSEDED and REFUSES TO EXECUTE.\n"
    "This script generates the retired CSV checksum (MD5 42157952f3441d1ce6fb06910c032c6b)\n"
    "using an outdated 2020 single-slice and midpoint diurnal mean.\n"
    "Execution is permanently halted to protect authoritative output data.\n"
    "To regenerate the authoritative CSV (MD5 52b119f0b4f2441592f2d3af866eef3f),\n"
    "run: python rebuild_village_corrections.py"
)

import json, pathlib, math, hashlib
import numpy as np
import pandas as pd

grids = np.load("data/cache/node_orography_grids.npz")
lats = grids['lats']
lons = grids['lons']
z_era5 = grids['z_era5']
srtm_node_grid = grids['srtm_node_grid']

# Real temperature arrays
diurnal = np.load("data/cache/real_diurnal_temperatures.npz")
t_jjas_max = diurnal['t_jjas_max']
t_jjas_min = diurnal['t_jjas_min']
t_prem_max = diurnal['t_prem_max']
t_prem_min = diurnal['t_prem_min']

d2m_cache = np.load("data/cache/d2m_grid.npz")
d2m_grid = d2m_cache['d2m']

with open("data/cache/signed_village_results.json", "r", encoding="utf-8") as f:
    results = json.load(f)

geojson_dir = pathlib.Path("data/cache/geojson")
files_data = {}
for name in ["ga.geojson", "ka.geojson", "mh1.geojson", "mh2.geojson"]:
    with open(geojson_dir / name, "r", encoding="utf-8", errors="replace") as f:
        files_data[name] = json.load(f)

def get_flat(coords):
    if isinstance(coords[0], list): return [v for sub in coords for v in get_flat(sub)]
    return [coords]

def calc_ra(lat_rad, doy):
    Gsc = 0.0820
    dr = 1 + 0.033 * math.cos(2 * math.pi * doy / 365)
    delta = 0.409 * math.sin((2 * math.pi * doy / 365) - 1.39)
    tan_val = max(-1.0, min(1.0, -math.tan(lat_rad) * math.tan(delta)))
    ws = math.acos(tan_val)
    ra = (24 * 60 / math.pi) * Gsc * dr * (ws * math.sin(lat_rad) * math.sin(delta) + math.cos(lat_rad) * math.cos(delta) * math.sin(ws))
    return ra

def poly_area(coords):
    if len(coords) < 3: return 0.0
    lons_p = [c[0] for c in coords]
    lats_p = [c[1] for c in coords]
    lat_rad = np.radians(np.mean(lats_p))
    x = [np.radians(lon) * 6371000.0 * np.cos(lat_rad) for lon in lons_p]
    y = [np.radians(lat) * 6371000.0 for lat in lats_p]
    return 0.5 * abs(sum(x[i]*y[i+1] - x[i+1]*y[i] for i in range(len(x)-1)))

def calc_eto_hs(t_max_c, t_min_c, t_mean_c, ra_mj):
    tr = max(t_max_c - t_min_c, 0.0)
    return 0.0023 * 0.408 * ra_mj * math.sqrt(tr) * (t_mean_c + 17.8)

# Code extraction with Karnataka census_code set to 'unavailable'
# and state_loc_code preserving LOC_CODE
first_pass = []
census_code_counts = {}

for r in results:
    src = r['src_file']
    idx = r['idx']
    feat = files_data[src]['features'][idx]
    props = feat.get('properties', {})
    
    district = props.get('DISTRICT') or props.get('DIST_NAME') or 'unavailable'
    taluka = props.get('SUB_DIST') or props.get('TALUK') or props.get('TALUKA_NAM') or 'unavailable'
    
    if src in ['mh1.geojson', 'mh2.geojson', 'ga.geojson']:
        c_code = props.get('CEN_2001')
        if c_code is None or str(c_code).strip() in ['', 'None', '0']:
            census_code = 'unavailable'
        else:
            census_code = str(c_code).strip()
            census_code_counts[census_code] = census_code_counts.get(census_code, 0) + 1
        state_loc_code = census_code
    elif src == 'ka.geojson':
        # B38: Karnataka codes are NOT Census codes (internal state survey codes)
        census_code = 'unavailable'
        loc = props.get('LOC_CODE') or props.get('V_CT_CODE')
        state_loc_code = str(loc).strip() if loc else 'unavailable'
        
    first_pass.append((census_code, state_loc_code, district, taluka))

doy_jjas = 196
doy_prem = 120
records = []
count_exact_zero_dz = 0
count_near_zero_dz = 0

for idx, r in enumerate(results):
    census_code, state_loc_code, district, taluka = first_pass[idx]
    src = r['src_file']
    f_idx = r['idx']
    feat = files_data[src]['features'][f_idx]
    coords = feat['geometry']['coordinates']
    
    if feat['geometry']['type'] == 'Polygon': area_m2 = poly_area(coords[0])
    elif feat['geometry']['type'] == 'MultiPolygon': area_m2 = sum(poly_area(p[0]) for p in coords)
    else: area_m2 = 1.0
    poly_area_km2 = round(area_m2 / 1e6, 4)
    
    pts = get_flat(coords)
    lon_c = float(np.mean([p[0] for p in pts]))
    lat_c = float(np.mean([p[1] for p in pts]))
    
    i = int(np.argmin(np.abs(lats - lat_c)))
    j = int(np.argmin(np.abs(lons - lon_c)))
    
    node_lat = float(lats[i])
    node_lon = float(lons[j])
    
    fine_elev = float(r['elev_fine'])
    era5_elev = float(z_era5[i, j])
    srtm_elev = float(srtm_node_grid[i, j])
    
    raw_dz = fine_elev - era5_elev
    if raw_dz == 0.0: count_exact_zero_dz += 1
    if abs(raw_dz) < 0.05: count_near_zero_dz += 1
    
    dz_era5 = raw_dz
    dt_era5 = -dz_era5 * 0.0065
    
    dz_srtm = fine_elev - srtm_elev
    dt_srtm = -dz_srtm * 0.0065
    
    is_material = abs(dz_era5) >= 150.0
    materiality = "MATERIAL" if is_material else "SUB-THRESHOLD"
    
    if dz_era5 > 0: direction = "COOLING"
    elif dz_era5 < 0: direction = "WARMING"
    else: direction = "NEUTRAL"
    
    all_lons = [p[0] for p in pts]
    all_lats = [p[1] for p in pts]
    wholly_inside = (min(all_lats) >= node_lat - 0.125 and max(all_lats) <= node_lat + 0.125 and
                     min(all_lons) >= node_lon - 0.125 and max(all_lons) <= node_lon + 0.125)
    multi_cell_flag = not wholly_inside
    duplicate_code_flag = (census_code != 'unavailable' and census_code_counts.get(census_code, 0) > 1)
    
    # Real WeatherBench-2 temperatures
    # 1. Monsoon
    t_c_max_jjas = float(t_jjas_max[i, j])
    t_c_min_jjas = float(t_jjas_min[i, j])
    t_c_mean_jjas = 0.5 * (t_c_max_jjas + t_c_min_jjas)
    
    t_fine_max_jjas = t_c_max_jjas + dt_era5
    t_fine_min_jjas = t_c_min_jjas + dt_era5
    t_fine_mean_jjas = t_c_mean_jjas + dt_era5
    
    # Single marked K -> C site (coarse was converted on extraction):
    # Confirm unit range: values are in Celsius.
    
    # 2. Pre-monsoon
    t_c_max_prem = float(t_prem_max[i, j])
    t_c_min_prem = float(t_prem_min[i, j])
    t_c_mean_prem = 0.5 * (t_c_max_prem + t_c_min_prem)
    
    t_fine_max_prem = t_c_max_prem + dt_era5
    t_fine_min_prem = t_c_min_prem + dt_era5
    t_fine_mean_prem = t_c_mean_prem + dt_era5
    
    # Real Dewpoint
    d_c = float(d2m_grid[i, j]) - 273.15 # MARKED K->°C SITE
    e = 0.61078 * math.exp(17.27 * d_c / (d_c + 237.3))
    es = 0.61078 * math.exp(17.27 * t_fine_mean_jjas / (t_fine_mean_jjas + 237.3))
    rh_raw = (e / es) * 100.0
    rh_clamped = rh_raw > 100.0
    rh_final = min(rh_raw, 100.0)
    
    # Real ETo (Hargreaves-Samani)
    lat_rad = math.radians(lat_c)
    ra_jjas = calc_ra(lat_rad, doy_jjas)
    ra_prem = calc_ra(lat_rad, doy_prem)
    
    eto_jjas = calc_eto_hs(t_fine_max_jjas, t_fine_min_jjas, t_fine_mean_jjas, ra_jjas)
    eto_prem = calc_eto_hs(t_fine_max_prem, t_fine_min_prem, t_fine_mean_prem, ra_prem)
    
    heat_stress_jjas = t_fine_max_jjas >= 35.0
    irrig_demand_jjas = eto_jjas > 5.0
    
    heat_stress_prem = t_fine_max_prem >= 35.0
    irrig_demand_prem = eto_prem > 5.0
    
    v_name = r['name'] if r['name'] else f"[Unnamed code:{state_loc_code}]"
    
    records.append({
        'village_id': f"{src}:{f_idx}",
        'src_file': src,
        'feature_idx': f_idx,
        'village_name': v_name,
        'state': r['state'],
        'district': district,
        'taluka': taluka,
        'census_code': census_code,
        'state_loc_code': state_loc_code,
        'polygon_area_km2': poly_area_km2,
        'multi_cell_flag': int(multi_cell_flag),
        'duplicate_code_flag': int(duplicate_code_flag),
        'centroid_lat': round(lat_c, 5),
        'centroid_lon': round(lon_c, 5),
        'node_lat': round(node_lat, 2),
        'node_lon': round(node_lon, 2),
        'node_i': i,
        'node_j': j,
        'fine_elev_m': round(fine_elev, 1),
        'era5_elev_m': round(era5_elev, 1),
        'srtm_node_elev_m': round(srtm_elev, 1),
        'dz_era5_m': round(dz_era5, 1),
        'dt_era5_c': round(dt_era5, 2),
        'direction': direction,
        'materiality': materiality,
        'dz_srtm_m': round(dz_srtm, 1),
        'dt_srtm_c': round(dt_srtm, 2),
        'real_jjas_tmax_c': round(t_fine_max_jjas, 2),
        'real_jjas_tmin_c': round(t_fine_min_jjas, 2),
        'real_jjas_tmean_c': round(t_fine_mean_jjas, 2),
        'real_jjas_eto_mm_day': round(eto_jjas, 2),
        'real_jjas_heat_stress': int(heat_stress_jjas),
        'real_jjas_irrig_demand': int(irrig_demand_jjas),
        'real_prem_tmax_c': round(t_fine_max_prem, 2),
        'real_prem_tmin_c': round(t_fine_min_prem, 2),
        'real_prem_tmean_c': round(t_fine_mean_prem, 2),
        'real_prem_eto_mm_day': round(eto_prem, 2),
        'real_prem_heat_stress': int(heat_stress_prem),
        'real_prem_irrig_demand': int(irrig_demand_prem),
        'rh_downscaled_pct': round(rh_final, 1),
        'rh_clamped_flag': int(rh_clamped),
        'wind_block_status': 'SOURCED — SOURCED FROM ARCO ERA5 10M WIND',
        'wind_tpi_status': 'ESTIMATED — NO SOURCE'
    })

df_final = pd.DataFrame(records)
csv_path = pathlib.Path("outputs/village_corrections.csv")
df_final.to_csv(csv_path, index=False)

with open(csv_path, "rb") as f:
    final_md5 = hashlib.md5(f.read()).hexdigest()

print("=== FINAL REPAIRED CSV SUMMARY ===")
print(f"File: {csv_path}")
print(f"Rows: {len(df_final)}, Columns: {len(df_final.columns)}")
print(f"MD5 Checksum: {final_md5}")
print(f"Exact dz == 0 count: {count_exact_zero_dz}")
print(f"Near zero dz (<0.05m) count: {count_near_zero_dz}")
print(f"Karnataka genuine census_code == 'unavailable': {(df_final[df_final['state']=='KA']['census_code'] == 'unavailable').sum()} / {(df_final['state']=='KA').sum()}")
