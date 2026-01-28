from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from datetime import datetime, timedelta
from models import Appointment, AppointmentCreate, AppointmentUpdate
from motor.motor_asyncio import AsyncIOMotorDatabase

router = APIRouter(
    prefix="/api/appointments",
    tags=["Appointments"]
)

# Database injection
db: Optional[AsyncIOMotorDatabase] = None


def set_db(database: AsyncIOMotorDatabase):
    global db
    db = database


@router.post("", response_model=Appointment, status_code=201)
async def create_appointment(appointment: AppointmentCreate):
    """
    Create new appointment (web or telegram)
    """

    # 🔹 Normaliza data (zera horário)
    selected_date = appointment.date.replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    day_of_week = selected_date.weekday()  # 0 = segunda

    # 🔹 Verifica se a data está bloqueada
    blocked = await db.blocked_dates.find_one({
        "date": selected_date.strftime("%Y-%m-%d")
    })

    if blocked:
        raise HTTPException(
            status_code=400,
            detail="This date is blocked"
        )

    # 🔹 Verifica horário de trabalho
    working_hours = await db.working_hours.find_one({
        "day_of_week": day_of_week,
        "active": True
    })

    if not working_hours:
        raise HTTPException(
            status_code=400,
            detail="No working hours for this day"
        )

    # 🔹 Verifica conflito de horário
    conflict = await db.appointments.find_one({
        "date": {
            "$gte": selected_date,
            "$lt": selected_date + timedelta(days=1)
        },
        "time": appointment.time,
        "status": {"$ne": "cancelled"}
    })

    if conflict:
        raise HTTPException(
            status_code=400,
            detail="Time slot already booked"
        )

    # 🔹 Busca serviço
    service = await db.services.find_one({"id": appointment.service_id})
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    # 🔹 Cria objeto final
    appointment_obj = Appointment(
        **appointment.dict(),
        service_name=service["name"],
        status="pending",
        source="web"  # o bot usará "telegram"
    )

    await db.appointments.insert_one(
        appointment_obj.dict(exclude_none=True)
    )

    return appointment_obj


@router.get("", response_model=List[Appointment])
async def get_appointments(
    status: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    limit: int = Query(100, le=500)
):
    """
    List appointments with filters
    """
    query = {}

    if status:
        query["status"] = status

    if date_from:
        query["date"] = {"$gte": datetime.fromisoformat(date_from)}

    if date_to:
        if "date" in query:
            query["date"]["$lte"] = datetime.fromisoformat(date_to)
        else:
            query["date"] = {"$lte": datetime.fromisoformat(date_to)}

    appointments = await db.appointments.find(query) \
        .sort("date", -1) \
        .limit(limit) \
        .to_list(limit)

    return [Appointment(**a) for a in appointments]


@router.get("/{appointment_id}", response_model=Appointment)
async def get_appointment(appointment_id: str):
    """
    Get appointment by ID
    """
    appointment = await db.appointments.find_one({"id": appointment_id})

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    return Appointment(**appointment)


@router.patch("/{appointment_id}", response_model=Appointment)
async def update_appointment(
    appointment_id: str,
    update: AppointmentUpdate
):
    """
    Update appointment (status, date, time, notes)
    """
    appointment = await db.appointments.find_one({"id": appointment_id})

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    update_data = {
        k: v for k, v in update.dict().items()
        if v is not None
    }
    update_data["updated_at"] = datetime.utcnow()

    await db.appointments.update_one(
        {"id": appointment_id},
        {"$set": update_data}
    )

    updated = await db.appointments.find_one({"id": appointment_id})

    return Appointment(**updated)


@router.delete("/{appointment_id}")
async def delete_appointment(appointment_id: str):
    """
    Cancel appointment
    """
    result = await db.appointments.delete_one({"id": appointment_id})

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Appointment not found"
        )

    return {"message": "Appointment deleted"}
