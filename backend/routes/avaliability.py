from fastapi import APIRouter, Query, HTTPException
from datetime import datetime, timedelta

router = APIRouter(
    prefix="/api/availability",
    tags=["Availability"]
)

_db = None

def set_db(db):
    global _db
    _db = db


@router.get("/")
async def get_availability(
    date: str = Query(..., example="2026-01-27")
):
    """
    Retorna horários disponíveis para uma data
    """
    try:
        selected_date = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")

    # 🔴 AJUSTE: verificar se a data está bloqueada
    blocked = await _db.blocked_dates.find_one({"date": date})
    if blocked:
        return {
            "date": date,
            "available_times": [],
            "blocked": True,
            "reason": blocked.get("reason")
        }

    day_of_week = selected_date.weekday()  # 0 = segunda

    working_hours = await _db.working_hours.find_one({
        "day_of_week": day_of_week,
        "active": True
    })

    if not working_hours:
        return {
            "date": date,
            "available_times": []
        }

    start_time = datetime.strptime(working_hours["start_time"], "%H:%M")
    end_time = datetime.strptime(working_hours["end_time"], "%H:%M")
    interval = working_hours.get("interval_minutes", 30)

    slots = []
    current = start_time

    while current < end_time:
        slots.append(current.strftime("%H:%M"))
        current += timedelta(minutes=interval)

    # Buscar agendamentos do dia
    appointments = await _db.appointments.find({
        "date": {
            "$gte": selected_date,
            "$lt": selected_date + timedelta(days=1)
        },
        "status": {"$ne": "cancelled"}
    }).to_list(100)

    booked_times = {a["time"] for a in appointments}

    available_slots = [
        slot for slot in slots if slot not in booked_times
    ]

    return {
        "date": date,
        "available_times": available_slots
    }
