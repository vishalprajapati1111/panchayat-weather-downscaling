import ee, time, sys, pathlib
import pandas as pd
from datetime import datetime, timedelta

ee.Initialize()

stations = {
    "IN009070100": {"name": "CHITRADURGA", "lat": 14.23, "lon": 76.43},
    "IN009090300": {"name": "GADAG", "lat": 15.43, "lon": 75.63},
    "IN009120100": {"name": "KARWAR", "lat": 14.80, "lon": 74.13},
    "IN009120400": {"name": "HONAVAR", "lat": 14.28, "lon": 74.45},
    "IN022030600": {"name": "GOA/PANJIM", "lat": 15.48, "lon": 73.81}
}

pts = [ee.Feature(ee.Geometry.Point([info['lon'], info['lat']]), {'stn_id': stn_id}) for stn_id, info in stations.items()]
fc_stations = ee.FeatureCollection(pts)

cache_dir = pathlib.Path("data/cache/hourly_era5_chunks")
cache_dir.mkdir(parents=True, exist_ok=True)

# Generate 1-month intervals from 2015-06-01 to 2018-06-02
start = datetime(2015, 6, 1)
end_total = datetime(2018, 6, 2)

months = []
curr = start
while curr < end_total:
    # 1 month step
    # advance to next month 1st
    if curr.month == 12:
        nxt = datetime(curr.year + 1, 1, 1)
    else:
        nxt = datetime(curr.year, curr.month + 1, 1)
    nxt = min(nxt, end_total)
    months.append((curr.strftime("%Y-%m-%d"), nxt.strftime("%Y-%m-%d"), curr.strftime("%Y%m")))
    curr = nxt

print(f"Total 1-month intervals to fetch: {len(months)}", flush=True)

for idx, (s_date, e_date, tag) in enumerate(months, 1):
    chunk_file = cache_dir / f"chunk_{tag}.csv"
    if chunk_file.exists() and chunk_file.stat().st_size > 100:
        print(f"  [{idx}/{len(months)}] {tag} ({s_date} to {e_date}) already cached on disk.", flush=True)
        continue
        
    success = False
    for attempt in range(3):
        try:
            t0 = time.time()
            col = ee.ImageCollection('ECMWF/ERA5/HOURLY') \
                    .filterDate(s_date, e_date) \
                    .filterBounds(fc_stations) \
                    .select(['u_component_of_wind_10m', 'v_component_of_wind_10m', 'total_cloud_cover', 'temperature_2m'])
                    
            raw_list = col.getRegion(fc_stations, 1000).getInfo()
            header = raw_list[0]
            data = raw_list[1:]
            chunk_df = pd.DataFrame(data, columns=header)
            chunk_df.to_csv(chunk_file, index=False)
            t1 = time.time()
            print(f"  [{idx}/{len(months)}] Fetched {tag} ({s_date} to {e_date}): {len(chunk_df)} rows in {t1 - t0:.2f} s", flush=True)
            success = True
            break
        except Exception as e:
            print(f"  [{idx}/{len(months)}] Attempt {attempt+1} failed for {tag}: {e}. Retrying in 3s...", flush=True)
            time.sleep(3)
    if not success:
        raise RuntimeError(f"Failed to fetch month {tag} after 3 attempts!")

# Combine all chunks
print("Combining all cached monthly chunks into master CSV...", flush=True)
all_dfs = []
for _, _, tag in months:
    chunk_file = cache_dir / f"chunk_{tag}.csv"
    all_dfs.append(pd.read_csv(chunk_file))

full_df = pd.concat(all_dfs, ignore_index=True)
full_df['datetime_utc'] = pd.to_datetime(full_df['time'], unit='ms')
full_df = full_df.drop_duplicates(subset=['datetime_utc', 'longitude', 'latitude'])

def match_stn(row):
    lon, lat = row['longitude'], row['latitude']
    best_stn = None
    min_dist = 999.0
    for stn_id, info in stations.items():
        dist = (lon - info['lon'])**2 + (lat - info['lat'])**2
        if dist < min_dist:
            min_dist = dist
            best_stn = stn_id
    return best_stn

full_df['station_id'] = full_df.apply(match_stn, axis=1)
out_file = pathlib.Path("data/cache/station_hourly_era5.csv")
full_df.to_csv(out_file, index=False)
print(f"Successfully saved master file {out_file}: {len(full_df)} rows!", flush=True)
