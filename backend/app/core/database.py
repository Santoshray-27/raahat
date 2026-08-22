from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.exc import ArgumentError
from app.core.config import settings
from app.core.logging import logger

Base = declarative_base()

_engine = None
_session_maker = None

def get_engine():
    global _engine, _session_maker
    if _engine is not None:
        return _engine
        
    db_url = settings.DATABASE_URL
    if not db_url or not db_url.strip():
        logger.warning("DATABASE_URL is empty. Running in degraded no-DB mode.")
        return None
        
    try:
        connect_args = {}
        if "?ssl=require" in db_url:
            db_url = db_url.replace("?ssl=require", "")
            connect_args["ssl"] = "require"
            
        _engine = create_async_engine(
            db_url,
            echo=False,
            future=True,
            pool_size=5,
            pool_pre_ping=True,
            pool_recycle=300,
            connect_args=connect_args
        )
        _session_maker = async_sessionmaker(
            bind=_engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False
        )
        return _engine
    except ArgumentError as e:
        logger.warning(f"Invalid DATABASE_URL. Running in degraded no-DB mode. Error: {e}")
        return None
    except Exception as e:
        logger.warning(f"Failed to create database engine: {e}")
        return None

async def get_db():
    if not settings.DATABASE_URL:
        yield None
        return
        
    engine = get_engine()
    if engine is None:
        yield None
        return
        
    if _session_maker:
        try:
            async with _session_maker() as session:
                yield session
        except Exception:
            raise

def get_session_factory():
    get_engine()
    return _session_maker

async def create_all_tables():
    engine = get_engine()
    if engine is None:
        return
    # import models to register them with Base.metadata before creating tables
    import app.models.user
    import app.models.conversation
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session = AsyncSessionLocal()
    try:
        yield session
    finally:
        await session.close()
