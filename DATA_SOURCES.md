# Data Sources

This project ingests five datasets. Code and data carry different licences; see
[LICENSE](LICENSE) for the code licence and this file for data obligations.

No village polygon *geometry* is distributed in this repository until the
DataMeet share-alike question is resolved in writing. Village attributes are
distributed keyed to census code only (column `census_code` in
`outputs/village_corrections.csv`).

---

## Source Table

| # | Name | URL | Licence Name & Version | Required Attribution | Citation |
|---|------|-----|------------------------|---------------------|----------|
| 1 | ERA5 Hourly Data on Single Levels (ECMWF ERA5) | https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels | Copernicus Licence to Use Copernicus Products v1.2 | "Generated using Copernicus Climate Change Service information 2026. Neither the European Commission nor ECMWF is responsible for any use that may be made of the Copernicus information or data it contains." | Hersbach et al. (2020), doi:10.1002/qj.3803 |
| 2 | SRTM 1 Arc-Second Global (USGS SRTMGL1) | https://lpdaac.usgs.gov/products/srtmgl1v003/ | NASA/USGS Public Domain (U.S. Government Work) | "Courtesy of the U.S. Geological Survey." | Farr et al. (2007), doi:10.1029/2005RG000183 |
| 3 | Indian Village Boundaries (DataMeet India Maps) | https://projects.datameet.org/maps/subdistricts/ | Open Database Licence (ODbL) v1.0 | "© DataMeet India Maps Contributors, available under ODbL v1.0 (https://opendatacommons.org/licenses/odbl/1-0/)" | DataMeet India Maps Community (2023) |
| 4 | GHCN-Daily (Global Historical Climatology Network) | https://www.ncei.noaa.gov/products/land-based-station/global-historical-climatology-network-daily | U.S. Government Work (NOAA, public domain) | "Data obtained from NOAA National Centers for Environmental Information (NCEI)." | Menne et al. (2012), doi:10.1175/JTECH-D-11-00103.1 |
| 5 | MODIS/Aqua Land Surface Temperature MYD11A1 v006 | https://lpdaac.usgs.gov/products/myd11a1v006/ | NASA / USGS Public Domain (U.S. Government Work) | "MODIS data courtesy of the NASA EOSDIS Land Processes Distributed Active Archive Center (LP DAAC), USGS/Earth Resources Observation and Science (EROS) Center, Sioux Falls, South Dakota." | Wan (2014), doi:10.5067/MODIS/MYD11A1.006 |

---

## DataMeet ODbL Licence — Verbatim Text and Share-Alike Analysis

The Open Database Licence (ODbL) v1.0 states (https://opendatacommons.org/licenses/odbl/1-0/):

> **Section 4.1 — Rights Granted.** The Licensor grants You a worldwide, royalty-free, non-exclusive,
> perpetual licence to Use the Database... including rights to extract, re-utilise, and distribute.
>
> **Section 4.4 — Share-Alike.** If you publicly use any adapted version of this database, or you
> produce a work from an adapted database, you must also offer that adapted database under the ODbL.

**Legal Verdict on Redistribution:** **Licence permits redistribution, conditional on share-alike.**
ODbL v1.0 does not forbid redistribution. The decision to withhold raw polygon geometries (GeoJSON files)
from this repository is an internal **project policy decision** pending legal clarity on share-alike scope.

**Resolution of Derived Centroids & Dual-Licence Terms:**
- **Status: RESOLVED - HUMAN DECISION (Item J7)**
- DataMeet Indian Village Boundary data is used under the **Open Database Licence (ODbL) v1.0**.
- In strict adherence to share-alike compliance (ODbL §4.4) — and NOT under any educational or non-commercial exemption (ODbL provides neither) — all derived centroid columns (`centroid_lat`, `centroid_lon`) and associated village summary attributes in `outputs/village_corrections.csv` and `signed_village_results.json` are made available under **ODbL 1.0** with explicit attribution to DataMeet (https://projects.datameet.org/maps/subdistricts/).
- The repository's **MIT License covers the code only**, not the derived village data.
- Raw polygon geometries (GeoJSON files, ~160 MB) remain excluded from this repository under internal distribution size policy. `signed_village_results.json` contains derived scalar summary attributes (elevation differences, centroid indices) and no raw polygon geometries; it is distributed under ODbL 1.0 with DataMeet attribution.

---

## ERA5 Licence Key Points & Shipped Caches

- Source: Copernicus Climate Change Service (C3S) via ECMWF Climate Data Store.
- Licence Name & URL: Copernicus Licence to Use Copernicus Products v1.2 (https://cds.climate.copernicus.eu/api/v2/terms/static/licence-to-use-copernicus-products.pdf)
- Operative Licence Clause (Section 3.2 — Rights):
  > "The Licensee is authorised to communicate or distribute Copernicus Products to the public, in whole or in part, in their original or modified form, as well as to make them available through an on-line service or otherwise, and to license third parties with the right to do the same."
- Mandatory Attribution Notice (Section 4):
  > "Generated using Copernicus Climate Change Service information 2026. Neither the European Commission nor ECMWF is responsible for any use that may be made of the Copernicus information or data it contains."
- Shipped Cache Files in Repository:
  * `data/cache/d2m_grid.npz` (3,210 B): Canonical 19x13 0.25° 2m dewpoint grid for domain.
  * `data/cache/node_orography_grids.npz` (6,452 B, co-derived with SRTM): 19x13 coarse surface geopotential height array.
- Distribution Status: **Licence permits redistribution with attribution; shipped in release/.**
- **ERA5 Back Extension Note (1960–1978)**: Full-record climatological series ingesting 1960–1978 draw from the preliminary ERA5 back extension (pre-satellite era). This period relies predominantly on conventional in-situ and sparse upper-air soundings and carries reduced observational constraint and confidence relative to the 1979–present satellite-era reanalysis. Any published daily series or downscaled climatologies must flag 1960–1978 separately from the 1979–2023 primary record.

---

## SRTM Licence Key Points & Shipped Cache

- Source: USGS/NASA Shuttle Radar Topography Mission (SRTMGL1 v003).
- Licence Name & Law: U.S. Government Work in the Public Domain (17 U.S.C. § 105).
- Operative Licence Clause:
  > "Copyright protection under this title is not available for any work of the United States Government... USGS-authored or produced data and information are in the public domain from the U.S. Government and may be used, distributed, or copied without copyright restriction."
- Mandatory Attribution Notice:
  > "Courtesy of the U.S. Geological Survey."
- Shipped Cache Files in Repository:
  * `data/cache/node_orography_grids.npz` (6,452 B, co-derived with ERA5): Aggregated 19x13 SRTM 30m node elevation array. (Full multi-gigabyte raw 30m rasters remain external via GEE asset `USGS/SRTMGL1_003`).
- Distribution Status: **Public domain; licence permits unrestricted distribution; shipped in release/.**

---

## GHCN-Daily Licence Key Points & Shipped Cache

- Source: NOAA National Centers for Environmental Information (NCEI).
- Licence Name & Law: U.S. Government Work in the Public Domain (17 U.S.C. § 105).
- Operative Licence Clause:
  > "Copyright protection under this title is not available for any work of the United States Government... NOAA environmental information is in the public domain worldwide and free of copyright restrictions."
- Mandatory Attribution Notice:
  > "Data obtained from NOAA National Centers for Environmental Information (NCEI)."
- Shipped Cache Files in Repository:
  * `data/cache/ghcn_daily/IN012131800_parsed.csv` (2,091,878 B): Authentic empirical daily weather series for station Kolhapur, IN (`LAT: 16.700, LON: 74.233`).
- Distribution Status: **Public domain; licence permits unrestricted distribution; shipped in release/.** Station records for IN009070100 (Chitradurga), IN009090300 (Gadag), IN009120100 (Karwar), IN009120400 (Honavar), and IN022030600 (Goa/Panjim) remain fetchable on demand via `fetch_ghcn_daily.py`.

---

## MODIS MYD11A1 Licence Key Points

- Source: NASA LP DAAC, U.S. Government Work, public domain.
- No MODIS files are distributed. MODIS LST was used for an exploratory
  probe (Items F12, F14, F15) which was reclassified as a skin-temperature test
  (not a 2 m air-pooling falsification); see `docs/feasibility_gate.md`.

---

*Items tagged ESTIMATED — NO SOURCE indicate that a licence URL or citation
could not be independently verified at the time of writing.*
