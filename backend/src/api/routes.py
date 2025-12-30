from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List

# Import Orchestrator ONLY
from src.orchestrator.orchestrator import orchestrator

router = APIRouter()

# =====================
# Request Models
# =====================

class LocationData(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)

class EmergencyRequest(BaseModel):
    location: LocationData
    symptoms: List[str]
    vitals: dict
    age: int
    description: str
    contact_email: str


# =====================
# Emergency API
# =====================

@router.post("/emergency")
async def create_emergency(
    request: EmergencyRequest,
    background_tasks: BackgroundTasks
):
    """
    Receives emergency request from frontend
    Delegates full workflow to Orchestrator
    """
    return await orchestrator.handle_emergency(request, background_tasks)