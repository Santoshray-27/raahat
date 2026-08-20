import urllib.request
import json
import time

time.sleep(3) # Wait for server startup

def request_json(url, method='GET', payload=None):
    try:
        req = urllib.request.Request(url, method=method)
        if payload:
            req.add_header('Content-Type', 'application/json')
            req.data = json.dumps(payload).encode('utf-8')
        with urllib.request.urlopen(req) as res:
            return json.loads(res.read().decode('utf-8'))
    except Exception as e:
        return str(e)

print("--- 3. FAILOVER TO GEOAPIFY PLACES ---")
res = request_json('http://127.0.0.1:8000/api/v1/emergency-assistance', 'POST', {
    "message": "My tyre got punctured on the highway",
    "location": {"latitude": 22.7196, "longitude": 75.8577}
})
if isinstance(res, dict) and 'data' in res:
    print('SOURCE:', res['data']['services'][0]['source'])
else:
    print("FAILED", res)

print("\n--- 4. FAILOVER TO GEOAPIFY ROUTING ---")
res2 = request_json('http://127.0.0.1:8000/api/v1/routes/plan', 'POST', {
    "origin": {"latitude": 22.7196, "longitude": 75.8577},
    "destination": {"latitude": 23.2599, "longitude": 77.4126}
})
if isinstance(res2, dict) and 'data' in res2:
    print('ROUTE SOURCE:', res2['data']['provider_source'])
    print('DISTANCE:', res2['data']['total_distance_km'])
else:
    print("FAILED", res2)

print("\n--- 5. FAILOVER TO GEOAPIFY NEARBY ---")
res3 = request_json('http://127.0.0.1:8000/api/v1/services/nearby?lat=22.7196&lng=75.8577&category=HOSPITAL&limit=3')
if isinstance(res3, dict) and 'data' in res3:
    print('NEARBY SOURCE:', res3['data']['services'][0]['source'])
else:
    print("FAILED", res3)
