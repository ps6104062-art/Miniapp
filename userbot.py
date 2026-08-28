"""
userbot.py — Следит за аккаунтом менеджера на входящие NFT/gift.
Оптимизирован для Railway: все настройки через переменные окружения,
сессия хранится как строка в SESSION_STRING (не файл).
"""

import asyncio
import logging
import os
import aiohttp
from pyrogram import Client, filters, idle
from pyrogram.types import Message

# ── Настройки из переменных окружения ─────────────────────────────────────────

API_ID         = int(os.environ.get("API_ID", "0"))
API_HASH       = os.environ.get("API_HASH", "")
SESSION_STRING = os.environ.get("SESSION_STRING", "")   # строка сессии Pyrogram
USERBOT_SECRET = os.environ.get("USERBOT_SECRET", "CHANGE_ME")
BOT_WEBHOOK_URL = os.environ.get("BOT_WEBHOOK_URL", "")  # https://твой-бот.railway.app/nft_received

# ── Логирование ────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [userbot] %(levelname)s: %(message)s",
)
log = logging.getLogger("userbot")

# ── Клиент Pyrogram (через строку сессии, без файлов) ─────────────────────────

app = Client(
    name="manager",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING or None,
)


def _extract_nft_info(message: Message) -> dict | None:
    """Извлекает данные NFT/gift из сообщения. None если не gift."""

    # Unique Gift (NFT) — Pyrogram 2.x
    ug = getattr(message, "unique_gift", None)
    if ug is None:
        gift_obj = getattr(message, "gift", None)
        if gift_obj:
            ug = getattr(gift_obj, "unique_gift", None)

    if ug is not None:
        name = getattr(ug, "name", None) or getattr(ug, "base_name", None) or "UniqueGift"
        nft_link = f"https://t.me/nft/{name}" if name else ""
        return {"nft_link": nft_link, "nft_name": name, "nft_count": 1}

    # Обычный Stars Gift
    gift_obj = getattr(message, "gift", None)
    if gift_obj is not None:
        name = getattr(gift_obj, "name", None) or "Telegram Gift"
        return {"nft_link": "", "nft_name": name, "nft_count": 1}

    return None


async def _notify_bot(buyer_id: int, nft_info: dict):
    """POST на бота с данными о полученном NFT."""
    if not BOT_WEBHOOK_URL:
        log.error("BOT_WEBHOOK_URL не задан!")
        return
    payload = {
        "secret":    USERBOT_SECRET,
        "buyer_id":  buyer_id,
        "nft_link":  nft_info["nft_link"],
        "nft_name":  nft_info["nft_name"],
        "nft_count": nft_info["nft_count"],
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                BOT_WEBHOOK_URL, json=payload,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                text = await resp.text()
                log.info(f"Бот уведомлён: status={resp.status} resp={text!r}")
    except Exception as e:
        log.error(f"Не удалось уведомить бота: {e}")


@app.on_message(filters.private & filters.incoming)
async def on_incoming_message(client: Client, message: Message):
    nft_info = _extract_nft_info(message)
    if nft_info is None:
        return

    sender = message.from_user
    if sender is None:
        return

    buyer_id = sender.id
    buyer_username = sender.username or str(buyer_id)
    log.info(f"Gift от @{buyer_username} (id={buyer_id}): {nft_info['nft_name']}")
    await _notify_bot(buyer_id, nft_info)


async def main():
    if not API_ID or not API_HASH:
        log.error("API_ID и API_HASH не заданы в переменных окружения!")
        return
    if not SESSION_STRING:
        log.error("SESSION_STRING не задана! Сначала запусти generate_session.py локально.")
        return

    log.info("Userbot запускается...")
    async with app:
        log.info("✅ Userbot авторизован и слушает входящие gift-сообщения")
        await idle()


if __name__ == "__main__":
    asyncio.run(main())
