from fastapi import APIRouter
from datetime import datetime, timedelta
from models import DashboardStats
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

# Database will be injected
db: Optional[AsyncIOMotorDatabase] = None


def set_db(database: AsyncIOMotorDatabase):
    global db
    db = database


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats():
    """Get dashboard statistics"""
    # Total appointments
    total_appointments = await db.appointments.count_documents({})
    
    # Pending appointments
    pending_appointments = await db.appointments.count_documents({"status": "pending"})
    
    # Confirmed appointments
    confirmed_appointments = await db.appointments.count_documents({"status": "confirmed"})
    
    # Total services
    total_services = await db.services.count_documents({"active": True})
    
    # Revenue this month (completed appointments)
    start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    completed_this_month = await db.appointments.find({
        "status": "completed",
        "date": {"$gte": start_of_month}
    }).to_list(1000)
    
    revenue_month = 0.0
    for appointment in completed_this_month:
        # Get service price
        service = await db.services.find_one({"id": appointment["service_id"]})
        if service:
            revenue_month += service["price"]
    
    # Appointments today
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    appointments_today = await db.appointments.count_documents({
        "date": {"$gte": today_start, "$lt": today_end}
    })
    
    return DashboardStats(
        total_appointments=total_appointments,
        pending_appointments=pending_appointments,
        confirmed_appointments=confirmed_appointments,
        total_services=total_services,
        revenue_month=revenue_month,
        appointments_today=appointments_today
    )
