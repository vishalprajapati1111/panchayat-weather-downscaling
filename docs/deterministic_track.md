# Deterministic Physical Downscaling Track

## 1. Overview
The deterministic track implements physically constrained downscaling for Temperature, Humidity, and Wind (`engine/deterministic/`). It operates independently of any precipitation-specific statistical weight fields, relying exclusively on physical principles (lapse rates, barometric formulas, and terrain exposure).

*   **Validated Layers:** Temperature (TMAX, TMIN).
*   **Unvalidated Layers:** Humidity, Wind, Agronomic (ETo). These rely purely on conserved physical state and heuristics, as no dense station network was available for their validation.

## 2. GHCN Temperature Station Validation

We validated the lapse-rate downscaling against the GHCN-Daily network in India. 
*   **Target Region:** 13.0–17.5°N, 73.5–76.5°E
*   **Time Window:** 2015-06-01 to 2018-05-31 (3 years)
*   **Data Source:** ERA5 (0.25° ~28 km native grid) downscaled to actual station point elevations.

> [!WARNING]
> **Station Scarcity and Representativeness:** The validation window retains only **6 viable stations** passing a 70% completeness threshold (5,655 total valid station-days). 
> 
> Furthermore, an Earth Engine analysis of the 30m SRTM DEM against the ERA5 0.25° grid reveals that the 6 GHCN stations are highly unrepresentative of the complex terrain:
> - **Domain Terrain:** 13.5% of the land area has sub-grid topographic differences exceeding 100m, requiring $>0.65^\circ\text{C}$ corrections. 
> - **Station Network:** The median absolute elevation difference for the 6 stations is ~53m. They perfectly sample the flat "median" terrain but fail to sample the severe terrain where downscaling is most critical.

### 2.1 The Directional Test (Bias)
Due to the small magnitude of the expected temperature correction (median 0.39 °C across the 6 stations), the primary metric is **Bias**, not MAE. 

**Pre-registered Physical Prediction:**
At a fixed environmental lapse rate of 6.5 °C/km:
1.  **Coastal Cluster** (ERA5 cell elevation > Station elevation): The lapse correction must apply a WARMING effect.
2.  **Plateau Cluster** (ERA5 cell elevation < Station elevation): The lapse correction must apply a COOLING effect.
3.  If the baseline ERA5 model's bias aligns with these errors, both biases should step toward zero. 
4.  **TMIN Limitation:** TMIN is expected to behave worse than TMAX because nocturnal cold-air drainage and inversions violate the constant-lapse-rate assumption.

### 2.2 Validation Results (Moving-Block Bootstrap)
*Confidence intervals (95%) computed using a 10-day moving-block bootstrap to preserve temporal autocorrelation.*

#### Coastal Cluster (Elevation < 200m)
*   **TMAX (n=2,750):** 
    *   Naive ERA5: -4.54 °C [-4.64, -4.42]
    *   Downscaled: -4.15 °C [-4.25, -4.04]
    *   **Result:** Warmed by 0.39 °C. **CONFIRMED** (bias moved toward zero).
*   **TMIN (n=2,765):**
    *   Naive ERA5: +2.24 °C [+2.07, +2.40]
    *   Downscaled: +2.62 °C [+2.46, +2.80]
    *   **Result:** Warmed by 0.39 °C. **CONTRADICTED** (bias moved away from zero).

#### Plateau Cluster (Elevation 500-1000m)
*   **TMAX (n=2,712):**
    *   Naive ERA5: -1.23 °C [-1.30, -1.16]
    *   Downscaled: -1.50 °C [-1.58, -1.43]
    *   **Result:** Cooled by 0.27 °C. **CONTRADICTED** (bias moved away from zero).
*   **TMIN (n=3,083):**
    *   Naive ERA5: +1.26 °C [+1.19, +1.31]
    *   Downscaled: +0.99 °C [+0.92, +1.05]
    *   **Result:** Cooled by 0.27 °C. **CONFIRMED** (bias moved toward zero).

### 2.3 Interpretation and Known Limitations
The physical engine works exactly as designed: it unequivocally warms the coast and cools the plateau. However, the success of this downscaling depends entirely on the baseline ERA5 bias:
*   **Daytime (TMAX):** The lapse rate successfully improves TMAX on the coast but worsens it on the plateau (where ERA5 is already anomalously cold).
*   **Nighttime (TMIN):** As physically expected, a constant lapse rate fails for nocturnal coastal TMIN. Inversions and cold-air pooling frequently invert the natural lapse rate, rendering daytime parameters counterproductive at night. This is documented as a known physical limitation of the model.

> [!NOTE]
> **MAE and RMSE:** As predicted, sub-0.5°C corrections barely shift MAE/RMSE (e.g., Coastal TMAX MAE moved from 4.54 to 4.16). Bias was the correct metric for detecting the physical signal.

---

## 3. Unvalidated Layers (Humidity and Wind)

Because GHCN India daily records lack robust humidity and wind data, the following modules are physically derived but unvalidated against local telemetry.

### 3.1 Humidity Downscaling (`humidity.py`)
*   **Mechanism:** Conserves the parent cell's dewpoint temperature. Adjusts the surface pressure via the barometric formula using the elevation delta. Recomputes Relative Humidity (RH) from the downscaled temperature and conserved dewpoint using the Magnus-Tetens formula.
*   **Failure Modes:** Assumes absolute moisture (dewpoint) is spatially uniform across the 28km parent cell. Does not model sub-grid moisture pooling in valleys.
*   **Bounds:** RH is strictly clamped to [0, 100], and clamping instances are logged.

### 3.2 Wind Downscaling (`wind.py`)
*   **Mechanism:** Scales 10m wind speed (u, v magnitudes) based on a terrain exposure index (e.g., Topographic Position Index, Sx) derived from the 30m DEM. Preserves parent cell wind direction.
*   **Failure Modes:** **LEAST CONSTRAINED MODULE.** Terrain channeling of wind direction in valleys is entirely unmodelled. The exposure scaling is heuristic and unvalidated against local anemometer data.

## 4. Provenance Rules
*   Every numeric constant, coefficient, and threshold in `config.py` is explicitly cited.
*   The environmental lapse rate ($\Gamma$) is fixed strictly at 6.5 °C/km and is **never** fitted to the evaluation data.
*   ERA5-Land is strictly prohibited as a baseline input to ensure no circular topographic corrections are applied.
