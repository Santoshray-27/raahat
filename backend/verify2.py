import asyncio, time, json
from app.core.database import get_engine, create_all_tables, get_db
from app.core.config import settings
from sqlalchemy import text
from app.schemas.emergency import EmergencyRequest, GeoPoint
from app.services.orchestrator import orchestrator

async def run():
    print('Starting Phase 2 verification...')
    engine = get_engine()
    if not engine:
        print('DB not configured')
        return
        
    await create_all_tables()

    # Count rows before
    async with engine.connect() as conn:
        before_count = await conn.scalar(text('SELECT COUNT(*) FROM conversations'))
        msg_before = await conn.scalar(text('SELECT COUNT(*) FROM conversation_messages'))
    print(f'Conversations before: {before_count}, Messages before: {msg_before}')

    async def test_query(query, conv_id=None):
        req = EmergencyRequest(
            user_query=query,
            location=GeoPoint(latitude=22.7196, longitude=75.8577), # Indore
            conversation_id=conv_id
        )
        async for db in get_db():
            res = await orchestrator.process_emergency(req, db, user=None)
            cat = res.incident.category.value
            sev = res.incident.severity.value
            ai_model = res.ai.model_version
            svc_cnt = len(res.services)
            top3 = [f'{s.name} ({s.source}, {s.distance_km}km)' for s in res.services[:3]]
            print(f'Query: "{query}"')
            print(f'  -> Category: {cat}, Severity: {sev}')
            print(f'  -> AI Model: {ai_model}, Service Count: {svc_cnt}')
            print(f'  -> Top 3: {", ".join(top3)}')
            print(f'  -> conversation_id: {res.conversation_id}')
            return res.conversation_id

    # 1. accident
    c_id = await test_query('accident hua hai aur khoon bahut nikal raha hai')
    # 2. puncture
    await test_query('tyre puncture ho gaya hai')
    # 3. English
    await test_query('my car broke down on the highway')
    # 4. Pure Hindi
    await test_query('meri gaadi kharab ho gayi hai raaste me')
    
    # 5. Follow-up
    print('\nFollow-up using conversation_id:', c_id)
    await test_query('aur paas wala hospital batao', conv_id=c_id)

    # Count rows after
    async with engine.connect() as conn:
        after_count = await conn.scalar(text('SELECT COUNT(*) FROM conversations'))
        msg_after = await conn.scalar(text('SELECT COUNT(*) FROM conversation_messages'))
    print(f'\nConversations after: {after_count}, Messages after: {msg_after}')

asyncio.run(run())
