import urllib.request
import json
import time

time.sleep(3)

def req(url, method='GET', payload=None):
    try:
        r = urllib.request.Request(url, method=method)
        if payload:
            r.add_header('Content-Type', 'application/json')
            r.data = json.dumps(payload).encode('utf-8')
        with urllib.request.urlopen(r, timeout=25) as res:
            return json.loads(res.read().decode('utf-8'))
    except Exception as e:
        return {'_error': str(e)}

print("=== 1. GEOAPIFY PARENT CATEGORY DIRECT API TEST ===")
direct_geo = req("https://api.geoapify.com/v2/places?categories=amenity&filter=circle:75.8577,22.7196,15000&limit=3&apiKey=4b1bebce094741a9a92afa15bc6edd5e")
if isinstance(direct_geo, dict) and "features" in direct_geo:
    print(f"Geoapify Direct Test: PASS (Returned {len(direct_geo['features'])} features from 'amenity')")
else:
    print(f"Geoapify Direct Test: FAIL ({direct_geo})")

print("\n=== 2. PROVIDERS STATUS ===")
status = req('http://127.0.0.1:8000/api/v1/providers/status')
print(json.dumps(status.get('data'), indent=2))

print("\n=== 3. EMERGENCY ASSISTANCE PUNCTURE ===")
em = req('http://127.0.0.1:8000/api/v1/emergency-assistance', 'POST', {
    "message": "My tyre got punctured on the highway",
    "location": {"latitude": 22.7196, "longitude": 75.8577}
})
if isinstance(em, dict) and em.get('data'):
    s0 = em['data']['services'][0]
    print(f"PASS -> name: {s0.get('name')}, source: {s0.get('source')}, category: {em['data']['incident']['category']}")
else:
    print(f"FAIL -> {em}")

print("\n=== 4. NEARBY POLICE (CATEGORY=POLICE) ===")
pol = req('http://127.0.0.1:8000/api/v1/services/nearby?lat=22.7196&lng=75.8577&category=POLICE&limit=3')
if isinstance(pol, dict) and pol.get('data'):
    svcs = pol['data'].get('services', [])
    print(f"PASS -> count: {len(svcs)}, source: {pol['data'].get('provider_source')}")
    for s in svcs:
        print(f"  - {s.get('name')} ({s.get('source')})")
else:
    print(f"FAIL -> {pol}")

print("\n=== 5. NEARBY AMBULANCE (CATEGORY=AMBULANCE) ===")
amb = req('http://127.0.0.1:8000/api/v1/services/nearby?lat=22.7196&lng=75.8577&category=AMBULANCE&limit=3')
if isinstance(amb, dict) and amb.get('data'):
    svcs = amb['data'].get('services', [])
    print(f"PASS -> count: {len(svcs)}, source: {amb['data'].get('provider_source')}")
    for s in svcs:
        print(f"  - {s.get('name')} ({s.get('source')})")
else:
    print(f"FAIL -> {amb}")

print("\n=== 6. NEARBY HOSPITAL (CATEGORY=HOSPITAL) ===")
hosp = req('http://127.0.0.1:8000/api/v1/services/nearby?lat=22.7196&lng=75.8577&category=HOSPITAL&limit=3')
if isinstance(hosp, dict) and hosp.get('data'):
    svcs = hosp['data'].get('services', [])
    print(f"PASS -> count: {len(svcs)}, source: {hosp['data'].get('provider_source')}")
    for s in svcs:
        print(f"  - {s.get('name')} ({s.get('source')})")
else:
    print(f"FAIL -> {hosp}")
