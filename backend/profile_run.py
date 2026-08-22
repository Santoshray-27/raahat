import asyncio
import time
from app.core.database import get_session_factory, get_engine, create_all_tables
from app.services.orchestrator import EmergencyOrchestrator
from app.schemas.emergency import EmergencyRequest
from app.schemas.common import GeoPoint

async def run_profile():
    await create_all_tables()
    async_session_factory = get_session_factory()
    orchestrator = EmergencyOrchestrator()
    
    queries = [
        "accident hua hai aur khoon bahut nikal raha hai",
        "tyre puncture ho gaya hai",
        "meri gaadi kharab ho gayi hai raaste me"
    ]
    
    # Pre-warm DB
    async with async_session_factory() as db:
        pass
        
    for idx, q in enumerate(queries):
        for run in range(2):
            print(f"\n--- Query {idx+1}, Run {run+1} ---")
            print(f"Query: {q}")
            req = EmergencyRequest(
                user_query=q,
                location=GeoPoint(latitude=28.7041, longitude=77.1025)
            )
            async with async_session_factory() as db:
                try:
                    await orchestrator.process_emergency(req=req, db=db)
                except Exception as e:
                    print(f"Failed: {e}")

if __name__ == "__main__":
    asyncio.run(run_profile())
