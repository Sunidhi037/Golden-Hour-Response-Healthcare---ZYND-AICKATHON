from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
from sqlalchemy.orm import Session

# Import schemas and orchestrator
from src.models.schemas import TriageInput, EmergencyRequest, LocationData
from src.orchestrator.orchestrator import orchestrator
from src.database.db import get_db, Emergency

router = APIRouter()


# =====================
# Frontend Triage Endpoint (NEW - matches your form)
# =====================

@router.post("/triage")
async def triage_emergency(
    request: TriageInput,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Receives emergency from new frontend form.
    Saves to DB and triggers orchestrator.
    """
    print(f"🚨 Received Emergency: {request.patientName}")
    print(f"   Age: {request.age}, Gender: {request.gender}")
    print(f"   Symptoms: {request.symptoms}")
    print(f"   Location: ({request.location.lat}, {request.location.lng})")
    
    try:
        # Create database entry
        emergency = Emergency(
            location=f"Lat: {request.location.lat}, Lng: {request.location.lng}",
            latitude=request.location.lat,
            longitude=request.location.lng,
            symptoms=[request.symptoms],  # Store as JSON array
            age_group=request.age,  # "40-45" format
            vitals={
                "bloodPressure": request.vitals.bloodPressure,
                "heartRate": request.vitals.heartRate,
                "oxygenLevel": request.vitals.oxygenLevel
            },
            status="REGISTERED"
        )
        
        db.add(emergency)
        db.commit()
        db.refresh(emergency)
        
        print(f"✅ Emergency saved with ID: {emergency.id}")
        
        # Prepare payload for orchestrator
        payload = {
            "patientName": request.patientName,
            "age": request.age,
            "gender": request.gender,
            "contact": request.contact,
            "symptoms": request.symptoms,
            "vitals": request.vitals.dict(),
            "location": {"lat": request.location.lat, "lng": request.location.lng}
        }
        
        # Trigger orchestrator in background - FIXED: pass as positional args
        background_tasks.add_task(
            orchestrator.handle_emergency,
            emergency.id,  # First positional argument
            payload        # Second positional argument
        )
        
        return {
            "success": True,
            "emergencyId": emergency.id,
            "message": "Emergency registered successfully",
            "status": "PROCESSING"
        }
        
    except Exception as e:
        print(f"❌ Error in /triage: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# =====================
# Hospital Endpoint (NEW - fixes 404 error)
# =====================

@router.get("/hospitals/{emergency_id}")
async def get_hospital_for_emergency(
    emergency_id: int,
    db: Session = Depends(get_db)
):
    """
    Get assigned hospital for an emergency
    """
    try:
        # Fetch emergency from database
        emergency = db.query(Emergency).filter(Emergency.id == emergency_id).first()
        
        if not emergency:
            raise HTTPException(status_code=404, detail="Emergency not found")
        
        if not emergency.assigned_hospital_id:
            return {
                "status": "pending", 
                "message": "Hospital assignment in progress",
                "emergencyId": emergency_id
            }
        
        # TODO: Fetch hospital details from your Hospital table
        # For now, return mock data
        return {
            "emergencyId": emergency_id,
            "status": "assigned",
            "hospital": {
                "id": emergency.assigned_hospital_id,
                "name": "City General Hospital",  # Replace with actual query
                "address": "123 Main St",
                "phone": "+91-1234567890",
                "estimatedArrivalTime": emergency.estimated_arrival_time
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error fetching hospital: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =====================
# Supporting Endpoints
# =====================

@router.get("/status/{emergency_id}")
async def get_agent_status(emergency_id: int, db: Session = Depends(get_db)):
    """Get emergency processing status"""
    emergency = db.query(Emergency).filter(Emergency.id == emergency_id).first()
    
    if not emergency:
        raise HTTPException(status_code=404, detail="Emergency not found")
    
    return {
        "emergencyId": emergency.id,
        "status": emergency.status,
        "severity": emergency.severity,
        "assignedHospital": emergency.assigned_hospital_id,
        "eta": emergency.estimated_arrival_time,
        "timestamp": emergency.created_at.isoformat() if emergency.created_at else None
    }


@router.post("/notify")
async def notify_hospital(data: dict):
    """Send notification to selected hospital"""
    hospital_id = data.get("hospitalId")
    emergency_id = data.get("emergencyId")
    
    if not hospital_id or not emergency_id:
        raise HTTPException(status_code=400, detail="Missing hospitalId or emergencyId")
    
    return {
        "success": True,
        "message": f"Hospital {hospital_id} notified about emergency {emergency_id}",
        "confirmationId": f"notify_{int(datetime.utcnow().timestamp())}"
    }


# =====================
# Legacy Endpoint (Backward compatibility)
# =====================

@router.post("/emergency/create")
async def create_emergency(
    request: EmergencyRequest,
    background_tasks: BackgroundTasks
):
    """
    Legacy endpoint - kept for backward compatibility.
    Use /triage for new frontend.
    """
    return await orchestrator.handle_emergency(request, background_tasks)
