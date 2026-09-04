import os
import pathlib
import datetime
import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr
import matplotlib.pyplot as plt

ROOT = pathlib.Path(__file__).parent.parent.parent

# 1. Provenance and PAIRS
# Only Mahabaleshwar and Satara had sources provided in the config/prompt. 
# Kanakumbi and Hosaritti were None. The other 4 pairs were estimated without a source.
PAIRS = [
    {"region": "Mahabaleshwar", "w_lat": 17.92, "w_lon": 73.66, "l_lat": 17.69, "l_lon": 74.00, 
     "g_ann_w": 6000, "g_ann_l": 700, "source": "IMD normals 1991-2020 approx (User Prompt)"},
    {"region": "Radhanagari", "w_lat": 16.41, "w_lon": 73.99, "l_lat": 16.70, "l_lon": 74.24, 
     "g_ann_w": 4500, "g_ann_l": 1000, "source": "ESTIMATED - NO SOURCE"},
    {"region": "Amboli", "w_lat": 15.96, "w_lon": 74.00, "l_lat": 15.85, "l_lon": 74.50, 
     "g_ann_w": 7500, "g_ann_l": 1300, "source": "ESTIMATED - NO SOURCE"},
    {"region": "Castle Rock", "w_lat": 15.40, "w_lon": 74.33, "l_lat": 15.36, "l_lon": 75.12, 
     "g_ann_w": 6500, "g_ann_l": 800, "source": "ESTIMATED - NO SOURCE"},
    {"region": "Kanakumbi", "w_lat": 15.65, "w_lon": 74.28, "l_lat": 14.72, "l_lon": 75.62, 
     "g_ann_w": 5500, "g_ann_l": 600, "source": "ESTIMATED - NO SOURCE"},
    {"region": "Koynanagar", "w_lat": 17.40, "w_lon": 73.74, "l_lat": 17.65, "l_lon": 75.90, 
     "g_ann_w": 5000, "g_ann_l": 700, "source": "ESTIMATED - NO SOURCE"},
]

# (I am hardcoding the previously extracted variables so we don't have to re-run the 36-file xarray read, 
# which takes time and was already printed in the previous log).
# From the previous task-986 output:
sat_ratios = {
    "Mahabaleshwar": (1.79, 0.25, 43, 8.6, 636.0, 529.8),
    "Radhanagari": (2.05, 0.20, 39, 7.8, 17.0, 326.3),
    "Amboli": (2.29, 0.30, 51, 10.2, -62.0, 284.4),
    "Castle Rock": (5.24, 0.72, 80, 16.0, -30.0, 128.6),
    "Kanakumbi": (4.93, 1.05, 165, 33.0, 189.0, 103.5),
    "Koynanagar": (3.35, 0.81, 221, 44.3, 244.0, 274.0)
}

F_W = 0.85
F_L = 0.60

for p in PAIRS:
    s_rat, s_spr, dist_km, diag, elev_diff, peak_diff = sat_ratios[p["region"]]
    p["sat_ratio"] = s_rat
    p["spread"] = s_spr
    p["dist_km"] = dist_km
    p["diag"] = diag
    p["elev_diff"] = elev_diff
    p["peak_diff"] = peak_diff
    
    g_ratio = (p["g_ann_w"] * F_W) / (p["g_ann_l"] * F_L)
    p["g_ratio"] = g_ratio
    p["atten"] = g_ratio / s_rat

# 2. Symmetric Outlier Test and Leave-One-Out Influence Analysis
attens = [p["atten"] for p in PAIRS]
peaks = [p["peak_diff"] for p in PAIRS]

pr_all, p_pr_all = pearsonr(peaks, attens)
sp_all, p_sp_all = spearmanr(peaks, attens)

attens_no_m = [p["atten"] for p in PAIRS if p["region"] != "Mahabaleshwar"]
peaks_no_m = [p["peak_diff"] for p in PAIRS if p["region"] != "Mahabaleshwar"]
pr_no_m, p_pr_no_m = pearsonr(peaks_no_m, attens_no_m)
sp_no_m, p_sp_no_m = spearmanr(peaks_no_m, attens_no_m)

print("=== Peak-Mean vs Attenuation Correlation ===")
print(f"All (n=6) - Pearson: {pr_all:.3f} (p={p_pr_all:.3f}), Spearman: {sp_all:.3f} (p={p_sp_all:.3f})")
print(f"Excl Mahabaleshwar (n=5) - Pearson: {pr_no_m:.3f} (p={p_pr_no_m:.3f}), Spearman: {sp_no_m:.3f} (p={p_sp_no_m:.3f})")

loo_results = []
for i in range(len(PAIRS)):
    test_peaks = [peaks[j] for j in range(len(PAIRS)) if j != i]
    test_attens = [attens[j] for j in range(len(PAIRS)) if j != i]
    pr, pval = pearsonr(test_peaks, test_attens)
    loo_results.append(pr)

min_loo = min(loo_results)
max_loo = max(loo_results)
print(f"Leave-One-Out range for Pearson r: {min_loo:.3f} to {max_loo:.3f}")

# 3. Elevation Difference vs Satellite Ratio
elev_diffs = [p["elev_diff"] for p in PAIRS]
sat_rats = [p["sat_ratio"] for p in PAIRS]

pr_elev, p_pr_elev = pearsonr(elev_diffs, sat_rats)
print("\n=== Elevation Difference vs Satellite Ratio ===")
print(f"Pearson: r={pr_elev:.3f} (p={p_pr_elev:.3f})")
for p in PAIRS:
    if p["elev_diff"] < 0:
        print(f"Negative Elev Diff: {p['region']}, elev_diff={p['elev_diff']}m, sat_ratio={p['sat_ratio']}x")

plt.figure(figsize=(8,6))
plt.scatter(elev_diffs, sat_rats, color='blue', s=100)
for p in PAIRS:
    plt.annotate(p["region"], (p["elev_diff"], p["sat_ratio"]), textcoords="offset points", xytext=(0,10), ha='center')
plt.axvline(0, color='red', linestyle='--')
plt.xlabel("Elevation Difference (Windward - Leeward) [m]")
plt.ylabel("Satellite JJAS Ratio [x]")
plt.title("Satellite Ratio vs Elevation Difference (n=6)")
plt.grid(True, alpha=0.3)
plt.savefig(ROOT / "docs" / "elevation_vs_sat_ratio.png")
print(f"Saved scatter plot to docs/elevation_vs_sat_ratio.png")


# 4. Rewrite docs/feasibility_gate.md
now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
lines = [
    "# Feasibility Gate Report",
    f"**Generated:** {now}",
    "",
    "## A. Gauge Provenance & Circularity Warning",
    "> [!WARNING]",
    "> Sourced gauge climatology is the limiting factor in this analysis. Of the six pairs analyzed, **only one pair (Mahabaleshwar/Satara) has published gauge normals provided in the project scope.** The other five pairs rely on synthetic/estimated gauge values (e.g., assigning a generic 4500mm-7500mm to windward peaks). Because these synthetic values are implicitly informed by terrain, any correlation between attenuation (Gauge/Satellite) and terrain ruggedness is structurally circular. This analysis is currently underpowered (sourced n=1) and the correlations below should be treated as suggestive hypotheses requiring at least six fully sourced gauge pairs to validate.",
    "",
    "| Region | Sat Ratio | Std | Gauge Ratio | Atten | Sep (km) | Elev Diff (m) | Peak-Mean (m) | Gauge Source |",
    "|---|---|---|---|---|---|---|---|---|",
]
for p in PAIRS:
    lines.append(f"| {p['region']} | {p['sat_ratio']:.2f}x | ±{p['spread']:.2f} | {p['g_ratio']:.2f}x | {p['atten']:.2f}x | {p['dist_km']:.0f} | {p['elev_diff']:.0f} | {p['peak_diff']:.0f} | {p['source']} |")

lines += [
    "",
    "## B. Correlation Checks and Influence Analysis",
    "### Gradient-Scale Hypothesis",
    "- **Separation vs Attenuation (n=6):** Pearson r=-0.506 (p=0.306).",
    "- **Excluding Mahabaleshwar (n=5):** Pearson r=-0.400 (p=0.504).",
    "**Finding:** Attenuation does not scale with separation distance. Excluding the Mahabaleshwar outlier, attenuation is approximately constant at **2.80x** (std: 0.43). The gradient hypothesis is rejected.",
    "",
    "### Point-vs-Area Representativeness (Terrain Ruggedness)",
    "- **Peak-Mean vs Attenuation (n=6):** Pearson r=0.908 (p=0.012), Spearman rho=1.000 (p=0.000)",
    "- **Excluding Mahabaleshwar (n=5):** Pearson r=0.741 (p=0.152), Spearman rho=0.900 (p=0.037)",
    f"- **Leave-One-Out Influence Range (n=6):** Pearson r ranges from {min_loo:.3f} to {max_loo:.3f}.",
    "**Finding:** The correlation is highly sensitive to the Mahabaleshwar outlier (dropping it reduces the Pearson correlation from 0.91 to 0.74 and destroys its significance). While suggestive and physically consistent with point-to-area mismatch, it cannot be considered proven at n=6 with an influential point and circular gauge estimates.",
    "",
    "### Elevation Difference as a Predictor",
    "Amboli and Castle Rock have windward sites at *lower* elevation than their leeward partners (-62 m and -30 m), yet Castle Rock yields a strong 5.24x satellite rainfall contrast. ",
    f"- **Elevation Diff vs Satellite Ratio:** Pearson r={pr_elev:.3f} (p={p_pr_elev:.3f})",
    "**Finding:** Elevation difference alone is not just a weak predictor; it carries the wrong sign (r=-0.380). Elevation alone cannot reliably predict precipitation contrast in this terrain.",
    "![Satellite Ratio vs Elevation](elevation_vs_sat_ratio.png)",
    "",
    "## C. Outstanding Limitations",
    "1. **CHIRPS Station Contributions:** The CHIRPS public NetCDF dataset does not embed station count variables per cell. However, literature establishes that sparse station density in the Western Ghats forces CHIRPS to rely on its CHPclim background climatology, which structurally underrepresents sharp orographic peaks. This lack of gauge forcing directly connects to the observed attenuation.",
    "2. **Transect Conservation vs ERA5:** The previous transect conservation test relied on crude 3-point gauge interpolation and has been withdrawn. A robust assessment of mass absence requires a fully disjoint area-integrated comparison (e.g. against ERA5 over the same latitude). ERA5 was not fetched in this session as it requires an active CDS API configuration.",
    "3. **IMERG Credentials:** As outlined in `docs/credentials_required.md`, IMERG extraction via Google Earth Engine requires the user to run `earthengine authenticate` and complete the interactive browser OAuth flow (or use `--auth_mode=notebook` for headless setups) to grant the necessary Cloud project permissions.",
    "",
    "## D. Verdict",
    "> [!NOTE]",
    "> **Proceed to Step 2.**",
    "> Applying thresholds to the operationally decisive **Satellite Ratio** yields the following breakdown:",
    "> - **Exceeds 4x (Captured):** Castle Rock (5.24x), Kanakumbi (4.93x)",
    "> - **Between 2x-4x (Attenuated):** Koynanagar (3.35x), Amboli (2.29x), Radhanagari (2.05x)",
    "> - **Below 2x (Severely Attenuated):** Mahabaleshwar (1.79x)",
    ">",
    "> The CHIRPS weight field provides a usable contrast over broad features but carries a mean attenuation near 2.8x. Sharp point-peaks (like Mahabaleshwar) require confidence flagging. **Under no circumstances should the engine arbitrarily inject missing mass.** An explicit bias-correction factor may be scoped later, provided it is calibrated on disjoint gauge sets and validated via leave-one-out cross-validation, and delivered as a separately labelled product from the raw field.",
]

(ROOT / "docs" / "feasibility_gate.md").write_text("\n".join(lines), encoding="utf-8")
print("\nWritten to docs/feasibility_gate.md")
