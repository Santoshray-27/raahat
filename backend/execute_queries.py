import requests
import json
import time

URL = "http://127.0.0.1:8001/api/v1/emergency-assistance"

def query(text):
    print(f"\n--- Query: {text} ---")
    payload = {
        "user_query": text,
        "location": {"latitude": 28.6139, "longitude": 77.2090},
        "language": "english"
    }
    t0 = time.time()
    resp = requests.post(URL, json=payload)
    latency = time.time() - t0
    print(f"Status: {resp.status_code}, Latency: {latency:.2f}s")
    if resp.status_code == 200:
        data = resp.json().get('data', {})
        model = data.get("ai", {}).get("model_version", "unknown")
        print(f"Model used: {model}")
        services = data.get("services", [])
        if services:
            print("Top 3 Services:")
            for s in services[:3]:
                print(f" - {s.get('name')} | {s.get('distance_km')}km | Source: {s.get('source')}")
        else:
            print("No services returned.")
    else:
        print(resp.text)

print("Accident Query 1:")
query("There's a huge car crash on the highway and someone is bleeding heavily")

print("\nAccident Query 2:")
query("Two cars collided at the intersection, send ambulance")

print("\nAccident Query 3:")
query("I got hit by a truck and need emergency medical help")

print("\nPuncture Query:")
query("tyre puncture ho gaya hai")

print("\nNearby Services Direct Query:")
resp = requests.get("http://127.0.0.1:8001/api/v1/services/nearby?lat=28.6139&lng=77.2090&category=HOSPITAL&limit=5")
print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    data = resp.json().get('data', {})
    services = data.get('services', [])
    for s in services[:3]:
        print(f" - {s.get('name')} | {s.get('distance_km')}km | Source: {s.get('source')}")

