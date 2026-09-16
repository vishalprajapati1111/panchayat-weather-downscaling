"""
match_station_era5.py
=====================
Extract Aurad_3 station observations and match them to ERA5 hourly data.

Steps:
  1. Load Aurad_3 rows from data/raw/maha_temp_raw.csv
  2. Parse timestamps and rename temperature column
  3. Connect to public WeatherBench2 ERA5 Zarr
  4. Find nearest ERA5 grid point to Aurad_3
  5. Extract ERA5 2m temperature for the overlapping period
  6. Convert ERA5 K -> C
  7. Inner-join on hourly timestamp
  8. Save matched DataFrame to data/processed/aurad3_matched.csv
"""

from __future__ import annotations

import sys
from pathlib import Path

import gcsfs
import numpy as np
import pandas as pd
import xarray as xr

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

STATION_NAME = "Aurad_3"
STATION_LAT = 18.07666667
STATION_LON = 76.91916667

RAW_CSV = Path(__file__).resolve().parent.parent / "data" / "raw" / "maha_temp_raw.csv"
OUT_CSV = Path(__file__).resolve().parent.parent / "data" / "processed" / "aurad3_matched.csv"

ERA5_ZARR = "weatherbench2/datasets/era5/1959-2023_01_10-full_37-1h-0p25deg-chunk-1.zarr"

# Column names in the raw CSV
COL_STATION = "Station"
COL_TIME = "Data Acquisition Time"
COL_TEMP = "Air Temperature Telemetry Hourly (AoC)"

TIME_FMT = "%d-%m-%Y %H:%M"  # DD-MM-YYYY HH:MM


# ---------------------------------------------------------------------------
# 1. Load station data
# ---------------------------------------------------------------------------

def load_station_data(csv_path: Path, station_name: str) -> pd.DataFrame:
    """Load only the rows for *station_name* from the raw CSV."""
    print(f"[1/7] Loading {station_name} rows from {csv_path.name} ...")

    # Read only the columns we need to keep memory low on the 286 MB file.
    df = pd.read_csv(
        csv_path,
        usecols=[COL_STATION, COL_TIME, COL_TEMP],
        dtype={COL_STATION: str, COL_TEMP: str},
    )
    df = df[df[COL_STATION] == station_name].copy()
    print(f"      Found {len(df):,} rows for {station_name}.")
    return df


# ---------------------------------------------------------------------------
# 2. Parse timestamps & rename columns
# ---------------------------------------------------------------------------

def parse_station_df(df: pd.DataFrame) -> pd.DataFrame:
    """Parse timestamps, rename temp column, floor to nearest hour."""
    print("[2/7] Parsing timestamps and renaming columns ...")

    # Parse timestamp
    df["timestamp"] = pd.to_datetime(df[COL_TIME], format=TIME_FMT)

    # Rename temperature
    df["station_temp_c"] = pd.to_numeric(df[COL_TEMP], errors="coerce")

    # Floor to nearest hour so we can join with ERA5 hourly data.
    # (Some station entries have non-round minutes, e.g. 11:15.)
    df["timestamp"] = df["timestamp"].dt.floor("h")

    # If multiple readings fall in the same hour after flooring, keep the mean.
    df = df.groupby("timestamp", as_index=False)["station_temp_c"].mean()

    # Drop NaN temperatures
    before = len(df)
    df = df.dropna(subset=["station_temp_c"]).reset_index(drop=True)
    print(f"      {len(df):,} unique hourly timestamps ({before - len(df)} NaN temps dropped).")
    print(f"      Station date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    return df


# ---------------------------------------------------------------------------
# 3-4. Connect to ERA5 & find nearest grid point
# ---------------------------------------------------------------------------

def open_era5() -> xr.Dataset:
    """Open the WeatherBench2 ERA5 Zarr store (anonymous access)."""
    print("[3/7] Connecting to WeatherBench2 ERA5 Zarr (anonymous GCS) ...")
    fs = gcsfs.GCSFileSystem(token="anon")
    mapper = fs.get_mapper(ERA5_ZARR)
    ds = xr.open_zarr(mapper, consolidated=True)
    print(f"      ERA5 time range: {ds.time.values[0]} to {ds.time.values[-1]}")
    return ds


def find_nearest_era5_point(ds: xr.Dataset, lat: float, lon: float):
    """Return the nearest ERA5 lat/lon to the given station coordinates."""
    print(f"[4/7] Finding nearest ERA5 grid point to ({lat:.4f}, {lon:.4f}) ...")

    nearest = ds.sel(latitude=lat, longitude=lon, method="nearest")
    era5_lat = float(nearest.latitude.values)
    era5_lon = float(nearest.longitude.values)
    dlat = abs(lat - era5_lat)
    dlon = abs(lon - era5_lon)
    print(f"      Nearest ERA5 point: ({era5_lat:.2f}, {era5_lon:.2f})")
    print(f"      Distance: dlat={dlat:.4f} deg, dlon={dlon:.4f} deg")
    return era5_lat, era5_lon


# ---------------------------------------------------------------------------
# 5-6. Extract ERA5 temperature for overlap period
# ---------------------------------------------------------------------------

def extract_era5_temperature(
    ds: xr.Dataset,
    era5_lat: float,
    era5_lon: float,
    station_df: pd.DataFrame,
) -> pd.DataFrame:
    """Extract ERA5 2m temperature (in C) for the period that overlaps the station data."""
    print("[5/7] Determining time overlap ...")

    station_start = station_df["timestamp"].min()
    station_end = station_df["timestamp"].max()

    era5_start = pd.Timestamp(ds.time.values[0])
    era5_end = pd.Timestamp(ds.time.values[-1])

    overlap_start = max(station_start, era5_start)
    overlap_end = min(station_end, era5_end)

    print(f"      Station period : {station_start} to {station_end}")
    print(f"      ERA5 period    : {era5_start} to {era5_end}")

    if overlap_start > overlap_end:
        print("      *** NO TIME OVERLAP between station and ERA5 data. ***")
        print()
        print("      The WeatherBench2 ERA5 dataset ends at", era5_end)
        print("      but the Aurad_3 station data begins at", station_start)
        print()
        print("      Searching for newer ERA5 datasets on WeatherBench2 ...")
        _list_available_era5_datasets()
        return pd.DataFrame(columns=["timestamp", "era5_temp_c", "era5_latitude", "era5_longitude"])

    print(f"      Overlap period : {overlap_start} to {overlap_end}")

    print("[6/7] Extracting ERA5 2m temperature for overlap period (K -> C) ...")

    t2m = ds["2m_temperature"].sel(
        latitude=era5_lat,
        longitude=era5_lon,
        time=slice(str(overlap_start), str(overlap_end)),
    )
    # Load only the small slice into memory
    t2m = t2m.load()

    era5_df = t2m.to_dataframe().reset_index()
    era5_df = era5_df.rename(columns={"time": "timestamp", "2m_temperature": "era5_temp_c"})

    # Convert Kelvin to Celsius
    era5_df["era5_temp_c"] = era5_df["era5_temp_c"] - 273.15
    era5_df["era5_latitude"] = era5_lat
    era5_df["era5_longitude"] = era5_lon

    # Keep only the columns we need
    era5_df = era5_df[["timestamp", "era5_temp_c", "era5_latitude", "era5_longitude"]]
    print(f"      Extracted {len(era5_df):,} ERA5 hourly values.")
    return era5_df


def _list_available_era5_datasets():
    """List ERA5 datasets in the WeatherBench2 GCS bucket to find alternatives."""
    try:
        fs = gcsfs.GCSFileSystem(token="anon")
        items = fs.ls("weatherbench2/datasets/era5")
        zarr_items = [item for item in items if "zarr" in item]
        print(f"      Found {len(zarr_items)} ERA5 Zarr datasets on WeatherBench2:")
        for item in sorted(zarr_items):
            name = item.split("/")[-1]
            print(f"        - {name}")
    except Exception as e:
        print(f"      Could not list datasets: {e}")


# ---------------------------------------------------------------------------
# 7. Match station & ERA5
# ---------------------------------------------------------------------------

def merge_station_era5(station_df: pd.DataFrame, era5_df: pd.DataFrame) -> pd.DataFrame:
    """Inner-join station and ERA5 DataFrames on timestamp."""
    print("[7/7] Merging station and ERA5 data on timestamp ...")
    merged = pd.merge(station_df, era5_df, on="timestamp", how="inner")
    merged = merged.sort_values("timestamp").reset_index(drop=True)
    print(f"      Matched rows: {len(merged):,}")
    return merged


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    # Step 1: Load station data
    station_raw = load_station_data(RAW_CSV, STATION_NAME)
    if station_raw.empty:
        print(f"ERROR: No data found for station '{STATION_NAME}'.")
        sys.exit(1)

    # Step 2: Parse & clean
    station_df = parse_station_df(station_raw)

    # Steps 3-4: Open ERA5 & find nearest point
    ds = open_era5()
    era5_lat, era5_lon = find_nearest_era5_point(ds, STATION_LAT, STATION_LON)

    # Steps 5-6: Extract ERA5 temperature
    era5_df = extract_era5_temperature(ds, era5_lat, era5_lon, station_df)

    # Step 7: Merge
    matched = merge_station_era5(station_df, era5_df)

    # Output
    if matched.empty:
        print()
        print("=" * 70)
        print("RESULT: No matched rows (no time overlap).")
        print("=" * 70)
    else:
        OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
        matched.to_csv(OUT_CSV, index=False)
        print()
        print("=" * 70)
        print(f"RESULT: {len(matched):,} matched rows saved to {OUT_CSV.name}")
        print("=" * 70)
        print()
        print(matched.head(10).to_string(index=False))
        print()
        print("Summary statistics:")
        print(f"  station_temp_c: mean={matched['station_temp_c'].mean():.1f}, "
              f"std={matched['station_temp_c'].std():.1f}")
        print(f"  era5_temp_c:    mean={matched['era5_temp_c'].mean():.1f}, "
              f"std={matched['era5_temp_c'].std():.1f}")
        bias = (matched["era5_temp_c"] - matched["station_temp_c"]).mean()
        print(f"  ERA5 bias (ERA5 - station): {bias:+.2f} C")


if __name__ == "__main__":
    main()
