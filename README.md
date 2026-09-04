# Panchayat Weather Downscaling

In the Western Ghats, roughly one village in twelve receives weather data wrong
by more than the forecast's own error margin, because the data has no knowledge
of the village's elevation, and the correction runs both warmer and cooler.

---

## What this project does

ERA5 reanalysis delivers temperature at a 0.25° × 0.25° grid (~28 km) whose
node elevation (from the ERA5 model orography) can differ by hundreds of metres
from the actual village elevation recorded in SRTM. We apply an elevation
correction T_village = T_ERA5_node − Γ · Δz, where Γ = 6.5 °C km⁻¹ (the
International Standard Atmosphere environmental lapse rate) and
Δz = z_SRTM − z_ERA5 (SRTM 30 m polygon mean minus ERA5 model orography at the
nearest 0.25° node). The correction is applied to every village centroid in the
domain; no regression fitting, no station-dependent tuning.

---

## Audited headline figures

| Quantity | Value | Citation |
|---|---|---|
| Villages in domain | 16,943 | `logs/item_b0_b16.log:5` |
| Window | 2015-06-01 – 2018-05-31 (1,096 days) | `logs/item_b28_b34.log:14` |
| Villages with \|ΔT\| > ERA5 diurnal noise floor (8.28 %) | 1,403 | `docs/feasibility_gate.md` |
| Of those: cooling corrections | 741 | `docs/feasibility_gate.md` |
| Of those: warming corrections | 662 | `docs/feasibility_gate.md` |
| village_corrections.csv MD5 | `42157952f3441d1ce6fb06910c032c6b` | verified at packaging |
| Largest single cooling error | −519.0 m (Nagave, mh2.geojson) | `logs/item_b17_b25.log` |
| Largest single warming error | +640.5 m (Dattathreyapeeta, ka.geojson) | `logs/item_b17_b25.log` |

---

## Validation

Five GHCN-Daily stations were used for independent validation:

| Station ID | Name | Type |
|---|---|---|
| IN009070100 | Chitradurga | Inland plateau |
| IN009090300 | Gadag | Inland plateau |
| IN009120100 | Karwar | Maritime coastal |
| IN009120400 | Honavar | Maritime coastal |
| IN022030600 | Goa/Panjim | Maritime coastal |

**Station IN009021000 (Belgaum) is excluded from validation** on grounds of
circularity (Belgaum is within 2 km of an ERA5 land node used to derive the
correction) and a documented 2004 reporting break in the GHCN archive. See
`logs/item_b35_b39.log` for the formal removal record.

Pooled T_min MAE against the five stations: **1.68 °C** (Scheme 1, fixed Γ),
evaluated over 4,811 station-nights (2015-06-01 – 2018-05-31).
Citation: `logs/item_g0_g6.log` (Item G4).

---

## One-command reproduction

```bash
# Requires Python 3.10+, earthengine-api (authenticated), rasterio, xarray, geopandas
python pipeline.py --domain Karnataka,Maharashtra,Goa --window 2015-06-01:2018-05-31
```

All intermediate artefacts land in `data/cache/` (excluded from this repo).
Final output is `outputs/village_corrections.csv`.

**Data access note:** ERA5 data is fetched via Google Earth Engine
(`ECMWF/ERA5/HOURLY`). SRTM is fetched via `USGS/SRTMGL1_003`. Both require a
free GEE account. See `docs/credentials_required.md`.

---

## Licence note

**Code** (Python scripts) is released under the MIT Licence; see [LICENSE](LICENSE).
**Data** (outputs, logs, docs) is governed by the upstream data licences described
in [DATA_SOURCES.md](DATA_SOURCES.md). Code and data licences differ — read
DATA_SOURCES.md before redistributing any file from `outputs/`.

---

## Limitations

1. **Elevation-only correction.** The correction Γ · Δz adjusts temperature for
   static elevation difference only. Land use, aspect, canopy cover, cold-air
   pooling, and coastal sea-breeze effects are not captured.

2. **Fixed lapse rate.** Γ = 6.5 °C km⁻¹ is the ISA standard. The ERA5-derived
   free-air nocturnal lapse rate over the domain averages 5.82 °C km⁻¹
   (seasonal range 4.8–7.5 °C km⁻¹). Scheme comparison showed no skill
   improvement from dynamic Γ at station locations; fixed Γ is retained.
   Citation: `logs/item_g0_g6.log` (Item G4).

3. **Historical reconstruction, not forecasting.** This is a post-hoc correction
   applied to ERA5 reanalysis. The method does not constitute a numerical weather
   prediction or a real-time advisory system.

4. **Three-year window.** The validation window (2015-06-01 – 2018-05-31, 1,096
   days) was chosen to coincide with GHCN data availability at all five stations.
   Decadal climate trends are not characterised.

5. **Items G5–G6 open.** The nocturnal lapse-rate and frost-feature items (G5–G6)
   are incomplete. Results may be revised in v0.2; see [AUDIT.md](AUDIT.md).
