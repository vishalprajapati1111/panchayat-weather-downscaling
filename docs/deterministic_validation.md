# Deterministic Physical Downscaling Validation

This document presents the spatial hold-out validation for the deterministic temperature downscaling module (`engine/deterministic/temperature.py`), employing physically constrained lapse-rate adjustments over the Western Ghats domain (13.0–17.5°N, 73.5–76.5°E). 

*Time Window:* 2015-06-01 to 2018-05-31 (3 years)
*Target Baseline:* ERA5 0.25°

> [!WARNING]
> **Key Limitations**
> - **Station Scarcity:** Only 6 stations met the 70% completeness threshold. None are above 753 m elevation.
>   *(Screen disambiguation: The 70% threshold is the station-level screen across the 3-year temperature window [2015-06-01 to 2018-05-31; >=767/1096 days; audit_part2.py:50, task-2893:6], yielding 6 usable stations [5,072 station-days]. The 80% threshold [THRESHOLD_80 = 97 days; corrections.py:21] is a separate season-level screen governing inclusion of JJAS rainfall seasons.)*
> - **Unrepresentative Network:** The station network fails to sample the extreme sub-grid topography.
> - **Day-Boundary Mismatch:** GHCN India uses an 0830 IST reporting day, while ERA5 aggregates on UTC calendar days.
> - **Fixed Lapse Rate:** $\Gamma$ is strictly fixed at 6.5 °C/km based on physical literature; it is explicitly never fitted to the evaluation data.

---

## 1. Assimilation Circularity and Baseline Variance

The six validation stations in our dataset correspond directly to WMO SYNOP reporting stations:
*   BELGAUM/SAMBRA (WMO 43198)
*   CHITRADURGA (WMO 43233)
*   GADAG (WMO 43201)
*   KARWAR (WMO 43225)
*   HONAVAR (WMO 43226)
*   GOA/PANJIM (WMO 43192)

*(Note: WMO IDs were retrieved directly from the GHCN `ghcnd-stations.txt` metadata file.)*

ERA5's 2 m temperature field is produced by a 2D optimal interpolation analysis that actively assimilates SYNOP screen-level observations (Hersbach et al. 2020, Q. J. R. Meteorol. Soc., section on screen-level analysis). Because these are synoptic stations, assimilation is plausible but unverified. However, if these specific station records were transmitted and assimilated into the reanalysis, the plateau evaluation is circular, and the near-zero naive baseline bias is mechanically expected rather than impressive.

Supporting this possibility, we observe exceptionally low error variance for naive ERA5 on the plateau, which is highly consistent with direct assimilation:
*   **Plateau Naive ERA5 TAVG Error Variance:** 0.908 °C² (StdDev ~0.95 °C, Bias +0.023 °C).
*   **Coastal Naive ERA5:** Severely ocean-blended (see below).

## 2. Land-Sea Contamination and Diurnal Compression

Coastal stations in the coarse ERA5 baseline suffer from severe diurnal-range (TMAX - TMIN) compression. Applying a strict >0.90 land-fraction threshold for "clean" stations, all coastal stations are severely contaminated:

*   **BELGAUM/SAMBRA:** Land Fraction 1.00 (CLEAN) | DR Error = -3.53 °C
*   **CHITRADURGA:** Land Fraction 0.99 (CLEAN) | DR Error = -2.38 °C
*   **GADAG:** Land Fraction 1.00 (CLEAN) | DR Error = -1.47 °C
*   **HONAVAR:** Land Fraction 0.73 (**CONTAMINATED**) | DR Error = -6.97 °C
*   **KARWAR:** Land Fraction 0.64 (**CONTAMINATED**) | DR Error = -7.22 °C
*   **GOA/PANJIM:** Land Fraction 0.33 (**CONTAMINATED**) | DR Error = -6.19 °C

**Consequence:** The coastal cluster contains **no** clean validation stations. Therefore, the ~0.40 °C improvement previously observed on the coast cannot be safely attributed to the lapse correction; it is terminally confounded with land-sea blending, as coastal cells simultaneously mix ocean fraction, escarpment relief, and $\Delta z$.

---

## 3. ERA5-Land Comparison (Independent Third-Party Check)

As an external benchmark, we compared plain ERA5 daily against ERA5-Land daily (`ECMWF/ERA5_LAND/DAILY_AGGR`). ERA5-Land operates at roughly 9 km and applies its own operational lapse-rate elevation correction. *This is a comparison to validate the physical premise, not a baseline substitution.*

Because ERA5-Land explicitly masks out ocean pixels, it returned NaN for the contaminated coastal stations at their exact coordinates. By sampling the nearest valid land pixel, we recovered the coastal values.

### ERA5-Land Sampling Offsets
The exact distances from the true station coordinates to the sampled pixel centres are:
*   BELGAUM/SAMBRA: 4.17 km
*   CHITRADURGA: 4.61 km
*   GADAG: 3.18 km
*   GOA/PANJIM: 4.83 km
*   HONAVAR: 5.70 km (**SAMPLED DIFFERENT LOCATION: OFFSET > 5km**)
*   KARWAR: 6.54 km (**SAMPLED DIFFERENT LOCATION: OFFSET > 5km**)

### Orography Differences
*   **BELGAUM/SAMBRA (747.0 m):** ERA5 $\Delta z = -17.6\text{m}$ | ERA5-Land $\Delta z = -30.0\text{m}$
*   **CHITRADURGA (733.0 m):** ERA5 $\Delta z = -44.1\text{m}$ | ERA5-Land $\Delta z = +34.0\text{m}$
*   **GADAG (650.0 m):** ERA5 $\Delta z = -24.3\text{m}$ | ERA5-Land $\Delta z = -35.1\text{m}$
*   **KARWAR (4.0 m):** ERA5 $\Delta z = -53.7\text{m}$ | ERA5-Land $\Delta z = -2.5\text{m}$
*   **HONAVAR (9.0 m):** ERA5 $\Delta z = -5.1\text{m}$ | ERA5-Land $\Delta z = +1.5\text{m}$
*   **GOA/PANJIM (60.0 m):** ERA5 $\Delta z = +39.9\text{m}$ | ERA5-Land $\Delta z = +55.4\text{m}$

In general, ERA5-Land's higher-resolution grid (9 km) successfully reduces the $\Delta z$ magnitude at the coastal stations compared to Plain ERA5 (28 km). Specifically at Karwar, the apparent $\Delta z$ of -2.5m is consistent with having sampled a near-shore land pixel located roughly 6.5 km offset from the station, rather than accurately reflecting the station's true sea-level elevation profile.

### Coastal Cluster (Elevation < 200m) Daily Mean Temperature
*   **Plain ERA5:** Bias -1.199 °C [-1.285, -1.112] | MAE 1.356 °C
*   **ERA5-Land:** Bias -2.029 °C [-2.119, -1.939] | MAE 2.063 °C

### Plateau Cluster (Elevation 500-1000m) Daily Mean Temperature
*   **Plain ERA5:** Bias +0.023 °C [-0.034, +0.082] | MAE 0.751 °C
*   **ERA5-Land:** Bias -1.129 °C [-1.226, -1.027] | MAE 1.330 °C

**Result:** ERA5-Land significantly underperforms Plain ERA5 on these specific plateau stations. However, as noted by Muñoz-Sabater et al. 2021 (ESSD 13, 4349), ERA5-Land is a forced land-surface model without its own screen-level assimilation, and it possesses a documented independent cold bias. Thus, its −1.13 °C bias is consistent with both the assimilation explanation (Plain ERA5 was pulled to zero by assimilation while ERA5-Land free-ran) and with a baseline cold bias in ERA5-Land itself. The two cannot be separated with only three plateau stations.

---

## 4. Elevation Dependence Regression

We regressed the naive ERA5 daily-mean bias against the elevation difference $\Delta z$.

With $n=4$ to $6$, $p$ values between $0.22$ and $0.45$, and confidence intervals broadly spanning zero, this regression is completely uninformative about the actual environmental lapse rate. Any apparent slope is terminally confounded with land fraction and with the possible assimilation of the plateau stations.

---

## 5. Village-Scale Representativeness

To quantify sub-grid topographic impact at the operational unit, we intersected the Datameet Indian Village boundaries for the entire domain with the 30m SRTM DEM. 

*   **Total Village Polygons:** 16,945 ingested, 16,943 successfully reduced, 2 null (Goa: 402, Karnataka: 12,366, Maharashtra: 4,177). All percentages use the reduced denominator n=16,943.
*   **Geographic Consistency:** Both the ADM4 and Village rows cover exactly the same geographic area, explicitly clipped to the domain bounding box (13.0–17.5°N, 73.5–76.5°E), meaning their distributions are directly comparable.

| Spatial Unit | Median | p75 | p90 | p95 | p99 | Max |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **ADM4 (Sub-district)** | 37.5 m | 79.2 m | 142.4 m | 168.7 m | 213.1 m | 223.3 m |
| **ADM5 (Village, KA+GA Only)** | 29.1 m | 50.6 m | 90.8 m | 140.9 m | 254.2 m | 601.7 m |
| **ADM5 (Village, Full Domain)** | 33.9 m | 60.4 m | 116.9 m | 170.7 m | 321.0 m | 610.7 m |

[^1]

[^1]: Pixel-level maximum difference was 1,488.9 m. There are 17,210 individual 30m pixels exhibiting $>1,000\text{m}$ difference from their parent 0.25° ERA5 cell mean. This equates to ~15.5 square kilometres (0.009% of the domain area), capturing the sheer vertical drop of the Western Ghats escarpments.

The inclusion of Maharashtra, which contains the steepest Ghats terrain, materially shifts the upper tails of the distribution. For specific highly characterised rainfall locations within the domain, the sub-grid topographic divergence ($\Delta z$) is extreme:
*   **Koynanagar:** $\Delta z = 212.7\text{m}$
*   **Radhanagari:** $\Delta z = 93.4\text{m}$
*   **Top High-Relief Villages:** The true polygon-mean maximum is **Dattathreyapeeta** (KA, code 21692, $\Delta z_{\text{ERA5}} = +640.5\text{ m}$, $\Delta T = -4.16^\circ\text{C}$; against area-averaged SRTM: $+548.8\text{ m}$) and **Torane** (MH, code 9058, $\Delta z_{\text{SRTM}} = +604.9\text{ m}$, $\Delta T = -3.93^\circ\text{C}$; Feature 7508 code 2753104295, $\Delta z = +610.7\text{ m}$, $\Delta T = -3.97^\circ\text{C}$). The former flagship Amboli ($590.9\text{ m}$) was an unrepresentative single-pixel point sample; its actual polygon mean is $\Delta z = +130.3\text{ m}$ ($\Delta T = -0.85^\circ\text{C}$), which sits below the $150\text{ m}$ material threshold and is retracted as a flagship example (overstated by $4.53\times$).
*(Note: Mahabaleshwar and Satara are located just north of 17.5°N and therefore fall outside the bounds of this specific downscaling domain).*

---

## 6. Design Consequence and Operational Gate

The correction magnitude at every available validation station was between 0.02 °C and 0.78 °C. This is at or below the reanalysis's own uncertainty (MAE of 0.75 °C on the plateau, >1.0 °C on the coast). Because the validation network only samples flat terrain where the correction is negligible, it cannot rigorously test the physical downscaling in the regime where it actually matters (the steep escarpments).

**Operational Gate:**
To prevent injecting noise in regions where the baseline dominates, we establish the operating principle that the physical correction must explicitly exceed the baseline uncertainty (Plateau MAE ~0.75 °C). 

Sensitivity to the chosen threshold across the full domain is outlined below:
*   **Gate Threshold > 100 m:** Explicit correction $>0.65^\circ\text{C}$. Impact: 12.5% of villages. (87.5% receive no adjustment).
*   **Gate Threshold > 150 m:** Explicit correction $>0.97^\circ\text{C}$. Impact: 6.7% of villages. (93.3% receive no adjustment).
*   **Gate Threshold > 200 m:** Explicit correction $>1.30^\circ\text{C}$. Impact: 3.6% of villages. (96.4% receive no adjustment).
*   **Gate Threshold > 250 m:** Explicit correction $>1.62^\circ\text{C}$. Impact: 2.0% of villages. (98.0% receive no adjustment).

To ensure the physical correction clearly exceeds the baseline MAE (~0.75 °C on the plateau), the recommended lower bound for the gate is **150 m** ($\sim 0.97^\circ\text{C}$). Under a 150 m gate, 93.3% of the villages (mostly flat plateau/coastal plains) pass the reanalysis through unadjusted, while the 6.7% situated on the escarpments receive the targeted topographic downscaling.
