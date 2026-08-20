import urllib.request
import json
def get(url):
    try:
        with urllib.request.urlopen(url) as res:
            return json.loads(res.read().decode('utf-8'))
    except Exception as e:
        return str(e)
res = get('http://127.0.0.1:8000/api/v1/diagnostics')
print('TOTAL QUERIES LOGGED:', res.get('data', {}).get('total_queries_logged'))
print('LAST CALL:', res.get('data', {}).get('recent_call_history', [{}])[0])
