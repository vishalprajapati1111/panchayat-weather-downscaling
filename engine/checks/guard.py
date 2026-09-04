import math
import numpy as np

def haversine(lon1, lat1, lon2, lat2):
    R = 6371.0 # km
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = math.sin(dLat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def safe_extract(ds, var, lat, lon, lat_dim='latitude', lon_dim='longitude', max_dist_km=None):
    """
    Safely extract a point using nearest neighbor.

    Two independent checks, both must pass:
      1. BOUNDS CHECK  (independent of distance): the requested coordinate must lie
         inside the array's actual lat/lon range ± half a cell.  A point just outside
         the domain would otherwise be silently clamped to the boundary cell and could
         pass a distance check if it happened to be close to that edge cell.
      2. DISTANCE CHECK: the returned cell centre must be within max_dist_km
         (defaults to 1.1 × the half-cell diagonal).

    Raises ValueError on either violation rather than returning a silently wrong value.
    """
    lats = ds[lat_dim].values
    lons = ds[lon_dim].values

    dlat = abs(float(np.diff(lats).mean()))
    dlon = abs(float(np.diff(lons).mean()))

    # --- 1. BOUNDS CHECK (independent of distance) ---
    # Allow up to half a cell beyond the declared extent; anything further is
    # definitely outside the grid and must not be clamped silently.
    lat_lo = float(lats.min()) - dlat / 2
    lat_hi = float(lats.max()) + dlat / 2
    lon_lo = float(lons.min()) - dlon / 2
    lon_hi = float(lons.max()) + dlon / 2

    if lat < lat_lo or lat > lat_hi:
        raise ValueError(
            f"BOUNDS VIOLATION: requested lat {lat} is outside array extent "
            f"[{lat_lo:.4f}, {lat_hi:.4f}] (half-cell padded). "
            f"Array covers [{float(lats.min()):.4f}, {float(lats.max()):.4f}]."
        )
    if lon < lon_lo or lon > lon_hi:
        raise ValueError(
            f"BOUNDS VIOLATION: requested lon {lon} is outside array extent "
            f"[{lon_lo:.4f}, {lon_hi:.4f}] (half-cell padded). "
            f"Array covers [{float(lons.min()):.4f}, {float(lons.max()):.4f}]."
        )

    # --- nearest extraction ---
    px = ds.sel({lat_dim: lat, lon_dim: lon}, method="nearest")
    if var is not None:
        px = px[var]

    actual_lat = float(px[lat_dim].item())
    actual_lon = float(px[lon_dim].item())

    dist = haversine(lon, lat, actual_lon, actual_lat)

    # --- 2. DISTANCE CHECK ---
    if max_dist_km is None:
        # Half-cell diagonal × 1.1 tolerance
        max_dist_km = haversine(0, 0, dlon / 2, dlat / 2) * 1.1

    if dist > max_dist_km:
        raise ValueError(
            f"DISTANCE VIOLATION: ({lat}, {lon}) mapped to ({actual_lat}, {actual_lon}) "
            f"at {dist:.2f} km > allowed {max_dist_km:.2f} km (1.1 × half-cell diagonal)."
        )

    return px
