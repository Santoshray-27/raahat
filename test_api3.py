import json
import urllib.request
import traceback

def post(url, data):
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as res:
            return json.loads(res.read().decode('utf-8'))
    except Exception as e:
        if hasattr(e, 'read'):
            return json.loads(e.read().decode('utf-8'))
        return str(e)

def get(url):
    try:
        with urllib.request.urlopen(url) as res:
            return json.loads(res.read().decode('utf-8'))
    except Exception as e:
        if hasattr(e, 'read'):
            return json.loads(e.read().decode('utf-8'))
        return str(e)

print('--- Puncture ---')
p_res = post('http://127.0.0.1:8000/api/v1/emergency-assistance', {'user_query':'My tyre got punctured on the highway','language':'en','location':{'latitude':22.7196,'longitude':75.8577},'network_mode':'ONLINE'})
if isinstance(p_res, dict) and p_res.get('success'):
    data = p_res['data']
    print(f"incident_type: {data['analysis']['incident_type']}")
    print(f"severity: {data['analysis']['severity']}")
    if data['guidance']:
        print(f"guidance title: {data['guidance'][0]['title']}")
    if data['services']:
        s = data['services'][0]
        print(f"services[0] name: {s['name']}, source: {s.get('source')}, retrieved_at: {s.get('retrieved_at')}, availability_status: {s.get('availability_status')}, is_cached: {s.get('is_cached')}")
else:
    print('Failed:', p_res)

print('--- Accident ---')
a_res = post('http://127.0.0.1:8000/api/v1/emergency-assistance', {'user_query':'accident hua hai aur khoon bahut nikal raha hai','language':'en','location':{'latitude':22.7196,'longitude':75.8577},'network_mode':'ONLINE'})
if isinstance(a_res, dict) and a_res.get('success'):
    print(f"severity: {a_res['data']['analysis']['severity']}")
else:
    print('Failed:', a_res)

print('--- Nearby ---')
n_res = get('http://127.0.0.1:8000/api/v1/services/nearby?latitude=22.7196&longitude=75.8577&category=HOSPITAL&limit=3')
if isinstance(n_res, dict) and n_res.get('success'):
    print(f"count: {len(n_res['data']['services'])}")
    if n_res['data']['services']:
        print(f"first source: {n_res['data']['services'][0].get('source')}")
else:
    print('Failed:', n_res)

print('--- Route ---')
r_res = post('http://127.0.0.1:8000/api/v1/routes/plan', {'origin':{'latitude':22.7196,'longitude':75.8577},'destination':{'latitude':23.2599,'longitude':77.4126}})
if isinstance(r_res, dict) and r_res.get('success'):
    rt = r_res['data']['routes'][0]
    print(f"distance_meters: {rt['distance_meters']}, duration_seconds: {rt['duration_seconds']}, polyline present: {bool(rt.get('polyline'))}")
else:
    print('Failed:', r_res)

print('--- Offline ---')
o_res = post('http://127.0.0.1:8000/api/v1/offline-packs', {'region_name': 'Test Route', 'bounding_box': {'min_lat': 22.7196, 'min_lng': 75.8577, 'max_lat': 23.2599, 'max_lng': 77.4126}, 'route_id': 'xyz'})
if isinstance(o_res, dict) and o_res.get('success'):
    print(f"pack_id: {o_res['data']['pack_id']}, status: {o_res['data']['status']}, checksum present: {bool(o_res['data'].get('checksum'))}")
else:
    print('Failed:', o_res)

