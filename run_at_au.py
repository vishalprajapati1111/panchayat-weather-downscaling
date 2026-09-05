import json, pathlib, ee, time
import numpy as np

ee.Initialize()

geojson_dir = pathlib.Path("data/cache/geojson")
files = [
    ("GA", geojson_dir / "ga.geojson"),
    ("KA", geojson_dir / "ka.geojson"),
    ("MH", geojson_dir / "mh1.geojson"),
    ("MH", geojson_dir / "mh2.geojson")
]

min_lon, max_lon, min_lat, max_lat = 73.5, 76.5, 13.0, 17.5

domain_features = []
amboli_idx = None

print("Loading cached GeoJSONs...")
total_input_count = 0
state_counts = {}

for state, path in files:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        data = json.load(f)
    print(f"Loaded {path.name}: {len(data['features'])} features")
    for idx, feat in enumerate(data['features']):
        geom = feat.get('geometry')
        if not geom: continue
        props = feat.get('properties', {})
        
        def get_flat(coords):
            if isinstance(coords[0], list):
                return [v for sub in coords for v in get_flat(sub)]
            return [coords]
        try:
            pts = get_flat(geom['coordinates'])
            lons = [p[0] for p in pts]
            lats = [p[1] for p in pts]
            p_min_lon, p_max_lon = min(lons), max(lons)
            p_min_lat, p_max_lat = min(lats), max(lats)
            
            if (p_max_lon > min_lon and p_min_lon < max_lon and p_max_lat > min_lat and p_min_lat < max_lat):
                total_input_count += 1
                state_counts[state] = state_counts.get(state, 0) + 1
                
                vname = str(props.get('NAME', props.get('name', props.get('VILL_NAME', f'Village_{idx}')))).strip()
                vcode = str(props.get('censuscode', props.get('ID', props.get('OBJECTID', idx)))).strip()
                
                # Whitelist properties
                feat['properties'] = {
                    'name': vname,
                    'state': state,
                    'src_file': path.name,
                    'idx': idx,
                    'code': vcode
                }
                domain_features.append(feat)
                if 'amboli' in vname.lower() and state == 'MH':
                    amboli_idx = len(domain_features) - 1
        except Exception as e:
            pass

print(f"Total domain features ingested: {len(domain_features)} (state counts: {state_counts})")
if amboli_idx is not None:
    print(f"Amboli feature found at index {amboli_idx}: {domain_features[amboli_idx]['properties']}")

# Earth Engine setup
dem = ee.Image('USGS/SRTMGL1_003').select('elevation')
era5_proj = ee.ImageCollection('ECMWF/ERA5/DAILY').first().select(0).projection()
dem_900 = dem.reduceResolution(reducer=ee.Reducer.mean(), maxPixels=65535).reproject(crs=era5_proj.crs(), scale=900)
dem_e5 = dem_900.reduceResolution(reducer=ee.Reducer.mean(), maxPixels=65535).reproject(crs=era5_proj)

# SIGNED DIFFERENCE: dem - dem_e5 (NO .abs())
signed_diff = dem.subtract(dem_e5)

# Combined image to get polygon-mean fine elevation, coarse height, and signed dz
combined = ee.Image.cat([
    dem.rename('elev_fine'),
    dem_e5.rename('elev_coarse'),
    signed_diff.rename('dz')
])

print("\nStarting Earth Engine reduction...")
results = []
null_count = 0
batch_size = 1000

t0 = time.time()
for i in range(0, len(domain_features), batch_size):
    batch = domain_features[i:i+batch_size]
    fc = ee.FeatureCollection([ee.Feature(f) for f in batch])
    reduced = combined.reduceRegions(collection=fc, reducer=ee.Reducer.mean(), scale=30, tileScale=4).getInfo()
    for feat in reduced['features']:
        p = feat['properties']
        dz = p.get('dz')
        if dz is not None:
            results.append({
                'name': p.get('name'),
                'state': p.get('state'),
                'src_file': p.get('src_file'),
                'idx': p.get('idx'),
                'code': p.get('code'),
                'elev_fine': p.get('elev_fine'),
                'elev_coarse': p.get('elev_coarse'),
                'dz': dz
            })
        else:
            null_count += 1
    print(f"  Processed batch {i} to {min(i+batch_size, len(domain_features))} in {time.time()-t0:.1f}s (valid={len(results)}, null={null_count})", flush=True)

print(f"\nReduction complete: valid={len(results)}, null={null_count}, total={len(domain_features)}")

# Save raw results to JSON for instant analysis
out_json = pathlib.Path("data/cache/signed_village_results.json")
with open(out_json, "w", encoding="utf-8") as f:
    json.dump(results, f)
print(f"Saved results to {out_json}")
