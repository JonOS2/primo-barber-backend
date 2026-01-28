"""
Seed script to populate initial data for Primo Barber
Run this script once to populate services and settings
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path
from models import Service, Setting
from datetime import datetime

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Initial services data
INITIAL_SERVICES = [
    {
        "name": "Corte Clássico",
        "description": "Corte tradicional com acabamento impecável e lavagem completa",
        "price": 60.0,
        "duration": "45 min",
        "image": "https://images.pexels.com/photos/7518761/pexels-photo-7518761.jpeg",
        "active": True
    },
    {
        "name": "Barba Completa",
        "description": "Aparar, modelar e finalização com produtos premium",
        "price": 50.0,
        "duration": "30 min",
        "image": "https://images.pexels.com/photos/3998415/pexels-photo-3998415.jpeg",
        "active": True
    },
    {
        "name": "Corte + Barba",
        "description": "Pacote completo para um visual impecável",
        "price": 95.0,
        "duration": "1h 15min",
        "image": "https://images.pexels.com/photos/4625632/pexels-photo-4625632.jpeg",
        "active": True
    },
    {
        "name": "Tratamento Premium",
        "description": "Corte, barba, massagem e tratamentos especiais",
        "price": 150.0,
        "duration": "2h",
        "image": "https://images.pexels.com/photos/4663134/pexels-photo-4663134.jpeg",
        "active": True
    }
]

# Initial settings data
INITIAL_SETTINGS = [
    {
        "key": "barber_name",
        "value": "Primo Barber",
        "type": "string"
    },
    {
        "key": "phone",
        "value": "(11) 98765-4321",
        "type": "string"
    },
    {
        "key": "email",
        "value": "contato@primobarber.com.br",
        "type": "string"
    },
    {
        "key": "address",
        "value": "Av. Paulista, 1578 - Bela Vista, São Paulo - SP",
        "type": "string"
    },
    {
        "key": "hours_weekdays",
        "value": "Segunda a Sexta: 9h às 20h",
        "type": "string"
    },
    {
        "key": "hours_saturday",
        "value": "Sábado: 9h às 18h",
        "type": "string"
    },
    {
        "key": "hours_sunday",
        "value": "Domingo: 10h às 16h",
        "type": "string"
    },
    {
        "key": "telegram_bot",
        "value": "https://t.me/primobarber_bot",
        "type": "string"
    },
    {
        "key": "instagram",
        "value": "https://instagram.com/primobarber",
        "type": "string"
    },
    {
        "key": "facebook",
        "value": "https://facebook.com/primobarber",
        "type": "string"
    }
]


async def seed_database():
    """Populate database with initial data"""
    # Connect to MongoDB
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    print("🌱 Starting database seeding...")
    
    # Seed Services
    print("\n📋 Seeding services...")
    existing_services = await db.services.count_documents({})
    
    if existing_services > 0:
        print(f"⚠️  Found {existing_services} existing services. Skipping services seed.")
    else:
        for service_data in INITIAL_SERVICES:
            service = Service(**service_data)
            await db.services.insert_one(service.dict())
            print(f"✅ Created service: {service.name}")
        print(f"✅ Successfully seeded {len(INITIAL_SERVICES)} services")
    
    # Seed Settings
    print("\n⚙️  Seeding settings...")
    existing_settings = await db.settings.count_documents({})
    
    if existing_settings > 0:
        print(f"⚠️  Found {existing_settings} existing settings. Skipping settings seed.")
    else:
        for setting_data in INITIAL_SETTINGS:
            setting = Setting(**setting_data)
            await db.settings.insert_one(setting.dict())
            print(f"✅ Created setting: {setting.key}")
        print(f"✅ Successfully seeded {len(INITIAL_SETTINGS)} settings")
    
    # Close connection
    client.close()
    print("\n🎉 Database seeding completed!")


if __name__ == "__main__":
    asyncio.run(seed_database())
