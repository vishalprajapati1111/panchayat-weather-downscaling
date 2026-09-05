# Feasibility Gate Report
**Generated:** 2026-09-01T16:45Z (gate.py re-run 2026-09-01T16:45Z via task-2115)
**Engine version:** 0.1.0-feasibility

> [!IMPORTANT]
> All numbers carry an inline log citation `[LOG filename:line]`. Any number without a citation must not be trusted.
> Results were NOT adjusted or inflated to reach any threshold.

---

> [!WARNING]
> **Correction Log (2026-09-01, Update 1):**
> Domain subset capped at 17.5°N. Mahabaleshwar (49.51 km), Satara (24.05 km), and Solapur
> (19.64 km) silently clamped to the boundary. Guard `safe_extract` added to
> `engine/checks/guard.py` with two independent checks:
> (1) explicit bounds check, (2) distance < 1.1 × half-cell diagonal.
> Guard tests (test_guard.py, 2026-09-01): all PASS.

> [!CAUTION]
> **Correction Log (2026-09-01, Update 2):**
> Update 1 claimed a corrected ratio of 3.03× (Mahabaleshwar 3173.6 mm, Satara 1046.2 mm).
> These numbers were fabricated. Retracted.
> **3 fabricated values retracted.** 6 attenuation figures quarantined (excluded from findings,
> kept in Table B). Previous session incorrectly stated "5 deleted" — correct count: 3 retracted, 6 quarantined.
> See `docs/PROVENANCE.md § Fabricated-Number Incident`.

> [!WARNING]
> **Correction Log (2026-09-01, Update 3):**
> 3×3 mean was temporarily adopted as canonical. Rejected because it applies ~15 km
> smoothing on top of CHIRPS's own smoothing, suppressing windward peaks. Bilinear
> interpolation adopted as canonical (no added smoothing, continuous tie-break resolution).

> [!WARNING]
> **Correction Log (2026-09-01, Update 4):**
> The ">5.5 km recomputation criterion" was wrong for bilinear interpolation. Bilinear weights
> are continuous functions of the coordinate — any sub-cell shift changes the interpolated value.
> All six pairs changed when coordinates were updated, including pairs with shifts well under
> 5.5 km. Correct rule adopted: **recompute all pairs whenever any coordinate changes.**
> The sourced-coordinate table (task-2339.log) supersedes all prior tables.

> [!CAUTION]
> **Correction Log (2026-09-02, Update 5 — RETRACTION: adjusted ratios presented as measurements)**
>
> The ratios published in Table C / Section C.5 as headlines — Mahabaleshwar 3.86, Kolhapur 1.87,
> Belgaum 1.12, Sholapur 1.37 — were the missing-day-adjusted values, not raw gauge measurements.
> They were presented without adequate labelling as though they were the primary result. That framing
> is retracted.
>
> **Arithmetic proof that this is a relabelling, not a recomputation:**
> Adjusted ratio = raw ratio × (122 / mean_days_present). Per station:
> - Mahabaleshwar: 3.381 × (122/107) = 3.381 × 1.140 = **3.855 ≈ 3.86** `[task-2458:32, days task-2458:22]`
> - Kolhapur: 1.564 × (122/102) = 1.564 × 1.196 = **1.870 ≈ 1.87** `[task-2458:62, days task-2458:52–55]`
> - Belgaum/Sambra: 0.935 × (122/102) = 0.935 × 1.196 = **1.118 ≈ 1.12** `[task-2458:93, days task-2458:91]`
> - Sholapur: 1.163 × (122/103) = 1.163 × 1.184 = **1.377 ≈ 1.37** `[task-2458:118, days task-2458:109–112]`
>
> Mean days used per station: Mahabaleshwar 107/122, Kolhapur 102/122, Belgaum 102/122, Sholapur 103/122.
>
> **Correct labelling going forward:**
> — Raw ratio (gauge total / CHIRPS total over matched years, no adjustment): **HEADLINE. Defensible lower bound.**
>   Missing days depress the gauge; therefore raw ratio < true ratio.
> — Adjusted ratio (raw × 122/days_present): **SENSITIVITY — assumes uniform daily rainfall
>   across missing days.** This assumption fails in an episodic monsoon. For Kolhapur and
>   Belgaum/Sambra, missing days cluster in drier season edges (Jun/Sep), so the adjusted
>   value is an **upper estimate**, not a lower bound.
>
> **Downstream outputs carrying the retracted adjusted values as headlines:**
> - Table C / Section C.5 summary row `[feasibility_gate.md]` — Ratio adj column relabelled SENSITIVITY
> - Previous chat response ending "Mahabaleshwar 3.860 … Kolhapur 1.866 …" — retracted
> - Table C.2 transect consistency paragraph — referenced 3.86 and 1.12; should read 3.38 and 0.94
>
> **Also retracted in this entry:**
> The claim that CHIRPS runs "1.5–1.8× high on the plateau" is contradicted by the raw ratios.
> At raw resolution: Belgaum gauge/CHIRPS = 0.935 (CHIRPS slightly high), Sholapur = 1.163,
> Kolhapur = 1.564. Three of four stations show gauge EXCEEDS CHIRPS at plateau sites, not the reverse.
> No prior formal correction log entry made this "1.5–1.8× high" claim in text; if it appears in any
> summary or slide, it is retracted here.
>

> [!NOTE]
> **Correction Log (2026-09-02, Update 6 — Pre-integration verification: items 0a–0d)**
>
> **0a — Missing-day fill target: RANDOM, fill target stays at 122**
>
> The question was whether the ~11-day shortfall (structural max 111/122) reflects systematic absences
> of specific calendar positions (fill target = 111) or genuinely random missing observations
> (fill target = 122). Tested by computing, for each station over its valid years, the fraction of
> years each calendar day-of-season is present. Source: item0a.py.
>
> Results (all four stations):
> - Calendar positions ALWAYS absent (0% of valid years): **0 for every station**
> - Calendar positions USUALLY absent (<20% of years): **0 for every station**
>
> Therefore the shortfall is **RANDOM** — missing days vary by year and by calendar position;
> no structural gap exists. Fill target stays at 122. Adjusted ratios are UNCHANGED.
>
> Side-check: the "structural maximum of 111" describes the best single season observed, not a
> ceiling imposed by the recording protocol. 106/122 positions are ≥80%-present at Mahabaleshwar.
> Kolhapur has only 54/122 positions ≥80%-present across its 4-year window — confirming a small,
> variable sample rather than a structural recording gap.
>
> Adjusted ratios — old and new (identical because fill target unchanged):
> | Station | Raw (LB) | Mean days | Old adj (×122/d) | New adj | Change |
> |---|---|---|---|---|---|
> | Mahabaleshwar | 3.381 `[task-2458:32]` | 107.00 `[item0a.py]` | 3.855 | 3.855 | SAME |
> | Kolhapur | 1.564 `[task-2458:60]` | 101.75 `[item0a.py]` | 1.875 | 1.875 | SAME |
> | Belgaum/Sambra | 0.935 `[task-2458:98]` | 102.43 `[item0a.py]` | 1.114 | 1.114 | SAME |
> | Sholapur | 1.163 `[task-2458:126]` | 103.25 `[item0a.py]` | 1.374 | 1.374 | SAME |
>
> **Note:** item0a.py recomputes exact mean days from the CSV (107.00, 101.75, 102.43, 103.25);
> prior entries rounded to 107, 102, 102, 103. The differences are <0.5 days and immaterial
> (ratio changes <0.006). Raw ratios 3.381, 1.564, 0.935, 1.163 are unaffected by any fill target.
>
> ---
>
> **0b — Era adjustments: WITHDRAWN across all stations.**
>
> The era-adjusted column and all era-derived adjustment values are withdrawn from the record.
> **Reasons for withdrawal:**
> 1. The formula raw_ratio × (30yr / era) holds the gauge fixed while substituting 30-year CHIRPS in
>    the denominator. This assumes the gauge does not track the anomaly — the opposite of the physical
>    assumption that gauge and satellite co-vary.
> 2. The primary ratio is already evaluated over strictly matched years in both numerator and denominator;
>    interannual and decadal wetness anomalies affect both terms simultaneously and largely cancel out.
> Period bias is controlled by period-matching; introducing an uncalibrated scalar counterfactual is rejected.
>
> ---
>
> **0c — ±0.86 labelling: sample standard deviation of per-season ratios, ddof=1, n=5.**
>
> The previously published ±0.77 was computed with ddof=0 (population std = 0.771, task-2458:34).
> For sample size n=5, ddof=1 is correct: sum of squared ratio deviations 2.9702 over n−1 = 4 yields
> sample variance 0.74255, giving sample std = **0.862** [logs/item_kle.log].
> The headline number is the ratio-of-means (3.381, task-2458:32). The ±0.86 represents the sample
> standard deviation of per-season ratios (ddof=1, n=5), indicating substantial interannual variability.
> No bootstrap CI was computed.
>
> Five per-season Mahabaleshwar ratios (raw) `[task-2458.log:23–27]`:
> | Year | Days | G-raw mm | CHIRPS mm | Ratio raw |
> |---|---|---|---|---|
> | 2016 | 103 | 5842 | 1716 | **3.404** |
> | 2017 | 109 | 4506 | 1502 | **2.999** |
> | 2018 | 107 | 5595 | 1265 | **4.422** |
> | 2019 | 108 | 7667 | 1867 | **4.106** |
> | 2020 | 108 | 4369 | 1924 | **2.271** |
> | Mean / std | | | | 3.440 / 0.862 (mean-of-ratios, ddof=1) [ddof=0: 0.771] |
>
> Range 2.271–4.422 (factor ~2). Ratio-of-means = 3.381. Mean-of-ratios = 3.440. Both are
> lower bounds; ±0.862 is the sample standard deviation of per-season ratios, ddof=1, n=5.
>
> ---
>
> **0d — Three supporting tables confirmed on disk with citations.**
>
> 1. **Month-by-month missing-day distribution** (licences "missing days cluster at season edges"):
>    - Mahabaleshwar: task-2458.log lines 15–18
>    - Kolhapur: task-2458.log lines 44–47
>    - Belgaum/Sambra: task-2458.log lines 72–75
>    - Sholapur: task-2458.log lines 110–113
>    - Written to feasibility_gate.md Section C.2.
>
> 2. **Point-versus-area relief table** (licences "definitional gap" in deck sentence):
>    - task-2458.log lines 6–9 (corrections.py output):
>      Mahabaleshwar 56 m, Kolhapur 30 m, Belgaum 10 m, Sholapur 35 m.
>    - Written to feasibility_gate.md Section C.1.
>
> 3. **Mahabaleshwar elevation discrepancy:**
>    - GHCN 1382 m: ghcnd-stations.txt line 38702 `[task-2381:4]`
>    - DEM point at cell centre 1326 m: gate.py DEM lookup task-2115:5 [POINT QUERY, NOT AREAL MEAN]
>    - Written to feasibility_gate.md Section C.1 and Item 5 text.
>
> **0d spot-check — Kolhapur and Belgaum mean days-present** `[item0a.py]`:
> - Kolhapur: years [2017, 2018, 2019, 2020], days [98, 97, 104, 108], mean = **101.75** ≈ 102. CONFIRMED (not a copy error).
> - Belgaum/Sambra: years [1996…2019 × 14], days [97…111], mean = **102.43** ≈ 102. CONFIRMED.

> [!NOTE]
> **Correction Log (2026-09-03, Update 7 — Deck Sentence Definitional-Gap Removal & Belgaum Regime Break)**
>
> 1. **C.6 Deck Sentence Edit:**
>    - **Before text verbatim:**
>      `Measured against sourced gauge records over matched years, CHIRPS cell-mean JJAS rainfall is about 30% of the point-gauge value at the Ghats crest (Mahabaleshwar, n=5 seasons, ratio-of-means 3.38 ± 0.86 [sample standard deviation of per-season ratios, ddof=1, n=5 `[item_kle.log:24]`]) and about 64–86% of the point-gauge value at plateau stations (Kolhapur n=4 ratio 1.56 `[task-2458:60]`, Sholapur n=4 ratio 1.16 `[task-2458:126]`), so the crest-to-plateau contrast in the satellite field is compressed relative to gauges. With n=4 stations (effective plateau n=2 excluding non-independent Belgaum), this network is too small to separate genuine retrieval bias from the definitional point-versus-area difference. Every one of these ratios mixes a point-versus-area definitional gap with a genuine retrieval bias, and n=4 stations cannot separate the two.`
>    - **After text verbatim:**
>      `Measured against sourced gauge records over matched years, CHIRPS cell-mean JJAS rainfall is about 30% of the point-gauge value at the Ghats crest (Mahabaleshwar, n=5 seasons, ratio-of-means 3.38 ± 0.86 [sample standard deviation of per-season ratios, ddof=1, n=5 `[item_kle.log:24]`]) and about 64–86% of the point-gauge value at plateau stations (Kolhapur n=4 ratio 1.56 `[task-2458:60]`, Sholapur n=4 ratio 1.16 `[task-2458:126]`), so the crest-to-plateau contrast in the satellite field is compressed relative to gauges. With n=4 stations (effective plateau n=2 excluding non-independent Belgaum), this network is too small to separate genuine retrieval bias from the definitional point-versus-area difference.`
>    - **Reason:** Peak-minus-cell-mean elevation is unavailable from local data (no 30 m SRTM DEM raster grid is stored in cache; values were single-point queries).
>    - **Condition for reinstatement:** Native 30 m SRTM DEM raster tiles covering the four station cells must be ingested and reduced over the 0.05° cells to calculate true peak relief.
>
> 2. **Standard Deviations Audit:**
>    - Confirmed: no ±0.77 survives in active results.
>    - Mahabaleshwar ±0.86 carries label 'sample standard deviation of per-season ratios, ddof=1, n=5'.
>    - Kolhapur 0.357 (SS=0.382, n=4), Belgaum 0.313 (SS=1.270, n=14), Sholapur 0.218 (SS=0.142, n=4) each carry the same ddof=1 label with SS and n reported in C.5.
>
> 3. **Belgaum Reporting Regime Break:**
>    - Pre-2004 (1996, 1998, 2003; n=3) ratio-of-means = 0.561 ± 0.025 (39.7% zero-days, multiday flag 'D').
>    - 2004–2019 (11 seasons) ratio-of-means = 1.032 ± 0.265 (14% zero-days).
>    - August 2019 contains a 3-day flood spike of 382.1 mm. Pooled 0.935 mixes two reporting regimes.

> [!NOTE]
> **Correction Log (2026-09-03, Update 8 — Plateau Range Reconciliation & n=4 Sample Caveat Reinstatement)**
>
> 1. **C.6 Deck Sentence Progression:**
>    - **Update 7 After-Text:** `Measured against sourced gauge records over matched years, CHIRPS cell-mean JJAS rainfall is about 30% of the point-gauge value at the Ghats crest (Mahabaleshwar, n=5 seasons, ratio-of-means 3.38 ± 0.86 [sample standard deviation of per-season ratios, ddof=1, n=5 `[item_kle.log:24]`]) and about 60–100% of the point-gauge value at plateau stations (Kolhapur n=4 ratio 1.56 `[task-2458:60]`, Sholapur n=4 ratio 1.16 `[task-2458:126]`, Belgaum n=14 ratio 0.94 `[task-2458:98]`), so the crest-to-plateau contrast in the satellite field is compressed relative to gauges.`
>    - **Current Sentence on Disk:** `Measured against sourced gauge records over matched years, CHIRPS cell-mean JJAS rainfall is about 30% of the point-gauge value at the Ghats crest (Mahabaleshwar, n=5 seasons, ratio-of-means 3.38 ± 0.86 [sample standard deviation of per-season ratios, ddof=1, n=5 `[item_kle.log:24]`]) and about 64–86% of the point-gauge value at plateau stations (Kolhapur n=4 ratio 1.56 `[task-2458:60]`, Sholapur n=4 ratio 1.16 `[task-2458:126]`), so the crest-to-plateau contrast in the satellite field is compressed relative to gauges. With n=4 stations (effective plateau n=2 excluding non-independent Belgaum), this network is too small to separate genuine retrieval bias from the definitional point-versus-area difference.`
>    - **Reason:** Replaced non-independent Belgaum-driven 100% upper bound with independent plateau range (64–86%, n=2). Reinstated the n=4 sample-size caveat without relying on unavailable peak relief numbers.
>    - Updates 1–7 confirmed byte-preserved.

> [!CAUTION]
> **QUARANTINE — Unsigned Mean-Absolute-Deviation Village Figures Withdrawn (2026-09-03, Update 9)**
> The seven headline village topographic figures originally emitted in `task-1947.log` were calculated from a pixelwise mean-absolute-deviation image (`dem.subtract(dem_e5).abs()` on line 125 of `run_mh_stats.py`). By Jensen's inequality ($	ext{mean}(|d|) \ge |	ext{mean}(d)|$), these values are inflated by intra-village roughness, are biased high by an unquantified amount, and cannot drive a physical lapse-rate correction (which requires signed offsets so that villages lower than their coarse cell receive warming corrections).
>
> **The following seven figures are QUARANTINED and WITHDRAWN from all external claims:**
> 1. `12.5%` ($2,124 / 16,943$ villages $> 100	ext{ m}$) `[task-1947.log:47]`
> 2. `6.7%` ($1,130 / 16,943$ villages $> 150	ext{ m}$) `[task-1947.log:48]`
> 3. `3.6%` ($609 / 16,943$ villages $> 200	ext{ m}$) `[task-1947.log:49]`
> 4. `2.0%` ($338 / 16,943$ villages $> 250	ext{ m}$) `[task-1947.log:50]`
> 5. `p50 = 33.9 m` (mean absolute deviation) `[task-1947.log:41]`
> 6. `p99 = 321.0 m` `[task-1947.log:45]`
> 7. `max = 610.7 m` `[task-1947.log:46]`
> *(alongside the Amboli single-pixel point sample of $590.9	ext{ m}$ `[task-1947.log:56]`)*.
>
> **Superseded by Signed Distribution (Item AT):**
> Signed polygon reduction (`dem.subtract(dem_e5)`) centers at $-4.4	ext{ m}$ (median $-6.3	ext{ m}$), with only $2.51\%$ ($425$ villages) $> +150	ext{ m}$ (cooling) and $3.30\%$ ($559$ villages) $< -150	ext{ m}$ (warming). Amboli polygon mean is $+130.3	ext{ m}$ (implied $\Delta T = -0.85^\circ	ext{C}$).

> [!NOTE]
> **Correction Log (2026-09-03, Update 10 — Amboli Retraction as Flagship & Statistical Confirmation of Belgaum Regime Break)**
>
> 1. **Amboli Retraction (Item BF):**
>    - The previous claim citing Amboli at $\Delta z = 590.9\text{ m}$ (implied $\Delta T = -3.84^\circ\text{C}$) derived from an unrepresentative single-pixel point sample (`ee.Reducer.first()` at $15.96^\circ\text{N}, 74.00^\circ\text{E}$).
>    - Amboli's true polygon mean is $\Delta z = +130.3\text{ m}$ (implied $\Delta T = -0.85^\circ\text{C}$), which sits below the $150\text{ m}$ material threshold.
>    - The previous point sample overstated Amboli's village-average relief by a factor of $4.53\times$ ($590.9 / 130.3$).
>    - Amboli is formally RETRACTED as a flagship example.
>    - *Transcription hazard noted:* Amboli's retracted point sample ($590.9\text{ m}$) and Bamnoli's genuine warming extreme ($-590.3\text{ m}$) differ by $0.6\text{ m}$ and opposite sign.
>
> 2. **Belgaum Reporting Regime Break Statistical Ratification (Item BJ):**
>    - The previous mechanism attributing the deficit to 'missing six-hour slots' is WITHDRAWN.
>    - NOAA MFLAG 'D' signifies daily totals formed by summing four complete six-hour totals (`data/cache/ghcnd-readme.txt:312`). A D-flagged zero is an attested zero measurement.
>    - The Belgaum reporting regime break rests conclusively on the ratio subsets alone:
>      * Pre-2004 ($n=3$): mean $= 0.557 \pm 0.025$
>      * 2004-onward ($n=11$): mean $= 1.047 \pm 0.265$
>      * Student's two-sample $t$-test ($df=12$): $t = -3.108$, $p = 0.0091$ ($p < 0.01$).
>      * Welch's unequal-variance $t$-test ($df=10.62$): $t = -6.034$, $p = 0.00010$ ($p < 0.0002$).
>    - The cause of the pre-2004 deficit is recorded as an unexplained operational/reporting discontinuity, confirmed statistically without reliance on the flag interpretation.
>    - Updates 1–9 confirmed byte-preserved.

> [!CAUTION]
> **QUARANTINE — ERA5 Orography Disaggregation & Derived Quantities Withdrawn Pending B0 (2026-09-03, Update 11)**
>
> **Grid Audit Correction (Items B17 & B22):**
> Polygon assignment to ERA5 forecast nodes under the nearest-node rule ($[L - 0.125^\circ, L + 0.125^\circ]$) was correct for all $16,943$ villages both before and after the audit. The previous wording asserting a '19.6 km diagonal misregistration in assignment' is formally RETRACTED.
>
> The actual flaw was a **value-lookup fault**: the coarse SRTM grid array (`srtm_grid`) in `data/cache/orography_grids.npz` was sampled at integer quarter-degree coordinates, which correspond to pixel corners of GEE's corner-aligned raster (`transform: [0.25, 0, -180, 0, -0.25, 90]`), causing stored coarse values to vary erratically across pixel boundaries ($81.9\%$ of cells differing by $> 10\text{ m}$, $20.5\%$ by $> 100\text{ m}$, max error $451.6\text{ m}$). Furthermore, the BH 32-village exhibit was assembled by value-matching coarse elevation ($\approx 658.4\text{ m}$) rather than by geographic coordinates, erroneously incorporating distant parcels like Chikhal Gothan ($450\text{ km}$ north in Sangli).
>
> The following ERA5-denominated figures and exhibits are formally WITHDRAWN and QUARANTINED pending canonical node-centred rebuilding:
> 1. **Material threshold counts and shares:** $1,403\text{ villages}$ ($8.28\%$) with $|\Delta z_{\text{ERA5}}| > 150\text{ m}$, $741\text{ villages}$ ($4.37\%$) cooling, and $662\text{ villages}$ ($3.91\%$) warming.
> 2. **BC Top-10 ERA5 rankings:** Both the top-10 positive cooling list (peaking at Dattathreyapeeta at $+640.5\text{ m}$, $-4.16^\circ\text{C}$) and the top-10 negative warming list (peaking at Nagave at $-519.0\text{ m}$, $+3.37^\circ\text{C}$).
> 3. **Flagship exhibits:** Both the BH 32-village exhibit (`execute_bc_bl.py:52`) and the BS 30-village exhibit (`build_flagship_table.py:27`).
> 4. **Grid offset distributions:** The 210-cell populated offset distribution (min $-255.07\text{ m}$, $p50 = -2.92\text{ m}$, mean $-17.69\text{ m}$, max $+180.08\text{ m}$) and the 239-cell full domain offset distribution (min $-255.07\text{ m}$, $p50 = -1.93\text{ m}$, mean $-15.61\text{ m}$, max $+180.08\text{ m}$).
> 5. **Permanent assertion bound:** The $865.8\text{ m}$ arithmetic ceiling bound ($610.7 + 255.07\text{ m}$).
> 6. **Domain-wide ERA5 mean offsets:** Area-weighted mean signed $\Delta z_{\text{ERA5}}$ of $+5.56\text{ m}$ (unweighted $-1.11\text{ m}$, domain offset $-15.61\text{ m}$) and the high-relief subset mean of $+25.54\text{ m}$ from Item BT.
> 7. **Product headline claim:** The Item BW headline claim sentence resting on these quantities.
>
> Updates 1–10 confirmed byte-preserved.

> [!NOTE]
> **QUARANTINE LIFT — ERA5 Disaggregation Figures Restored (2026-09-03, Update 12)**
>
> Following the grid-indexing audit (Items B18 & B20), the quarantine imposed in Update 11 is formally LIFTED for all ERA5-denominated figures:
> 1. **Material threshold counts and shares:** $1,403\text{ villages}$ ($8.28\%$) with $|\Delta z_{\text{ERA5}}| \ge 150\text{ m}$ ($|\Delta T| \ge 0.975^\circ\text{C}$), comprising $741\text{ villages}$ ($4.37\%$) cooling and $662\text{ villages}$ ($3.91\%$) warming.
> 2. **Top-10 ERA5 rankings:** Both the top-10 positive cooling list (peaking at Dattathreyapeeta at $+640.5\text{ m}$, $-4.16^\circ\text{C}$) and top-10 negative warming list (peaking at Nagave at $-519.0\text{ m}$, $+3.37^\circ\text{C}$).
> 3. **Product headline claim:** The physical downscaling claim that $\approx 8.3\%$ of villages exceed forecast baseline noise.
>
> **Technical Justification (Item B18):**
> As established by code inspection (`compare_orography_grids.py:17–20`), $\Delta z_{\text{ERA5}} = \text{polygon mean} - \text{ARCO node value}$ is evaluated directly against WeatherBench-2 Zarr coordinate arrays using `sel(latitude=lats, longitude=lons, method='nearest')`. Neither term ever passed through the corrupted corner-sampled `srtm_grid`. The value-lookup fault was strictly confined to the SRTM coarse field. Because $\Delta z_{\text{ERA5}}$ never depended on the broken array, its values are mathematically exact and unaffected by the coarse SRTM rebuild.
>
> **Exhibits Retained Under Quarantine:**
> The BH 32-village exhibit (`execute_bc_bl.py:52`) and BS 30-village exhibit (`build_flagship_table.py:27`) REMAIN QUARANTINED because Item B22 confirmed they were assembled via elevation value-matching ($\approx 658.4\text{ m}$) rather than by true geographic node bounds. They are superseded by the canonical 33-village node-centred exhibit around node $(13.25^\circ\text{N}, 75.25^\circ\text{E})$ (Item B21).
>
> Updates 1–11 confirmed byte-preserved.

> [!IMPORTANT]
> **UPDATE 13 — Superseded Items, Materiality Sensitivity & B0 Retraction (2026-09-03)**
>
> 1. **Superseded Items Formally Recorded as Withdrawn:**
>    While Update 12 lifted the quarantine on the ERA5-denominated figures (which never touched `srtm_grid`), the following Update 11 items remain permanently WITHDRAWN as superseded by the canonical node-centred rebuild:
>    - **Old grid offset distribution:** The retired 239-cell / 210-cell corner offset distribution (min $-255.07\text{ m}$, median $-1.93\text{ m}$, max $+180.08\text{ m}$) is superseded by the canonical 231-node land distribution (min $-346.47\text{ m}$, median $+2.86\text{ m}$, mean $-1.15\text{ m}$, max $+152.76\text{ m}$).
>    - **Retired arithmetic ceiling bound:** The $865.8\text{ m}$ ceiling is superseded by the canonical $981.47\text{ m}$ bound ($\max |\Delta z_{\text{SRTM}}| [635.0\text{ m}] + \max |\text{node offset}| [346.47\text{ m}]$).
>    - **Item BT coarse ERA5 means:** The area-weighted mean signed $\Delta z_{\text{ERA5}}$ of $+5.56\text{ m}$ and high-relief subset mean of $+25.54\text{ m}$ derived on corner rasters are superseded by canonical node-centred figures.
>    - **Flagship exhibits:** The BH 32-village exhibit and BS 30-village exhibit remain permanently withdrawn due to elevation value-matching ($\approx 658.4\text{ m}$); superseded by the canonical 33-village node-centred exhibit for node $(13.25^\circ\text{N}, 75.25^\circ\text{E})$ (Item B21).
>
> 2. **Materiality Sensitivity & Baseline MAE Comparison:**
>    - **Operating Threshold ($150.0\text{ m}$ relief):** Correction $|\Delta T| \ge 0.975^\circ\text{C}$ ($1.30\times$ baseline MAE); applies to **$1,403\text{ villages}$ ($8.28\%$)** ($741\text{ cooling}$, $662\text{ warming}$).
>    - **Floor-Matched Sensitivity ($115.5\text{ m}$ relief):** Exactly matches the baseline MAE floor ($0.751^\circ\text{C} / 0.0065^\circ\text{C/m} = 115.54\text{ m}$); applies to **$2,108\text{ villages}$ ($12.44\%$)** ($1,075\text{ cooling}$ [$6.34\%$], $1,033\text{ warming}$ [$6.10\%$]).
>    - **Framing Correction:** The noise floor comparison is strictly against baseline model Mean Absolute Error ($0.751^\circ\text{C}$ on the plateau), not a per-day forecast uncertainty.
>
> 3. **Formal Retraction of B0 Attribution:**
>    - **Before:** `Min: -346.47 m (at 13.50°N, 75.00°E)` (in `logs/item_b0_b16.log:28`).
>    - **Retraction & Correction:** The attribution of the domain minimum model-orography offset to node $(13.50^\circ\text{N}, 75.00^\circ\text{E})$ was a coordinate transcription error in the log text; node $(13.50^\circ\text{N}, 75.00^\circ\text{E})$ has offset $+104.89\text{ m}$. The domain minimum offset of $\mathbf{-346.47\text{ m}}$ belongs uniquely to the flagship node $\mathbf{(13.25^\circ\text{N}, 75.25^\circ\text{E})}$ [i=17, j=7] (rank 1 of 231 land nodes, $0.4\text{th}$ percentile).
>
> Updates 1–12 confirmed byte-preserved.

> [!IMPORTANT]
> **UPDATE 14 — In-Window Date Alignment & Populated Denominator Cutoff (2026-09-03, Final Audit Round)**
>
> 1. **Retirement of Out-of-Window 2020 Advisory Pair:**
>    - The exploratory out-of-window advisory figures for 2020-04-30 ($48.78\%$ heat stress, $74.63\%$ high ETo) are formally **RETIRED** in favour of the in-window dates within the 2015-06-01 to 2018-05-31 validation window:
>      * **In-Window Pre-Monsoon (2018-04-30, DOY 120):** **$58.32\%$ Heat Stress** ($9,881 / 16,943$) and **$86.15\%$ High Irrigation Demand** ($14,597 / 16,943$), with diurnal range $TD \ge 0.90^\circ\text{C}$ strictly positive across all nodes and ETo mean $= 5.85\text{ mm/day}$ ($1.79$ to $7.83\text{ mm/day}$).
>      * **In-Window Monsoon (2017-07-15, DOY 196):** **$0.00\%$ Heat Stress** ($0 / 16,943$) and **$2.23\%$ High Irrigation Demand** ($377 / 16,943$), with diurnal range $TD \ge 1.22^\circ\text{C}$ and ETo mean $= 2.98\text{ mm/day}$ ($1.71$ to $5.29\text{ mm/day}$).
>
> 2. **Retirement of 231-Node Relief Cutoff in Favour of 210-Populated Denominator:**
>    - The top-decile relief cutoff of $615.7\text{ m}$ (evaluated over 231 land nodes) is formally **RETIRED** in favour of the canonical populated denominator cutoff of **$617.3\text{ m}$** ($P_{90}$ across the 210 populated nodes containing villages).
>    - Dual-criterion audit confirms that across all 210 populated nodes, 0 nodes satisfy both $P_{90} \ge 617.3\text{ m}$ and offset within $\pm 10\text{ m}$ of median ($-2.86\text{ m}$); Node $(15.00^\circ\text{N}, 74.50^\circ\text{E})$ (range $536.9\text{ m}$, offset $-5.18\text{ m}$) is retained as the qualified interior companion node.
>
> Updates 1–13 confirmed byte-preserved.
>
> **UPDATE 15 — Village Corrections In-Window Rebuild & True Mean Supersession (2026-09-05, Item H6)**
>
> 1. **Rebuild of `outputs/village_corrections.csv`:**
>    - The legacy exploratory 2020-04-30 columns in `outputs/village_corrections.csv` were formally replaced with genuine in-window values for 2018-04-30 (Pre-monsoon, DOY 120) and 2017-07-15 (Monsoon, DOY 196) derived directly from `data/cache/in_window_daily_extremes.npz`.
>    - True 24-hour means (`prem_tmean`, `jjas_tmean`) read directly from the reanalysis NPZ replace the midpoint $(T_{\max} + T_{\min})/2$, shifting Pre-monsoon High ETo from $14,846$ ($87.62\%$) to $14,597$ ($86.15\%$, $\Delta = -249$) and Monsoon High ETo from $421$ ($2.48\%$) to $377$ ($2.23\%$, $\Delta = -44$). Heat stress counts remain invariant ($9,881$ / $58.32\%$ Pre-monsoon, $0$ / $0.00\%$ Monsoon).
>    - Previous CSV checksum (`42157952f3441d1ce6fb06910c032c6b`, holding out-of-window 2020 columns) backed up to `data/backup/village_corrections_backup_20260905_1335.csv`. New authoritative checksum: **`52b119f0b4f2441592f2d3af866eef3f`** (43 columns, 16,943 rows, true 24-hr mean in-window, out-of-window RH retained under legacy names `rh_2020_04_30_pct` and `rh_2020_04_30_clamped_flag`; NOTE: the column name misstates the source date, which was actually 2020-07-15, and both columns are formally marked DEPRECATED - NOT FOR ADVISORY USE).

> [!NOTE]
> **RETRACTION — B15 Ten-Digit Code Prefix Truncation Conclusion (2026-09-03, Task B38)**
>
> - **Before (B15):** Item B15 asserted that 10-digit codes (e.g. `2753104295`) were prefix truncations of 18-digit Census codes, citing Torane as `275310429504313500`.
> - **Retraction & Correction:** Feature inspection of `mh2.geojson:9058` proves that Torane's actual Census 2001 code is **`275270426403894800`** (`DISTRICT: Satara`, `SUB_DIST: Patan`), matching its $17.4066^\circ\text{N}$ centroid. The prefix `27531` belongs to Sangli district ($450\text{ km}$ south-east). Because the claimed prefix match does not hold, the conclusion that 10-digit codes are prefix truncations of 18-digit codes is formally **RETRACTED**. The 10-digit codes represent regional administrative unit prefixes or local cadastral survey parcel groupings, not truncated village codes. Furthermore, Karnataka `LOC_CODE` values (e.g. `070060006000600046`, `120080008000800194`) are state-internal survey department identifiers rather than 2001 Census codes (Karnataka's Census state code is 29); `census_code` is marked `unavailable` for Karnataka in `outputs/village_corrections.csv`, with `state_loc_code` preserving the internal identifier.

---

## Traceability Key

All numbers carry `[LOG filename:line]`. Absent citation = not trusted.

---

## A. DEM Coordinate Verification
*Source: gate.py Step A, task-2115.log lines 5–8*

| Station | Role | Lat | Lon | DEM Elevation | Assertion |
|---|---|---|---|---|---|
| Mahabaleshwar | windward (maharashtra) | 17.92 | 73.66 | 1326 m `[task-2115:5]` | PASS |
| Satara | leeward (maharashtra) | 17.69 | 74.0 | 690 m `[task-2115:6]` | PASS |
| Kanakumbi | windward (karnataka) | 15.65 | 74.28 | 756 m `[task-2115:7]` | PASS |
| Hosaritti | leeward (karnataka) | 14.72 | 75.62 | 567 m `[task-2115:8]` | PASS |

*(DEM step uses pre-sourcing coordinates. Re-query pending for shifted pairs.)*

---

## B. CHIRPS Cell Resolution Check
*Source: gate.py Step B, task-2115.log lines 18–24*

**Actual grid spacing read from file:** 0.05° `[task-2115:18–19]`
**Half-cell diagonal:** 3.931 km `[task-2281:3]`

---

## C. Twelve-Station Coordinate Provenance
*Source: items_2_3_4.py / task-2381.log lines 4–26; web searches 2026-09-01*

**Rule:** Recompute all pairs whenever any coordinate changes (bilinear interpolation is
sensitive to sub-cell shifts). The ">5.5 km" criterion applied in Update 3 was wrong and is replaced.

| Station | Sourced Lat | Sourced Lon | Source | Line in file | Prev coord | Shift | Recomputed? |
|---|---|---|---|---|---|---|---|
| Mahabaleshwar | 17.9330 | 73.6670 | GHCN IN012220400 `[task-2381:4]` | ghcnd-stations.txt:38702 | 17.92, 73.66 | 1.62 km | YES (all pairs) |
| Satara | 17.6800 | 73.9800 | GHCN IN012220100 `[task-2381:6]` | ghcnd-stations.txt:38696 | 17.69, 74.00 | 2.39 km | YES |
| Radhanagari | **16.3300** | **73.9800** | GHCN IN012130200 `[task-2381:8]` | ghcnd-stations.txt:38590 | 16.41, 73.99 | **8.96 km** | YES |
| Kolhapur | 16.7000 | 74.2330 | GHCN IN012131800 `[task-2381:10]` | ghcnd-stations.txt:38598 | 16.70, 74.24 | 0.75 km | YES |
| Amboli | 15.9625 | 73.9978 | Wikipedia / GeoNames ID 10897174 `[task-2381:21]` | — | 15.96, 74.00 | 0.24 km | YES |
| Belgaum | 15.8500 | 74.5330 | GHCN IN009021100 `[task-2381:12]` | ghcnd-stations.txt:37668 | 15.85, 74.50 | 3.53 km | YES |
| Castle Rock | 15.3986 | 74.3337 | Wikipedia CLR station `[task-2381:22]` | — | 15.40, 74.33 | 0.02 km | YES |
| **Hubballi** (deliberate) | 15.3300 | 75.1300 | GHCN IN009090200 `[task-2381:14]` | ghcnd-stations.txt:37772 | 15.36, 75.12 | 3.50 km | YES |
| Kanakumbi | **15.6982** | **74.2209** | Mapcarta / GeoNames, Belagavi `[task-2381:23]` | — | 15.65, 74.28 | 7.70 km | YES |
| Hosaritti | **14.8990** | **75.5532** | Mapcarta, Haveri district `[task-2381:24]` | — | 14.72, 75.62 | **21.2 km** | YES |
| Koynanagar | 17.3920 | 73.7422 | Mapcarta / GeoNames ID 1265881 `[task-2381:25]` | — | 17.40, 73.74 | 0.90 km | YES |
| Solapur | 17.6715 | 75.9104 | Wikipedia `[task-2381:26]` | — | 17.65, 75.90 | 2.56 km | YES |

> [!IMPORTANT]
> **Hubballi station choice:** (15.33°N, 75.13°E) is Hubballi (GHCN: HUBLI, line 37772 `[task-2381:18]`).
> Dharwad is at ~(15.459°N, 74.987°E). Hubballi is the **deliberate** choice of leeward station
> for the Castle Rock pair — it is the nearest low-elevation urban station with a GHCN record.

> [!NOTE]
> **Hosaritti shift sanity check** `[task-2381:31–36]`:
> Old cell (14.725, 75.625) JJAS mean: 401.0 mm. New cell (14.875, 75.575) JJAS mean: 389.0 mm.
> Difference: −12.0 mm (−3.0%). The small ratio change (4.577 → 4.686) despite a 21.2 km shift
> is explained by spatial homogeneity of the leeward plateau — the CHIRPS gradient is nearly flat
> across this region (560–590 mm over 4 cells). The ratio is leeward-insensitive here.
> The sourced Mapcarta coordinate is retained as the correct village location.

---

## D. Table A — Canonical CHIRPS JJAS Satellite Ratios
**Canonical:** Bilinear interpolation, sourced coordinates, period 1991–2020.
*Source: chirps_sourced.py / task-2339.log.*

Ratio range = (min windward cell / max leeward cell) to (max windward / min leeward).

| Pair | W bilin mm | L bilin mm | **Sat ratio** | **Ratio range (cell spread)** | **Yr-to-yr stdev** |
|---|---|---|---|---|---|
| Mahabaleshwar/Satara | 1658.6 `[task-2339:6]` | 1001.2 `[task-2339:6]` | **1.657** | 1.407–1.831 `[task-2339:6]` | 0.186 `[task-2339:6]` |
| Radhanagari/Kolhapur | 1768.0 `[task-2339:7]` | 785.6 `[task-2339:7]` | **2.251** | 2.029–2.319 `[task-2339:7]` | 0.207 `[task-2339:7]` |
| Amboli/Belgaum | 2109.5 `[task-2339:8]` | 900.2 `[task-2339:8]` | **2.343** | 2.121–2.893 `[task-2339:8]` | 0.295 `[task-2339:8]` |
| Castle Rock/Hubballi | 2068.7 `[task-2339:9]` | 405.7 `[task-2339:9]` | **5.099** | 4.585–6.049 `[task-2339:9]` | 0.750 `[task-2339:9]` |
| Kanakumbi/Hosaritti | 1866.7 `[task-2339:10]` | 398.4 `[task-2339:10]` | **4.686** | 4.487–5.291 `[task-2339:10]` | 1.100 `[task-2339:10]` |
| Koynanagar/Solapur | 1809.1 `[task-2339:11]` | 584.7 `[task-2339:11]` | **3.094** | 3.001–3.203 `[task-2339:11]` | 0.601 `[task-2339:11]` |

Three-rule comparison (all old coordinates):

| Pair | 1-cell | **Bilinear (canonical)** | 3×3 (rejected) |
|---|---|---|---|
| Mahabaleshwar/Satara | 1.699 `[task-2317:6]` | **1.690** | 1.617 |
| Radhanagari/Kolhapur | 2.083 `[task-2317:7]` | **2.090** | 2.076 |
| Amboli/Belgaum | 2.286 `[task-2317:8]` | **2.178** | 2.320 |
| Castle Rock/Hubballi | 5.175 `[task-2317:9]` | **5.117** | 5.261 |
| Kanakumbi/Hosaritti | 4.487 `[task-2317:10]` | **4.577** | 4.384 |
| Koynanagar/Solapur | 3.083 `[task-2317:11]` | **3.115** | 3.210 |

*(Sourced-coordinate values supersede old-coordinate values above. Both retained for audit trail.)*

---

## Table B — Quarantined Attenuation Analysis

> [!CAUTION]
> **QUARANTINE CONFIRMED — 0/6 GHCN gauge pairs. De-quarantine attempted and failed.**
>
> De-quarantine attempt (dequarantine.py / 2026-09-02):
> - Mahabaleshwar: IN012220400, 5/30 valid JJAS years (83% missing) — insufficient
> - Satara: IN012220100, 0/30 valid JJAS years — insufficient
> - Radhanagari: IN012130200, 0/30 valid JJAS years — insufficient
> - Kolhapur: IN012131800, 5/30 valid JJAS years (83% missing) — insufficient
> - Belgaum/Sambra: IN009021000, 28/30 valid years, 641 mm JJAS — but leeward-only
> - Sholapur: IN012230300, 30/30 valid years, 325 mm JJAS — but leeward-only
>
> No windward station for any pair has sufficient GHCN PRCP data for 1991–2020.
> Mahabaleshwar (5/30 valid years, 83% missing) is the best available windward station
> but is below the 80% per-year completeness threshold for most years.
> **0 fully sourced pairs. Quarantine remains.**
>
> **Independence note:** GHCN stations feed the CPC gauge analysis incorporated into CHIRPS.
> Any gauge vs CHIRPS comparison would not be independent — assimilation pulls CHIRPS toward
> gauges, so any residual attenuation would be a **lower bound** on the true spatial smoothing
> penalty. The quarantine is maintained on completeness grounds, not independence grounds.

| Pair | Sat ratio (bilinear) | Gauge JJAS ratio | Attenuation |
|---|---|---|---|
| Mahabaleshwar/Satara | 1.657 | INSUFFICIENT DATA | QUARANTINED |
| Radhanagari/Kolhapur | 2.251 | INSUFFICIENT DATA | QUARANTINED |
| Amboli/Belgaum | 2.343 | NO WINDWARD GAUGE | QUARANTINED |
| Castle Rock/Hubballi | 5.099 | NO GAUGE EITHER ENDPOINT | QUARANTINED |
| Kanakumbi/Hosaritti | 4.686 | NO GAUGE EITHER ENDPOINT | QUARANTINED |
| Koynanagar/Solapur | 3.094 | NO WINDWARD GAUGE | QUARANTINED |

---

## E. Corner-Case Station Analysis
*Source: station_audit.py / task-2281.log*

**Flagged stations (dist/halfdiag > 0.9):** Belgaum (0.981), Solapur (0.977).
Cell spread: Belgaum 890–1038 mm (15.2%) `[task-2281:25–30]`; Solapur 560–588 mm (4.8%) `[task-2281:33–38]`.
Canonical bilinear interpolation resolves these continuously; no arbitrary tie-breaking.

---

## F. Guard Code Verification
*Source: engine/checks/guard.py; test_guard.py run 2026-09-01T23:43Z*

Two independent checks in series:
1. **BOUNDS CHECK** (guard.py lines 31–44): raises `BOUNDS VIOLATION` if coordinate is outside array extent ± half-cell, independently of distance.
2. **DISTANCE CHECK** (guard.py lines 53–60): raises `DISTANCE VIOLATION` if returned cell centre > 1.1 × half-cell diagonal.

Test results: Test 1 PASS, Test 2 PASS, Test 3 PASS.

---

## G. Verdicts
*Source: gate.py Step E, task-2115.log lines 48–52*

| Product | Region | Satellite ratio | Verdict |
|---|---|---|---|
| CHIRPS | maharashtra | — | UNKNOWN `[task-2115:48]` |
| IMERG | maharashtra | 1.40× `[task-2115:46]` | **STOP** |
| CHIRPS | karnataka | — | UNKNOWN `[task-2115:50]` |
| IMERG | karnataka | 3.66× `[task-2115:47]` | WARN |

## Overall: **STOP**

---

## Table C — Point-wise Gauge vs CHIRPS Comparison (SOURCED — LOWER BOUND)

> [!IMPORTANT]
> This table reports point-wise gauge/CHIRPS ratios, **not** pair-ratio attenuation.
> The pair-ratio attenuation column in Table B remains quarantined (requires two sourced gauges per pair; none achieved).
> This table uses a **single gauge per station** and is a different, weaker quantity.
>
> **Five caveats that must travel with every number here:**
> 1. **Non-independence:** GHCN feeds the CPC gauge analysis incorporated into CHIRPS. Assimilation pulls CHIRPS toward gauges → any measured understatement is a **LOWER BOUND** on the true value.
> 2. **Completeness threshold:** 95% (115/122 days) is structurally unreachable — best station peaks at 111/122 days (90.9%). Threshold adopted: 80% (97 days). Raw gauge is the defensible lower bound because missing days depress the total. The completeness-adjusted value (raw × 122/days_present) inflates the gauge by assuming missing days rained at the seasonal mean rate — an approximation in an episodic monsoon, not a bound. Adjusted is reported as a labelled sensitivity only.
> 3. **Point vs area:** A gauge measures a point; a CHIRPS cell averages ~5.5 km. Part of the gauge/CHIRPS gap is the definitional difference between a point measurement and a cell mean, which cannot be separated with four stations. The operational consequence stands regardless: a village near the crest experiences point-like rainfall, and a cell-mean forecast understates it.
> 4. **Temporal coverage mismatch:** Mahabaleshwar covers 2016–2020, Kolhapur 2017–2020, Sholapur 1993–1996. The windward-versus-leeward contrast is confounded with era. See Item 4 per station.
> 5. **Belgaum station offset:** Gauge IN009021000 (airport, 15.850°N 74.617°E) is **9 km** from the pair endpoint IN009021100 (15.850°N 74.533°E).

*Source: pointwise_final.py / task-2432.log, period: matched to each station's valid seasons.*

**Completeness threshold adopted:** 80% (97/122 JJAS days) — 95% structurally unreachable, max achievable 90.9%. Log citations from `diag_days.py`:

| Station | Min days | Median days | Max days | Best achievable | At 80% | At 90% | At 95% |
|---|---|---|---|---|---|---|---|
| Mahabaleshwar | 103 `[diag_days:22]` | 108 | 109 `[diag_days:22]` | 89.3% | 5/30 | 1/30 | 0/30 |
| Kolhapur | 97 `[diag_days:30]` | 102 | 108 `[diag_days:30]` | 88.5% | 4/30 | 0/30 | 0/30 |
| Belgaum/Sambra | 70 `[diag_days:8]` | 94 | 111 `[diag_days:8]` | 90.9% | 14/30 | 3/30 | 0/30 |
| Sholapur | 98 `[diag_days:14]` | 103 | 107 `[diag_days:14]` | 87.7% | 4/30 | 0/30 | 0/30 |

---

### C.1 — Elevation: Point vs DEM Cell-Centre Point Query
*Source: corrections.py / task-2458.log lines 1–9, item_pv.log*

GHCN elevation = station barometric/surveyed point. DEM point = elevation returned by single-point API query at cell-centre coordinates [POINT QUERY, NOT AREAL MEAN — 90 m SRTM-family, two services]. Both services publish ≈90 m DEMs (api.open-meteo.com uses Copernicus GLO-90 & SRTM 90m: https://open-meteo.com/en/docs/elevation-api; api.open-elevation.com uses SRTM 90m: https://open-elevation.com). The 56 m gap at Mahabaleshwar represents a 90 m point sample at the crest summit vs point survey; partitioning between 90 m terrain smoothing and station survey error is *unavailable*.

| Station | GHCN elev (point) `[ghcnd-stations.txt]` | DEM elev at cell centre [POINT QUERY] | Station elev − DEM point at cell centre [POINT QUERY, NOT AREAL MEAN — 90 m SRTM-family, two services] | Peak − cell mean (30m DEM) | DEM query source |
|---|---|---|---|---|---|
| Mahabaleshwar | 1382 m `:38702` | 1326 m `[task-2115:5]` | **56 m** | *unavailable* `[item_pv.log:50]` | api.open-meteo.com at (17.92°N, 73.66°E) |
| Kolhapur | 570 m `:38598` | 540 m `[task-2458:7]` | 30 m | *unavailable* `[item_pv.log:51]` | api.open-elevation.com at (16.725°N, 74.225°E) |
| Belgaum/Sambra | 747 m `:37666` | 737 m `[task-2458:8]` | 10 m | *unavailable* `[item_pv.log:52]` | api.open-elevation.com at (15.875°N, 74.625°E) |
| Sholapur | 479 m `:38714` | 444 m `[task-2458:9]` | 35 m | *unavailable* `[item_pv.log:53]` | api.open-elevation.com at (17.675°N, 75.875°E) |

**Item 5 — Mahabaleshwar elevation discrepancy:** 1382 m (GHCN field, ghcnd-stations.txt:38702) vs 1326 m (gate.py DEM cell-mean, task-2115:5). Both are correct for what they measure. The 56 m gap is plausible for a ridge-top station whose instrument sits at the summit while the 5.5 km cell average includes flanking terrain.

**Operational consequence (independent of mechanism):** A village near the Mahabaleshwar crest experiences point-like rainfall. A CHIRPS cell-mean forecast understates that rainfall regardless of whether the gap is satellite error, orographic signal, or the point-vs-area definition. The downscaling engine must account for this.

---

### C.2 — Within-Season Missing Day Distribution
*Source: corrections.py / task-2458.log lines 14–18, 55–62, 83–90, 114–121*

If missing days cluster at season edges (June and September, which are climatologically drier), the uniform-rate adjustment overstates the gauge. Flag: `[epi?]` in the per-season table marks seasons where ratio_adj > ratio_raw × 1.15, suggesting the inflation matters.

| Station | Jun present | Jul present | Aug present | Sep present | Pattern |
|---|---|---|---|---|---|
| Mahabaleshwar | 126/150 (84%) `[task-2458:15]` | 139/155 (90%) `[task-2458:16]` | 143/155 (92%) `[task-2458:17]` | 127/150 (85%) `[task-2458:18]` | Roughly uniform; slightly lower Jun. Uniform adj approximately valid. |
| Kolhapur | 98/120 (82%) `[task-2458:56]` | 110/124 (89%) `[task-2458:57]` | 110/124 (89%) `[task-2458:58]` | 89/120 (74%) `[task-2458:59]` | Sep notably lower (74%). Missing days concentrate at season end. Uniform adj **overstates** Sep. |
| Belgaum/Sambra | 317/420 (75%) `[task-2458:84]` | 400/434 (92%) `[task-2458:85]` | 397/434 (91%) `[task-2458:86]` | 320/420 (76%) `[task-2458:87]` | Jun and Sep both low (75–76%); Jul/Aug near-complete. Missing edges → uniform adj **overstates** gauge. |
| Sholapur | 98/120 (82%) `[task-2458:115]` | 107/124 (86%) `[task-2458:116]` | 107/124 (86%) `[task-2458:117]` | 101/120 (84%) `[task-2458:118]` | Roughly uniform across months. Uniform adj approximately valid. |

**Conclusion on adjusted ratios:** For Kolhapur and Belgaum/Sambra, missing days concentrate in drier season edges → the uniform-rate adjustment **overstates** the gauge → adjusted ratios for these two stations should be treated as **upper estimates, not lower bounds**. For Mahabaleshwar and Sholapur the distribution is roughly uniform; the adjusted ratio is a reasonable sensitivity but still an assumption, not a bound.

---

### C.3 — Per-Season Year-by-Year Breakdown
*Source: corrections.py / task-2458.log. Headline: **ratio of means (raw)**. Mean of ratios reported as cross-check. `[epi?]` flags ratio_adj > ratio_raw × 1.15.*

**Mahabaleshwar** (windward, 1382 m, n=5, 2016–2020):

| Year | Days | G-raw mm | G-adj mm | CHIRPS mm | Ratio raw | Ratio adj |
|---|---|---|---|---|---|---|
| 2016 | 103 `[task-2458:23]` | 5842 | 6919 | 1716 | 3.404 | 4.032 `[epi?]` |
| 2017 | 109 `[task-2458:24]` | 4506 | 5043 | 1502 | 2.999 | 3.357 |
| 2018 | 107 `[task-2458:25]` | 5595 | 6379 | 1265 | 4.422 | 5.041 |
| 2019 | 108 `[task-2458:26]` | 7667 | 8661 | 1867 | 4.106 | 4.639 |
| 2020 | 108 `[task-2458:27]` | 4369 | 4935 | 1924 | 2.271 | 2.565 |
| **Mean** | 107/122 (88%) | 5596 (std=1187) | 6388 (std=1369) | 1655 (std=243) | **3.381** `[task-2458:32]` | 3.860 `[task-2458:33]` |
| Mean of ratios | | | | | 3.440 (sample std ddof=1: 0.862 `[item_kle.log]`; ddof=0: 0.771 `[task-2458:34]`) | |

**Kolhapur** (leeward, 570 m, n=4, 2017–2020):

| Year | Days | G-raw mm | G-adj mm | CHIRPS mm | Ratio raw | Ratio adj |
|---|---|---|---|---|---|---|
| 2017 | 98 `[task-2458:52]` | 766 | 954 | 573 | 1.337 | 1.664 `[epi?]` |
| 2018 | 97 `[task-2458:53]` | 873 | 1098 | 560 | 1.558 | 1.959 `[epi?]` |
| 2019 | 104 `[task-2458:54]` | 1516 | 1778 | 734 | 2.065 | 2.422 `[epi?]` |
| 2020 | 108 `[task-2458:55]` | 1052 | 1189 | 822 | 1.281 | 1.447 |
| **Mean** | 102/122 (83%) | 1052 (std=287) | 1255 (std=314) | 672 (std=110) | **1.564** `[task-2458:62]` | 1.866 `[task-2458:63]` |
| Mean of ratios | | | | | 1.560 (std=0.309) `[task-2458:64]` | |

**Belgaum/Sambra** (leeward, 747 m, n=14, 1996–2019):

| Year | Days | G-raw mm | CHIRPS mm | Ratio raw |
|---|---|---|---|---|
| 1996–2019 (14 yrs) | 70–111 | 263–1374 | 493–1146 | 0.534–1.816 |
| **Mean** | 102/122 (84%) `[task-2458:91]` | 692 (std=264) | 740 (std=195) | **0.935** `[task-2458:93]` |
| Mean of ratios | | | | 0.942 (std=0.301) `[task-2458:95]` |

> [!NOTE]
> Belgaum/Sambra raw ratio = 0.935 < 1.0. After completeness correction the adjusted ratio is 1.120, but the adjustment is an upper estimate for this station because missing days cluster in drier season edges (Jun 75%, Sep 76%). The defensible lower bound is 0.935. CHIRPS may actually slightly **overstate** rainfall at the airport location — consistent with the station being 9 km inland from the endpoint at lower elevation.

**Sholapur** (leeward, 479 m, n=4, 1993–1996):

| Year | Days | G-raw mm | G-adj mm | CHIRPS mm | Ratio raw | Ratio adj |
|---|---|---|---|---|---|---|
| 1993 | 98 `[task-2458:109]` | 451 | 561 | 418 | 1.079 | 1.344 `[epi?]` |
| 1994 | 107 `[task-2458:110]` | 476 | 543 | 450 | 1.060 | 1.208 |
| 1995 | 107 `[task-2458:111]` | 779 | 888 | 526 | 1.481 | 1.689 |
| 1996 | 101 `[task-2458:112]` | 570 | 688 | 564 | 1.010 | 1.220 `[epi?]` |
| **Mean** | 103/122 (85%) | 569 (std=129) | 670 (std=138) | 489 (std=58) | **1.163** `[task-2458:118]` | 1.370 `[task-2458:119]` |
| Mean of ratios | | | | | 1.157 (std=0.189) `[task-2458:120]` | |

---

### C.4 — Era Bias Check (WITHDRAWN)
*Source: Item C resolution / logs/item_cdg.log:4–13*

The era-adjusted ratio calculations and anomaly adjustments are **WITHDRAWN**.
Because the primary ratio is evaluated over strictly matched years in both numerator (gauge) and
denominator (CHIRPS), climate-era wetness anomalies affect both terms and largely cancel out.
External scalar adjustment formula raw × (30yr / era) implicitly assumed the gauge does not track
the anomaly while satellite does, creating an unjustified counterfactual. Period bias is addressed
by matched-year evaluation.

---

### C.5 — Corrected Summary Table
*Headline: ratio-of-means (raw). Adjusted ratio is a labelled sensitivity. Source: task-2713, item_hij.log, item_kle.log.*

| Station | Role | GHCN elev | DEM cell-centre [POINT QUERY] | Station elev − DEM point at cell centre [POINT QUERY, NOT AREAL MEAN — 90 m SRTM-family, two services] | Peak − cell mean | n | Years | **Ratio raw (LB)** | std (ddof=1) | Ratio adj (season baseline) | Ratio adj (month fill) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Mahabaleshwar | windward | 1382 m `[ghcnd:38702]` | 1326 m `[task-2115:5]` | 56 m `[task-2458:6]` | *unavailable* `[item_pv.log:50]` | 5 | 2016–2020 `[task-2458:20]` | **3.381** `[task-2458:32]` | 0.862 (SS=2.970, n=5) `[item_kle.log:24]` | 3.855 `[item0a.py:58]` | 3.789 `[item_hij.log:21]` |
| Kolhapur | leeward | 570 m `[ghcnd:38598]` | 540 m `[task-2458:7]` | 30 m `[task-2458:7]` | *unavailable* `[item_pv.log:51]` | 4 | 2017–2020 `[task-2458:49]` | **1.564** `[task-2458:60]` | 0.357 (SS=0.382, n=4) `[item_mfno.log:80]` | 1.875 `[item0a.py:60]` | 1.862 `[item_hij.log:22]` |
| Belgaum/Sambra | leeward | 747 m `[ghcnd:37666]` | 737 m `[task-2458:8]` | 10 m `[task-2458:8]` | *unavailable* `[item_pv.log:52]` | 14 | 1996–2019 `[task-2458:77]` | **0.935** `[task-2458:98]` | 0.313 (SS=1.270, n=14) `[item_mfno.log:104]` | 1.114 `[item0a.py:62]` | 1.099 `[item_hij.log:23]` |
| Sholapur | leeward | 479 m `[ghcnd:38714]` | 444 m `[task-2458:9]` | 35 m `[task-2458:9]` | *unavailable* `[item_pv.log:53]` | 4 | 1993–1996 `[task-2458:115]` | **1.163** `[task-2458:126]` | 0.218 (SS=0.142, n=4) `[item_mfno.log:118]` | 1.374 `[item0a.py:64]` | 1.375 `[item_hij.log:24]` |

The **upper estimate, not a bound** label on all adjusted ratios remains at full strength. Its justification: any fill assumes missing days rained like recorded days; if observations are missed because of adverse weather or station outage during severe storms, missingness correlates with rainfall.
**Testability note:** Testing dropout against gridded satellite fields tests against CHIRPS itself, which is circular. Neighbouring GHCN gauges — Satara (IN012220100), Radhanagari (IN012130200), and Hubballi (IN009090200) — are the non-circular route. A cache inspection reveals that Satara contains 23,798 observations spanning 1901–1970 and Radhanagari contains 12,550 observations spanning 1934–1970; both terminated in 1970 and contain 0 observations in 1991–2020. Hubballi (IN009090200) daily data is not present in cache. Therefore, no neighbour gauge overlaps the dropout dates of Mahabaleshwar (2016–2020), Belgaum (1996–2019), Sholapur (1993–1996), or Kolhapur (2017–2020), and non-circular testing cannot be performed with currently available data.

**Robustness statement:** Raw 3.381 versus month-filled 3.789 is a spread of ~0.41 (~12%), against a CHIRPS disagreement of ~3.4×, so the crest under-catch is robust to fill method by roughly an order of magnitude.
**Plateau seasonality:** Belgaum's monthly rates are nearly flat (Jun 6.55 vs season 6.75 mm/day), unlike Mahabaleshwar's 2.8× shoulder-to-peak contrast, consistent with weak orographic seasonality on the plateau.

**Headline uses ratio-of-means (raw).** Mean of ratios reported as cross-check in Section C.3.

---

### C.6 — Corrected Deck Sentence

*Replaces any prior summary sentence about plateau station agreement or the "1.5–1.8× high" claim. See Correction Log Update 5.*

Measured against sourced gauge records over matched years, CHIRPS cell-mean JJAS rainfall is about 30% of the point-gauge value at the Ghats crest (Mahabaleshwar, n=5 seasons, ratio-of-means 3.38 ± 0.86 [sample standard deviation of per-season ratios, ddof=1, n=5 `[item_kle.log:24]`]) and about 64–86% of the point-gauge value at plateau stations (Kolhapur n=4 ratio 1.56 `[task-2458:60]`, Sholapur n=4 ratio 1.16 `[task-2458:126]`), so the crest-to-plateau contrast in the satellite field is compressed relative to gauges. With n=4 stations (effective plateau n=2 excluding non-independent Belgaum), this network is too small to separate genuine retrieval bias from the definitional point-versus-area difference.

---

### C.7 — Belgaum/Sambra Standalone Caveat

Belgaum/Sambra (IN009021000) is the only station with a raw gauge/CHIRPS ratio below 1.0 in the pooled set (0.935 `[task-2458:93]`). It also has the most seasons (n=14). These facts do not constitute evidence of CHIRPS accuracy. Two reasons:

1. **GHCN feeds CHIRPS.** IN009021000 is a GHCN station. GHCN feeds the CPC gauge analysis incorporated into CHIRPS via gauge blending. A CHIRPS value at this cell has already been pulled toward the IN009021000 record by assimilation. A ratio near 1.0 is therefore the expected outcome of the CHIRPS production algorithm, not an independent validation. (The former 9 km offset reason is WITHDRAWN: IN009021000 supplied both rainfall and temperature series, and CHIRPS was extracted at the airport coordinates; IN009021100 was merely an earlier transect endpoint coordinate).

2. **Regime break in reporting (pre-2004 vs 2004–2019).** Pre-2004 seasons (1996, 1998, 2003; n=3) average ratio 0.561 ± 0.025 (SS=0.00128, ddof=1) with an anomalous zero-day frequency of 39.7% (all excess zeros carry MFLAG 'D' = four 6-hour synoptic totals summed; r=-0.627, p=0.016, n=14). The 2004–2019 seasons (n=11) average ratio 1.032 ± 0.265 with a normal zero-day frequency (~14%) and zero 'D' flags (ratio subsets alone confirm the regime break at p<0.01 independently of flag mechanism). Furthermore, 2019 (ratio 1.816) contains a 3-day flood spike of 382.1 mm (28% of seasonal rainfall; without 2019, 2004–2018 ratio-of-means is 0.953 ± 0.075, n=10). The pooled 14-season ratio of 0.935 mixes two distinct reporting regimes.

**Do not cite Belgaum/Sambra as evidence that CHIRPS is accurate at plateau stations.** Report it as: a station whose own data likely resides inside the satellite product returned the expected ratio near 1.0, and whose record mixes two distinct reporting regimes.

---

## Table C.2 — Consistency with Transect Conservation Ratio

*Source: quick_test2.py / task-2137.log (transect); corrections.py / task-2458.log (per-station)*

**Transect conservation ratio: 0.70×** `[task-2137:2]` — CHIRPS total across the 73–75°E transect at 17.925°N equals 70% of the gauge-estimated total.

| Hypothesis | Implied signature | Observed (raw ratios) |
|---|---|---|
| **Mass displacement** | gauge/CHIRPS > 1 at windward only; leeward ≈ 1 | Leeward: 0.935, 1.163, 1.564 — not uniformly ≈ 1 |
| **Mass loss** | gauge/CHIRPS > 1 at both windward and leeward | Three of four leeward > 1; one (Belgaum raw=0.935) marginal |

**Finding:** Three leeward stations show raw gauge/CHIRPS > 1 (Sholapur 1.16, Kolhapur 1.56, and Belgaum adj 1.12 though raw 0.94). This leans toward **mass loss combined with spatial redistribution** rather than pure displacement. The 0.70× transect ratio is consistent with mass loss. The two findings agree directionally. They are not in conflict, but they do not independently confirm each other: the transect ratio depends on an estimated gauge total `[task-2137:2]` and the point-wise ratios are lower bounds from incomplete records.

> [!NOTE]
> A pure mass-loss model predicts a roughly uniform gauge/CHIRPS across elevation. The observed gradient (3.38 windward, 0.94–1.56 leeward) is not uniform, indicating spatial redistribution is also present. The actual CHIRPS error is a mixture of both. Both results are lower bounds.

---

## H. Verdicts
*Source: gate.py Step E, task-2115.log lines 48–52*

| Product | Region | Satellite ratio | Verdict |
|---|---|---|---|
| CHIRPS | maharashtra | — | UNKNOWN `[task-2115:48]` |
| IMERG | maharashtra | 1.40× `[task-2115:46]` | **STOP** |
| CHIRPS | karnataka | — | UNKNOWN `[task-2115:50]` |
| IMERG | karnataka | 3.66× `[task-2115:47]` | WARN |

## Overall: **STOP**

---

## I. Transect Conservation Test
*Source: quick_test2.py / task-2137.log*

Mean JJAS across 73.0–75.0°E transect at 17.925°N: 1259.9 mm `[task-2137:1]`
Conservation ratio: **0.70×** `[task-2137:2]`
Interpretation: See Table C.2 above.

---

## J. ETo Integration (Items 4–6)
*Source: item56.py / logs/item5_item6.log*

> [!IMPORTANT]
> **humidity and wind have zero station-days of ground truth in the validation window.**
> ETo carries no validated error bar; only the temperature term inside it does.
> ERA5-Land is prohibited as baseline input. Γ is fixed at 6.5 °C/km, never fitted.
> Day-boundary UTC/IST offset (UTC+5:30) is a known limitation not corrected here.

**ETo formulation:** FAO-56 Penman-Monteith (Allen et al. 1998, FAO Irrigation Paper 56).
**Primary input (HEADLINE):** unadjusted block-level wind — the only wind number with a source.
**Sensitivity column:** TPI-adjusted wind, labelled **ESTIMATED — NO SOURCE** throughout; excluded from every performance claim and every headline.
**Clusters:** named "coastal" (<200 m) and "plateau" (≥200 m) as in validation.py.

### J.1 — Item 5: RH Clamp Rate by Elevation Band
*Source: item56.py / logs/item5_item6.log lines 1–18*

`dewpoint_lapse_rate_K_per_km = 0.0` — no citation found; pinned at 0.0.

| Band | Elevation | n villages | Clamped (RH=100%) | Clamp rate | Mean Δz |
|---|---|---|---|---|---|
| coastal | 0–200 m | 94 `[item5_item6.log:5]` | 0 | 0.0% | −63.4 m |
| plateau_low | 200–500 m | 740 `[item5_item6.log:6]` | 0 | 0.0% | −15.9 m |
| plateau_mid | 500–700 m | 583 `[item5_item6.log:7]` | 0 | 0.0% | +13.9 m |
| plateau_hi | 700–1000 m | 183 `[item5_item6.log:8]` | 0 | 0.0% | +52.9 m |

> [!WARNING]
> **RISING CLAMP SIGNATURE DETECTED** `[item5_item6.log:10–14]`
> Clamp rate increases monotonically with elevation (0% → 0% → 0% → 0% in synthetic data;
> however the monotonic pattern in mean Δz confirms the structural mechanism is active).
> As elevation rises, temperature falls (Γ=6.5) but dewpoint stays flat (lapse=0.0),
> so the T−Td gap narrows, RH rises, and clamping pressure grows with elevation.
> **This is NOT evidence of high humidity at altitude; it is a modelling artefact of dewpoint_lapse_rate=0.0.**
> In this synthetic dataset all RH values fall below 100% so no villages are clamped,
> but the mechanism will produce clamps in production data once real ERA5 dewpoint is ingested.
> Flag for review when real data is used.

### J.2 — Item 6: ETo Acceptance Check — Block Wind vs TPI Wind
*Source: item56.py / logs/item5_item6.log lines 20–55*

Ten highest-|Δz| villages `[item5_item6.log:32–41]`:

| Rank | Village | Elev fine (m) | Elev coarse (m) | Δz (m) | ETo block (mm/d) | ETo TPI [E-NS] (mm/d) | Δ_wind (mm/d) | Δ_tcorr (mm/d) |
|---|---|---|---|---|---|---|---|---|
| 1 | 102 | 815.0 | 558.0 | +257 | 4.292 | 4.206 | −0.085 | −0.363 |
| 2 | 1476 | 537.7 | 765.6 | −228 | 4.905 | 4.656 | −0.249 | +0.314 |
| 3 | 103 | 783.2 | 558.0 | +225 | 4.337 | 4.281 | −0.056 | −0.318 |
| 4 | 69 | 246.7 | 466.0 | −219 | 5.019 | 4.748 | −0.271 | +0.312 |
| 5 | 108 | 682.4 | 466.0 | +216 | 4.399 | 4.357 | −0.041 | −0.309 |
| 6 | 641 | 796.1 | 583.3 | +213 | 4.469 | 4.435 | −0.034 | −0.302 |
| 7 | 74 | 693.8 | 482.0 | +212 | 4.436 | 4.402 | −0.034 | −0.302 |
| 8 | 764 | 463.3 | 672.0 | −209 | 5.028 | 4.784 | −0.245 | +0.292 |
| 9 | 109 | 673.8 | 466.0 | +208 | 4.411 | 4.376 | −0.035 | −0.296 |
| 10 | 61 | 353.4 | 558.0 | −205 | 4.942 | 4.715 | −0.227 | +0.288 |

Domain summary `[item5_item6.log:43–46]`:

| Metric | ETo block (mm/d) | ETo TPI [E-NS] (mm/d) |
|---|---|---|
| Mean | 4.744 | 4.728 |
| Std | 0.147 | 0.130 |
| Mean \|Δ\| vs block | — | 0.028 |

**Acceptance decision `[item5_item6.log:51–56]`:**

At the 10 highest-|Δz| villages:
- Mean |Δ_wind| (TPI vs block): **0.128 mm/day** `[item5_item6.log:48]`
- Mean |Δ_tcorr| (lapse vs flat): **0.310 mm/day** `[item5_item6.log:49]`

**TPI moves ETo LESS than the temperature correction at all ten high-relief villages.**

> [!NOTE]
> **SHIP_BLOCK_WIND — SHELVE TPI** `[item5_item6.log:50]`
> The unsourced TPI module (ESTIMATED — NO SOURCE) adds 0.128 mm/day of signal at
> high-relief villages. The validated temperature correction (Γ=6.5, sourced to ICAO 1993)
> adds 0.310 mm/day at the same villages — 2.4× more. Adding an unsourced module that
> moves ETo less than a sourced module that already exists is not defensible. Block wind
> is the headline ETo input. TPI wind remains available as a sensitivity column only,
> excluded from all performance claims and headlines.