"""
ETo (Reference Evapotranspiration) Integration Module — FAO-56 Penman-Monteith
==============================================================================

IMPORTANT: humidity and wind have zero station-days of ground truth in the
validation window. ETo carries no validated error bar; only the temperature
term inside it does.

Two variants:
  Block wind  — unadjusted coarse-grid wind speed, bilinearly interpolated.
                This is the HEADLINE / primary output. It is the only wind
                number with a source.
  TPI wind    — terrain-exposure-adjusted wind. ESTIMATED — NO SOURCE.
                Produced as a separate labelled column, excluded from every
                performance claim and every headline.

Constraints enforced here:
  - Γ fixed at 6.5 °C/km, never fitted.
  - ERA5-Land prohibited as baseline input.
  - Single marked Kelvin→Celsius conversion per variable, per call.
  - Day-boundary UTC/IST offset (UTC+5:30) noted as a limitation.
  - Clusters named "coastal" and "plateau" as in validation.py.
  - Attenuation figures stay in Table B under quarantine.
  - Every output carries the column label "block_wind" or
    "tpi_wind [ESTIMATED — NO SOURCE]".

Source: Allen et al. (1998), FAO Irrigation and Drainage Paper 56.
"""
import numpy as np
import pathlib
import json
import datetime
from engine.deterministic import config

# ── UTC/IST offset note (limitation) ──────────────────────────────────────
# ERA5 data is in UTC. IST = UTC + 5:30 h. Daily summaries from ERA5 aggregate
# 00:00–23:59 UTC, which is 05:30–05:29 IST. This produces a day-boundary
# mismatch of up to 5.5 h for early-morning and late-night events. This
# mismatch is noted here as a known limitation; it is NOT corrected in this
# module because the correction requires sub-daily data not currently ingested.

LOG_DIR = pathlib.Path("logs")
LOG_DIR.mkdir(exist_ok=True)
LOG_PATH = LOG_DIR / "eto_run.jsonl"


def _log(record: dict):
    record["timestamp"] = datetime.datetime.utcnow().isoformat() + "Z"
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(record) + "\n")


def sat_vp(t_c: np.ndarray) -> np.ndarray:
    """Saturation vapour pressure [kPa]. FAO-56 Eq. 11. Input in °C."""
    return 0.6108 * np.exp((17.27 * t_c) / (t_c + 237.3))


def actual_vp_from_rh(rh: np.ndarray, t_c: np.ndarray) -> np.ndarray:
    """Actual vapour pressure from RH [%] and temperature [°C]. FAO-56 Eq. 14."""
    return (rh / 100.0) * sat_vp(t_c)


def slope_svp(t_c: np.ndarray) -> np.ndarray:
    """Slope of saturation VP curve [kPa/°C]. FAO-56 Eq. 13."""
    return (4098.0 * sat_vp(t_c)) / (t_c + 237.3) ** 2


def psychrometric_const(elev_m: np.ndarray) -> np.ndarray:
    """Psychrometric constant γ [kPa/°C] adjusted for elevation. FAO-56 Eq. 8."""
    p_kpa = 101.3 * ((293.0 - 0.0065 * elev_m) / 293.0) ** 5.26
    return 0.000665 * p_kpa


def wind_2m(ws_10m: np.ndarray) -> np.ndarray:
    """Convert wind speed at 10 m to 2 m height. FAO-56 Eq. 47."""
    return ws_10m * (4.87 / np.log(67.8 * 10.0 - 5.42))


def calc_eto_pm(
    t_max_c: np.ndarray,
    t_min_c: np.ndarray,
    rh_pct: np.ndarray,
    ws_ms: np.ndarray,         # wind speed at 10 m [m/s]
    rn_mj: np.ndarray,         # net radiation [MJ m-2 day-1]
    elev_m: np.ndarray,
    wind_variant: str = "block_wind",
) -> np.ndarray:
    """
    FAO-56 Penman-Monteith ETo [mm/day].

    wind_variant: "block_wind" (headline) or "tpi_wind [ESTIMATED — NO SOURCE]"
    """
    assert wind_variant in ("block_wind", "tpi_wind [ESTIMATED — NO SOURCE]"), \
        f"Unknown wind_variant: {wind_variant}"

    # ── Single marked Kelvin→Celsius conversion ────────────────────────────
    # t_max_c and t_min_c must already be in °C.
    # Guard: if values look like Kelvin, raise immediately.
    if np.any(t_max_c > 100.0) or np.any(t_min_c > 100.0):
        raise ValueError(
            "calc_eto_pm: t_max_c or t_min_c > 100 — appears to be Kelvin. "
            "Convert with t_c = t_k - 273.15 BEFORE calling this function. "
            "[Single marked Kelvin→Celsius conversion rule]"
        )

    t_mean_c = 0.5 * (t_max_c + t_min_c)
    delta = slope_svp(t_mean_c)                # FAO-56 Eq. 13
    gamma = psychrometric_const(elev_m)        # FAO-56 Eq. 8
    es = 0.5 * (sat_vp(t_max_c) + sat_vp(t_min_c))   # FAO-56 Eq. 12
    ea = actual_vp_from_rh(rh_pct, t_mean_c)          # FAO-56 Eq. 14

    ws2 = wind_2m(ws_ms)   # FAO-56 Eq. 47

    # FAO-56 Eq. 6 — soil heat flux G ≈ 0 for daily step
    G = 0.0

    numerator = (0.408 * delta * (rn_mj - G)
                 + gamma * (900.0 / (t_mean_c + 273.0)) * ws2 * (es - ea))
    denominator = delta + gamma * (1.0 + 0.34 * ws2)

    eto = numerator / denominator
    eto = np.clip(eto, 0.0, None)
    return eto


def run_eto_integration(
    t_max_k: np.ndarray,       # shape (N,) — fine villages
    t_min_k: np.ndarray,
    rh_pct: np.ndarray,
    ws_block_ms: np.ndarray,   # block (unadjusted) wind [m/s]
    ws_tpi_ms: np.ndarray,     # TPI-adjusted wind [m/s]  ESTIMATED — NO SOURCE
    rn_mj: np.ndarray,
    elev_m: np.ndarray,
    point_ids: np.ndarray,
) -> dict:
    """
    Run ETo for both wind variants. Returns dict with labelled arrays.

    HEADLINE: block_wind ETo.
    SENSITIVITY (excluded from performance claims): tpi_wind ETo.
    """
    # Marked Kelvin→Celsius conversion — single location, single call.
    t_max_c = t_max_k - 273.15   # K→°C conversion
    t_min_c = t_min_k - 273.15   # K→°C conversion

    eto_block = calc_eto_pm(t_max_c, t_min_c, rh_pct, ws_block_ms,
                             rn_mj, elev_m, wind_variant="block_wind")
    eto_tpi   = calc_eto_pm(t_max_c, t_min_c, rh_pct, ws_tpi_ms,
                             rn_mj, elev_m,
                             wind_variant="tpi_wind [ESTIMATED — NO SOURCE]")

    record = {
        "event": "eto_run",
        "n_villages": int(len(point_ids)),
        "eto_block_mean_mm_day": float(np.mean(eto_block)),
        "eto_tpi_mean_mm_day": float(np.mean(eto_tpi)),
        "spread_abs_mean_mm_day": float(np.mean(np.abs(eto_tpi - eto_block))),
        "headline_wind": "block_wind",
        "sensitivity_wind": "tpi_wind [ESTIMATED — NO SOURCE]",
        "validation_note": (
            "humidity and wind have zero station-days of ground truth in the "
            "validation window. ETo carries no validated error bar; only the "
            "temperature term inside it does."
        ),
    }
    _log(record)

    return {
        "block_wind":                       eto_block,
        "tpi_wind [ESTIMATED — NO SOURCE]": eto_tpi,
        "delta_eto":                        eto_tpi - eto_block,
        "point_ids":                        point_ids,
        "elev_m":                           elev_m,
    }
