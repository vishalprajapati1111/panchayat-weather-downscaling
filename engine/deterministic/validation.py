"""
Temperature Downscaling Validation

Performs rigorous spatial holdout validation of deterministic temperature downscaling against GHCN stations.
Sweeps the environmental lapse rate, evaluates null-models, and asserts zero data leakage.
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple

def bootstrap_ci(y_true: np.ndarray, y_pred: np.ndarray, metric_func, n_boot=1000) -> Tuple[float, float, float]:
    """Compute metric with 95% bootstrap confidence intervals."""
    if len(y_true) < 2:
        val = metric_func(y_true, y_pred)
        return val, val, val
        
    vals = []
    idx = np.arange(len(y_true))
    for _ in range(n_boot):
        b_idx = np.random.choice(idx, size=len(idx), replace=True)
        vals.append(metric_func(y_true[b_idx], y_pred[b_idx]))
    
    vals = np.array(vals)
    return metric_func(y_true, y_pred), np.percentile(vals, 2.5), np.percentile(vals, 97.5)

def calc_mae(y_true, y_pred):
    return np.mean(np.abs(y_true - y_pred))

def calc_rmse(y_true, y_pred):
    return np.sqrt(np.mean((y_true - y_pred)**2))

def calc_bias(y_true, y_pred):
    return np.mean(y_pred - y_true)

def assert_no_leakage(train_stations: List[str], eval_stations: List[str]):
    """Strictly assert that no station used for fitting appears in the evaluation set."""
    intersection = set(train_stations).intersection(set(eval_stations))
    if intersection:
        raise AssertionError(f"LEAKAGE DETECTED: Stations {intersection} found in both train and eval sets!")
        
def evaluate_holdout(
    df_eval: pd.DataFrame, 
    lapse_rate: float, 
    apply_aspect: bool = False
) -> Dict[str, Tuple[float, float, float]]:
    """
    Evaluates temperature downscaling on a held-out dataset.
    df_eval must contain: 'true_temp', 'coarse_temp', 'fine_elev', 'coarse_elev', 'aspect', 'slope', 'lat', 'doy'
    """
    # 1. Naive Baseline (Raw Coarse ERA5)
    naive_preds = df_eval['coarse_temp'].values
    
    # 2. Null Model (Domain Mean)
    # Using the mean true temperature across the domain on that day.
    # We simulate this by taking the daily mean of 'true_temp' (this assumes we have it, in practice 
    # the null model uses the coarse grid mean, which is close).
    null_preds = df_eval.groupby('date')['coarse_temp'].transform('mean').values
    
    # 3. Downscaled
    from engine.deterministic.temperature import downscale_temperature
    
    down_preds = downscale_temperature(
        coarse_temp=df_eval['coarse_temp'].values,
        coarse_elev=df_eval['coarse_elev'].values,
        fine_elev=df_eval['fine_elev'].values,
        lapse_rate=lapse_rate,
        apply_aspect=apply_aspect,
        aspect_rad=df_eval.get('aspect', np.zeros(len(df_eval))).values,
        slope_rad=df_eval.get('slope', np.zeros(len(df_eval))).values,
        lat_rad=df_eval.get('lat', np.zeros(len(df_eval))).values,
        day_of_year=df_eval.get('doy', np.ones(len(df_eval))).values
    )
    
    true_vals = df_eval['true_temp'].values
    
    # Define elevation bands
    coastal_mask = df_eval['fine_elev'] < 200
    plateau_mask = (df_eval['fine_elev'] >= 500) & (df_eval['fine_elev'] < 1000)
    
    # Assert crest limitation
    if (df_eval['fine_elev'] >= 1000).any():
        print("WARNING: Stations found above 1000m. Check station metadata.")
    else:
        print("NOTE: No station exceeds 1000m. Crest performance is extrapolated and unvalidated.")
    
    results = {'Overall': {}, 'Coastal_<200m': {}, 'Plateau_500-1000m': {}}
    
    masks = {
        'Overall': np.ones(len(df_eval), dtype=bool),
        'Coastal_<200m': coastal_mask.values,
        'Plateau_500-1000m': plateau_mask.values
    }
    
    for band_name, mask in masks.items():
        if not np.any(mask):
            continue
            
        band_true = true_vals[mask]
        
        for name, preds in [('Naive_ERA5', naive_preds), ('Null_Mean', null_preds), ('Downscaled', down_preds)]:
            band_preds = preds[mask]
            mae, m_low, m_high = bootstrap_ci(band_true, band_preds, calc_mae)
            rmse, r_low, r_high = bootstrap_ci(band_true, band_preds, calc_rmse)
            bias, b_low, b_high = bootstrap_ci(band_true, band_preds, calc_bias)
            
            results[band_name][name] = {
                'MAE': (mae, m_low, m_high),
                'RMSE': (rmse, r_low, r_high),
                'Bias': (bias, b_low, b_high)
            }
        
    return results

def fit_lapse_rate(df_train: pd.DataFrame, search_space=np.linspace(4.5, 7.5, 31)) -> float:
    """Empirically fit the lapse rate on training stations."""
    best_lr = 6.5
    best_mae = float('inf')
    
    from engine.deterministic.temperature import downscale_temperature
    true_vals = df_train['true_temp'].values
    
    for lr in search_space:
        preds = downscale_temperature(
            coarse_temp=df_train['coarse_temp'].values,
            coarse_elev=df_train['coarse_elev'].values,
            fine_elev=df_train['fine_elev'].values,
            lapse_rate=lr,
            apply_aspect=False
        )
        mae = calc_mae(true_vals, preds)
        if mae < best_mae:
            best_mae = mae
            best_lr = lr
            
    return best_lr
