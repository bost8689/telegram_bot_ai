# python3 cli/test_openai.py run

import os
import sys
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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
from app.openapi.handler import _send_promt_to_ai, _execute_query_from_json
from app.core.logging import get_logger
logger = get_logger("test_openai")

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

    user_requests = [       
        "Сколько всего видео есть в системе?",        
        "Сколько видео у id 8b76e572635b400c9052286a56176e03?",       
        "Сколько всего видео есть в системе 01.10.2025?",       
        "Сколько всего видео есть в системе c 01.10.2025 по 10.11.2025 ?",
        "Сколько всего видео есть в системе c 01.10.2025 по 10.11.2025 у id 8b76e572635b400c9052286a56176e03?",
        "Cколько видео у креатора с id 8b76e572635b400c9052286a56176e03 вышло 2025-11-01",
        "Cколько видео у креатора с id 8b76e572635b400c9052286a56176e03 за всё время",
        "Cколько видео у креатора с id 8b76e572635b400c9052286a56176e03 вышло с 2025-11-01 по 2025-11-02",

        "На сколько просмотров в сумме выросли все видео 2025-11-28?",
        "На сколько просмотров в сумме выросли все видео c 2025-11-28 по 2025-11-30??",
        "На сколько просмотров в сумме выросли все видео c 2025-11-28 по 2025-11-30 у id 8b76e572635b400c9052286a56176e03",

        "Сколько разных видео получали новые просмотры 2025-11-27?",
        "Сколько разных видео получали новые просмотры c 2025-11-27 по 2025-11-28?",
        "Сколько разных видео получали новые просмотры id 8b76e572635b400c9052286a56176e03 c 2025-11-27 по 2025-11-28?",
        
        "Сколько видео набрало больше 100000 просмотров за всё время?",
        "Сколько видео набрало больше 100000 просмотров за всё время у id 8b76e572635b400c9052286a56176e03?"
        "Сколько видео набрало больше 100000 просмотров за 10.01.2025 у id 8b76e572635b400c9052286a56176e03?",
        "Сколько видео набрало больше 100000 просмотров c 10.01.2025 по 25.01.2025 у id 8b76e572635b400c9052286a56176e03?",
    ]

    # {'type': 'total_videos', 'filters': {}}
    # {'type': 'total_videos', 'filters': {'creator_id': '8b76e572635b400c9052286a56176e03'}}
    # {'type': 'total_videos', 'filters': {'date': '2025-10-01'}}
    # {'type': 'total_videos', 'filters': {'start_date': '2025-10-01', 'end_date': '2025-11-10'}}
    # {'type': 'total_videos', 'filters': {'creator_id': '8b76e572635b400c9052286a56176e03', 'start_date': '2025-10-01', 'end_date': '2025-11-10'}}
    # {'type': 'total_videos', 'filters': {'creator_id': '8b76e572635b400c9052286a56176e03', 'date': '2025-11-01'}}
    # {'type': 'total_videos', 'filters': {'creator_id': '8b76e572635b400c9052286a56176e03'}}
    # {'type': 'total_videos', 'filters': {'creator_id': '8b76e572635b400c9052286a56176e03', 'start_date': '2025-11-01', 'end_date': '2025-11-02'}}
    # {'type': 'total_views_growth_on_date', 'filters': {'date': '2025-11-28'}}
    # {'type': 'total_views_growth_on_date', 'filters': {'start_date': '2025-11-28', 'end_date': '2025-11-30'}}
    # {'type': 'total_views_growth_on_date', 'filters': {'creator_id': '8b76e572635b400c9052286a56176e03', 'start_date': '2025-11-28', 'end_date': '2025-11-30'}}
    # {'type': 'videos_with_new_views_on_date', 'filters': {'date': '2025-11-27'}}
    # {'type': 'videos_with_new_views_on_date', 'filters': {'start_date': '2025-11-27', 'end_date': '2025-11-28'}}
    # {'type': 'videos_with_new_views_on_date', 'filters': {'creator_id': '8b76e572635b400c9052286a56176e03', 'start_date': '2025-11-27', 'end_date': '2025-11-28'}}
    # {'type': 'videos_with_views_over', 'filters': {'threshold': 100000}}
    # {'type': 'videos_with_views_over', 'filters': {'creator_id': '8b76e572635b400c9052286a56176e03', 'threshold': 100000, 'date': '2025-01-10'}}
    # {'type': 'videos_with_views_over', 'filters': {'threshold': 100000, 'start_date': '2025-01-10', 'end_date': '2025-01-25', 'creator_id': '8b76e572635b400c9052286a56176e03'}}

    for user_request in user_requests:
        #logger.info(user_request)
        #typer.echo(f"\"{user_request}\",")  
        result_json = await _send_promt_to_ai(user_request)
        # logger.info(result_json)
        typer.echo(f"# {result_json}")   

        answer = await _execute_query_from_json(query=result_json)
        typer.echo(f"{answer}")

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
