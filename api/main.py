import os
from pathlib import Path
from typing import List
import numpy as np
import pandas as pd
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="AgroMet Downscaling API",
    description="High-resolution lookup API for downscaled JJAS weather and crop water variables across the Western Ghats",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "village_serving.csv"
if not DATA_PATH.exists():
    DATA_PATH = Path("api/data/village_serving.csv")
if not DATA_PATH.exists():
    DATA_PATH = Path("release/api/data/village_serving.csv")

if not DATA_PATH.exists():
    raise FileNotFoundError(f"Serving table not found at {DATA_PATH}")

df = pd.read_csv(DATA_PATH)
df["village_id"] = df["village_id"].astype(str)
df["name"] = df["name"].astype(str)
df["name_lower"] = df["name"].str.lower()
df["state"] = df["state"].astype(str)
df["inside_validated_band"] = df["inside_validated_band"].astype(bool)

# Serving configuration flag: set to False for instant 1-line mid-demo revert to physics-only
SERVE_ML_TEMPERATURE: bool = False

if SERVE_ML_TEMPERATURE:
    DAILY_DATA_PATH = BASE_DIR / "data" / "village_daily_ml.csv"
else:
    DAILY_DATA_PATH = BASE_DIR / "data" / "village_daily_physics.csv"

if not DAILY_DATA_PATH.exists():
    DAILY_DATA_PATH = BASE_DIR / "data" / "village_daily_physics.csv"
if not DAILY_DATA_PATH.exists():
    DAILY_DATA_PATH = Path("outputs/village_daily_20260917.csv")
if not DAILY_DATA_PATH.exists():
    DAILY_DATA_PATH = BASE_DIR.parent / "outputs" / "village_daily_20260917.csv"

if DAILY_DATA_PATH.exists():
    df_daily = pd.read_csv(DAILY_DATA_PATH)
    df_daily["village_id"] = df_daily["village_id"].astype(str)
    df_daily["name"] = df_daily["name"].astype(str)
    df_daily["state"] = df_daily["state"].astype(str)
    df_daily["inside_validated_band"] = df_daily["inside_validated_band"].astype(bool)
else:
    df_daily = None

VILLAGE_LATS = df["lat"].to_numpy(dtype=np.float64)
VILLAGE_LONS = df["lon"].to_numpy(dtype=np.float64)
VILLAGE_LATS_RAD = np.radians(VILLAGE_LATS)
VILLAGE_LONS_RAD = np.radians(VILLAGE_LONS)

DOMAIN_LAT_MIN = 12.948
DOMAIN_LAT_MAX = 17.550
DOMAIN_LON_MIN = 73.448
DOMAIN_LON_MAX = 76.552

# Load optional gauge transect data if present on disk
GAUGE_PATH = BASE_DIR / "data" / "rain_stations_transect.csv"
if not GAUGE_PATH.exists():
    GAUGE_PATH = Path("outputs/rain_stations_transect.csv")
if not GAUGE_PATH.exists():
    GAUGE_PATH = BASE_DIR.parent / "outputs" / "rain_stations_transect.csv"

GAUGES_LIST = []
if GAUGE_PATH.exists():
    gdf = pd.read_csv(GAUGE_PATH)
    if "name" in gdf.columns and "latitude" in gdf.columns and "longitude" in gdf.columns:
        for _, r in gdf.iterrows():
            GAUGES_LIST.append({
                "village_id": str(r.get("id", "")),
                "name": str(r["name"]).strip(),
                "state": str(r.get("zone", "")),
                "lat": round(float(r["latitude"]), 5),
                "lon": round(float(r["longitude"]), 5),
                "type": "gauge"
            })


def haversine_vectorized(query_lat: float, query_lon: float) -> np.ndarray:
    r = 6371.0
    query_lat_rad = np.radians(query_lat)
    query_lon_rad = np.radians(query_lon)

    dlat = VILLAGE_LATS_RAD - query_lat_rad
    dlon = VILLAGE_LONS_RAD - query_lon_rad

    a = np.sin(dlat / 2.0) ** 2 + np.cos(query_lat_rad) * np.cos(VILLAGE_LATS_RAD) * np.sin(dlon / 2.0) ** 2
    a = np.clip(a, 0.0, 1.0)
    c = 2.0 * np.arctan2(np.sqrt(a), np.sqrt(1.0 - a))
    return r * c


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.get("/api/predict")
def predict(
    lat: float = Query(..., description="Latitude of query location"),
    lon: float = Query(..., description="Longitude of query location")
):
    distances = haversine_vectorized(lat, lon)
    min_idx = int(np.argmin(distances))
    distance_km = round(float(distances[min_idx]), 2)

    row = df.iloc[min_idx]
    in_domain = bool(
        DOMAIN_LAT_MIN <= lat <= DOMAIN_LAT_MAX and
        DOMAIN_LON_MIN <= lon <= DOMAIN_LON_MAX
    )

    v_name = str(row["name"])
    v_state = str(row["state"])
    v_lat = round(float(row["lat"]), 5)
    v_lon = round(float(row["lon"]), 5)
    v_elev = round(float(row["elevation_m"]), 1)
    v_temp = round(float(row["temp_c"]), 2)
    v_eto = round(float(row["eto_mm_day"]), 2)
    v_rain = round(float(row["rainfall_jjas_mm"]), 1)
    v_val_band = bool(row["inside_validated_band"])

    sentences = [
        "Seasonal JJAS values downscaled from ERA5 0.25 degree reanalysis using 30 m SRTM terrain; rainfall calibrated against 19 NOAA GHCN gauges."
    ]
    if v_val_band:
        sentences.append("Rainfall estimate lies within the 12.8-15.3N gauge-validated band (19-gauge calibrated).")
    else:
        sentences.append("Rainfall estimate lies outside the 12.8-15.3N gauge-validated band and represents uncalibrated spatial extrapolation.")

    if distance_km > 20.0:
        sentences.append(f"Warning: Nearest village ({v_name}) is {distance_km:.1f} km away; local microclimate and terrain effects may differ.")
    else:
        sentences.append(f"Nearest village is {v_name} at a distance of {distance_km:.1f} km.")

    note = " ".join(sentences)

    return {
        "village_id": str(row["village_id"]),
        "name": v_name,
        "village_name": v_name,
        "state": v_state,
        "lat": v_lat,
        "lon": v_lon,
        "elevation_m": v_elev,
        "temp_c": v_temp,
        "eto_mm_day": v_eto,
        "rainfall_jjas_mm": v_rain,
        "inside_validated_band": v_val_band,
        "distance_km": distance_km,
        "in_domain": in_domain,
        "note": note
    }


@app.get("/api/daily")
def daily(
    lat: float = Query(..., description="Latitude of query location"),
    lon: float = Query(..., description="Longitude of query location")
):
    if df_daily is None:
        return {"error": "Daily forecast table not loaded"}

    distances = haversine_vectorized(lat, lon)
    min_idx = int(np.argmin(distances))
    distance_km = round(float(distances[min_idx]), 2)

    row = df_daily.iloc[min_idx]
    in_domain = bool(
        DOMAIN_LAT_MIN <= lat <= DOMAIN_LAT_MAX and
        DOMAIN_LON_MIN <= lon <= DOMAIN_LON_MAX
    )

    return {
        "village_id": str(row["village_id"]),
        "name": str(row["name"]),
        "state": str(row["state"]),
        "lat": round(float(row["lat"]), 5),
        "lon": round(float(row["lon"]), 5),
        "elevation_m": round(float(row["elevation_m"]), 1),
        "forecast_date": str(row["forecast_date"]),
        "cell_precip_sum_mm": round(float(row["cell_precip_sum_mm"]), 2),
        "rain_ratio": round(float(row["rain_ratio"]), 4),
        "wind_dir_deg": int(row["wind_dir_deg"]),
        "wind_speed_max_kmh": round(float(row["wind_speed_max_kmh"]), 1),
        "gate_g": round(float(row["gate_g"]), 4),
        "effective_ratio": round(float(row["effective_ratio"]), 4),
        "rain_mm": round(float(row["rain_mm"]), 2),
        "cell_tmax_c": round(float(row["cell_tmax_c"]), 2),
        "cell_tmin_c": round(float(row["cell_tmin_c"]), 2),
        "temp_offset_c": round(float(row["temp_offset_c"]), 2),
        "tmax_c": round(float(row["tmax_c"]), 2),
        "tmin_c": round(float(row["tmin_c"]), 2),
        "tmean_c": round(float(row["tmean_c"]), 2),
        "eto_mm_day": round(float(row["eto_mm_day"]), 2),
        "tmax_source": str(row["tmax_source"]) if "tmax_source" in row else ("ml_corrected" if SERVE_ML_TEMPERATURE else "physics"),
        "ml_offset_tmax_c": round(float(row["ml_offset_tmax_c"]), 2) if "ml_offset_tmax_c" in row else 0.0,
        "ml_model_version": str(row["ml_model_version"]) if "ml_model_version" in row else ("v2" if SERVE_ML_TEMPERATURE else "none"),
        "ml_applied_to": str(row["ml_applied_to"]) if "ml_applied_to" in row else ("tmax_only" if SERVE_ML_TEMPERATURE else "none"),
        "clamp_limit_c": 2.0,
        "inside_validated_band": bool(row["inside_validated_band"]),
        "distance_km": distance_km,
        "in_domain": in_domain,
        "driver_model": "ecmwf_ifs025",
        "driver_source": "Open-Meteo ECMWF IFS (0.25 deg)"
    }


@app.get("/api/search")
def search(q: str = Query("", description="Search query")):
    query = q.strip().lower()
    if not query:
        return []

    results = []
    # Search gauge stations from file if available
    for g in GAUGES_LIST:
        if query in g["name"].lower():
            results.append(g)

    # Search village table
    matches = df[df["name_lower"].str.contains(query, regex=False)]
    for _, row in matches.iterrows():
        if len(results) >= 8:
            break
        results.append({
            "village_id": str(row["village_id"]),
            "name": str(row["name"]),
            "state": str(row["state"]),
            "lat": round(float(row["lat"]), 5),
            "lon": round(float(row["lon"]), 5),
            "type": "village"
        })

    return results[:8]


@app.get("/api/model_info")
def model_info():
    return {
        "rainfall": {
            "canonical_median_ape_pct": 16.09,
            "windward_median_ape_pct": 9.53,
            "leeward_median_ape_pct": 32.03,
            "n_gauges": 19,
            "domain_band": "12.8-15.3N",
            "n_villages_in_band": 8634,
            "n_villages_total": 16943,
            "per_station_spread_ape_pct": {
                "Hulikal": 50.6,
                "Agumbe_Obsy": 27.7
            },
            "cell_mass_conservation_worst_error": 4.44e-16
        },
        "temperature": {
            "tmax_serving_method": "XGBoost diurnal residual correction (v2) applied to lapse-rate base with hard +/-2.0 C clamp" if SERVE_ML_TEMPERATURE else "physics-only lapse-rate (6.5 C/km) on 30 m SRTM terrain",
            "tmin_serving_method": "physics-only lapse-rate (6.5 C/km); ML disabled (-14.4% negative transfer on Tmin)",
            "served_tmax_source": "ml_corrected" if SERVE_ML_TEMPERATURE else "physics",
            "clamp_rule": "hard +/-2.0 C ceiling applied to hourly residuals and daily offsets",
            "revert_command": "Set SERVE_ML_TEMPERATURE = False in release/api/main.py",
            "accuracy": {
                "ecmwf_ifs_forecast_served": {
                    "input_source": "Open-Meteo ECMWF IFS 0.25 deg operational forecasts (2024-03 to 2024-12, 605 station-days)",
                    "tmax_baseline_mae_c": 2.1225,
                    "tmax_ml_corrected_mae_c": 1.5320,
                    "improvement_pct": 27.8,
                    "worse_days_pct": 15.5,
                    "tmin_physics_mae_c": 1.1876
                },
                "era5_reanalysis_reference": {
                    "input_source": "ERA5 hourly reanalysis (2023-01 to 2024-12, 1,500 station-days)",
                    "tmax_baseline_mae_c": 1.8404,
                    "tmax_ml_corrected_mae_c": 1.5558,
                    "improvement_pct": 15.5,
                    "worse_days_pct": 31.9,
                    "tmin_physics_mae_c": 1.0540
                }
            },
            "note": "The batch pipeline precomputes both village_daily_physics.csv and village_daily_ml.csv. Served values use ECMWF IFS 0.25 deg forecast inputs with ML-corrected Tmax (MAE 2.12 -> 1.53 C across 605 IFS station-days) and physics-only Tmin (1.19 C on IFS / 1.054 C on ERA5). A 1-line mid-demo revert to physics is enabled via SERVE_ML_TEMPERATURE = False."
        }
    }
