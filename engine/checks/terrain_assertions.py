"""
Permanent Terrain and Downscaling Disaggregation Assertions.
Ministry of Earth Sciences, sih074.
Updated 2026-09-03 (B23: Pixel raster footprint containment & canonical bound).
"""
import numpy as np

def assert_raster_footprint_containment(lat_c: float, lon_c: float, node_lat: float, node_lon: float, half_box: float = 0.125):
    """
    Assertion 2 / Check (a) (Replaced B23):
    Assert that polygon centroid falls strictly inside the spatial footprint of the raster pixel
    whose value was read: [node_lat - half_box, node_lat + half_box] x [node_lon - half_box, node_lon + half_box].
    Fails on the retired corner-registered grid (75.3% failure rate) and passes on canonical grid.
    """
    inside = (node_lat - half_box - 1e-6 <= lat_c <= node_lat + half_box + 1e-6) and \
             (node_lon - half_box - 1e-6 <= lon_c <= node_lon + half_box + 1e-6)
    assert inside, f"Centroid ({lat_c:.4f}, {lon_c:.4f}) outside raster pixel footprint for node ({node_lat:.4f}, {node_lon:.4f})"
    return True

def assert_identical_box_coarse_height(villages_in_box: list):
    """
    Assertion 2 / Check (b):
    Ensure all villages sharing an ERA5 node box receive identical coarse heights.
    """
    e5_vals = set(v['era5_orog'] for v in villages_in_box)
    assert len(e5_vals) == 1, f"Differing ERA5 coarse values in same box: {e5_vals}"
    return True

def assert_arithmetic_bound(dz_era5: np.ndarray, max_abs_srtm: float = 635.0, max_cell_offset: float = 346.47):
    """
    Assertion 1 / Check (c) (Rebuilt B20):
    Ensure no polygon dz_era5 violates the canonical triangle bound:
    |dz_era5| <= max|dz_srtm| + max|cell_offset_regrid| = 635.0 + 346.47 = 981.47 m.
    """
    bound = max_abs_srtm + max_cell_offset
    max_observed = float(np.max(np.abs(dz_era5)))
    assert max_observed <= bound + 1e-6, (
        f"Arithmetic bound violation: max |dz_era5| = {max_observed:.2f} m > bound = {bound:.2f} m "
        f"(max |dz_srtm| {max_abs_srtm} + max cell offset {max_cell_offset})"
    )
    return True, max_observed, bound

def assert_area_weighted_conservation(dz_srtm: np.ndarray, areas: np.ndarray, tolerance_m: float = 5.0):
    """
    Assertion 3:
    Ensure area-weighted mean signed dz_srtm integrates near zero over domain.
    """
    weighted_mean = float(np.average(dz_srtm, weights=areas))
    assert abs(weighted_mean) <= tolerance_m, (
        f"Area-weighted mean signed dz_srtm = {weighted_mean:+.2f} m exceeds tolerance +- {tolerance_m:.1f} m"
    )
    return True, weighted_mean
