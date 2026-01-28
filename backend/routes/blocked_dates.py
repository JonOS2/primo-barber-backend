from fastapi import APIRouter, HTTPException
from typing import List
from models import BlockedDate

router = APIRouter(
    prefix="/api/blocked-dates",
    tags=["Blocked Dates"]
)

_db = None

def set_db(db):
    global _db
    _db = db


@router.get("/", response_model=List[BlockedDate])
async def list_blocked_dates():
    return await _db.blocked_dates.find({}, {"_id": 0}).to_list(100)


@router.post("/", response_model=BlockedDate)
async def create_blocked_date(payload: BlockedDate):
    exists = await _db.blocked_dates.find_one({"date": payload.date})
    if exists:
        raise HTTPException(status_code=400, detail="Date already blocked")

    await _db.blocked_dates.insert_one(payload.dict())
    return payload


@router.delete("/{date}")
async def delete_blocked_date(date: str):
    result = await _db.blocked_dates.delete_one({"date": date})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Blocked date not found")

    return {"message": "Blocked date removed"}
