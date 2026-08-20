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

def get(url):
    try:
        with urllib.request.urlopen(url) as res:
            return res.read().decode('utf-8')
    except Exception as e:
        if hasattr(e, 'read'):
            return e.read().decode('utf-8')
        return str(e)

print('--- Puncture ---')
print(post('http://127.0.0.1:8000/api/v1/emergency-assistance', {'user_query':'My tyre got punctured on the highway','language':'en','location':{'latitude':22.7196,'longitude':75.8577},'network_mode':'ONLINE'}))

print('--- Accident ---')
print(post('http://127.0.0.1:8000/api/v1/emergency-assistance', {'user_query':'accident hua hai aur khoon bahut nikal raha hai','language':'en','location':{'latitude':22.7196,'longitude':75.8577},'network_mode':'ONLINE'}))

print('--- Nearby ---')
print(get('http://127.0.0.1:8000/api/v1/services/nearby?latitude=22.7196&longitude=75.8577&category=HOSPITAL&limit=3'))

print('--- Route ---')
print(post('http://127.0.0.1:8000/api/v1/routes/plan', {'origin':{'latitude':22.7196,'longitude':75.8577},'destination':{'latitude':23.2599,'longitude':77.4126}}))

print('--- Offline ---')
print(post('http://127.0.0.1:8000/api/v1/offline-packs', {'region_name': 'Test Route', 'bounding_box': {'min_lat': 22.7196, 'min_lng': 75.8577, 'max_lat': 23.2599, 'max_lng': 77.4126}, 'route_id': 'xyz'}))

