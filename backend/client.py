import asyncio
import httpx
import time

async def test_backend():
    url = "http://localhost:8000/api/v1/emergency-assistance"
    queries = [
        "accident hua hai aur khoon bahut nikal raha hai",
        "tyre puncture ho gaya hai",
        "meri gaadi kharab ho gayi hai raaste me"
    ]
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        for idx, q in enumerate(queries):
            for run in range(2):
                print(f"\\n--- Query {idx+1}, Run {run+1} ---")
                start = time.time()
                payload = {
                    "user_query": q,
                    "location": {"latitude": 28.7041, "longitude": 77.1025}
                }
                headers = {"Authorization": "Bearer dev_user_999"}
                resp = await client.post(url, json=payload, headers=headers)
                end = time.time()
                print(f"Status: {resp.status_code}")
                if resp.status_code != 200:
                    print(resp.text)
                print(f"Time Taken: {(end - start)*1000:.2f}ms")

if __name__ == "__main__":
    asyncio.run(test_backend())
