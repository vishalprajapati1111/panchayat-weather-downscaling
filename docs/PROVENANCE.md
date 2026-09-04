# PROVENANCE.md
*Started: 2026-08-31. Must be maintained as each dataset is ingested, not reconstructed afterwards.*

This document proves non-circularity of the weight-field pipeline:
weights derived from satellite precipitation archives must not use
the same ERA5 reanalysis data that drives the coarse forecast inputs.

> [!CAUTION]
> ERA5-Land derived products (including INDmet and any product that
> ingests ERA5-Land as a prior) must NEVER appear in this pipeline.
> Flag any such path here immediately.

## Dataset Registry

### CHIRPS v2.0 Daily (0.05°)
- **Source**: UCSB Climate Hazards Group (CHG)
- **GEE asset**: `UCSB-CHG/CHIRPS/DAILY`
- **Direct URL**: `https://data.chc.ucsb.edu/products/CHIRPS-2.0/`
- **Native resolution**: 0.05° (~5.5 km)
- **Coverage**: 50°S–50°N, global land, 1981–present
- **Ingests rain gauges?**: YES — blended satellite-gauge; CPC daily gauge analysis is incorporated
- **Ingests reanalysis?**: Partially — uses TMPA satellite precip + CHPclim climatology; does NOT ingest ERA5
- **ERA5-Land contamination?**: NO
- **Role in pipeline**: Source of fine-grid climatological weight fields
- **Status**: Not yet fetched

### GPM IMERG V07 Daily (0.1°)
- **Source**: NASA / JAXA
- **GEE asset**: `NASA/GPM_L3/IMERG_V07`
- **Direct URL**: `https://gpm.nasa.gov/data/imerg`
- **Native resolution**: 0.1° (~11 km)
- **Coverage**: 60°S–60°N, global, 2000–present
- **Ingests rain gauges?**: YES — gauge-calibrated in Final Run
- **Ingests reanalysis?**: NO (uses MERRA-2 for morphing only, not as precip input; V07 change note: MERRA-2 motion vectors)
- **ERA5-Land contamination?**: NO (MERRA-2 ≠ ERA5-Land)
- **Role in pipeline**: Secondary weight source; disagreement with CHIRPS = uncertainty field
- **Status**: Not yet fetched

### ERA5 (0.25°, pressure levels + single levels)
- **Source**: ECMWF via Copernicus CDS or GEE
- **GEE asset**: `ECMWF/ERA5/DAILY` or `ECMWF/ERA5_LAND/DAILY`
- **Variables**: tp (total precip), t2m, d2m, u850, v850
- **Native resolution**: ~0.25° (~28 km)
- **Ingests rain gauges?**: NO (reanalysis, model-based)
- **Ingests reanalysis?**: IS a reanalysis
- **ERA5-Land contamination?**: ERA5 ≠ ERA5-Land. Use ERA5 (atmospheric) only. NEVER ERA5-Land.
- **Role in pipeline**: Coarse-resolution input to application functions (forecast proxy)
- **Status**: Not yet fetched

> [!WARNING]
> ERA5-Land (`ECMWF/ERA5_LAND/DAILY` in GEE) must NOT be used as a precipitation
> source anywhere in this pipeline. It ingests ERA5 atmospheric fields and is NOT
> independent of ERA5. Using it as both the weight-field source AND the forecast
> input would be circular. Any use of ERA5-Land must be flagged here.

### SRTM 30m DEM
- **Source**: NASA/USGS
- **GEE asset**: `USGS/SRTMGL1_003`
- **Direct URL**: https://e4ftl01.cr.usgs.gov/MEASURES/SRTMGL1.003/
- **Native resolution**: 1 arc-second (~30m)
- **Ingests rain gauges?**: NO
- **Ingests reanalysis?**: NO
- **ERA5-Land contamination?**: NO
- **Role in pipeline**: Elevation for lapse-rate temperature adjustment and terrain feature computation
- **Status**: Not yet fetched

### IMD Gridded (excluded)
- **Status**: EXCLUDED — requires institutional access; API not publicly available
- **Note**: Would be useful for validation weight fields against observed gauge climatology

### KSNDMC / India-WRIS station data (excluded from weights)
- **Status**: EXCLUDED from weight construction — no public programmatic API.
  Available only via manual KSNDMC dashboard (24 clicks per station-year).
  India-WRIS CKAN Karnataka resource does not cover Western Ghats windward stations.
  Maharashtra NWDP resource has no Mahabaleshwar tehsil stations.
- **Note**: If obtained manually, usable ONLY for validation, never for weight construction.


### Gauge Data Quality
- **Status**: NO SOURCED CLIMATOLOGY. We currently possess no verified, long-term (e.g., 1991-2020) IMD or GHCN station normals for the Western Ghats crest. Any historical gauge normals mentioned in this repo are either estimated from topography or weakly sourced from web snippets, and must be quarantined from rigorous statistical evaluation.

---

## Methodological Incident Record

### Fabricated-Number Incident (2026-09-01)

**What happened.** During a session where the AI assistant's context window was partially truncated, the assistant fabricated two rainfall climatology figures — Mahabaleshwar JJAS ~3173.6 mm and Satara JJAS ~1046.2 mm — yielding a claimed satellite ratio of 3.03×. No script was run that produced these numbers; they were invented during a reasoning step and presented as if they had been read from a log. The actual script output (task-2208.log, lines 3–5) shows Mahabaleshwar 1663.2 mm and Satara 978.7 mm, giving a ratio of 1.70×.

**How it was detected.** The user noted that the claimed direction of change (contrast *rising* from 1.79× to 3.03× after fixing a coordinate clamping bug) was not consistent with the stated fix (pointing extraction to a wetter crest should increase the windward value and either increase or moderately change the ratio, not triple it). The user also correctly pointed out that a uniform 4× inflation from a divide-by-120-instead-of-30 bug would produce a uniform scaling, not the asymmetric 1.91×/1.07× change claimed. Neither explanation was correct; the numbers were fabricated.

**Traceability rule adopted in response.** Effective 2026-09-01, no number may appear in any document or report unless it can be traced to a specific log file and line number produced by a script run. Numbers that cannot be traced must be deleted, not re-derived from memory. Log file paths and line numbers are cited inline next to every numeric result in docs/feasibility_gate.md and docs/deterministic_validation.md.

**Why this is documented here rather than hidden.** Traceability is a genuine methodological strength. A pipeline that catches its own errors via provenance tracking and records them openly provides stronger evidence of reliability than one that silently corrects them. Future reviewers should be able to see both the error and the correction mechanism.

