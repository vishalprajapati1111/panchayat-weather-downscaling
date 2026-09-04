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
| 1 | ERA5 Hourly Data on Single Levels (ECMWF ERA5) | https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels | Copernicus Licence to Use Copernicus Products v1.2 | "Generated using Copernicus Climate Change Service information 2024. Neither the European Commission nor ECMWF is responsible for any use that may be made of the Copernicus information or data it contains." | Hersbach et al. (2020), doi:10.1002/qj.3803 |
| 2 | SRTM 1 Arc-Second Global (USGS SRTMGL1) | https://lpdaac.usgs.gov/products/srtmgl1v003/ | NASA/USGS Public Domain (U.S. Government Work) | "Courtesy of the U.S. Geological Survey." | Farr et al. (2007), doi:10.1029/2005RG000183 |
| 3 | Indian Village Boundaries (DataMeet India Maps) | https://projects.datameet.org/maps/subdistricts/ | Open Database Licence (ODbL) v1.0 | "© DataMeet India Maps Contributors, available under ODbL v1.0 (https://opendatacommons.org/licenses/odbl/1-0/)" | DataMeet India Maps Community (2023) |
| 4 | GHCN-Daily (Global Historical Climatology Network) | https://www.ncei.noaa.gov/products/land-based-station/global-historical-climatology-network-daily | U.S. Government Work (NOAA, public domain) | "Data obtained from NOAA National Centers for Environmental Information (NCEI)." | Menne et al. (2012), doi:10.1175/JTECH-D-11-00103.1 |
| 5 | MODIS/Aqua Land Surface Temperature MYD11A1 v006 | https://lpdaac.usgs.gov/products/myd11a1v006/ | NASA / USGS Public Domain (U.S. Government Work) | "MODIS data courtesy of the NASA EOSDIS Land Processes Distributed Active Archive Center (LP DAAC), USGS/Earth Resources Observation and Science (EROS) Center, Sioux Falls, South Dakota." | Wan (2014), doi:10.5067/MODIS/MYD11A1.006 |

---

## DataMeet ODbL Licence — Verbatim Text (relevant excerpt) and Share-Alike Analysis

The Open Database Licence (ODbL) v1.0 states (https://opendatacommons.org/licenses/odbl/1-0/):

> **Section 4.4 — Share-Alike.** If you publicly use any adapted version of this
> database, or you produce a work from an adapted database, you must also offer
> that adapted database under the ODbL.

**Share-alike verdict:** ODbL **does impose share-alike obligations** on any
*adapted database* (a database that modifies, re-structures, or adds to the
original polygon data). Derived *works* (e.g. a map rendered from the data, or
a statistical analysis) do not trigger share-alike if they are separated from
the underlying adapted database.

**Consequence for this repository:** The `outputs/village_corrections.csv` file
contains attributes (elevation corrections, ERA5 node assignments) computed
**from** village centroids derived from the DataMeet polygon boundaries. It does
**not** re-distribute the polygon geometries themselves. The file is distributed
under ODbL obligations until legal review confirms that centroid coordinates
derived from polygon geometry constitute a "produced work" rather than an
"adapted database". Until that confirmation is received in writing, polygon
geometry (GeoJSON, GeoPackage, Shapefile) is excluded from this repository, and
the `centroid_lat`/`centroid_lon` columns in `village_corrections.csv` are
distributed under ODbL pending review. All other columns (elevation, ERA5
corrections) are derived computations and are covered by the MIT code licence.

---

## ERA5 Licence Key Points

- Source: Copernicus Climate Change Service (C3S) via the Climate Data Store.
- Licence URL: https://cds.climate.copernicus.eu/api/v2/terms/static/licence-to-use-copernicus-products.pdf
- No ERA5 data files are distributed in this repository. Reproduction scripts
  fetch data via the GEE `ECMWF/ERA5/HOURLY` collection.
- The Copernicus licence does not impose share-alike on derived statistical
  products such as correction tables, but requires the attribution string above
  to appear wherever ERA5-derived quantities are published.

---

## SRTM Licence Key Points

- Source: USGS/NASA Shuttle Radar Topography Mission.
- U.S. Government Works are in the public domain. No share-alike obligations.
- No SRTM raster files are distributed. Reproduction fetches via GEE
  `USGS/SRTMGL1_003`.

---

## GHCN-Daily Licence Key Points

- Source: NOAA NCEI, U.S. Government Work, public domain.
- Station records for IN009070100 (Chitradurga), IN009090300 (Gadag),
  IN009120100 (Karwar), IN009120400 (Honavar), IN022030600 (Goa/Panjim) were
  used for validation only; no raw GHCN files are distributed.

---

## MODIS MYD11A1 Licence Key Points

- Source: NASA LP DAAC, U.S. Government Work, public domain.
- No MODIS files are distributed. MODIS LST was used for an exploratory
  probe (Items F12, F14, F15) which was reclassified as a skin-temperature test
  (not a 2 m air-pooling falsification); see `docs/feasibility_gate.md`.

---

*Items tagged ESTIMATED — NO SOURCE indicate that a licence URL or citation
could not be independently verified at the time of writing.*
