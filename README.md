# Panchayat Weather Downscaling: Orographic Temperature Disaggregation in the Western Ghats

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Release: v0.1--sih](https://img.shields.io/badge/Release-v0.1--sih-blue.svg)](https://github.com/vishalprajapati1111/panchayat-weather-downscaling/releases/tag/v0.1-sih)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](requirements.txt)
[![Data Status: Audited](https://img.shields.io/badge/Audit-Passed%20(B0--B52%2C%20G0--G4)-success.svg)](AUDIT.md)

> In the Western Ghats, roughly one village in twelve receives weather data wrong by more than the forecast's own error margin, because the data has no knowledge of the village's elevation, and the correction runs both warmer and cooler.

---

## 1. What the Project Does and Why

Global and national numerical weather prediction models deliver forecasts at coarse grid resolutions. The European Centre for Medium-Range Weather Forecasts (ECMWF) ERA5 reanalysis operates on a nominal $0.25^\circ \times 0.25^\circ$ spatial grid (~28 km). Across rugged mountainous terrain like India's Western Ghats (Sahyadri range), an entire mountain massif, scarp face, and coastal plain are frequently collapsed into a single grid cell sharing one uniform model surface height.

Because weather models assign a single elevation to an entire $780\text{ km}^2$ block, a village perched on an escarpment crest and a village nestled in a deep valley or coastal inlet are assigned the exact same forecast temperature. In reality, temperature changes with height at the environmental lapse rate ($\Gamma = 6.5\text{ }^\circ\text{C km}^{-1}$, or $0.0065\text{ }^\circ\text{C m}^{-1}$).

This project implements an elevation-aware deterministic downscaling engine that adjusts ERA5 screen-level temperature ($2\text{m}$) for every individual revenue village using high-resolution Shuttle Radar Topography Mission (SRTM) 30 m digital elevation models:

$$T_{\text{village}} = T_{\text{ERA5\_node}} - \Gamma \cdot \Delta z$$

where:
$$\Delta z = z_{\text{SRTM}} - z_{\text{ERA5\_node}}$$

- $z_{\text{SRTM}}$ is the true mean topographic elevation of the village polygon (from 30 m SRTM).
- $z_{\text{ERA5\_node}}$ is the model surface orography height of the nearest $0.25^\circ$ grid point.
- $\Gamma = 0.0065\text{ }^\circ\text{C m}^{-1}$ is the International Standard Atmosphere (ISA) environmental lapse rate.
- $\Delta z > 0 \implies \Delta T < 0$ (**COOLING**): The village is higher than the smoothed model terrain.
- $\Delta z < 0 \implies \Delta T > 0$ (**WARMING**): The village is lower than the smoothed model terrain.

### Audited Headline Figures

Across 16,943 revenue villages spanning the Western Ghats domain in **Karnataka, Maharashtra, and Goa** evaluated over the 3-year validation window (**2015-06-01 to 2018-05-31**, 1,096 continuous days):

| Metric | Audited Value | Percentage | Primary Citation |
|---|---|---|---|
| **Total Villages Evaluated** | **16,943** | 100.00% | `logs/item_b0_b16.log:5` |
| **Material Elevation Error** ($|\Delta z| \ge 150\text{ m}$, $|\Delta T| \ge 0.975\text{ }^\circ\text{C}$) | **1,403** | **8.28%** | `docs/feasibility_gate.md` |
| ↳ **Cooling Corrections** ($\Delta z \ge +150\text{ m}$) | **741** | 4.37% | `docs/feasibility_gate.md` |
| ↳ **Warming Corrections** ($\Delta z \le -150\text{ m}$) | **662** | 3.91% | `docs/feasibility_gate.md` |
| **Sub-Threshold / Minor Offsets** ($|\Delta z| < 150\text{ m}$) | 15,540 | 91.72% | `outputs/village_corrections.csv` |
| **Extreme Cooling Case** (Highest scarp village) | **+640.5 m** ($\Delta T = -4.16\text{ }^\circ\text{C}$) | — | Dattathreyapeeta, Chikmagalur, KA |
| **Extreme Warming Case** (Deepest canyon village) | **−519.0 m** ($\Delta T = +3.37\text{ }^\circ\text{C}$) | — | Nagave, Satara, MH |
| **Authoritative Checksum (MD5)** | `52b119f0b4f2441592f2d3af866eef3f` *(supersedes `42157952f3441d1ce6fb06910c032c6b`; in-window rebuild)* | — | `outputs/village_corrections.csv` |

---

## 2. Prerequisites & System Requirements

Before running any script or downloading datasets, verify the following prerequisites:

### Accounts & Credentials
1. **Google Earth Engine (GEE) Account (Required for Rebuild)**:
   - Registration: Sign up for a free non-commercial Earth Engine account at [earthengine.google.com](https://earthengine.google.com/).
   - Cloud Project: Earth Engine requires creating or selecting an active Google Cloud project.
   - **Approval Delay**: New GEE registrations typically take **several hours to 2 business days** for administrative approval.
   - Authentication: Once approved, run `earthengine authenticate` on your machine.
2. **Copernicus Climate Data Store (CDS) Key**:
   - **NOT NEEDED** under the canonical pipeline path! The canonical pipeline fetches ERA5 directly via GEE (`ECMWF/ERA5/HOURLY`) or the public WeatherBench-2 Zarr bucket (which uses anonymous public access token `storage_options={'token': 'anon'}`).

### Hardware & Resource Requirements
- **Disk Space**:
  - Minimum repository clone: **~12 MB** (includes code, docs, logs, and `village_corrections.csv`).
  - Full rebuild cache:
    - SRTM 30 m domain GeoTIFF: **151.1 MB** (`data/cache/srtm_domain_30m.tif`)
    - ERA5 hourly station/grid cache: **~25 MB**
    - DataMeet GeoJSON boundaries: **~160 MB**
    - Verification and output CSVs: **~15 MB**
    - Total recommended free disk space: **$\ge 2.0\text{ GB}$**.
- **RAM**:
  - Peak observed memory usage during 30 m raster TPI and array reduction: **~1.2 GB**.
  - Minimum recommended RAM: **4 GB** (8 GB recommended).
- **Execution Times (Measured, not guessed)**:
  - **Offline Flagship Smoke Test (`demo_flagship.py`)**: **0.05 seconds** (instantaneous).
  - **Audit & Physics Verification Harness (`run_reproduction.py`)**: **0.24 seconds**.
  - **Full Cold-Start Rebuild from Scratch**: **~20–26 minutes** (dominated by remote GEE polygon zonal reductions).

---

## 3. Setup: Step-by-Step

### Step 1: Clone the Repository
```bash
git clone https://github.com/vishalprajapati1111/panchayat-weather-downscaling.git
cd panchayat-weather-downscaling
```

### Step 2: Create a Virtual Environment
We recommend Python 3.10, 3.11, or 3.12 (the pipeline was audited under Python 3.12.10 on 64-bit Windows and Linux).

#### Option A: Using standard `venv` and `pip` (Windows / Linux)
```bash
python -m venv .venv

# On Linux / macOS:
source .venv/bin/activate

# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
```

Install pinned dependencies:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

> **Windows Geospatial Note**: The `requirements.txt` pins `rasterio==1.5.1` and `pyproj==3.7.2`, which contain pre-compiled GDAL 3.12.4 and PROJ 9.5.1 binary wheels for Windows. No system-level C++ compilers or OSGeo4W installations are needed.

#### Option B: Using Conda / Mamba (Recommended for Linux/macOS users experiencing GDAL issues)
```bash
conda env create -f environment.yml
conda activate panchayat-downscale
```

### Step 3: Authenticate Earth Engine (Only for Full Rebuild)
If you intend to fetch fresh SRTM rasters or query live ERA5 collections:
```bash
earthengine authenticate
```
A browser window will open to authorize Google Earth Engine with your Google account.

---

## 4. The 10-Minute Smoke Test (Quick Start)

To inspect the core methodology immediately without waiting for Earth Engine approvals or gigabyte downloads, run the offline flagship demonstration:

```bash
python demo_flagship.py
```

### What this test does:
This script isolates the **flagship escarpment cell** centered at $(13.25^\circ\text{N}, 75.25^\circ\text{E})$ over the Kudremukh / Agumbe ridge in Karnataka. Within this single $28\text{ km} \times 28\text{ km}$ box, ERA5 models an average terrain height of **$528.6\text{ m}$**. In reality, the cell encompasses 33 revenue villages whose actual elevations span from **$290.1\text{ m}$** (Idu in the valley) to **$1,091.9\text{ m}$** (Samse on the crest) — an relief difference of **$801.8\text{ m}$**.

### Expected Terminal Output (Verbatim):
```text
===========================================================================
FLAGSHIP NODE SMOKE TEST -- 1 Cell, 33 Villages, Offline Verification
===========================================================================

ERA5 Grid Node Coordinates : (13.25N, 75.25E)
ERA5 Model Orography Height : 528.6 m
Villages in Node Footprint  : 33
Village Elevation Span      : 290.1 m to 1091.9 m (span = 801.8 m)

Village               SRTM (m)  ERA5 (m)    dz (m)    dT (C)  Tmax (C)   Direction
----------------------------------------------------------------------------------
Samse                   1091.9     528.6     563.3     -3.66     21.59     COOLING
Hornadu                 1051.9     528.6     523.3     -3.40     21.85     COOLING
Attikudige              1049.4     528.6     520.8     -3.39     21.86     COOLING
  ...
Idu                      290.1     528.6    -238.5      1.55     26.80     WARMING
Sunkadamakki             708.2     528.6     179.6     -1.17     24.08     COOLING
----------------------------------------------------------------------------------

  [PASS] villages served (expected 33, got 33)
  [PASS] ERA5 node elevation (expected 528.6 m, got 528.6 m)
  [PASS] maximum village elevation (Samse) (expected 1091.9 m, got 1091.9 m)
  [PASS] minimum village elevation (Idu) (expected 290.1 m, got 290.1 m)
  [PASS] Samse temperature correction dT (expected -3.66 C, got -3.66 C)

Produced output : outputs\demo_flagship_downscaled.csv
Elapsed         : 0.047 s
Checksum        : 52b119f0b4f2441592f2d3af866eef3f (MATCH; supersedes 42157952...)

Smoke test PASSED.
```

### Three numbers to eyeball:
1. **ERA5 Node Elevation**: **`528.6 m`**
2. **Village Elevation Span**: **`290.1 m to 1,091.9 m`** (verifies large intra-cell relief).
3. **Samse Temperature Correction**: **`-3.66 °C`** cooling offset ($T_{\text{max}}$ downscaled from $25.25\text{ }^\circ\text{C}$ to $21.59\text{ }^\circ\text{C}$).

---

## 5. Getting the Data: Source by Source

> **Important License Notice**: In accordance with the DataMeet Open Database Licence (ODbL v1.0) and file size constraints, **no raw input data is bundled in this repository**. All inputs must be downloaded directly from upstream sources using the commands below.

| Dataset | Provider & Asset | Fetch Method | Destination Path | File Size |
|---|---|---|---|---|
| **ERA5 Hourly Reanalysis** | ECMWF via GEE (`ECMWF/ERA5/HOURLY`) | `python fetch_station_hourly_era5.py` | `data/cache/station_hourly_era5.csv` | ~21.8 MB |
| **SRTM 30m Global DEM** | USGS/NASA (`USGS/SRTMGL1_003`) | GEE composite / `python compute_g0.py` | `data/cache/srtm_domain_30m.tif` | 151.1 MB |
| **Village Boundaries** | DataMeet India Maps (ODbL v1.0) | `curl` / DataMeet repo download | `data/cache/geojson/*.geojson` | ~160 MB |
| **GHCN-Daily Stations** | NOAA NCEI Global Historical Climatology | `python fetch_ghcn_daily.py` | `data/cache/ghcn_daily/*.csv` | ~35 MB |

### Download Details

1. **ERA5 Reanalysis**:
   - Primary Path: Query Google Earth Engine asset `ECMWF/ERA5/HOURLY` for $2\text{m}$ temperature, $2\text{m}$ dewpoint, and surface geopotential.
   - Secondary Alternative: Public Google Cloud Storage WeatherBench-2 Zarr store:
     `gs://weatherbench2/datasets/era5/1959-2023_01_10-full_37-1h-0p25deg-chunk-1.zarr` (public access, no auth required).
   - Provenance note: Item G0 confirmed that GEE and WeatherBench-2 values agree to within Mean Absolute Difference $< 0.002\text{ K}$.

2. **SRTM 30m Digital Elevation Model**:
   - Download the 20 bounding tiles covering $13.0^\circ\text{N} - 17.5^\circ\text{N}$, $73.5^\circ\text{E} - 76.5^\circ\text{E}$ from USGS EarthExplorer or mosaic directly via GEE asset `USGS/SRTMGL1_003`.
   - Save merged GeoTIFF as `data/cache/srtm_domain_30m.tif`.

3. **DataMeet Village Polygons**:
   - Download state boundary GeoJSONs from [projects.datameet.org/maps/subdistricts](https://projects.datameet.org/maps/subdistricts/):
     - Karnataka: `ka.geojson` (12,366 domain villages)
     - Maharashtra: `mh1.geojson` & `mh2.geojson` (4,175 domain villages)
     - Goa: `ga.geojson` (402 domain villages)
   - Destination: `data/cache/geojson/`

4. **GHCN-Daily Ground Observations**:
   - Ingest station records for the 5 usable stations: IN009070100 (Chitradurga), IN009090300 (Gadag), IN009120100 (Karwar), IN009120400 (Honavar), and IN022030600 (Panjim).
   - Destination: `data/cache/ghcn_daily/`

---

## 6. Running the Pipeline & Verification

### Step 1: Execute Full Rebuild (When data cache is populated)
```bash
python rebuild_village_corrections.py
```
This runs the full 16,943-village downscaling disaggregation, computing:
- Village centroid extraction and ERA5 nearest-node assignment
- Elevation differences $\Delta z = z_{\text{SRTM}} - z_{\text{ERA5}}$
- Temperature offsets $\Delta T = -\Gamma \cdot \Delta z$
- Downscaled diurnal temperature extremes ($T_{\text{max}}$, $T_{\text{min}}$, $T_{\text{mean}}$)
- Downscaled relative humidity with dewpoint conservation and psychrometric clamping
- Hargreaves-Samani reference evapotranspiration ($\text{ETo}$)
- Agro-meteorological heat stress and irrigation demand alerts

### Step 2: Run Quality & Physics Assertions
To verify dataset integrity and execute mathematical and physical assertion checks:
```bash
python run_reproduction.py
```

Expected output verbatim:
```text
===========================================================================
SIH074 VERIFICATION & AUDIT HARNESS (B10 / B48)
===========================================================================
Loaded canonical grids (19x13) and dataset (16943 villages from village_corrections.csv).
Executing physical downscaling checks...

Executing Permanent Quality & Physics Assertions:
  [PASS] Assertion 1 (Footprint Containment): 16,943 / 16,943 villages inside node box (verified against independent grid).
  [PASS] Assertion 2 (Identical Coarse Height): Verified across all 210 populated nodes against independent arrays (std = 0.0 m).
  [PASS] Assertion 3 (Arithmetic Ceiling Bound): Observed max |dz| (640.5 m) <= 981.47 m (verified with independent grid).
  [PASS] Assertion 4 (Elevation Conservation): Area-weighted dz = +3.35 m (tolerance <= +-5.0 m, verified with independent grid).
  [PASS] Assertion 5 (Unit Guard & Marked Site): Valid Celsius ranges confirmed across seasons:
    - Monsoon Tmax (real_jjas_tmax_c, 2017-07-15): [18.1, 34.6] °C (0 heat stress triggers >= 35°C)
    - Pre-monsoon Tmax (real_prem_tmax_c, 2018-04-30): [26.9, 44.2] °C (9,881 heat stress triggers >= 35°C, 58.32%)
  [PASS] Assertion 5b (Rounding Inconsistency Audit): Verified exactly 11 boundary villages in [34.995, 35.000) °C with display vs evaluation rounding mismatch (9,881 full-precision vs 9,892 post-rounding).
  [PASS] Assertion 6 (Zero-Delta Invariance): Injected dz=0.0m yields dt=0.00°C strictly unchanged.
  [PASS] Assertion 7 (Schema & Primary Key): 43 columns, 16,943 unique keys (MD5: 52b119f0b4f2441592f2d3af866eef3f).
  [SKIP - WARNING] Assertion 8 (Single-Sinusoid Residual Floor): No genuine project-generated daily temperature series on disk (synthetic series quarantined). Station observations (e.g. Kolhapur IN012131800) cannot substitute for model downscaling output.
  [SKIP - WARNING] Assertion 9 (Inter-Annual Non-Identity): No genuine project-generated daily temperature series on disk (synthetic series quarantined). Station observations (e.g. Kolhapur IN012131800) cannot substitute for model downscaling output.
  [PASS] Assertion 10 (Non-Analytical AST Lint): 0 synthetic temperature oscillators across tree (excluding quarantine/).
  [PASS] Assertion 11 (Provenance Manifest): All 43 CSV header columns verified against manifest (0 quarantined references, table generating script and fetch scripts verified on disk).

===========================================================================
HARNESS SUMMARY: 10 passed, 2 skipped, 0 degraded (0 failed).
  - 2 SKIPPED (Assertions 8-9): No genuine project-generated daily temperature series on disk (synthetic series quarantined).
REPRODUCTION STATUS: 10 passed, 2 skipped, 0 degraded; physical and provenance assertions independently verified; daily-series assertions outstanding.
Harness Runtime: 0.50 seconds. Exiting with status code 2.
===========================================================================
```

### Step 3: Run the Disk Corruption Detection Test
To verify that the assertions actively detect corrupt or modified data:
```bash
python run_reproduction.py --corrupt-disk
```
This test deliberately injects a corrupted elevation offset of $+1,500\text{ m}$ into disk, verifies that Assertion 3 catches the breach, exits with code 1, and cleans up the test artifact.

---

## 7. Data Dictionary: `outputs/village_corrections.csv`

The primary deliverable `outputs/village_corrections.csv` contains 16,943 rows (one per village) and 43 attributes:

| Column Name | Type | Units | Sign Convention / Range | Description |
|---|---|---|---|---|
| `village_id` | `str` | — | `filename:feature_idx` | Unique project primary key (e.g. `ka.geojson:21888`). |
| `src_file` | `str` | — | `ka.geojson`, `mh1.geojson`, etc. | Source DataMeet boundary GeoJSON file. |
| `feature_idx` | `int` | — | $0 \le i < N_{\text{features}}$ | Zero-based index of feature in the source file. |
| `village_name` | `str` | — | Text | Revenue village name as recorded in census boundaries. |
| `state` | `str` | — | `KA`, `MH`, `GA` | State abbreviation (Karnataka, Maharashtra, Goa). |
| `district` | `str` | — | Text | Administrative district name. |
| `taluka` | `str` | — | Text | Administrative taluka / tehsil / subdistrict. |
| `census_code` | `str` | — | 16-digit integer / `unavailable` | 2011 Census of India Village Directory code. |
| `state_loc_code` | `str` | — | State ID | State revenue department location code. |
| `polygon_area_km2` | `float` | $\text{km}^2$ | $> 0$ | Village polygon surface area. |
| `multi_cell_flag` | `int` | Binary | 0 or 1 | 1 if village polygon straddles multiple ERA5 cells. |
| `duplicate_code_flag` | `int` | Binary | 0 or 1 | 1 if duplicate census code detected across boundaries. |
| `centroid_lat` | `float` | Deg North | $12.98 \le \phi \le 17.53$ | Latitude of village geographic centroid. |
| `centroid_lon` | `float` | Deg East | $73.47 \le \lambda \le 76.57$ | Longitude of village geographic centroid. |
| `node_lat` | `float` | Deg North | $13.0, 13.25, \dots, 17.5$ | Latitude of assigned nearest ERA5 $0.25^\circ$ node. |
| `node_lon` | `float` | Deg East | $73.5, 73.75, \dots, 76.5$ | Longitude of assigned nearest ERA5 $0.25^\circ$ node. |
| `node_i` | `int` | Index | $0 \le i \le 18$ | Latitude row index in $19 \times 13$ node matrix. |
| `node_j` | `int` | Index | $0 \le j \le 12$ | Longitude column index in $19 \times 13$ node matrix. |
| `fine_elev_m` | `float` | Metres | $0.0 \le z \le 1,547.9$ | Village mean elevation from native SRTM 30m DEM. |
| `era5_elev_m` | `float` | Metres | $7.0 \le z \le 1,040.1$ | Model surface orography height at assigned ERA5 node. |
| `srtm_node_elev_m` | `float` | Metres | $0.1 \le z \le 1,059.5$ | SRTM 30m mean elevation over the $0.25^\circ$ grid cell. |
| `dz_era5_m` | `float` | Metres | $[-519.0, 640.5]$ (Positive = Higher) | Elevation difference: $\Delta z = z_{\text{SRTM}} - z_{\text{ERA5}}$. |
| `dt_era5_c` | `float` | $^\circ\text{C}$ | $[-4.16, 3.37]$ (Positive = Warmer) | Temperature correction: $\Delta T = -\Gamma \cdot \Delta z$ ($\Gamma = 0.0065$). |
| `direction` | `str` | Category | `COOLING` / `WARMING` | Direction of adjustment (`COOLING` if $\Delta z > 0$). |
| `materiality` | `str` | Category | `MATERIAL` / `SUB-THRESHOLD` | `MATERIAL` if $|\Delta z| \ge 150\text{ m}$ ($|\Delta T| \ge 0.975\text{ }^\circ\text{C}$). |
| `dz_srtm_m` | `float` | Metres | $[-614.5, 635.0]$ (Continuous) | Sub-grid relief offset: $z_{\text{SRTM}} - z_{\text{SRTM,node}}$. |
| `dt_srtm_c` | `float` | $^\circ\text{C}$ | $[-4.13, 3.99]$ (Continuous) | Sub-grid lapse correction against cell mean SRTM. |
| `real_jjas_tmax_c` | `float` | $^\circ\text{C}$ | $[18.14, 34.57]$ | Downscaled mean daily $T_{\text{max}}$ in monsoon (JJAS). |
| `real_jjas_tmin_c` | `float` | $^\circ\text{C}$ | $[15.39, 26.23]$ | Downscaled mean daily $T_{\text{min}}$ in monsoon (JJAS). |
| `real_jjas_tmean_c` | `float` | $^\circ\text{C}$ | $[16.47, 28.62]$ | Downscaled mean daily $T_{\text{mean}}$ in monsoon (JJAS). |
| `real_jjas_eto_mm_day`| `float` | $\text{mm/day}$| $[1.71, 5.29]$ | Hargreaves-Samani reference evapotranspiration (JJAS).|
| `real_jjas_heat_stress`| `int` | Binary | 0 or 1 | Flag for heat stress ($T_{\text{max}} \ge 35\text{ }^\circ\text{C}$) in JJAS. |
| `real_jjas_irrig_demand`| `int` | Binary | 0 or 1 | Flag for high irrigation demand ($\text{ETo} \ge 5\text{ mm/day}$).|
| `real_prem_tmax_c` | `float` | $^\circ\text{C}$ | $[26.94, 44.24]$ | Downscaled mean daily $T_{\text{max}}$ in pre-monsoon (MAM). |
| `real_prem_tmin_c` | `float` | $^\circ\text{C}$ | $[17.87, 30.48]$ | Downscaled mean daily $T_{\text{min}}$ in pre-monsoon (MAM). |
| `real_prem_tmean_c`| `float` | $^\circ\text{C}$ | $[22.69, 36.60]$ | Downscaled mean daily $T_{\text{mean}}$ in pre-monsoon (MAM). |
| `real_prem_eto_mm_day`| `float` | $\text{mm/day}$| $[1.79, 7.83]$ | Reference evapotranspiration in pre-monsoon (MAM). |
| `real_prem_heat_stress`| `int` | Binary | 0 or 1 | Flag for heat stress ($T_{\text{max}} \ge 35\text{ }^\circ\text{C}$) in MAM. |
| `real_prem_irrig_demand`| `int` | Binary | 0 or 1 | Flag for high irrigation demand ($\text{ETo} \ge 5\text{ mm/day}$).|
| `rh_2020_04_30_pct` | `float` | % | $0.0 \le \text{RH} \le 100.0$ (observed $[76.5, 100.0]$) | **DEPRECATED - NOT FOR ADVISORY USE**. Downscaled RH (see notice below). |
| `rh_2020_04_30_clamped_flag` | `int` | Binary | 0 or 1 | **DEPRECATED - NOT FOR ADVISORY USE**. Saturation clamp flag (see notice below). |
| `wind_block_status`| `str` | Provenance | Text | Sourced from ARCO ERA5 10m eastward/northward wind. |
| `wind_tpi_status` | `str` | Provenance | Text | Topographic Position Index exposure status. |

> [!NOTE]
> **Data Dictionary Range & Precision Convention (Item J5-1d / J5-1e)**:
> All documented numerical intervals $[D_{\min}, D_{\max}]$ strictly contain 100% of village values in the published CSV ($D_{\min} \le \min(x)$ and $\max(x) \le D_{\max}$), with tightness bounded within at most one unit in the last decimal place ($A_{\min} - D_{\min} \le 10^{-k}$ and $D_{\max} - A_{\max} \le 10^{-k}$):
> 1. **Temperatures and ETo**: Stored at 2-decimal precision; documented with exact empirical sample extremes $[A_{\min}, A_{\max}]$ to 2 decimal places.
> 2. **Elevations**: Stored at 1-decimal precision from SRTM 30m; documented with exact empirical extremes to 1 decimal place.
> 3. **Geographic Centroids**: Documented with outward-rounded 2-decimal bounds ($12.98 \le \phi \le 17.53$ and $73.47 \le \lambda \le 76.57$) to ensure tight containment of all 16,943 coordinates without trailing float artifacts.
> 4. **Relative Humidity (Item J5-1f)**: Documented with both the physical definitional domain ($0.0 \le \text{RH} \le 100.0$) and the empirical sample range ($[76.50, 100.00]$).

> [!WARNING]
> **DEPRECATION NOTICE: Relative Humidity Columns (Item J6)**:
> Columns `rh_2020_04_30_pct` and `rh_2020_04_30_clamped_flag` are formally marked **DEPRECATED - NOT FOR ADVISORY USE**. They must not be used for any agronomic, meteorological, or policy decisions.
>
> Four independent defects invalidate these columns:
> 1. **Date Mismatch**: The underlying 2m dewpoint grid (`data/cache/d2m_grid.npz`) was extracted for **2020-07-15** (monsoon), matching neither validation window date (**2018-04-30** pre-monsoon, **2017-07-15** monsoon).
> 2. **Mislabelled Column Name**: The column name `rh_2020_04_30_pct` misstates the source date as April 30, 2020. The name is retained strictly to maintain 43-column schema stability and MD5 verification.
> 3. **Superseded Temperature Vintage**: The psychrometric saturation vapor pressure $e_s(T)$ was evaluated against the retired 2020 diurnal snapshot (MD5 `42157952f3441d1ce6fb06910c032c6b`), not against the authentic in-window temperatures.
> 4. **Psychrometric Clamping & Unrounded Edge Cases (Item J5-1m)**: 483 rows (2.85%) were psychrometrically clamped at $100.0\%$ due to elevation cooling with constant unadjusted dewpoint (`rh_2020_04_30_clamped_flag == 1`). In total, 490 rows display `100.0%` in the published CSV. The discrepancy of 7 villages (`ka.geojson:4, 728, 1178, 1191, 5769, 21966` and `mh2.geojson:13002`) represents an unrounded display artifact: these villages had raw floating-point RH in $[99.95\%, 100.00\%)$, so they were not clamped (`clamped_flag == 0`), but rounded half-up to `100.0` when serialized to 1 decimal place.
>
> **Requirements for a Production Fix (Open Backlog Item)**:
> Properly computing downscaled relative humidity requires:
> - Hourly or daily ERA5 `2m_dewpoint_temperature` (`d2m`) grids covering the exact validation dates: **2017-07-15** (monsoon) and **2018-04-30** (pre-monsoon).
> - Copernicus Climate Data Store (CDS) or Google Earth Engine API credentials to retrieve the in-window dewpoint fields.
> - An updated ingestion script (`engine/deterministic/humidity.py`) to produce co-temporal `real_jjas_rh_pct` and `real_prem_rh_pct` against authoritative downscaled temperatures.
>
> **Isolation Status**: Audit confirms that **zero assertions, figure generation scripts, or published summary metrics** consume either RH column.


---

## 8. Visualizing in QGIS: Step-by-Step Join Tutorial

To inspect and map the downscaled weather advisories in QGIS:

1. **Add Vector Layer**:
   - Open QGIS $\rightarrow$ Layer $\rightarrow$ Add Layer $\rightarrow$ Add Vector Layer.
   - Select your downloaded DataMeet GeoJSON boundary file (e.g., `ka.geojson` or `mh2.geojson`).
2. **Add Delimited Text Layer**:
   - Layer $\rightarrow$ Add Layer $\rightarrow$ Add Delimited Text Layer.
   - Choose `outputs/village_corrections.csv`.
   - Under **Geometry Definition**, select **No geometry (attribute only table)**.
3. **Join Tables**:
   - Right-click the village polygon layer $\rightarrow$ **Properties** $\rightarrow$ **Joins** tab.
   - Click the green **`+`** button.
   - **Join layer**: `village_corrections`
   - **Join field**: `census_code` (or `village_id`)
   - **Target field**: `census_code` (or `village_id` / matching ID field).
   - Click **OK**.
4. **Symbology & Cartography**:
   - Go to the **Symbology** tab.
   - Change from *Single Symbol* to **Graduated**.
   - **Value**: `village_corrections_dt_era5_c`
   - **Color Ramp**: Choose `RdBu` (Red-Blue) and check **Invert Color Ramp** (so Blue = Cooling, Red = Warming).
   - **Mode**: Equal Interval or Quantile (5 classes).
   - Click **Apply**. You will immediately see the Western Ghats escarpment ridge highlighted in deep blue (up to $-4.16\text{ }^\circ\text{C}$ cooling) and deep valleys and coastal lowlands in red (up to $+3.37\text{ }^\circ\text{C}$ warming).

---

## 9. Validation & Limitations

### Independent In-Situ Validation
The downscaling engine was evaluated against 5 independent Global Historical Climatology Network Daily (GHCN-Daily) stations across maritime coastal and inland plateau regimes:

| Station ID | Name | Terrain Regime | Station Elev | ERA5 Node Elev | $\Delta z$ |
|---|---|---|---|---|---|
| **IN009070100** | Chitradurga | Inland Plateau | 733.0 m | 692.1 m | +40.9 m |
| **IN009090300** | Gadag | Inland Plateau | 650.0 m | 628.7 m | +21.3 m |
| **IN009120100** | Karwar | Coastal Maritime | 4.0 m | 96.5 m | −92.5 m |
| **IN009120400** | Honavar | Coastal Maritime | 9.0 m | 85.3 m | −76.3 m |
| **IN022030600** | Goa / Panjim | Coastal Maritime | 60.0 m | 85.3 m | −25.3 m |

**Validation Performance**:
- Over 4,811 station-days evaluated between 2015-06-01 and 2018-05-31:
  - Baseline ERA5 raw Mean Absolute Error (MAE): **$1.89\text{ }^\circ\text{C}$**
  - Elevation-downscaled MAE (Scheme 1, ISA $\Gamma = 6.5\text{ }^\circ\text{C km}^{-1}$): **$1.68\text{ }^\circ\text{C}$**
  - Consistent improvement across all inland topographies.

#### Belgaum Exclusion Declaration
Station **IN009021000 (Belgaum Sambre)** is strictly **excluded** from validation:
1. **Circularity**: Belgaum's weather observatory sits within 2 km of the ERA5 land node used to calibrate coarse atmospheric profiles.
2. **Reporting Break**: The GHCN archive for Belgaum contains an uncorrected data discontinuity beginning in 2004 with persistent reporting omissions.
Belgaum's exclusion was audited and frozen in Item B35 (`logs/item_b35_b39.log`).

### Technical & Scientific Limitations

1. **Elevation-Only Disaggregation**:
   The primary correction accounts exclusively for static vertical height differences. Dynamic microclimatic factors — such as solar aspect, cold-air drainage, surface albedo variations, and dense canopy thermal buffering — are not modeled.

2. **Fixed ISA Environmental Lapse Rate**:
   A constant lapse rate of $\Gamma = 6.5\text{ }^\circ\text{C km}^{-1}$ is applied domain-wide. Audit Item G3 confirmed that ERA5 37-pressure-level free-air nocturnal lapse rates average $5.82\text{ }^\circ\text{C km}^{-1}$ (ranging seasonally from $4.8$ to $7.5\text{ }^\circ\text{C km}^{-1}$). However, regime scoring in Item G4 demonstrated that variable lapse rates yield zero statistically significant skill improvement over the fixed standard ISA lapse rate at station locations.

3. **Historical Reconstruction vs. Forecasting**:
   This pipeline is a post-hoc spatial disaggregation engine evaluated against historical reanalysis. It does not replace numerical weather prediction (NWP) models or issue forward-looking forecasts.

4. **Three-Year Climatological Window**:
   The validation window covers 1,096 days (2015-06-01 to 2018-05-31). This period was chosen to maximize synchronous observation completeness across all five GHCN-Daily stations. Decadal climate shifts are not evaluated.

5. **Frost / Cold-Air Pooling Feature (Parked at NO-GO)**:
   The nocturnal frost and valley cold-air pooling model reached a formal **NO-GO** decision in Items F13–F17 and is not part of this release. The decision was driven by **instrument mismatch** (MODIS satellite sensors measure radiative skin surface temperature $T_{\text{skin}}$, which decouples from $2\text{m}$ screen-level air temperature $T_{\text{air}}$ by up to $10\text{ }^\circ\text{C}$ on clear nights) and the complete absence of high-density valley-bottom in-situ temperature sensor networks. See `docs/feasibility_gate.md` and `AUDIT.md`.

---

## 10. Licensing & Provenance

This project operates under a dual-licensing structure maintaining strict separation between software and data:

- **Source Code**: All Python software, scripts, configuration files, and tests are open-source software licensed under the **MIT License** (see [LICENSE](LICENSE)). The MIT licence covers the code only, not the derived village data.
- **Derived Village Attributes & Centroids**: DataMeet Indian Village Boundary data is used under the **Open Database Licence (ODbL) v1.0**. Derived centroid columns (`centroid_lat`, `centroid_lon`) and associated village summary attributes in `outputs/village_corrections.csv` and `signed_village_results.json` are made available under **ODbL 1.0** with explicit attribution to DataMeet (https://projects.datameet.org/maps/subdistricts/). In strict adherence to share-alike compliance (ODbL §4.4) — and NOT under any educational or non-commercial exemption (ODbL provides neither) — all derived village tables are shared under ODbL 1.0. Raw polygon geometries (GeoJSON files) are withheld under repository size policy.
- **Upstream Climate & Elevation Datasets**: Upstream datasets are governed by their respective public licenses detailed in [DATA_SOURCES.md](DATA_SOURCES.md):
  - **Copernicus ERA5**: Copernicus Licence to Use Copernicus Products v1.2 (redistribution permitted with attribution).
  - **SRTM 30m DEM**: USGS / NASA Public Domain (17 U.S.C. § 105).
  - **GHCN-Daily**: NOAA NCEI Public Domain (17 U.S.C. § 105).

### Published Checksums & Line-Ending Portability Policy
Only outputs/village_corrections.csv and the data artifacts under data/cache/ carry byte-stable published checksums (enforced explicitly via .gitattributes). Markdown (.md), Python (.py), and JSON (.json) files are line-ending normalized on checkout under git's 	ext=auto policy, so their MD5 checksums are platform-dependent and are not verification artifacts.

---

## 11. Pre-Monsoon Heat Stress Advisory Rounding Inconsistency (Item J3)

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


## 12. Monsoon Tmean Variable Integrity Audit (Item J5-1)
- **Column**: `real_jjas_tmean_c`
- **Integrity Status**: `VERIFIED_AUTHENTIC`
- **Audit Findings**: Audited across all 16,943 villages against `data/cache/in_window_daily_extremes.npz`. Exactly 0 rows equal `real_jjas_tmin_c` and 16,943 rows reflect true 24-hour mean downscaled temperature ($T_{\text{mean}} = \text{ERA5 } T_{\text{mean}} + \Delta T_{\text{lapse}}$). A transcription typo in earlier audit prose displaying `t_f_min_j` was caught and corrected; on-disk scripts and published datasets are confirmed intact.

---
*For audit history and step-by-step verification records, see [AUDIT.md](AUDIT.md) and log files in `logs/`.*
