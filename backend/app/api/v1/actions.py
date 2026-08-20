from typing import Optional, Dict, Any
from fastapi import APIRouter
from pydantic import BaseModel
from app.core.response import success_response

router = APIRouter()

class DispatchActionRequest(BaseModel):
    action_type: str  # CALL_VENDOR, DISPATCH_TOWING, ALERT_FAMILY
    target_id: str
    payload: Optional[Dict[str, Any]] = None

@router.post("/actions/dispatch")
async def dispatch_action(req: DispatchActionRequest):
    return success_response(
        data={
            "action_id": "act_disp_101",
            "status": "DISPATCHED",
            "message": f"Action '{req.action_type}' initialized for target '{req.target_id}'",
            "confirmation_code": "RAAHAT-SOS-8890"
        }
    )
