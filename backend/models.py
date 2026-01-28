from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid


class ServiceBase(BaseModel):
    name: str
    description: str
    price: float
    duration: str
    image: str
    active: bool = True


class ServiceCreate(ServiceBase):
    pass


class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    duration: Optional[str] = None
    image: Optional[str] = None
    active: Optional[bool] = None


class Service(ServiceBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AppointmentBase(BaseModel):
    client_name: str
    client_phone: str
    client_telegram_username: Optional[str] = None
    service_id: str
    date: str
    time: str
    notes: Optional[str] = None


class AppointmentCreate(BaseModel):
    client_name: str
    client_phone: str
    client_telegram_username: Optional[str] = None
    service_id: str
    date: str
    time: str
    notes: Optional[str] = None


class AppointmentUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None


class Appointment(AppointmentBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status: str = "pending"  # pending | confirmed | cancelled | completed
    source: str = "web"      # web | telegram
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }



class WorkingHours(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    day_of_week: int  # 0=segunda, 6=domingo
    start_time: str   # "09:00"
    end_time: str     # "20:00"
    interval_minutes: int = 60
    active: bool = True

class BlockedDate(BaseModel):
    date: str  # "2026-01-25"
    reason: Optional[str] = None


class SettingBase(BaseModel):
    key: str
    value: str
    type: str = "string"  # string, number, boolean, json


class SettingCreate(SettingBase):
    pass


class SettingUpdate(BaseModel):
    value: str
    type: Optional[str] = None


class Setting(SettingBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class DashboardStats(BaseModel):
    total_appointments: int
    pending_appointments: int
    confirmed_appointments: int
    total_services: int
    revenue_month: float
    appointments_today: int
