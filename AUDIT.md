# Audit Summary

This document records what the audit rounds found, what changed, what did not
move, and what is still open.

---

## Three Genuine Bugs Found and Fixed

### Bug 1 — SRTM grid sampled at pixel corners, not pixel centres (B11)
**What was found:** The initial SRTM ingestion script used GEE `getRegion` with
integer-quarter-degree coordinates. Those coordinates align with pixel *corners*
of the 1 arc-second raster, not pixel *centres*. Each stored elevation value was
therefore drawn from whichever of four adjacent pixels the sampler returned at
that corner point.
**Scale:** 81.9 % of grid cells wrong by > 10 m; 20.5 % wrong by > 100 m;
maximum error 451.6 m. Citation: `logs/item_b0_b16.log` (B11).
**Fix:** Rebuilt `srtm_grid` using per-village centroid sampling on native 30 m
raster (`data/cache/srtm_domain_30m.tif`), confirmed 0 edge-truncation against
the raster boundary.

### Bug 2 — ERA5 node-orography extraction used 250 m resampled DEM (B18)
**What was found:** ERA5 node elevations `z_era5` were computed from a
250 m resampled SRTM grid, introducing a representation discrepancy (σ = 27.14 m
at 250 m vs σ = 27.59 m at native 30 m). While the difference was small, the
source of the discrepancy was unclear until B18 confirmed that ARCO node values
(`sel(latitude=lats, longitude=lons, method='nearest')`) read directly from Zarr
coordinate arrays do not suffer the corner-sampling fault — they are correctly
centred at the model orography grid point.
**Fix:** Confirmed ARCO read path is sound; native 30 m raster used for all
village-level `z_SRTM` values; ERA5 node `z_era5` from model orography.

### Bug 3 — Belgaum (IN009021000) included in validation station set (B35)
**What was found:** Item B32 named IN009021000 (Belgaum) as one of six usable
validation stations. Belgaum is within 2 km of the ERA5 land node used to derive
the correction (circularity) and has a documented reporting break in 2004 in the
GHCN archive.
**Fix:** Belgaum removed from the validation set. Station count corrected from
6 to 5. All affected outputs re-emitted. Citation: `logs/item_b35_b39.log`.

---

## One False Alarm

### False Alarm — argmin village node assignment (B0 point 4)
**Initial claim:** argmin was claimed to misassign villages near 0.125°
node-box boundaries because the assignment used approximate floating-point
arithmetic.
**Retraction:** With ERA5 nodes at integer quarter-degrees (73.50, 73.75, …),
Torane's centroid at 73.6994 °E resolves under argmin to node 73.75, whose
node-centred box [73.625, 73.875] does contain it. Node assignment was correct
all along. "0 villages changed" in B0 point 4 is the right answer for the right
reason. Citation: `logs/item_b0_b16.log` (B0).

---

## Checksum Supersession

`village_corrections.csv` was rebuilt from scratch to correct Bug 1 and
incorporate the Belgaum removal. The MD5 checksum changed as follows:

| Version | MD5 |
|---|---|
| Pre-rebuild (Bug 1 present) | `f92240947de2099247ac659d5065cd1f` |
| Current (Bug 1 fixed, 5-station set) | `42157952f3441d1ce6fb06910c032c6b` |

Column count: **36 columns** (verified in `logs/item_b28_b34.log`).
Row count: 16,943 villages + 1 header.

---

## What Did Not Move

The following quantities reproduced exactly after the rebuild, confirming that
the correction logic itself was sound throughout:

- ERA5 Δz counts (741 cooling, 662 warming, 1,403 total above noise floor) —
  identical pre- and post-rebuild. Citation: `logs/item_b17_b25.log` (B20).
- Flagship node (rank 1 of 231 for model-orography deficit) and the 33 villages
  it serves. Citation: `logs/item_b26_b10.log` (B27).
- B23 failure-rate test: analytically predicted 75 % incorrect on retired grid;
  observed 75.3 % on 16,943 polygons. Citation: `logs/item_b17_b25.log` (B23).

---

## Frost / Cold-Air-Pool Feature — NO-GO, Parked

**Status:** NO-GO. Feature development halted at Items F13–F17; not included in
this release.

**Reason — Instrument Mismatch:** MODIS Land Surface Temperature (MYD11A1)
measures radiative skin temperature T_skin, not 2 m screen-level air temperature
T_2m. During decoupled clear-sky nights, T_skin can be 5–10 °C colder than T_2m
due to direct-sky radiative cooling of the ground surface while the overlying air
column remains warmer. Items F12/F14/F15 were reclassified as Surface
Skin-Temperature Radiative Response Tests and cannot physically falsify
sub-canopy 2 m air pooling. Citation: `logs/item_g0_g6.log` (G1);
Kindstedt et al. (2022) doi:10.5194/tc-16-3051-2022.

**Reason — Absent In-Situ Network:** The five GHCN-Daily stations have station
spacings > 50 km and none are located in confirmed cold-pool hollows. With n = 5
and df = 2 in the lapse-rate regression, it is impossible to isolate orographic
cooling from coastal marine exposure.

**Physics is not absent.** Cold-air pooling over the Western Ghats is a
well-documented phenomenon. The NO-GO reflects absence of instruments, not
absence of the effect.

---

## Items G0–G6 — Open, May Revise v0.1

Items G0–G4 are complete (lapse-rate scoring, 30 m raster unification, regime
evaluation). Items G5–G6 are pending.

**G4 finding (may affect v0.2):** Dynamic free-air lapse rate provides zero
measurable skill over fixed Γ = 6.5 °C km⁻¹ at the five station locations.
Regime-switched Γ = 0 on decoupled nights is rejected as a compensating
error artifact at coastal nodes. Baseline fixed lapse rate is retained.
Citation: `logs/item_g0_g6.log` (G4).

**If G5–G6 yield a revised nocturnal correction,** outputs will be tagged v0.2
and a new checksum recorded. Do not treat v0.1 checksums as final for any
nocturnal-temperature application.
