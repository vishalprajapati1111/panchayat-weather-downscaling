#!/usr/bin/env python3
"""
demo_flagship.py -- Ten-minute smoke test for the flagship ERA5 node.

Runs elevation-aware downscaling for one ERA5 cell:
  Node coordinates : (13.25N, 75.25E)
  Node elevation   : 528.6 m (ERA5 model orography)
  Villages served  : 33 villages (Chikkamagaluru & Udupi districts, Karnataka)
  Elevation span   : 290.1 m (Idu) to 1,091.9 m (Samse) -- 801.8 m relief within one cell!

Method:
  T_village = T_era5 - Gamma * (z_SRTM - z_ERA5)
  where Gamma = 6.5 C/km (0.0065 C/m) and dz = z_SRTM - z_ERA5.

Reads only committed project files -- no downloads or GEE account required.
Execution time: < 0.2 seconds.
Produces: outputs/demo_flagship_downscaled.csv
"""

import hashlib
import pathlib
import sys
import time

import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).parent

CORRECTIONS_CSV = ROOT / "outputs" / "village_corrections.csv"
FLAGSHIP_CSV    = ROOT / "outputs" / "figures" / "flagship_node_33_villages.csv"
OUT_CSV         = ROOT / "outputs" / "demo_flagship_downscaled.csv"
EXPECTED_MD5    = "42157952f3441d1ce6fb06910c032c6b"


def _check_file(path, label):
    if not path.exists():
        print("ERROR: " + label + " not found at " + str(path))
        print("  Make sure you cloned the full repository.")
        sys.exit(1)


def _verify_md5(path, expected):
    actual = hashlib.md5(path.read_bytes()).hexdigest()
    if actual != expected:
        print("CHECKSUM MISMATCH: " + path.name)
        print("  Expected : " + expected)
        print("  Got      : " + actual)
        sys.exit(1)
    return actual


def main():
    t0 = time.time()

    print("=" * 75)
    print("FLAGSHIP NODE SMOKE TEST -- 1 Cell, 33 Villages, Offline Verification")
    print("=" * 75)
    print()

    _check_file(CORRECTIONS_CSV, "village_corrections.csv")
    _check_file(FLAGSHIP_CSV,    "flagship_node_33_villages.csv")

    md5 = _verify_md5(CORRECTIONS_CSV, EXPECTED_MD5)

    flagship = pd.read_csv(FLAGSHIP_CSV)

    node_lat  = float(flagship["node_lat"].iloc[0])
    node_lon  = float(flagship["node_lon"].iloc[0])
    era5_elev = float(flagship["era5_elev_m"].iloc[0])
    v_min     = float(flagship["fine_elev_m"].min())
    v_max     = float(flagship["fine_elev_m"].max())

    print("ERA5 Grid Node Coordinates : ({:.2f}N, {:.2f}E)".format(node_lat, node_lon))
    print("ERA5 Model Orography Height : {:.1f} m".format(era5_elev))
    print("Villages in Node Footprint  : {:d}".format(len(flagship)))
    print("Village Elevation Span      : {:.1f} m to {:.1f} m (span = {:.1f} m)".format(v_min, v_max, v_max - v_min))
    print()

    # Apply lapse-rate correction
    # Reference parent temperature: July peak JJAS baseline Tmax at node = 25.25 C
    GAMMA = 0.0065  # C / m (6.5 C / km)
    T_NODE_MAX_C = 25.25
    flagship["calc_dz_m"] = np.round(flagship["fine_elev_m"] - era5_elev, 1)
    flagship["calc_dt_c"] = np.round(-GAMMA * flagship["calc_dz_m"], 2)
    flagship["calc_tmax_c"] = np.round(T_NODE_MAX_C + flagship["calc_dt_c"], 2)

    # Save output file
    flagship.to_csv(OUT_CSV, index=False)

    COL = "{:<20s}{:>10s}{:>10s}{:>10s}{:>10s}{:>10s}{:>12s}"
    print(COL.format("Village", "SRTM (m)", "ERA5 (m)", "dz (m)", "dT (C)", "Tmax (C)", "Direction"))
    print("-" * 82)

    top3 = flagship.nlargest(3, "calc_dz_m")
    bot2 = flagship.nsmallest(2, "calc_dz_m")

    ROW = "{:<20s}{:>10.1f}{:>10.1f}{:>10.1f}{:>10.2f}{:>10.2f}{:>12s}"
    for _, r in top3.iterrows():
        print(ROW.format(str(r["village_name"])[:20],
                         r["fine_elev_m"], r["era5_elev_m"],
                         r["calc_dz_m"], r["calc_dt_c"], r["calc_tmax_c"], r["direction"]))
    print("  ...")
    for _, r in bot2.iterrows():
        print(ROW.format(str(r["village_name"])[:20],
                         r["fine_elev_m"], r["era5_elev_m"],
                         r["calc_dz_m"], r["calc_dt_c"], r["calc_tmax_c"], r["direction"]))
    print("-" * 82)

    # Assertions
    print()
    ok = True
    samse = flagship[flagship["village_name"] == "Samse"].iloc[0]
    checks = [
        (len(flagship) == 33,
         "villages served",
         "33", str(len(flagship))),
        (abs(era5_elev - 528.6) < 0.1,
         "ERA5 node elevation",
         "528.6 m", "{:.1f} m".format(era5_elev)),
        (abs(v_max - 1091.9) < 0.5,
         "maximum village elevation (Samse)",
         "1091.9 m", "{:.1f} m".format(v_max)),
        (abs(v_min - 290.1) < 0.5,
         "minimum village elevation (Idu)",
         "290.1 m", "{:.1f} m".format(v_min)),
        (abs(samse["calc_dt_c"] - (-3.66)) < 0.05,
         "Samse temperature correction dT",
         "-3.66 C", "{:.2f} C".format(samse["calc_dt_c"])),
    ]
    for passed, label, expected_str, got_str in checks:
        status = "PASS" if passed else "FAIL"
        print("  [{}] {} (expected {}, got {})".format(status, label, expected_str, got_str))
        if not passed:
            ok = False

    t1 = time.time()
    print()
    print("Produced output : " + str(OUT_CSV.relative_to(ROOT)))
    print("Elapsed         : {:.3f} s".format(t1 - t0))
    print("Checksum        : " + md5 + " (MATCH)")
    print()
    if ok:
        print("Smoke test PASSED.")
    else:
        print("Smoke test FAILED.")
        sys.exit(1)


if __name__ == "__main__":
    main()
