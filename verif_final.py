import urllib.request
import json
import time

time.sleep(3)

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

status = request_json('http://127.0.0.1:8000/api/v1/providers/status')
if isinstance(status, dict):
    gp = status.get('data', {}).get('google_places', {}).get('status')
    gr = status.get('data', {}).get('google_routes', {}).get('status')
    if gp == 'OPERATIONAL' and gr == 'OPERATIONAL':
        print("PASS - Status check: google_places and google_routes are OPERATIONAL")
    else:
        print(f"FAIL - Status check: google_places={gp}, google_routes={gr}")
else:
    print("FAIL - Status check returned error:", status)

assist = request_json('http://127.0.0.1:8000/api/v1/emergency-assistance', 'POST', {
    "message": "My tyre got punctured on the highway",
    "location": {"latitude": 22.7196, "longitude": 75.8577}
})
if isinstance(assist, dict) and 'data' in assist:
    src = assist['data']['services'][0]['source']
    if src == 'GOOGLE_PLACES':
        print("PASS - Emergency assistance fallback restored: source is GOOGLE_PLACES")
    else:
        print(f"FAIL - Emergency assistance fallback restored: source is {src}")
else:
    print("FAIL - Emergency assistance returned error:", assist)
