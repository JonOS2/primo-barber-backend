from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from datetime import datetime
from models import Service, ServiceCreate, ServiceUpdate
from motor.motor_asyncio import AsyncIOMotorDatabase

router = APIRouter(prefix="/api/services", tags=["services"])

# Database will be injected
db: Optional[AsyncIOMotorDatabase] = None


def set_db(database: AsyncIOMotorDatabase):
    global db
    db = database


@router.get("", response_model=List[Service])
async def get_services(active: Optional[bool] = Query(None)):
    """Get all services"""
    query = {}
    
    if active is not None:
        query["active"] = active
    
    services = await db.services.find(query).sort("created_at", 1).to_list(100)
    
    return [Service(**service) for service in services]


@router.get("/{service_id}", response_model=Service)
async def get_service(service_id: str):
    """Get specific service"""
    service = await db.services.find_one({"id": service_id})
    
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    return Service(**service)


@router.post("", response_model=Service, status_code=201)
async def create_service(service: ServiceCreate):
    """Create new service (Admin)"""
    service_obj = Service(**service.dict())
    
    await db.services.insert_one(service_obj.dict())
    
    return service_obj


@router.put("/{service_id}", response_model=Service)
async def update_service(service_id: str, update: ServiceUpdate):
    """Update service (Admin)"""
    service = await db.services.find_one({"id": service_id})
    
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    # Update fields
    update_data = {k: v for k, v in update.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    
    await db.services.update_one(
        {"id": service_id},
        {"$set": update_data}
    )
    
    # Get updated service
    updated_service = await db.services.find_one({"id": service_id})
    
    return Service(**updated_service)


@router.delete("/{service_id}")
async def delete_service(service_id: str):
    """Delete service (Admin)"""
    result = await db.services.delete_one({"id": service_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Service not found")
    
    return {"message": "Service deleted successfully"}
