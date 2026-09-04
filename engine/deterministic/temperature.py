"""
Temperature Downscaling Module

Implements elevation-based lapse rate adjustment relative to the parent cell area-mean elevation.
Includes switchable slope-aspect solar radiation adjustment.
"""
import numpy as np
from engine.deterministic import config

def downscale_temperature(
    coarse_temp: np.ndarray,
    coarse_elev: np.ndarray,
    fine_elev: np.ndarray,
    lapse_rate: float = config.LAPSE_RATE_DEFAULT,
    apply_aspect: bool = False,
    aspect_rad: np.ndarray = None,
    slope_rad: np.ndarray = None,
    lat_rad: np.ndarray = None,
    day_of_year: int = None
) -> np.ndarray:
    """
    Downscale temperature based on physical environmental lapse rates.
    
    Args:
        coarse_temp: Temperature of the parent cell (Kelvin or Celsius).
        coarse_elev: Mean elevation of the parent cell (m).
        fine_elev: Elevation of the fine cell (m).
        lapse_rate: Environmental lapse rate (K/km or °C/km). Default is 6.5.
        apply_aspect: If True, apply a heuristic slope-aspect radiation correction.
        aspect_rad: Aspect of the fine cell (radians). Required if apply_aspect=True.
        slope_rad: Slope of the fine cell (radians). Required if apply_aspect=True.
        lat_rad: Latitude in radians. Required if apply_aspect=True.
        day_of_year: Integer day of year (1-365). Required if apply_aspect=True.
        
    Returns:
        np.ndarray: Downscaled fine temperature.
        
    Failure Modes (Documented):
        1. Nocturnal cold-air pooling (inversions): Valley floors may be colder than slopes. Unmodelled.
        2. Coastal sea breeze: Disrupts lapse rate relationship within ~20km of coast.
        3. Heavy cloud cover: Reduces the effective lapse rate and solar adjustments.
    """
    # 1. Base Lapse Rate Adjustment
    if np.any(coarse_temp < 150.0):
        raise ValueError("Input coarse_temp appears to be in Celsius; expected Kelvin (values < 150K).")
        
    # If fine_elev > coarse_elev, (fine_elev - coarse_elev) is positive, temperature drops.
    # Divide by 1000 since lapse rate is per km, but elevations are in meters.
    elev_diff_km = (fine_elev - coarse_elev) / 1000.0
    t_fine = coarse_temp - (elev_diff_km * lapse_rate)
    
    # 2. Slope-Aspect Solar Adjustment (Heuristic Term)
    if apply_aspect:
        if any(x is None for x in [aspect_rad, slope_rad, lat_rad, day_of_year]):
            raise ValueError("Aspect, slope, latitude, and day_of_year are required when apply_aspect=True")
        
        # Simple potential radiation heuristic (estimated effect)
        # Solar declination approximation
        declination = 0.409 * np.sin((2 * np.pi * day_of_year / 365) - 1.39)
        
        # Aspect effect peaks when facing equator (South in Northern Hemisphere, aspect = pi)
        # We model a small additive heuristic: e.g. up to +1.5 C for steep south-facing slopes in NH
        # This is explicitly marked as ESTIMATED heuristic coefficient.
        ASPECT_COEFF = 1.5 # [°C] ESTIMATED — NO SOURCE
        
        aspect_modifier = np.cos(aspect_rad - np.pi) * np.sin(slope_rad)
        t_fine += ASPECT_COEFF * aspect_modifier

    return t_fine
