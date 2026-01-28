from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import httpx

router = APIRouter(
    prefix="/api/telegram",
    tags=["Telegram"]
)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN não definido")

TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"


# =========================
# Schemas
# =========================

class TelegramMessage(BaseModel):
    chat_id: int
    text: str
    reply_markup: dict | None = None


# =========================
# Utils
# =========================

async def send_message(chat_id: int, text: str, reply_markup: dict | None = None):
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }

    if reply_markup:
        payload["reply_markup"] = reply_markup

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{TELEGRAM_API}/sendMessage",
            json=payload
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=500,
            detail=response.text
        )


# =========================
# Endpoint para o n8n
# =========================

@router.post("/send")
async def send_from_n8n(message: TelegramMessage):
    """
    Endpoint chamado pelo n8n para enviar mensagens Telegram
    """
    await send_message(
        chat_id=message.chat_id,
        text=message.text,
        reply_markup=message.reply_markup
    )

    return {"ok": True}
