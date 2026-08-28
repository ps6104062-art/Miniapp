"""
generate_session.py — Запусти это ОДИН РАЗ через терминал Railway.
Выдаст SESSION_STRING — строку которую вставишь в переменные окружения.

Запуск в терминале Railway:
  python generate_session.py
"""

import asyncio
from pyrogram import Client

API_ID   = int(input("Введи API_ID: ").strip())
API_HASH = input("Введи API_HASH: ").strip()

async def main():
    async with Client(
        name="temp_session",
        api_id=API_ID,
        api_hash=API_HASH,
        in_memory=True,
    ) as app:
        session_string = await app.export_session_string()
        print("\n" + "="*60)
        print("✅ ТВОЙ SESSION_STRING (скопируй целиком):")
        print("="*60)
        print(session_string)
        print("="*60)
        print("\nВставь эту строку в Railway как переменную SESSION_STRING")

asyncio.run(main())
