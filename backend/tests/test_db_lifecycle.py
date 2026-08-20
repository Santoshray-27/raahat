import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from app.core.database import get_db

@pytest.mark.asyncio
async def test_get_db_lifecycle():
    # Verify the get_db generator yields a session and closes properly
    db_gen = get_db()
    session = await anext(db_gen)
    
    assert session is not None
    assert hasattr(session, "execute")
    
    # Consume the generator to trigger the finally block
    try:
        await anext(db_gen)
        pytest.fail("Generator should have raised StopAsyncIteration")
    except StopAsyncIteration:
        pass
