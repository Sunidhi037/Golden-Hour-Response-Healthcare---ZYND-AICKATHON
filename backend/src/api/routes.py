from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

# Import your agents and services
from src.agents.routing_agent import routing_agent
from src.agents.notification_agent import notification_agent
from src.services.maps_service import maps_service

router = APIRouter()

# --- Request Models ---
class LocationData(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)

class EmergencyRequest(BaseModel):
    location: LocationData
    severity: str
    description: str
    contact_email: str

# --- Mock Data (Placeholder until DB is ready) ---
MOCK_HOSPITALS = [
    {"id": 1, "name": "City General Hospital", "coords": (28.7041, 77.1025)},
    {"id": 2, "name": "AIIMS Trauma Center", "coords": (28.5650, 77.2060)},
    {"id": 3, "name": "Max Super Specialty", "coords": (28.5744, 77.2343)}
]

# --- Endpoints ---
@router.post("/emergency")
async def create_emergency(request: EmergencyRequest, background_tasks: BackgroundTasks):
    print(f"🚨 Received Emergency: {request.description}")
    
    # 1. Reverse Geocode (Get Address)
    address = await maps_service.get_location_address(request.location.lat, request.location.lng)
    
    # 2. Find Best Hospital
    emergency_coords = (request.location.lat, request.location.lng)
    best_hospital = await routing_agent.find_best_hospital(emergency_coords, MOCK_HOSPITALS)
    
    if not best_hospital:
        raise HTTPException(status_code=404, detail="No reachable hospitals found")

    # 3. Send Notifications (Background Task)
    emergency_data = {
        "severity": request.severity,
        "description": request.description,
        "address": address,
        "contact_email": request.contact_email
    }
    
    background_tasks.add_task(
        notification_agent.send_emergency_alert,
        emergency_data,
        best_hospital
    )
    
    return {
        "status": "success",
        "message": "Emergency processing started",
        "assigned_hospital": best_hospital["name"],
        "eta_minutes": best_hospital["route_info"]["duration_min"],
        "detected_address": address
    }
