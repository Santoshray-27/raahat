import json
import urllib.request
def post(url, data):
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as res:
            return res.read().decode('utf-8')
    except Exception as e:
        if hasattr(e, 'read'):
            return e.read().decode('utf-8')
        return str(e)
print(post('http://127.0.0.1:8000/api/v1/offline-packs', {
    'region_name': 'Test Route',
    'bounding_box': [
        {'latitude': 22.7196, 'longitude': 75.8577},
        {'latitude': 23.2599, 'longitude": 77.4126}
    ],
    'route_id': 'groute_5c3c10d5'
}))
