import os, time, uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder

from app.core.config import settings
from app.core.logging import logger
from app.core.response import error_response
from app.core.database import get_engine, create_all_tables
from sqlalchemy import text

from app.api.v1 import (
    health, users, emergency, services, routes, rag, voice, offline, actions
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_all_tables()
    engine = get_engine()
    if engine is not None:
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
                logger.info("Startup check: Database connected successfully.")
        except Exception as e:
            logger.error(f"Startup check: Database connection failed. Service may be degraded. Error: {e}")
    else:
        logger.warning("Startup check: Running in degraded no-DB mode (engine is None).")
    yield
    if engine is not None:
        await engine.dispose()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware for Request ID & Execution Time tracking
@app.middleware("http")
async def add_request_metadata(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start_time = time.time()
    request.state.request_id = request_id
    
    response = await call_next(request)
    
    execution_time_ms = round((time.time() - start_time) * 1000, 2)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Execution-Time-MS"] = str(execution_time_ms)
    
    logger.info(f"[{request.method}] {request.url.path} -> Status {response.status_code} ({execution_time_ms}ms)")
    return response

# Standardized Validation Error Handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response(
            code="VALIDATION_ERROR",
            message="Invalid request parameters or body format",
            details={"errors": jsonable_encoder(exc.errors())},
            status_code=422,
            request_id=req_id
        )
    )

# Standardized Unhandled Exception Handler
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    import traceback
    traceback.print_exc()
    logger.error(f"Unhandled Exception on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response(
            code="INTERNAL_SERVER_ERROR",
            message="An unexpected server error occurred",
            details={"error": "A server error was recorded and will be investigated."},
            status_code=500,
            request_id=req_id
        )
    )

# API Router Registration
api_v1 = FastAPI()
app.include_router(health.router, prefix=settings.API_V1_STR, tags=["Health"])
app.include_router(users.router, prefix=settings.API_V1_STR, tags=["Users"])
app.include_router(emergency.router, prefix=settings.API_V1_STR, tags=["Emergency Assistance"])
app.include_router(services.router, prefix=settings.API_V1_STR, tags=["Nearby Services"])
app.include_router(routes.router, prefix=settings.API_V1_STR, tags=["Safe Routing"])
app.include_router(rag.router, prefix=settings.API_V1_STR, tags=["RAG AI Integration"])
app.include_router(voice.router, prefix=settings.API_V1_STR, tags=["Voice Assistance"])
app.include_router(offline.router, prefix=settings.API_V1_STR, tags=["Offline Packs"])
app.include_router(actions.router, prefix=settings.API_V1_STR, tags=["Actions Dispatch"])

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    reload_mode = (settings.ENVIRONMENT == "development")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=reload_mode)
