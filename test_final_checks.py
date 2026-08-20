import urllib.request
import json
import time

time.sleep(3) # Wait for server startup

def get(url):
    with urllib.request.urlopen(url) as res:
        return json.loads(res.read().decode('utf-8'))

def post(url, payload):
    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as res:
        return json.loads(res.read().decode('utf-8'))

# Check 1: Nearby Limit
r1 = get('http://127.0.0.1:8000/api/v1/services/nearby?lat=22.7196&lng=75.8577&category=HOSPITAL&limit=3')
count1 = len(r1.get('data', {}).get('services', []))
print(f'CHECK 1: {count1} items returned (expected 3) -> {"PASS" if count1 == 3 else "FAIL"}')

# Check 4: Emergency with "message" field
r4 = post('http://127.0.0.1:8000/api/v1/emergency-assistance', {
    "message": "My tyre got punctured on the highway",
    "location": {"latitude": 22.7196, "longitude": 75.8577}
})
status4 = r4.get('success', False)
print(f'CHECK 4: Emergency request with "message" field -> {"PASS" if status4 else "FAIL"}')

# Check 2: Diagnostics non-empty
r2 = get('http://127.0.0.1:8000/api/v1/diagnostics')
history = r2.get('data', {}).get('recent_call_history', [])
has_entry = len(history) > 0 and 'provider_source' in history[0] and 'latency_ms' in history[0]
print(f'CHECK 2: Diagnostics history populated -> {"PASS" if has_entry else "FAIL"}')
