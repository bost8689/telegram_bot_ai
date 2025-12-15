# python3 cli/test_tg.py run

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(PROJECT_ROOT)
sys.path.insert(0, PROJECT_ROOT)

import typer
app = typer.Typer()
from app.core.config import settings
from app.db.session import AsyncSessionLocal
import asyncio
from aiogram import Bot
import time
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from openai import AsyncOpenAI

from app.core.logging import get_logger
logger = get_logger("test_tg")

@app.command()
def zaglushka():
    pass

async def send_telegram_message(text):
    try:
        bot = Bot(token=settings.TG_BOT_TOKEN)
        await bot.send_message(
            chat_id=settings.TG_CHAT_ID,
            text=text
        )
        return {"status": "success", "message": "Сообщение отправлено!"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}    
    finally:
        await bot.session.close()    

async def execute():
    async with AsyncSessionLocal() as db:
        
        await send_telegram_message(text='Тест из cli test_tg')

        return True

@app.command()
def run():
    """Запустить"""   
    now = datetime.now()  
    typer.echo(f"Запуск {now}") 

    if not settings.TG_BOT_TOKEN or not settings.TG_BOT_ID:
            raise ValueError("TG_BOT_TOKEN и TG_BOT_ID должны быть указаны в .env")
       
    asyncio.run(execute())  
    typer.echo(f"🏁 Завершено {now}")

if __name__ == "__main__":
    app()
