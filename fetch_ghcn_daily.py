import requests
import pandas as pd
import pathlib
import io
import time

ROOT = pathlib.Path(__file__).parent
DATA_DIR = ROOT / "data" / "cache" / "ghcn_daily"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# List of target stations identified from our domain check
STATIONS = [
    "IN009021000", "IN009021100", "IN009050100", "IN009070100", 
    "IN009090300", "IN009120100", "IN009120400", "IN012131800", 
    "IN012212400", "IN022030400", "IN022030600"
]

def fetch_station(station_id):
    url = f"https://www.ncei.noaa.gov/data/global-historical-climatology-network-daily/access/{station_id}.csv"
    out_path = DATA_DIR / f"{station_id}.csv"
    
    if not out_path.exists():
        print(f"Downloading {station_id}...")
        r = requests.get(url, timeout=30)
        if r.status_code == 200:
            out_path.write_bytes(r.content)
            time.sleep(1) # Be nice to NOAA servers
        else:
            print(f"Failed to fetch {station_id}: {r.status_code}")
            return None
    
    # Process file
    df = pd.read_csv(out_path, low_memory=False)
    df['DATE'] = pd.to_datetime(df['DATE'])
    
    # GHCN temperatures are in tenths of degrees Celsius.
    # We must explicitly convert them.
    for col in ['TMAX', 'TMIN', 'TAVG']:
        if col in df.columns:
            df[col] = df[col] / 10.0
            
    # Assert plausible ranges
    for col in ['TMAX', 'TMIN', 'TAVG']:
        if col in df.columns:
            valid = df[col].dropna()
            if not valid.empty:
                min_v, max_v = valid.min(), valid.max()
                assert min_v > -50, f"Implausible {col} {min_v} at {station_id}"
                assert max_v < 60, f"Implausible {col} {max_v} at {station_id}"
                
    # Save back as parsed parquet or standardized CSV
    parsed_path = DATA_DIR / f"{station_id}_parsed.csv"
    df.to_csv(parsed_path, index=False)
    return len(df)

total_records = 0
for stn in STATIONS:
    records = fetch_station(stn)
    if records:
        total_records += records
        print(f"{stn}: parsed and verified {records} daily records.")

print(f"\nTotal records processed: {total_records}")
