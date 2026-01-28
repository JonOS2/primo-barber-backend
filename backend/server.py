from pathlib import Path
from dotenv import load_dotenv

# --------------------------------------------------
# Load ENV FIRST (ANTES DE TUDO)
# --------------------------------------------------
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

# --------------------------------------------------
# Imports depois do ENV
# --------------------------------------------------
from fastapi import FastAPI, APIRouter
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager
import os
import logging

from routes import (
    appointments,
    services,
    settings,
    dashboard,
    telegram,
    working_hours,
    avaliability,
)

# --------------------------------------------------
# Config
# --------------------------------------------------
mongo_url = os.environ["MONGO_URL"]
db_name = os.environ["DB_NAME"]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("primo-barber")

# --------------------------------------------------
# Lifespan
# --------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting Primo Barber API")

    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]

    appointments.set_db(db)
    services.set_db(db)
    settings.set_db(db)
    dashboard.set_db(db)
    working_hours.set_db(db)
    avaliability.set_db(db)

    app.state.db = db
    app.state.mongo_client = client

    yield

    logger.info("🛑 Shutting down Primo Barber API")
    client.close()

# --------------------------------------------------
# App
# --------------------------------------------------
app = FastAPI(
    title="Primo Barber API",
    version="1.0.0",
    lifespan=lifespan,
)

# --------------------------------------------------
# API Router
# --------------------------------------------------
api_router = APIRouter(prefix="/api")

@api_router.get("/")
async def root():
    return {
        "message": "Primo Barber API",
        "version": "1.0.0",
    }

@api_router.get("/health")
async def health_check():
    await app.state.db.command("ping")
    return {"status": "healthy"}

# --------------------------------------------------
# Routers
# --------------------------------------------------
app.include_router(api_router)
app.include_router(appointments.router)
app.include_router(services.router)
app.include_router(settings.router)
app.include_router(dashboard.router)
app.include_router(telegram.router)
app.include_router(working_hours.router)
app.include_router(avaliability.router)

# --------------------------------------------------
# CORS
# --------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
