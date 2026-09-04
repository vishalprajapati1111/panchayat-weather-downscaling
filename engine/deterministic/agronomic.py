"""
Agronomic Derived Variables and Advisory Thresholds

Computes Reference Evapotranspiration (FAO-56 PM or Hargreaves)
Computes advisory flags based on strict sourced physical thresholds.
"""
import numpy as np
from engine.deterministic import config

def calc_eto_hargreaves(
    t_min: np.ndarray, 
    t_max: np.ndarray, 
    t_mean: np.ndarray, 
    ra_mj_m2_day: np.ndarray
) -> np.ndarray:
    """
    Calculate Reference Evapotranspiration (ETo) using Hargreaves-Samani method.
    Fallback when solar radiation/wind are unavailable.
    
    Args:
        t_min: Daily minimum temperature (°C)
        t_max: Daily maximum temperature (°C)
        t_mean: Daily mean temperature (°C)
        ra_mj_m2_day: Extraterrestrial radiation (MJ m-2 day-1)
    """
    # Unit Guard: Hargreaves expects Celsius. If > 100, likely Kelvin.
    if np.any(t_mean > 100.0) or np.any(t_max > 100.0) or np.any(t_min > 100.0):
        raise ValueError("Temperature appears to be in Kelvin (value > 100); calc_eto_hargreaves expects Celsius.")
        
    # Hargreaves-Samani (1985)
    tr = np.clip(t_max - t_min, 0.0, None)
    eto = config.HARGREAVES_COEFF * 0.408 * ra_mj_m2_day * np.sqrt(tr) * (t_mean + 17.8)
    return np.clip(eto, 0.0, None)


def compute_advisories(
    fine_temp_c: np.ndarray,
    fine_rh: np.ndarray,
    fine_wind_speed: np.ndarray,
    eto_mm: np.ndarray
) -> dict:
    """
    Compute Boolean or categorical advisory flags based on downscaled fields.
    """
    advisories = {}
    
    # Spray Suitability (Wind)
    # 0 = Suitable (<= SPRAY_MAX_WIND), 1 = Unsuitable
    advisories['spray_unsuitable'] = fine_wind_speed > config.SPRAY_MAX_WIND
    
    # Disease Risk (Leaf Wetness proxy)
    advisories['disease_risk_high'] = fine_rh >= config.DISEASE_RH_THRESHOLD
    
    # Heat Stress
    advisories['heat_stress'] = fine_temp_c >= config.HEAT_STRESS_THRESHOLD
    
    # Irrigation Need (Raw proxy: ETo > 5mm implies high demand)
    # The actual threshold requires crop coefficients, but this provides a base layer.
    advisories['high_irrigation_demand'] = eto_mm > 5.0
    
    return advisories
