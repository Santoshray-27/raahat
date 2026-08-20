import urllib.request
import json
def get(url):
    try:
        with urllib.request.urlopen(url) as res:
            return json.loads(res.read().decode('utf-8'))
    except Exception as e:
        return str(e)
print('GET NEARBY limit=3:', len(get('http://127.0.0.1:8000/api/v1/services/nearby?lat=22.7196&lng=75.8577&category=HOSPITAL&limit=3').get('data', {}).get('services', [])))
