# SIH074 Authoritative Numbers Pack & Traceability Registry

*Generated: 2026-09-03. Authoritative reference catalog for all numerical deliverables, statuses, citations, and formal retractions.*

---

## 1. Domain Dimensions & Accounting

| Quantity / Metric | Value | Source Citation | Status | Notes & Constraints |
|---|---|---|---|---|
| Domain Latitude Bounds | $13.0^\circ\text{N}$ to $17.5^\circ\text{N}$ (19 rows at $0.25^\circ$) | `engine/config/default.yaml:5` | `SOURCED` | Northern boundary row $i=0$ is $17.50^\circ\text{N}$ |
| Domain Longitude Bounds | $73.5^\circ\text{E}$ to $76.5^\circ\text{E}$ (13 cols at $0.25^\circ$) | `engine/config/default.yaml:6` | `SOURCED` | Eastern boundary col $j=12$ is $76.50^\circ\text{E}$ |
| Total Domain Grid Nodes | 247 nodes ($19 \times 13$) | `compute_b19_b20.py:12` | `SOURCED` | Canonical quarter-degree node centres |
| Land Grid Nodes | 231 nodes | `list_high_relief.py:18` | `SOURCED` | Nodes with valid SRTM elevation |
| Populated Grid Nodes | 210 nodes | `outputs/village_corrections.csv` | `SOURCED` | Nodes containing $\ge 1$ village centroid |
| Total Village Polygons Ingested | 16,945 features | `logs/item_ag_ar.log:177` | `SOURCED` | GA (402), KA (12,366), MH (4,177) |
| Dropped Null Polygons | 2 features (Maharashtra) | `logs/item_ag_ar.log:177` | `SOURCED` | Dropped during GEE DEM reduction |
| Successfully Reduced In-Domain Villages | 16,943 villages | `outputs/village_corrections.csv` | `SOURCED` | GA (402), KA (12,366), MH (4,175) |
| Exact Zero Elevation Difference ($\Delta z = 0.0\text{ m}$) | 0 villages | `run_reproduction.py:Assertion 6` | `SOURCED` | Injected zero yields strictly $\Delta T = 0.00^\circ\text{C}$ |
| Near-Zero Difference ($|\Delta z| < 0.05\text{ m}$) | 11 villages | `logs/item_b35_b39.log:94` | `SOURCED` | Rounds to $0.0\text{ m}$; forecast unchanged |
| Top-Decile Within-Cell Relief Cutoff ($P_{90}$) | $617.3\text{ m}$ | `logs/item_b40_b48.log:120` | `SOURCED` | Evaluated across 210 populated nodes |
| Median Model Orography Offset ($\bar{z}_{\text{SRTM}} - z_{\text{ERA5}}$) | $-2.86\text{ m}$ | `logs/item_b40_b48.log:121` | `SOURCED` | Fixed convention across 210 populated nodes |

---

## 2. Core Downscaling & Materiality (Item B1 Rebuild)

| Quantity / Metric | Value | Source Citation | Status | Notes & Constraints |
|---|---|---|---|---|
| Environmental Lapse Rate ($\Gamma$) | $6.5^\circ\text{C/km}$ ($0.0065^\circ\text{C/m}$) | `engine/deterministic/config.py:12` | `SOURCED` | Fixed physical constant, never fitted |
| Maximum Elevation Difference ($\max \Delta z_{\text{ERA5}}$) | $+640.5\text{ m}$ (`Dattathreyapeeta`) | `logs/item_b17_b25.log:63` | `SOURCED` | Node ERA5: $1,257.5\text{ m}$; Village: $1,898.0\text{ m}$ |
| Minimum Elevation Difference ($\min \Delta z_{\text{ERA5}}$) | $-519.0\text{ m}$ (`Nagave`) | `logs/item_b17_b25.log:63` | `SOURCED` | Node ERA5: $584.2\text{ m}$; Village: $65.2\text{ m}$ |
| Permanent Arithmetic Ceiling Bound | $981.47\text{ m}$ | `logs/item_b17_b25.log:45` | `SOURCED` | $\max \|\Delta z_{\text{SRTM}}\| (635.0\text{m}) + \max \|\text{offset}\| (346.47\text{m})$ |
| Materiality Threshold (Operational) | $150.0\text{ m}$ ($|\Delta T| \ge 0.975^\circ\text{C}$) | `logs/item_b17_b25.log:64` | `SOURCED` | Factor of $1.30\times$ above plateau baseline MAE |
| Material Villages at Operational Threshold | 1,403 / 16,943 (8.28%) | `logs/item_b17_b25.log:64` | `SOURCED` | 741 cooling (4.37%), 662 warming (3.91%) |
| Materiality Threshold (Floor-Matched) | $115.54\text{ m}$ ($|\Delta T| \ge 0.751^\circ\text{C}$) | `docs/feasibility_gate.md:Update 13` | `SOURCED` | Exactly matches baseline plateau model MAE |
| Material Villages at Floor-Matched Threshold | 2,108 / 16,943 (12.44%) | `docs/feasibility_gate.md:Update 13` | `SOURCED` | 1,075 cooling (6.34%), 1,033 warming (6.10%) |
| Area-Weighted SRTM Conservation | $+3.35\text{ m}$ | `run_reproduction.py:Assertion 4` | `SOURCED` | Strict conservation across domain ($\le \pm 5.0\text{ m}$) |
| Valid Validation Stations | 5 stations | `logs/item_b35_b39.log:6` | `SOURCED` | Chitradurga, Gadag, Karwar, Honavar, Goa/Panjim |
| Plateau Baseline Temperature MAE | $0.751^\circ\text{C}$ | `docs/deterministic_validation.md:42` | `SOURCED` | Evaluated across plateau validation stations |

---

## 3. Flagship Exhibit: Node $(13.25^\circ\text{N}, 75.25^\circ\text{E})$

| Quantity / Metric | Value | Source Citation | Status | Notes & Constraints |
|---|---|---|---|---|
| Flagship Node Coordinates | $(13.25^\circ\text{N}, 75.25^\circ\text{E})$ | `logs/item_b17_b25.log:101` | `SOURCED` | Box $[13.125, 13.375]^\circ\text{N} \times [75.125, 75.375]^\circ\text{E}$ |
| Village Count | 33 | `logs/item_b17_b25.log:104` | `SOURCED` | Contiguous polygons whose centroids fall in box |
| Node ERA5 Orography | $528.6\text{ m}$ | `logs/item_b17_b25.log:102` | `SOURCED` | Constant across all 33 villages |
| Node SRTM Areal Mean | $875.1\text{ m}$ | `logs/item_b17_b25.log:102` | `SOURCED` | Constant across all 33 villages |
| Elevation Span | $801.8\text{ m}$ | `logs/item_b17_b25.log:105` | `SOURCED` | $290.1\text{ m}$ (`Idu`) to $1,091.9\text{ m}$ (`Samse`) |
| Split vs ERA5 Node | 32 cooling / 1 warming | `logs/item_b17_b25.log:106` | `SOURCED` | Driven by $-346.5\text{ m}$ model ridge smoothing deficit |
| Split vs SRTM Node-Box Mean | 14 cooling / 19 warming | `logs/item_b26_b10.log:40` | `SOURCED` | Demonstrates true subgrid microclimate split |
| Model Deficit Domain Rank | 1 of 231 land nodes | `logs/item_b26_b10.log:37` | `SOURCED` | Most severe model-orography depression in domain ($0.4\text{th}\%$) |
| Retained Interior Companion Node | $(15.00^\circ\text{N}, 74.50^\circ\text{E})$ | `logs/item_b40_b48.log:127` | `SOURCED` | Range $536.9\text{ m}$, offset $-5.18\text{ m}$ ($2.3\text{ m}$ from median) |

---

## 4. In-Window Agronomic & Meteorological Variables

| Quantity / Metric | Value | Source Citation | Status | Notes & Constraints |
|---|---|---|---|---|
| In-Window Validation Period | 2015-06-01 to 2018-05-31 | `outputs/daily_station_validation_series.csv` | `SOURCED` | 1,096 consecutive days across 5 valid stations |
| In-Window Station Observational Coverage | 5,156 / 5,480 days (94.1%) | `logs/item_b40_b48.log:39` | `SOURCED` | Explicit `observation_present` flag on disk |
| ETo Formulation | Hargreaves-Samani (1985) | `engine/deterministic/eto.py:25` | `SOURCED` | Justified by grass crop albedo ($\alpha=0.23$) mismatch |
| In-Window Monsoon Date | 2017-07-15 (DOY 196) | `data/cache/in_window_daily_extremes.npz` | `SOURCED` | Full 24-hr WeatherBench-2 series |
| Monsoon Downscaled ETo Mean | $2.98\text{ mm/day}$ (1.71–5.29) | `compute_in_window_b42_b43_b44.py:50` | `SOURCED` | Diurnal range non-degenerate ($TD \ge 1.22^\circ\text{C}$) |
| Monsoon Heat Stress Triggers ($T_{\max} \ge 35^\circ\text{C}$) | 0 / 16,943 (0.00%) | `compute_in_window_b42_b43_b44.py:51` | `SOURCED` | Max village $T_{\max} = 34.57^\circ\text{C}$ (`Kudal`, `mh1:24119`) |
| Monsoon High Irrigation Triggers ($\text{ETo} > 5.0\text{ mm/d}$) | 377 / 16,943 (2.23%) | `compute_in_window_b42_b43_b44.py:52` | `SOURCED` | Discovered in hot leeward plains |
| In-Window Pre-Monsoon Date | 2018-04-30 (DOY 120) | `data/cache/in_window_daily_extremes.npz` | `SOURCED` | Full 24-hr WeatherBench-2 series |
| Pre-Monsoon Downscaled ETo Mean | $5.85\text{ mm/day}$ (1.79–7.83) | `compute_in_window_b42_b43_b44.py:65` | `SOURCED` | Diurnal range non-degenerate ($TD \ge 0.90^\circ\text{C}$) |
| Pre-Monsoon Heat Stress Triggers ($T_{\max} \ge 35^\circ\text{C}$) | 9,881 / 16,943 (58.32%) | `compute_in_window_b42_b43_b44.py:66` | `SOURCED` | Lowlands trigger; cool ridges remain $< 35^\circ\text{C}$ |
| Pre-Monsoon High Irrigation Triggers ($\text{ETo} > 5.0\text{ mm/d}$) | 14,597 / 16,943 (86.15%) | `compute_in_window_b42_b43_b44.py:67` | `SOURCED` | High evaporative demand across domain |
| Clamping Threshold Elevation | $319.6\text{ m}$ | `fetch_d2m_and_run_clamp.py:90` | `SOURCED` | Lowest elevation where RH is clamped |
| Permanent Clamping Saturation Elevation | $1,142.0\text{ m}$ | `logs/item_b35_b39.log:97` | `SOURCED` | Elevation above which 100% of villages require clamping |
| Block Wind Speed | ERA5 10m Wind | `outputs/village_corrections.csv` | `SOURCED` | Sourced from ARCO ERA5 10m wind |
| TPI Wind Speed Modifier | Heuristic scale | `engine/deterministic/wind.py:15` | `ESTIMATED — NO SOURCE` | Unvalidated terrain multiplier |

---

## 5. Formal Retraction & Superseded Figures Registry

| Retracted Quantity | Erroneous / Retired Value | Retraction Reason & True Superseding Value | Retraction Anchor |
|---|---|---|---|
| Out-of-Window 2020-04-30 Advisory Pair | 48.78% Heat Stress / 74.63% High ETo | Retired as out-of-window exploratory snapshot; superseded by in-window 2018-04-30 values (58.32% and 86.15%) | `docs/feasibility_gate.md:Update 14` |
| 231-Node Relief Cutoff | $615.7\text{ m}$ | Replaced by canonical 210 populated-node cutoff of $617.3\text{ m}$ | `docs/feasibility_gate.md:Update 14` |
| B15 Ten-Digit Code Prefix Claim | "Ten-digit codes are prefix truncations" | Torane is `275270426403894800` (Satara/Patan), not `27531...` (Sangli); prefix match invalidated | `docs/feasibility_gate.md:Retraction Task B38` |
| Item AQ Maharashtra Ingestion Total | 4,177 villages | Contained 2 null polygons dropped in reduction; true in-domain count is 4,175 | `logs/item_b40_b48.log:109` |
| Edge-Row Node (17.50°N, 74.00°E) | Companion candidate | Dropped due to domain mask boundary truncation of box areal mean | `logs/item_b40_b48.log:129` |
| Assignment Fault Diagnoses | "19.6 km diagonal misregistration in assignment" | Centroid nearest-node argmin was 100% correct; flaw was raster corner-value lookup | `docs/feasibility_gate.md:246` |
| B0 Attributed Domain Min Node | $(13.50^\circ\text{N}, 75.00^\circ\text{E})$ | Transcription error in prose; true domain min offset ($-346.47\text{ m}$) belongs uniquely to flagship node $(13.25^\circ\text{N}, 75.25^\circ\text{E})$ | `docs/feasibility_gate.md:Update 13` |
| Retired Grid Offset Distribution | Min $-255.07\text{ m}$, mean $-15.61\text{ m}$, max $+180.08\text{ m}$ | Sampled at raster corners; superseded by canonical node grid (min $-346.47\text{ m}$, mean $-1.15\text{ m}$, max $+152.76\text{ m}$) | `docs/feasibility_gate.md:255` |
| Retired Arithmetic Bound | $865.8\text{ m}$ | Built on corner-sampled extremes; superseded by canonical $981.47\text{ m}$ bound | `docs/feasibility_gate.md:256` |
| Retired Flagship Exhibits | BH (32 villages) & BS (30 villages) | Assembled by matching coarse elevation ($\approx 658.4\text{ m}$); superseded by B21 canonical 33-village box | `docs/feasibility_gate.md:254` |
| BT's Area-Weighted Mean $\Delta z_{\text{ERA5}}$ | $+5.56\text{ m}$ (and $+25.54\text{ m}$ subset) | Derived on corner grid; superseded by canonical node-centred evaluations | `docs/feasibility_gate.md:257` |
| Belgaum Validation Citation | IN009021000 / IN009021100 | Sited 9 km from town with mixed instrument roles; Belgaum excluded from validation | `docs/feasibility_gate.md:18` |
| Stale CSV Advisory Columns (2020 Snapshot) | 48.78% Heat Stress / 74.63% High ETo | Superseded in `outputs/village_corrections.csv` (old MD5: `42157952f3441d1ce6fb06910c032c6b`) by genuine in-window values (2018-04-30: 58.32% Heat Stress / 86.15% High ETo; 2017-07-15: 0.00% / 2.23%) using true 24-hr mean, with out-of-window RH explicitly marked 2020_04_30; new authoritative MD5: `52b119f0b4f2441592f2d3af866eef3f` | `docs/feasibility_gate.md:Update 15` |

---

## 6. Pre-Monsoon Heat Stress Advisory Rounding Inconsistency (Item J3)

### Physical Root Cause: Full Precision vs 2-Decimal Display Storage
In `outputs/village_corrections.csv`, the agro-meteorological advisory flag `real_prem_heat_stress` is evaluated during downscaling execution against full IEEE 754 floating-point temperature values:
$$\text{heat\_p} = \begin{cases} 1 & \text{if } T_{\text{fine, max}} \ge 35.0^\circ\text{C} \\ 0 & \text{if } T_{\text{fine, max}} < 35.0^\circ\text{C} \end{cases}$$
The resulting authoritative physical trigger count across the domain is **9,881 / 16,943 villages (58.32%)**.

However, when temperature arrays are formatted and stored into the tabular CSV, values in `real_prem_tmax_c` are rounded to two decimal places:
$$\text{real\_prem\_tmax\_c} = \text{round}(T_{\text{fine, max}}, 2)$$

For exactly **11 villages**, unrounded fine temperatures lie in the half-open interval $[34.995, 35.000)^\circ\text{C}$. For these villages:
1. Full-precision downscaled temperature is strictly $< 35.000^\circ\text{C}$, so `real_prem_heat_stress` is recorded as `0`.
2. Stored display column `real_prem_tmax_c` rounds half-up to `35.00`.
3. A post-hoc SQL or pandas filter re-evaluating `df['real_prem_tmax_c'] >= 35.0` evaluates `35.00 >= 35.0` as `True`, resulting in **9,892 triggers** ($9,881 + 11$).

### Affected Village IDs & Properties
The 11 villages affected by this precision threshold artifact are:
1. `ka.geojson:3960` — **Bisalehalli** (Karnataka): $T_{\text{unrounded}} = 34.9958^\circ\text{C} \to$ stored `35.00`
2. `ka.geojson:5386` — **Malligenahalli** (Karnataka): $T_{\text{unrounded}} = 34.9986^\circ\text{C} \to$ stored `35.00`
3. `ka.geojson:5460` — **Hanumanthapura** (Karnataka): $T_{\text{unrounded}} = 34.9986^\circ\text{C} \to$ stored `35.00`
4. `ka.geojson:5517` — **Echavadi** (Karnataka): $T_{\text{unrounded}} = 34.9986^\circ\text{C} \to$ stored `35.00`
5. `ka.geojson:5601` — **Bhadravati Tmc** (Karnataka): $T_{\text{unrounded}} = 34.9986^\circ\text{C} \to$ stored `35.00`
6. `ka.geojson:5640` — **Kodihalli Og** (Karnataka): $T_{\text{unrounded}} = 34.9986^\circ\text{C} \to$ stored `35.00`
7. `ka.geojson:21484` — **Uppunse** (Karnataka): $T_{\text{unrounded}} = 34.9958^\circ\text{C} \to$ stored `35.00`
8. `mh2.geojson:7646` — **Jambharmala** (Maharashtra): $T_{\text{unrounded}} = 34.9972^\circ\text{C} \to$ stored `35.00`
9. `mh2.geojson:8044` — **Namasgaon** (Maharashtra): $T_{\text{unrounded}} = 34.9972^\circ\text{C} \to$ stored `35.00`
10. `mh2.geojson:8196` — **Pandur** (Maharashtra): $T_{\text{unrounded}} = 34.9972^\circ\text{C} \to$ stored `35.00`
11. `mh2.geojson:9526` — **Ondosha** (Maharashtra): $T_{\text{unrounded}} = 34.9972^\circ\text{C} \to$ stored `35.00`

### Engineering Recommendation
We recommend either storing temperatures at 3-decimal precision (e.g. `34.996`) or shipping an explicit unrounded floating-point column (`raw_prem_tmax_c`), so that downstream tabular threshold queries replicate the authoritative physical evaluation without rounding edge artifacts. Per standing audit policy, the column is preserved unchanged in the published dataset.


### Monsoon Tmean Variable Integrity Audit (Item J5-1)
- **Column**: `real_jjas_tmean_c`
- **Integrity Status**: `VERIFIED_AUTHENTIC`
- **Audit Findings**: Audited across all 16,943 villages against `data/cache/in_window_daily_extremes.npz`. Exactly 0 rows equal `real_jjas_tmin_c` and 16,943 rows reflect true 24-hour mean downscaled temperature ($T_{\text{mean}} = \text{ERA5 } T_{\text{mean}} + \Delta T_{\text{lapse}}$). A transcription typo in earlier audit prose displaying `t_f_min_j` was caught and corrected; on-disk scripts and published datasets are confirmed intact.

---
---

## 7. Relative Humidity Column Deprecation & Audit (Item J6)

- **Columns**: `rh_2020_04_30_pct` (Column 40), `rh_2020_04_30_clamped_flag` (Column 41)
- **Status**: **DEPRECATED - NOT FOR ADVISORY USE**
- **Reasons for Deprecation**:
  1. **Source Date Mismatch**: Underlying 2m dewpoint grid (`data/cache/d2m_grid.npz`) was extracted for **2020-07-15** (monsoon), matching neither validation window date (**2018-04-30** pre-monsoon, **2017-07-15** monsoon).
  2. **Mislabelled Column Name**: The column name `rh_2020_04_30_pct` and provenance manifest misstated the date as 2020-04-30. Retained solely for schema stability and MD5 verification.
  3. **Superseded Temperature Vintage**: Saturation vapor pressure $e_s(T)$ was evaluated against the retired 2020 diurnal snapshot (MD5 `42157952f3441d1ce6fb06910c032c6b`), not against the authentic in-window temperatures.
  4. **Psychrometric Clamping**: 483 rows (2.85%) were psychrometrically clamped at $100.0\%$.
- **Downstream Isolation**: Exactly **0 assertions, figures, or published advisory metrics** consume either column.
- **Production Fix Requirements**: Requires fetching in-window ERA5 `2m_dewpoint_temperature` grids for 2017-07-15 and 2018-04-30 via Copernicus CDS credentials and running co-temporal psychrometric downscaling.
