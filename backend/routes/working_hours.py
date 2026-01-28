from fastapi import APIRouter, HTTPException
from typing import List
from models import WorkingHours

router = APIRouter(
    prefix="/api/working-hours",
    tags=["Working Hours"]
)

_db = None

def set_db(db):
    global _db
    _db = db


# 📌 LISTAR
@router.get("/", response_model=List[WorkingHours])
async def list_working_hours():
    return await _db.working_hours.find({}, {"_id": 0}).to_list(100)


# 📌 CRIAR
@router.post("/", response_model=WorkingHours)
async def create_working_hours(payload: WorkingHours):
    exists = await _db.working_hours.find_one({
        "day_of_week": payload.day_of_week
    })

    if exists:
        raise HTTPException(
            status_code=400,
            detail="Working hours already exist for this day"
        )

    await _db.working_hours.insert_one(payload.dict(exclude_none=True))
    return payload


# ✏️ ATUALIZAR (por dia da semana)
@router.put("/{day_of_week}", response_model=WorkingHours)
async def update_working_hours(day_of_week: int, payload: WorkingHours):
    result = await _db.working_hours.find_one_and_update(
        {"day_of_week": day_of_week},
        {"$set": payload.dict(exclude_none=True)},
        return_document=True
    )

    if not result:
        raise HTTPException(status_code=404, detail="Working hours not found")

    result.pop("_id", None)
    return result


# 🗑️ DELETAR
@router.delete("/{day_of_week}")
async def delete_working_hours(day_of_week: int):
    result = await _db.working_hours.delete_one({
        "day_of_week": day_of_week
    })

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Working hours not found"
        )

    return {"message": "Working hours deleted"}
