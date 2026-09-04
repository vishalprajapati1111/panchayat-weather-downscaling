"""Sanity checks for the downscaling pipeline.

Run with:  python -m pytest tests/ -v
(or directly: python tests/test_pipeline.py)
"""

from pathlib import Path

import numpy as np

from baseline_bilinear import bilinear_upsample
from generate_synthetic import COARSE_SIZE, FINE_SIZE, LAPSE_RATE_TEMP, N_FINE, N_TIME, SUBDIV
from metrics import mae, rmse
from run_baseline_eval import load_synthetic
from spatial_split import check_no_group_leakage, spatial_group_split

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "synthetic"

ARRAY_NAMES = ["coarse_temp", "coarse_rain", "elevation", "true_temp", "true_rain"]


def _load():
    return load_synthetic(DATA_DIR)


def test_synthetic_data_has_no_nan():
    """All synthetic arrays must be finite (no NaN/inf anywhere)."""
    data = _load()
    for name in ARRAY_NAMES:
        arr = data[name]
        assert np.isfinite(arr).all(), f"{name} contains NaN/inf values"


def test_synthetic_data_shapes():
    """Coarse grids and fine arrays must have the documented shapes."""
    data = _load()
    assert data["coarse_temp"].shape == (N_TIME, COARSE_SIZE, COARSE_SIZE)
    assert data["coarse_rain"].shape == (N_TIME, COARSE_SIZE, COARSE_SIZE)
    assert data["elevation"].shape == (N_FINE,)
    assert data["true_temp"].shape == (N_TIME, N_FINE)
    assert data["true_rain"].shape == (N_TIME, N_FINE)


def test_spatial_split_no_overlap():
    """Train and test point IDs must be disjoint and cover all points."""
    data = _load()
    labels = data["meta"]["coarse_row"] * COARSE_SIZE + data["meta"]["coarse_col"]
    train_ids, test_ids = spatial_group_split(labels, test_fraction=0.2, seed=42)

    train_set, test_set = set(train_ids.tolist()), set(test_ids.tolist())
    assert not train_set & test_set, "train and test point IDs overlap"
    assert train_set | test_set == set(range(N_FINE)), "split does not cover all points"
    assert len(train_ids) > 0 and len(test_ids) > 0, "one of the splits is empty"


def test_spatial_split_group_purity():
    """All fine points of a coarse cell must land in the SAME set."""
    data = _load()
    labels = data["meta"]["coarse_row"] * COARSE_SIZE + data["meta"]["coarse_col"]
    train_ids, test_ids = spatial_group_split(labels, test_fraction=0.2, seed=42)
    assert check_no_group_leakage(labels, train_ids, test_ids)


def test_baseline_predictions_shape():
    """Bilinear predictions must match the true fine values' shape."""
    data = _load()
    pred_temp = bilinear_upsample(data["coarse_temp"], SUBDIV)
    pred_rain = bilinear_upsample(data["coarse_rain"], SUBDIV)
    assert pred_temp.shape == (N_TIME, FINE_SIZE, FINE_SIZE)
    assert pred_rain.shape == (N_TIME, FINE_SIZE, FINE_SIZE)
    assert pred_temp.reshape(N_TIME, N_FINE).shape == data["true_temp"].shape
    assert pred_rain.reshape(N_TIME, N_FINE).shape == data["true_rain"].shape


def test_metrics_sanity():
    """Metrics behave correctly on known inputs."""
    assert mae([1.0, 2.0], [1.0, 2.0]) == 0.0
    assert rmse([1.0, 2.0], [1.0, 2.0]) == 0.0
    assert mae([0.0, 0.0], [1.0, 3.0]) == 2.0
    assert rmse([0.0, 0.0], [3.0, 4.0]) == np.sqrt(12.5)
    try:
        mae([1.0], [1.0, 2.0])
    except ValueError:
        pass
    else:
        raise AssertionError("mae should reject mismatched shapes")


def test_synthetic_data_matches_ground_truth_formula():
    """The residual (true - coarse parent) must correlate with elevation
    per the known formula -- confirms the data generator is correct."""
    data = _load()
    meta = data["meta"]
    parent_temp = data["coarse_temp"][:, meta["coarse_row"], meta["coarse_col"]]
    residual = data["true_temp"] - parent_temp   # = coeff * elevation + noise
    corr = np.corrcoef(residual.ravel(), np.tile(data["elevation"], N_TIME))[0, 1]
    assert corr < -0.9, (
        f"temp residual vs elevation correlation is {corr:.3f}; expected "
        f"strong negative correlation (lapse rate {LAPSE_RATE_TEMP})"
    )


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in tests:
        fn()
        print(f"PASSED: {fn.__name__}")
    print(f"\nAll {len(tests)} checks passed.")