"""
rebuild_village_corrections.py
==============================
Provenance & Audit Trace:
- Original Provenance: Created in agent scratch directory (scratch/rebuild_village_corrections.py)
  during Item I4 to replace retired out-of-window 2020 diurnal snapshot (MD5 42157952...) with
  authentic in-window 2017-07-15 & 2018-04-30 true 24-hr daily extremes (B42-B44).
- Scratch Original Checksum: MD5 766577a988b226b7c3e069bd873eb37c (Size: 4,116 bytes).
- Path Normalisation Edit (Item J2b-10): Adjusted input/output paths to resolve both
  relative to repo root (outputs/village_corrections.csv) and parent workspace paths.
- Authoritative Output Checksum: Produces outputs/village_corrections.csv with
  MD5: 52b119f0b4f2441592f2d3af866eef3f
  SHA-256: 0c0748815cb9e9005e06a2063c14b7bbc27bbd9e4caad48874f57e8d4b236f2f
"""
import numpy as np
import pandas as pd
import math
import hashlib
import pathlib

csv_path = pathlib.Path("outputs/village_corrections.csv") if pathlib.Path("outputs/village_corrections.csv").exists() else pathlib.Path("sih074-downscale-poc/outputs/village_corrections.csv")
df = pd.read_csv(csv_path, low_memory=False)

npz_path = pathlib.Path("data/cache/in_window_daily_extremes.npz") if pathlib.Path("data/cache/in_window_daily_extremes.npz").exists() else pathlib.Path("sih074-downscale-poc/data/cache/in_window_daily_extremes.npz")
npz = np.load(npz_path)
prem_tmax = npz['prem_tmax']
prem_tmin = npz['prem_tmin']
prem_tmean = npz['prem_tmean']

jjas_tmax = npz['jjas_tmax']
jjas_tmin = npz['jjas_tmin']
jjas_tmean = npz['jjas_tmean']

def calc_ra(lat_rad, doy):
    Gsc = 0.0820
    dr = 1 + 0.033 * math.cos(2 * math.pi * doy / 365)
    delta = 0.409 * math.sin((2 * math.pi * doy / 365) - 1.39)
    tan_val = max(-1.0, min(1.0, -math.tan(lat_rad) * math.tan(delta)))
    ws = math.acos(tan_val)
    ra = (24 * 60 / math.pi) * Gsc * dr * (ws * math.sin(lat_rad) * math.sin(delta) + math.cos(lat_rad) * math.cos(delta) * math.sin(ws))
    return ra

def calc_eto_hs(t_max_c, t_min_c, t_mean_c, ra_mj):
    tr = max(t_max_c - t_min_c, 0.0)
    return 0.0023 * 0.408 * ra_mj * math.sqrt(tr) * (t_mean_c + 17.8)

doy_prem = 120 # 2018-04-30
doy_jjas = 196 # 2017-07-15

new_prem_tmax = []
new_prem_tmin = []
new_prem_tmean = []
new_prem_eto = []
new_prem_heat = []
new_prem_irrig = []

new_jjas_tmax = []
new_jjas_tmin = []
new_jjas_tmean = []
new_jjas_eto = []
new_jjas_heat = []
new_jjas_irrig = []

for idx, r in df.iterrows():
    i = int(r['node_i'])
    j = int(r['node_j'])
    lat_rad = math.radians(r['centroid_lat'])
    dt = r['dt_era5_c']
    
    # 1. In-window Pre-monsoon: 2018-04-30
    ra_p = calc_ra(lat_rad, doy_prem)
    t_f_max_p = prem_tmax[i, j] + dt
    t_f_min_p = prem_tmin[i, j] + dt
    t_f_mean_p = prem_tmean[i, j] + dt
    eto_p = calc_eto_hs(t_f_max_p, t_f_min_p, t_f_mean_p, ra_p)
    
    heat_p = int(t_f_max_p >= 35.0)
    irrig_p = int(eto_p > 5.0)
    
    new_prem_tmax.append(round(float(t_f_max_p), 2))
    new_prem_tmin.append(round(float(t_f_min_p), 2))
    new_prem_tmean.append(round(float(t_f_mean_p), 2))
    new_prem_eto.append(round(float(eto_p), 2))
    new_prem_heat.append(heat_p)
    new_prem_irrig.append(irrig_p)
    
    # 2. In-window Monsoon: 2017-07-15
    ra_j = calc_ra(lat_rad, doy_jjas)
    t_f_max_j = jjas_tmax[i, j] + dt
    t_f_min_j = jjas_tmin[i, j] + dt
    t_f_mean_j = jjas_tmean[i, j] + dt
    eto_j = calc_eto_hs(t_f_max_j, t_f_min_j, t_f_mean_j, ra_j)
    
    heat_j = int(t_f_max_j >= 35.0)
    irrig_j = int(eto_j > 5.0)
    
    new_jjas_tmax.append(round(float(t_f_max_j), 2))
    new_jjas_tmin.append(round(float(t_f_min_j), 2))
    new_jjas_tmean.append(round(float(t_f_mean_j), 2))
    new_jjas_eto.append(round(float(eto_j), 2))
    new_jjas_heat.append(heat_j)
    new_jjas_irrig.append(irrig_j)

df['real_prem_tmax_c'] = new_prem_tmax
df['real_prem_tmin_c'] = new_prem_tmin
df['real_prem_tmean_c'] = new_prem_tmean
df['real_prem_eto_mm_day'] = new_prem_eto
df['real_prem_heat_stress'] = new_prem_heat
df['real_prem_irrig_demand'] = new_prem_irrig

df['real_jjas_tmax_c'] = new_jjas_tmax
df['real_jjas_tmin_c'] = new_jjas_tmin
df['real_jjas_tmean_c'] = new_jjas_tmean
df['real_jjas_eto_mm_day'] = new_jjas_eto
df['real_jjas_heat_stress'] = new_jjas_heat
df['real_jjas_irrig_demand'] = new_jjas_irrig

# Save updated dataframe
df.to_csv(csv_path, index=False)

with open(csv_path, "rb") as f:
    new_md5 = hashlib.md5(f.read()).hexdigest()

print("=== REBUILD COMPLETED SUCCESSFULLY ===")
print(f"Target: {csv_path}")
print(f"Total Rows: {len(df)}")
print(f"Total Columns: {len(df.columns)}")
print(f"New MD5 Checksum: {new_md5}")
print(f"Pre-monsoon (2018-04-30):")
print(f"  Heat Stress Triggers (Tmax >= 35.0 C): {sum(new_prem_heat)} / {len(df)} ({sum(new_prem_heat)/len(df)*100:.2f}%)")
print(f"  High Irrigation Demand (ETo > 5.0 mm/d): {sum(new_prem_irrig)} / {len(df)} ({sum(new_prem_irrig)/len(df)*100:.2f}%)")
print(f"Monsoon (2017-07-15):")
print(f"  Heat Stress Triggers (Tmax >= 35.0 C): {sum(new_jjas_heat)} / {len(df)} ({sum(new_jjas_heat)/len(df)*100:.2f}%)")
print(f"  High Irrigation Demand (ETo > 5.0 mm/d): {sum(new_jjas_irrig)} / {len(df)} ({sum(new_jjas_irrig)/len(df)*100:.2f}%)")
