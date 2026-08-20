import urllib.request
import json
import time
import os

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

# 1. Status
print("--- 1. PROVIDERS STATUS ---")
status = request_json('http://127.0.0.1:8000/api/v1/providers/status')
print(status.get('data', {}).get('geoapify'))

# 2. Force fail Google (We will just simulate by sending bogus key to backend via env before restart if needed, but wait! The backend is already running with real Google key. Let's restart backend with bogus google key first).
