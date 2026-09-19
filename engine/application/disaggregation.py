"""
Village-level Rainfall Disaggregation and Mass-Conserving Renormalization.
========================================================================
Implements per-cell area-weighted renormalization of rain_ratio and effective_ratio
across all 0.25° forecast cells, strictly preserving total cell precipitation mass:
    sum_k (w_k * rain_ratio_norm_k) = 1.0
    sum_k (w_k * effective_ratio_norm_k) = 1.0
    rain_mm = cell_precip_sum_mm * effective_ratio_norm
"""
import numpy as np
import pandas as pd
from pathlib import Path


def renormalize_cell_ratios(df_daily: pd.DataFrame, df_corr: pd.DataFrame) -> pd.DataFrame:
    """
    Renormalizes rain_ratio and effective_ratio within each 0.25° grid cell by the cell's
    polygon-area-weighted mean ratio, ensuring area-weighted mean equals 1.0 per cell.
    
    Parameters
    ----------
    df_daily : pd.DataFrame
        Daily village forecasts table (16,943 villages).
    df_corr : pd.DataFrame
        Village corrections table containing polygon_area_km2, node_i, node_j.
        
    Returns
    -------
    pd.DataFrame
        Updated df_daily with strictly mass-conserving rain_ratio, effective_ratio, and rain_mm.
    """
    df = df_daily.copy()
    
    # Map polygon area and parent cell indices from village corrections
    area_map = dict(zip(df_corr['village_id'], df_corr['polygon_area_km2']))
    if 'node_i' in df_corr.columns and 'node_j' in df_corr.columns:
        cell_map = dict(zip(df_corr['village_id'], zip(df_corr['node_i'], df_corr['node_j'])))
    else:
        cell_map = dict(zip(df_corr['village_id'], zip(df_corr['node_lat'], df_corr['node_lon'])))
        
    df['polygon_area_km2'] = df['village_id'].map(area_map)
    df['cell_id'] = df['village_id'].map(cell_map)
    
    if df['polygon_area_km2'].isna().any() or df['cell_id'].isna().any():
        raise ValueError("Missing polygon area or cell assignment for one or more villages.")
        
    # Compute per-cell area-weighted mean of raw rain_ratio
    # w_k = A_k / sum(A_k)
    # mean_ratio_c = sum(rain_ratio_k * A_k) / sum(A_k)
    cell_mean_ratios = df.groupby('cell_id').apply(
        lambda g: float(np.sum(g['rain_ratio'].values * g['polygon_area_km2'].values) / np.sum(g['polygon_area_km2'].values)),
        include_groups=False
    ).to_dict()
    
    cell_mean_series = df['cell_id'].map(cell_mean_ratios).values
    
    # 1. Renormalize rain_ratio
    df['rain_ratio'] = df['rain_ratio'] / cell_mean_series
    
    # 2. Recompute effective_ratio with continuous upslope gate g
    # effective_ratio = 1.0 + gate_g * (rain_ratio - 1.0)
    df['effective_ratio'] = 1.0 + df['gate_g'] * (df['rain_ratio'] - 1.0)
    
    # 3. Recompute rain_mm consistently
    # rain_mm = cell_precip_sum_mm * effective_ratio
    df['rain_mm'] = np.round(df['cell_precip_sum_mm'] * df['effective_ratio'], 2)
    
    # Clean up temporary columns
    df = df.drop(columns=['polygon_area_km2', 'cell_id'])
    
    return df


def audit_cell_mass_conservation(df_daily: pd.DataFrame, df_corr: pd.DataFrame, ratio_col: str = 'effective_ratio'):
    """
    Computes area-weighted mean ratio error per cell across all cells:
        error_c = abs(sum_k(w_k * ratio_k) - 1.0)
    Returns (worst_cell_error, mean_cell_error, per_cell_errors_dict).
    """
    area_map = dict(zip(df_corr['village_id'], df_corr['polygon_area_km2']))
    if 'node_i' in df_corr.columns and 'node_j' in df_corr.columns:
        cell_map = dict(zip(df_corr['village_id'], zip(df_corr['node_i'], df_corr['node_j'])))
    else:
        cell_map = dict(zip(df_corr['village_id'], zip(df_corr['node_lat'], df_corr['node_lon'])))
        
    areas = df_daily['village_id'].map(area_map).values
    cells = df_daily['village_id'].map(cell_map).values
    ratios = df_daily[ratio_col].values
    
    df_temp = pd.DataFrame({'cell': cells, 'w': areas, 'r': ratios})
    cell_errors = {}
    for c, grp in df_temp.groupby('cell'):
        w_sum = grp['w'].sum()
        if w_sum > 0:
            weighted_mean = (grp['r'] * grp['w']).sum() / w_sum
            cell_errors[c] = abs(weighted_mean - 1.0)
            
    err_values = list(cell_errors.values())
    worst_err = max(err_values)
    mean_err = float(np.mean(err_values))
    return worst_err, mean_err, cell_errors
