import json
import urllib.request

def post(url, data):
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as res:
            print(res.read().decode('utf-8'))
    except Exception as e:
        print(f"Error: {e}")
        if hasattr(e, 'read'):
            print(e.read().decode('utf-8'))

def get(url):
    try:
        with urllib.request.urlopen(url) as res:
            print(res.read().decode('utf-8'))
    except Exception as e:
        print(f"Error: {e}")
        if hasattr(e, 'read'):
            print(e.read().decode('utf-8'))

print('--- Puncture ---')
post('http://127.0.0.1:8000/api/v1/emergency-assistance', {'message':'My tyre got punctured on the highway','language':'en','location':{'latitude':22.7196,'longitude':75.8577},'network_mode':'ONLINE'})

print('--- Accident ---')
post('http://127.0.0.1:8000/api/v1/emergency-assistance', {'message':'accident hua hai aur khoon bahut nikal raha hai','language':'en','location':{'latitude':22.7196,'longitude':75.8577},'network_mode':'ONLINE'})

print('--- Nearby ---')
get('http://127.0.0.1:8000/api/v1/services/nearby?latitude=22.7196&longitude=75.8577&category=HOSPITAL&limit=3')

print('--- Route ---')
post('http://127.0.0.1:8000/api/v1/routes/plan', {'origin':{'latitude':22.7196,'longitude':75.8577},'destination':{'latitude':23.2599,'longitude':77.4126}})

print('--- Offline ---')
post('http://127.0.0.1:8000/api/v1/offline-packs', {'origin':{'latitude':22.7196,'longitude':75.8577},'destination':{'latitude':23.2599,'longitude':77.4126}})
