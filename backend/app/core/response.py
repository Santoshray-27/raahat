import uuid
from typing import Any, Dict, Optional, Generic, TypeVar
from pydantic import BaseModel, Field

DataT = TypeVar("DataT")

class MetaResponse(BaseModel):
    timestamp: str
    version: str = "1.0.0"
    execution_time_ms: float = 0.0
    mode: str = "mock"

class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None

class StandardResponse(BaseModel, Generic[DataT]):
    success: bool = True
    data: Optional[DataT] = None
    meta: Optional[Dict[str, Any]] = None
    error: Optional[ErrorDetail] = None
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))

def success_response(
    data: Any,
    meta: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None
) -> Dict[str, Any]:
    return {
        "success": True,
        "data": data,
        "meta": meta or {},
        "error": None,
        "request_id": request_id or str(uuid.uuid4())
    }

def error_response(
    code: str,
    message: str,
    details: Optional[Dict[str, Any]] = None,
    status_code: int = 400,
    request_id: Optional[str] = None
) -> Dict[str, Any]:
    return {
        "success": False,
        "data": None,
        "meta": {},
        "error": {
            "code": code,
            "message": message,
            "details": details
        },
        "request_id": request_id or str(uuid.uuid4())
    }
