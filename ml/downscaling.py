"""
downscaling.py — Physics-based temperature downscaling via the lapse-rate method.

Reproduces the elevation-aware correction from:
    https://github.com/vishalprajapati1111/panchayat-weather-downscaling

Equation:
    T_local = T_ERA5 - LAPSE_RATE * (elevation_local - elevation_ERA5)

where LAPSE_RATE = 0.0065 °C/m  (≡ 6.5 °C/km, the environmental lapse rate).

When the local station sits *higher* than the ERA5 grid cell, the correction
is negative (temperature decreases with altitude); when it sits *lower*, the
correction is positive.

All units:
    temperature : °C  (Celsius)
    elevation   : m   (metres above sea level)
    lapse rate  : °C/m

References
----------
* International Standard Atmosphere (ISA) environmental lapse rate: 6.5 K/km.
* Prajapati et al., panchayat-weather-downscaling (GitHub).
"""

from __future__ import annotations

from typing import Union

import numpy as np

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

#: Environmental lapse rate in °C per metre (6.5 °C/km = 0.0065 °C/m).
LAPSE_RATE_C_PER_M: float = 0.0065


# ---------------------------------------------------------------------------
# Core function
# ---------------------------------------------------------------------------

def lapse_rate_correction(
    t_era5: Union[float, np.ndarray],
    elev_era5: Union[float, np.ndarray],
    elev_local: Union[float, np.ndarray],
    lapse_rate: float = LAPSE_RATE_C_PER_M,
) -> Union[float, np.ndarray]:
    """Apply the elevation-based lapse-rate temperature correction.

    Parameters
    ----------
    t_era5 : float or array-like
        ERA5 2-m temperature at the coarse grid cell, in **°C**.
    elev_era5 : float or array-like
        Mean elevation of the ERA5 grid cell, in **metres**.
    elev_local : float or array-like
        Elevation at the local/station point, in **metres**.
    lapse_rate : float, optional
        Lapse rate in **°C per metre** (default: 0.0065 °C/m = 6.5 °C/km).

    Returns
    -------
    float or numpy.ndarray
        Downscaled temperature at the local point, in **°C**.

    Notes
    -----
    The formula implemented is::

        T_local = T_ERA5 - lapse_rate × (elev_local - elev_ERA5)

    This means:
    * If the station is **above** the ERA5 cell → (elev_local - elev_ERA5) > 0
      → correction is **negative** → station is cooler.
    * If the station is **below** the ERA5 cell → (elev_local - elev_ERA5) < 0
      → correction is **positive** → station is warmer.

    Examples
    --------
    >>> lapse_rate_correction(t_era5=30.0, elev_era5=200.0, elev_local=700.0)
    26.75

    >>> lapse_rate_correction(t_era5=30.0, elev_era5=200.0, elev_local=200.0)
    30.0
    """
    t_era5 = np.asarray(t_era5, dtype=np.float64)
    elev_era5 = np.asarray(elev_era5, dtype=np.float64)
    elev_local = np.asarray(elev_local, dtype=np.float64)

    delta_elev = elev_local - elev_era5           # metres
    t_local = t_era5 - lapse_rate * delta_elev    # °C

    # Return a scalar when the inputs were scalar.
    if t_local.ndim == 0:
        return float(t_local)
    return t_local


# ---------------------------------------------------------------------------
# Quick self-test (runs when executed directly)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Example: station 500 m above the ERA5 grid-cell mean elevation.
    result = lapse_rate_correction(
        t_era5=30.0,
        elev_era5=200.0,
        elev_local=700.0,
    )
    print(f"T_ERA5 = 30.0 C, elev_ERA5 = 200 m, elev_local = 700 m")
    print(f"  => T_local = {result:.2f} C  (delta_elev = +500 m, correction = -3.25 C)")

    # Example: station at same elevation.
    result2 = lapse_rate_correction(
        t_era5=30.0,
        elev_era5=200.0,
        elev_local=200.0,
    )
    print(f"\nT_ERA5 = 30.0 C, elev_ERA5 = 200 m, elev_local = 200 m")
    print(f"  => T_local = {result2:.2f} C  (no correction)")

    # Example: vectorised call.
    import numpy as np
    temps = np.array([30.0, 28.0, 32.0])
    elev_era5_arr = np.array([200.0, 200.0, 200.0])
    elev_local_arr = np.array([700.0, 100.0, 200.0])
    results = lapse_rate_correction(temps, elev_era5_arr, elev_local_arr)
    print(f"\nVectorised: T_local = {results}")
