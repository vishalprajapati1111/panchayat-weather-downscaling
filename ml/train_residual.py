import json
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.metrics import mean_absolute_error, mean_squared_error
from xgboost import XGBRegressor

DATA_PATH = Path(r"C:\Users\VISHAL\Desktop\SIH, Prototype\sih074-downscale-poc\data\cache\ml_temp\clean_training_data.csv")
MODELS_DIR = Path(r"C:\Users\VISHAL\Desktop\SIH, Prototype\sih074-downscale-poc\release\ml\models")
MODELS_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(DATA_PATH)
df["time_utc"] = pd.to_datetime(df["time_utc"])
df["date"] = df["time_utc"].dt.date

features = [
    "temperature_C",
    "dewpoint_C",
    "wind_speed_ms",
    "surface_pressure_Pa",
    "precipitation_m",
    "solar_radiation_J_m2",
    "hour_sin",
    "hour_cos",
    "doy_sin",
    "doy_cos",
]

stations = df["Station"].unique()

print("=========================================================================")
print("LEAVE-ONE-STATION-OUT (LOSO) CROSS-VALIDATION EVALUATION")
print("=========================================================================")

loso_predictions = {}
daily_records = []

hourly_results = []

for held_out in stations:
    train_df = df[df["Station"] != held_out]
    test_df = df[df["Station"] == held_out].copy()

    X_train = train_df[features]
    y_train = train_df["residual_C"]

    X_test = test_df[features]
    y_test = test_df["residual_C"]

    model = XGBRegressor(
        n_estimators=300,
        max_depth=3,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        objective="reg:squarederror",
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)

    pred_residual = model.predict(X_test)
    test_df["pred_residual_C"] = pred_residual
    test_df["pred_temp_C"] = test_df["physics_prediction_C"] + pred_residual

    loso_predictions[held_out] = test_df

    # Hourly metrics
    mae_hourly_base = mean_absolute_error(test_df["observed_temperature_C"], test_df["physics_prediction_C"])
    mae_hourly_corr = mean_absolute_error(test_df["observed_temperature_C"], test_df["pred_temp_C"])

    # Aggregate to daily
    # Group by date
    daily_obs = test_df.groupby("date").agg(
        obs_tmax=("observed_temperature_C", "max"),
        obs_tmin=("observed_temperature_C", "min"),
        base_tmax=("physics_prediction_C", "max"),
        base_tmin=("physics_prediction_C", "min"),
        corr_tmax=("pred_temp_C", "max"),
        corr_tmin=("pred_temp_C", "min"),
        hour_count=("time_utc", "count")
    ).reset_index()

    # Require at least 20 hours for valid daily extremes
    daily_valid = daily_obs[daily_obs["hour_count"] >= 20].copy()
    daily_valid["obs_dtr"] = daily_valid["obs_tmax"] - daily_valid["obs_tmin"]
    daily_valid["base_dtr"] = daily_valid["base_tmax"] - daily_valid["base_tmin"]
    daily_valid["corr_dtr"] = daily_valid["corr_tmax"] - daily_valid["corr_tmin"]
    daily_valid["Station"] = held_out

    daily_records.append(daily_valid)

    mae_tmax_base = mean_absolute_error(daily_valid["obs_tmax"], daily_valid["base_tmax"])
    mae_tmax_corr = mean_absolute_error(daily_valid["obs_tmax"], daily_valid["corr_tmax"])

    mae_tmin_base = mean_absolute_error(daily_valid["obs_tmin"], daily_valid["base_tmin"])
    mae_tmin_corr = mean_absolute_error(daily_valid["obs_tmin"], daily_valid["corr_tmin"])

    mae_dtr_base = mean_absolute_error(daily_valid["obs_dtr"], daily_valid["base_dtr"])
    mae_dtr_corr = mean_absolute_error(daily_valid["obs_dtr"], daily_valid["corr_dtr"])

    hourly_results.append({
        "Station": held_out,
        "Hourly_Base_MAE": mae_hourly_base,
        "Hourly_Corr_MAE": mae_hourly_corr,
        "Hourly_Imp_%": (mae_hourly_base - mae_hourly_corr) / mae_hourly_base * 100,
        "Tmax_Base_MAE": mae_tmax_base,
        "Tmax_Corr_MAE": mae_tmax_corr,
        "Tmax_Imp_%": (mae_tmax_base - mae_tmax_corr) / mae_tmax_base * 100,
        "Tmin_Base_MAE": mae_tmin_base,
        "Tmin_Corr_MAE": mae_tmin_corr,
        "Tmin_Imp_%": (mae_tmin_base - mae_tmin_corr) / mae_tmin_base * 100,
        "DTR_Base_MAE": mae_dtr_base,
        "DTR_Corr_MAE": mae_dtr_corr,
        "DTR_Imp_%": (mae_dtr_base - mae_dtr_corr) / mae_dtr_base * 100,
    })

# Pooled calculations
all_test = pd.concat([loso_predictions[st] for st in stations], ignore_index=True)
pooled_hourly_base = mean_absolute_error(all_test["observed_temperature_C"], all_test["physics_prediction_C"])
pooled_hourly_corr = mean_absolute_error(all_test["observed_temperature_C"], all_test["pred_temp_C"])

all_daily = pd.concat(daily_records, ignore_index=True)
pooled_tmax_base = mean_absolute_error(all_daily["obs_tmax"], all_daily["base_tmax"])
pooled_tmax_corr = mean_absolute_error(all_daily["obs_tmax"], all_daily["corr_tmax"])

pooled_tmin_base = mean_absolute_error(all_daily["obs_tmin"], all_daily["base_tmin"])
pooled_tmin_corr = mean_absolute_error(all_daily["obs_tmin"], all_daily["corr_tmin"])

pooled_dtr_base = mean_absolute_error(all_daily["obs_dtr"], all_daily["base_dtr"])
pooled_dtr_corr = mean_absolute_error(all_daily["obs_dtr"], all_daily["corr_dtr"])

hourly_results.append({
    "Station": "Pooled (All 3)",
    "Hourly_Base_MAE": pooled_hourly_base,
    "Hourly_Corr_MAE": pooled_hourly_corr,
    "Hourly_Imp_%": (pooled_hourly_base - pooled_hourly_corr) / pooled_hourly_base * 100,
    "Tmax_Base_MAE": pooled_tmax_base,
    "Tmax_Corr_MAE": pooled_tmax_corr,
    "Tmax_Imp_%": (pooled_tmax_base - pooled_tmax_corr) / pooled_tmax_base * 100,
    "Tmin_Base_MAE": pooled_tmin_base,
    "Tmin_Corr_MAE": pooled_tmin_corr,
    "Tmin_Imp_%": (pooled_tmin_base - pooled_tmin_corr) / pooled_tmin_base * 100,
    "DTR_Base_MAE": pooled_dtr_base,
    "DTR_Corr_MAE": pooled_dtr_corr,
    "DTR_Imp_%": (pooled_dtr_base - pooled_dtr_corr) / pooled_dtr_base * 100,
})

res_df = pd.DataFrame(hourly_results)
print(res_df.to_string(index=False))

# Now train full model on all 3 stations
full_model = XGBRegressor(
    n_estimators=300,
    max_depth=3,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    objective="reg:squarederror",
    random_state=42,
    n_jobs=-1
)
full_model.fit(df[features], df["residual_C"])

model_path = MODELS_DIR / "residual_temp.json"
full_model.get_booster().save_model(str(model_path))
print(f"\nPersisted model to: {model_path}")

features_meta = {
    "feature_names": features,
    "target": "residual_C",
    "physics_formula": "temperature_C - 0.0065 * (srtm_elevation_m - era5_elevation_m)",
    "hyperparameters": {
        "n_estimators": 300,
        "max_depth": 3,
        "learning_rate": 0.05,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "objective": "reg:squarederror",
        "random_state": 42
    },
    "training_stations": [
        {"name": "Aurangpur", "lat": 20.821111, "lon": 77.540833, "year": 2023, "records": int((df['Station'] == 'Aurangpur').sum())},
        {"name": "Bhatsanagar_1", "lat": 19.519534, "lon": 73.409324, "year": 2024, "records": int((df['Station'] == 'Bhatsanagar_1').sum())},
        {"name": "Natuwadi Dam_1", "lat": 17.332778, "lon": 73.400000, "year": 2024, "records": int((df['Station'] == 'Natuwadi Dam_1').sum())}
    ],
    "training_date_range": {
        "start": str(df["time_utc"].min()),
        "end": str(df["time_utc"].max())
    },
    "total_training_records": len(df)
}

features_path = MODELS_DIR / "residual_temp_features.json"
with open(features_path, "w") as f:
    json.dump(features_meta, f, indent=2)
print(f"Saved feature metadata to: {features_path}")
