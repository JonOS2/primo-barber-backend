from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime
from models import Setting, SettingCreate, SettingUpdate
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional

router = APIRouter(prefix="/api/settings", tags=["settings"])

# Database will be injected
db: Optional[AsyncIOMotorDatabase] = None


def set_db(database: AsyncIOMotorDatabase):
    global db
    db = database


@router.get("", response_model=List[Setting])
async def get_settings():
    """Get all settings"""
    settings = await db.settings.find().to_list(100)
    
    return [Setting(**setting) for setting in settings]


@router.get("/{key}", response_model=Setting)
async def get_setting(key: str):
    """Get specific setting by key"""
    setting = await db.settings.find_one({"key": key})
    
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    
    return Setting(**setting)


@router.post("", response_model=Setting, status_code=201)
async def create_setting(setting: SettingCreate):
    """Create new setting (Admin)"""
    # Check if key already exists
    existing = await db.settings.find_one({"key": setting.key})
    if existing:
        raise HTTPException(status_code=400, detail="Setting key already exists")
    
    setting_obj = Setting(**setting.dict())
    
    await db.settings.insert_one(setting_obj.dict())
    
    return setting_obj


@router.put("/{key}", response_model=Setting)
async def update_setting(key: str, update: SettingUpdate):
    """Update setting (Admin)"""
    setting = await db.settings.find_one({"key": key})
    
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    
    # Update fields
    update_data = {k: v for k, v in update.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    
    await db.settings.update_one(
        {"key": key},
        {"$set": update_data}
    )
    
    # Get updated setting
    updated_setting = await db.settings.find_one({"key": key})
    
    return Setting(**updated_setting)


@router.delete("/{key}")
async def delete_setting(key: str):
    """Delete setting (Admin)"""
    result = await db.settings.delete_one({"key": key})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Setting not found")
    
    return {"message": "Setting deleted successfully"}
