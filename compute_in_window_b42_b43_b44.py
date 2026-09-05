import numpy as np, pandas as pd, math

# Load in-window daily extremes
data = np.load("data/cache/in_window_daily_extremes.npz")
lats = data['lats']
lons = data['lons']
jjas_tmax = data['jjas_tmax']
jjas_tmin = data['jjas_tmin']
jjas_tmean = data['jjas_tmean']

prem_tmax = data['prem_tmax']
prem_tmin = data['prem_tmin']
prem_tmean = data['prem_tmean']

df = pd.read_csv("outputs/village_corrections.csv", low_memory=False)

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

# 1. Monsoon: 2017-07-15 (DOY 196)
doy_jjas = 196
jjas_heat_triggers = 0
jjas_irrig_triggers = 0
jjas_eto_list = []
jjas_coarse_eto_list = []
jjas_tmax_fine_list = []

for idx, r in df.iterrows():
    i = int(r['node_i'])
    j = int(r['node_j'])
    lat_rad = math.radians(r['centroid_lat'])
    ra = calc_ra(lat_rad, doy_jjas)
    
    t_c_max = jjas_tmax[i, j]
    t_c_min = jjas_tmin[i, j]
    t_c_mean = jjas_tmean[i, j]
    
    t_f_max = t_c_max + r['dt_era5_c']
    t_f_min = t_c_min + r['dt_era5_c']
    t_f_mean = t_c_mean + r['dt_era5_c']
    
    eto_c = calc_eto_hs(t_c_max, t_c_min, t_c_mean, ra)
    eto_f = calc_eto_hs(t_f_max, t_f_min, t_f_mean, ra)
    
    jjas_coarse_eto_list.append(eto_c)
    jjas_eto_list.append(eto_f)
    jjas_tmax_fine_list.append(t_f_max)
    
    if t_f_max >= 35.0: jjas_heat_triggers += 1
    if eto_f > 5.0: jjas_irrig_triggers += 1

# 2. Pre-Monsoon: 2018-04-30 (DOY 120)
doy_prem = 120
prem_heat_triggers = 0
prem_irrig_triggers = 0
prem_eto_list = []
prem_coarse_eto_list = []
prem_tmax_fine_list = []

for idx, r in df.iterrows():
    i = int(r['node_i'])
    j = int(r['node_j'])
    lat_rad = math.radians(r['centroid_lat'])
    ra = calc_ra(lat_rad, doy_prem)
    
    t_c_max = prem_tmax[i, j]
    t_c_min = prem_tmin[i, j]
    t_c_mean = prem_tmean[i, j]
    
    t_f_max = t_c_max + r['dt_era5_c']
    t_f_min = t_c_min + r['dt_era5_c']
    t_f_mean = t_c_mean + r['dt_era5_c']
    
    eto_c = calc_eto_hs(t_c_max, t_c_min, t_c_mean, ra)
    eto_f = calc_eto_hs(t_f_max, t_f_min, t_f_mean, ra)
    
    prem_coarse_eto_list.append(eto_c)
    prem_eto_list.append(eto_f)
    prem_tmax_fine_list.append(t_f_max)
    
    if t_f_max >= 35.0: prem_heat_triggers += 1
    if eto_f > 5.0: prem_irrig_triggers += 1

df['in_window_jjas_tmax'] = jjas_tmax_fine_list
df['in_window_prem_tmax'] = prem_tmax_fine_list
df['in_window_jjas_eto'] = jjas_eto_list
df['in_window_prem_eto'] = prem_eto_list

print("=== IN-WINDOW TRUE 24-HOUR DAILY EXTREMES (B42, B43, B44) ===")
print(f"Monsoon Date: 2017-07-15 (in-window, DOY 196)")
print(f"  Coarse Tmax range: [{jjas_tmax.min():.2f}, {jjas_tmax.max():.2f}] °C")
print(f"  Downscaled ETo: mean = {np.mean(jjas_eto_list):.2f} mm/day, range = [{min(jjas_eto_list):.2f}, {max(jjas_eto_list):.2f}] mm/day")
print(f"  Heat Stress Triggers (Tmax >= 35.0 °C): {jjas_heat_triggers} / {len(df)} ({jjas_heat_triggers/len(df)*100:.2f}%)")
print(f"  High Irrigation Demand (ETo > 5.0 mm/day): {jjas_irrig_triggers} / {len(df)} ({jjas_irrig_triggers/len(df)*100:.2f}%)")

# Find actual peak village Tmax in Monsoon
max_j_idx = df['in_window_jjas_tmax'].idxmax()
v_j = df.loc[max_j_idx]
print(f"\nMonsoon Actual Peak Village:")
print(f"  Village Name: {v_j['village_name']}")
print(f"  Village ID (Key): {v_j['village_id']}")
print(f"  Node: ({v_j['node_lat']}°N, {v_j['node_lon']}°E) [i={v_j['node_i']}, j={v_j['node_j']}]")
print(f"  Fine Elev: {v_j['fine_elev_m']} m, ERA5 Elev: {v_j['era5_elev_m']} m, dz: {v_j['dz_era5_m']} m, dt: {v_j['dt_era5_c']} °C")
print(f"  Node Coarse Tmax: {jjas_tmax[int(v_j['node_i']), int(v_j['node_j'])]:.2f} °C")
print(f"  Actual Max Downscaled Village Tmax: {v_j['in_window_jjas_tmax']:.2f} °C")

print(f"\nPre-Monsoon Date: 2018-04-30 (in-window, DOY 120)")
print(f"  Coarse Tmax range: [{prem_tmax.min():.2f}, {prem_tmax.max():.2f}] °C")
print(f"  Downscaled ETo: mean = {np.mean(prem_eto_list):.2f} mm/day, range = [{min(prem_eto_list):.2f}, {max(prem_eto_list):.2f}] mm/day")
print(f"  Heat Stress Triggers (Tmax >= 35.0 °C): {prem_heat_triggers} / {len(df)} ({prem_heat_triggers/len(df)*100:.2f}%)")
print(f"  High Irrigation Demand (ETo > 5.0 mm/day): {prem_irrig_triggers} / {len(df)} ({prem_irrig_triggers/len(df)*100:.2f}%)")

# Find actual peak village Tmax in Pre-Monsoon
max_p_idx = df['in_window_prem_tmax'].idxmax()
v_p = df.loc[max_p_idx]
print(f"\nPre-Monsoon Actual Peak Village:")
print(f"  Village Name: {v_p['village_name']}")
print(f"  Village ID (Key): {v_p['village_id']}")
print(f"  Node: ({v_p['node_lat']}°N, {v_p['node_lon']}°E) [i={v_p['node_i']}, j={v_p['node_j']}]")
print(f"  Fine Elev: {v_p['fine_elev_m']} m, ERA5 Elev: {v_p['era5_elev_m']} m, dz: {v_p['dz_era5_m']} m, dt: {v_p['dt_era5_c']} °C")
print(f"  Node Coarse Tmax: {prem_tmax[int(v_p['node_i']), int(v_p['node_j'])]:.2f} °C")
print(f"  Actual Max Downscaled Village Tmax: {v_p['in_window_prem_tmax']:.2f} °C")
