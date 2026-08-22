import asyncio
import os
import sys

sys.path.append(os.getcwd())

from app.services.orchestrator import orchestrator
from app.schemas.emergency import EmergencyRequest
from app.schemas.common import GeoPoint

async def main():
    req = EmergencyRequest(
        user_message="I have a flat tire",
        location=GeoPoint(latitude=28.6, longitude=77.2)
    )
    res = await orchestrator.process_emergency(req)
    print("Success:", res.incident.category)

if __name__ == "__main__":
    asyncio.run(main())
