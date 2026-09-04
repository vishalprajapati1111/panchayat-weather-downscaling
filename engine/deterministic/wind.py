import numpy as np
import xarray as xr
import scipy.ndimage as ndimage

def compute_tpi(dem, radius_cells=10):
    """
    Compute Topographic Position Index (TPI).
    TPI = DEM - smoothed(DEM)
    """
    dem_np = dem.values
    # Uniform filter computes the local mean
    smoothed = ndimage.uniform_filter(dem_np, size=radius_cells*2+1)
    tpi = dem_np - smoothed
    return xr.DataArray(tpi, coords=dem.coords, dims=dem.dims)

def downscale_wind(u_coarse, v_coarse, dem_fine, alpha=0.3):
    """
    Downscale wind speed using a terrain exposure index.
    Outputs are marked ESTIMATED - NO SOURCE since TPI coefficients 
    are physically reasoned but not strictly calibrated to ground truth here.
    
    u_coarse: Coarse grid U wind
    v_coarse: Coarse grid V wind
    dem_fine: High-res DEM
    alpha: speed-up coefficient for TPI
    """
    wspd_coarse = np.sqrt(u_coarse**2 + v_coarse**2)
    wdir = np.arctan2(v_coarse, u_coarse)
    
    # Compute TPI on the fine DEM
    tpi = compute_tpi(dem_fine, radius_cells=10) # roughly ~300m to 500m radius if 30m DEM
    
    # Terrain exposure factor: simple log-linear speedup
    # Sx > 0 (ridges) -> speed > 1
    # Sx < 0 (valleys) -> speed < 1
    # Bounded to prevent extreme unphysical values
    tpi_scaled = tpi / 100.0 # scale by 100m
    exposure_factor = 1.0 + (alpha * tpi_scaled)
    exposure_factor = xr.where(exposure_factor < 0.2, 0.2, exposure_factor)
    exposure_factor = xr.where(exposure_factor > 3.0, 3.0, exposure_factor)
    
    wspd_fine = wspd_coarse * exposure_factor
    
    # Keep direction unchanged
    u_fine = wspd_fine * np.cos(wdir)
    v_fine = wspd_fine * np.sin(wdir)
    
    return u_fine, v_fine, wspd_fine
