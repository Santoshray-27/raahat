import asyncio
import traceback
from app.services.orchestrator import orchestrator
from app.schemas.emergency import EmergencyRequest, GeoPoint

async def test_error():
    req = EmergencyRequest(
        user_query="accident hua hai aur khoon bahut nikal raha hai",
        location=GeoPoint(latitude=28.7041, longitude=77.1025)
    )
    try:
        res = await orchestrator.process_emergency(req, db=None, user=None)
        print("Success:", res)
    except Exception as e:
        print("Crash!")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_error())
