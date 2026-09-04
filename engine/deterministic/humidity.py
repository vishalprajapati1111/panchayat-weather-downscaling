import numpy as np
import xarray as xr

# Source: standard barometric formula approximations
def barometric_pressure(elevation_m):
    """Estimate surface pressure (Pa) from elevation."""
    # P = P0 * (1 - L*h/T0)**(g*M/(R*L))
    # Approximation for lower troposphere
    return 101325.0 * np.exp(-9.80665 * 0.0289644 * elevation_m / (8.3144598 * 288.15))

def relative_humidity(t2m, d2m, pressure=None):
    """
    Compute RH from temperature and dewpoint.
    t2m: temperature in K
    d2m: dewpoint in K
    """
    # Tetens formula for vapor pressure
    # e = 0.61078 * exp(17.27 * T / (T + 237.3))  where T is in C
    t2m_c = t2m - 273.15
    d2m_c = d2m - 273.15
    
    # Vapor pressure
    e = 0.61078 * np.exp(17.27 * d2m_c / (d2m_c + 237.3))
    # Saturation vapor pressure
    es = 0.61078 * np.exp(17.27 * t2m_c / (t2m_c + 237.3))
    
    rh = (e / es) * 100.0
    return rh

def downscale_humidity(t2m_coarse, d2m_coarse, dem_fine, dem_coarse, lapse_rate=0.0):
    """
    t2m_coarse: Coarse temperature grid (K)
    d2m_coarse: Coarse dewpoint grid (K)
    dem_fine: High-res DEM
    dem_coarse: Coarse DEM
    lapse_rate: K/km (default 0.0 for strict conservation)
    
    Returns:
    rh_fine: Downscaled Relative Humidity (%)
    clamp_mask: Boolean mask where RH was clamped to 100%
    """
    dz = dem_fine - dem_coarse
    
    # Apply lapse rate to dewpoint (default 0)
    d2m_fine = d2m_coarse - (lapse_rate / 1000.0) * dz
    
    # Apply standard lapse rate to temperature (6.5 K/km)
    t2m_fine = t2m_coarse - (6.5 / 1000.0) * dz
    
    # Barometric pressure adjustment not strictly required for RH if using Tetens,
    # but we included pressure in the plan. Tetens is pressure-independent for e/es.
    
    rh_fine = relative_humidity(t2m_fine, d2m_fine)
    
    clamp_mask = rh_fine > 100.0
    rh_fine = xr.where(clamp_mask, 100.0, rh_fine)
    
    return rh_fine, clamp_mask
