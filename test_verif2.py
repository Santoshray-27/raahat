import urllib.request
import json
def post(url, payload):
    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as res:
            return json.loads(res.read().decode('utf-8'))
    except Exception as e:
        return str(e)
res = post('http://127.0.0.1:8000/api/v1/emergency-assistance', {
    "user_query": "My tyre got punctured on the highway",
    "location": {"latitude": 22.7196, "longitude": 75.8577}
})
first = res.get('data', {}).get('services', [{}])[0]
print('PUNCTURE FIRST SERVICE:', first.get('name'), '| TYPES:', first.get('service_types'))
