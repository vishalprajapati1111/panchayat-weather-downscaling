"""
Probe actual CHIRPS access options exhaustively, then run ClimateSERV API for CHIRPS.
ClimateSERV is a public NASA SERVIR service providing CHIRPS + IMERG with no auth.
"""
import sys, requests, time, json
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def rget(url, params=None, timeout=30, stream=False):
    r = requests.get(url, params=params, timeout=timeout, stream=stream)
    return r

# ---- 1. What is actually in byYear/ ? ----
print("=== UCSB byYear/ directory listing ===")
r = rget("https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_monthly/netcdf/byYear/")
print(f"HTTP {r.status_code}")
import re
links = re.findall(r'href="([^"]*chirps[^"]*)"', r.text, re.IGNORECASE)
for l in links[:20]: print(f"  {l}")
print(f"  (total chirps links: {len(links)})")

# ---- 2. Check if the single 7.2GB file supports byte-range (HTTP ranges) ----
print("\n=== HTTP Range support on chirps-v2.0.monthly.nc ===")
monthly_url = ("https://data.chc.ucsb.edu/products/CHIRPS-2.0/"
               "global_monthly/netcdf/chirps-v2.0.monthly.nc")
rh = requests.head(monthly_url, timeout=20)
print(f"  HEAD status: {rh.status_code}")
print(f"  Accept-Ranges: {rh.headers.get('Accept-Ranges', 'not set')}")
print(f"  Content-Length: {rh.headers.get('Content-Length', '?')} bytes")

# ---- 3. Test ClimateSERV API ----
print("\n=== ClimateSERV API test ===")
CS_BASE = "https://climateserv.servirglobal.net/api"

# ClimateSERV datatypes for CHIRPS: datatype=0 (chirps precip)
# Submit a small test request for Mahabaleshwar, JJAS 1991, monthly mean
test_payload = {
    "datatype": 26,        # CHIRPS monthly precip (type 26 in newer API)
    "begintime": "01/06/1991",
    "endtime": "30/09/1991",
    "intervaltype": 0,     # 0=monthly
    "operationtype": 5,    # 5=mean
    "geometry": json.dumps({"type": "Point", "coordinates": [73.66, 17.92]}),
    "isZip": "false"
}
try:
    r2 = requests.post(f"{CS_BASE}/submitDataRequest/", data=test_payload, timeout=30)
    print(f"  Submit POST status: {r2.status_code}")
    print(f"  Response: {r2.text[:500]}")
    if r2.status_code == 200:
        job_id = r2.text.strip().strip('"').strip("[]").split(",")[0].strip()
        print(f"  Job ID: {job_id}")

        # Poll for completion
        for attempt in range(10):
            time.sleep(5)
            rp = requests.get(f"{CS_BASE}/getDataRequestProgress/",
                              params={"id": job_id}, timeout=20)
            progress = rp.json() if rp.status_code == 200 else rp.text
            print(f"  Poll {attempt+1}: {progress}")
            if isinstance(progress, list) and len(progress) > 0:
                pct = progress[0].get("progress", 0)
                if pct >= 100:
                    break
        # Fetch data
        rd = requests.get(f"{CS_BASE}/getDataFromRequest/",
                          params={"id": job_id}, timeout=30)
        print(f"  Data response ({rd.status_code}): {rd.text[:600]}")
except Exception as ex:
    print(f"  ClimateSERV error: {ex}")

# ---- 4. Try ClimateSERV v2 API (newer endpoint) ----
print("\n=== ClimateSERV v2 timeseries endpoint ===")
# Some versions of ClimateSERV have a /timeseries/ endpoint
for chirps_type in [0, 26, 28]:
    try:
        payload2 = {
            "datatype": chirps_type,
            "begintime": "01/06/1991",
            "endtime": "30/09/2000",
            "intervaltype": 0,
            "operationtype": 5,
            "geometry": json.dumps({"type": "Point", "coordinates": [73.66, 17.92]}),
        }
        r3 = requests.post(f"{CS_BASE}/submitDataRequest/", data=payload2, timeout=20)
        print(f"  datatype={chirps_type}: HTTP {r3.status_code}  {r3.text[:200]}")
        time.sleep(1)
    except Exception as ex:
        print(f"  datatype={chirps_type}: ERROR {ex}")

# ---- 5. Check if CHC has a THREDDS/OpenDAP server ----
print("\n=== CHC THREDDS/OPeNDAP check ===")
for url in [
    "https://data.chc.ucsb.edu/thredds/",
    "https://chc-thredds.ucsb.edu/",
    "https://iridl.ldeo.columbia.edu/SOURCES/.UCSB/.CHIRPS/.v2p0/.monthly/.global/.0p05/.prcp/catalog.xml",
]:
    try:
        r4 = rget(url, timeout=10)
        print(f"  {url}: HTTP {r4.status_code}  ({len(r4.content)} bytes)")
    except Exception as ex:
        print(f"  {url}: {type(ex).__name__}: {str(ex)[:60]}")
    time.sleep(0.5)
