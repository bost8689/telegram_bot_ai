# python3 cli/test_load_data.py run

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
import json
from sqlalchemy import select
from app.video.models import *
from app.core.logging import get_logger
logger = get_logger("test_load_data")

@app.command()
def zaglushka():
    pass

async def load_data_from_file(file_path: str):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data
    

def parse_dt(dt_str: str) -> datetime:
    # Заменяем 'Z' на '+00:00', если нужно (ваш формат уже содержит +00:00)
    if dt_str.endswith('Z'):
        dt_str = dt_str[:-1] + '+00:00'
    dt = datetime.fromisoformat(dt_str)
    # Убедимся, что объект "aware" (с временной зоной)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt

async def execute():
    data = await load_data_from_file('videos.json')

    async with AsyncSessionLocal() as db:
        for video_data in data["videos"]:
            result = await db.execute(select(Video).where(Video.id == video_data["id"]))
            existing_video = result.scalar_one_or_none()

            if not existing_video:           
                new_video = Video(
                    id=video_data["id"],
                    creator_id=video_data["creator_id"],
                    video_created_at=parse_dt(video_data["video_created_at"]),
                    views_count=video_data["views_count"],
                    likes_count=video_data["likes_count"],
                    comments_count=video_data["comments_count"],
                    reports_count=video_data["reports_count"],
                    created_at=parse_dt(video_data["created_at"]),
                    updated_at=parse_dt(video_data["updated_at"]),
                )
                db.add(new_video)
                await db.flush() 

            # Обработка снапшотов
            for snap_data in video_data.get("snapshots", []):
                result = await db.execute(
                    select(VideoSnapshot).where(VideoSnapshot.id == snap_data["id"])
                )
                existing_snap = result.scalar_one_or_none()

                if not existing_snap:
                    new_snap = VideoSnapshot(
                        id=snap_data["id"],
                        video_id=snap_data["video_id"],
                        views_count=snap_data["views_count"],
                        likes_count=snap_data["likes_count"],
                        comments_count=snap_data["comments_count"],
                        reports_count=snap_data["reports_count"],
                        delta_views_count=snap_data["delta_views_count"],
                        delta_likes_count=snap_data["delta_likes_count"],
                        delta_comments_count=snap_data["delta_comments_count"],
                        delta_reports_count=snap_data["delta_reports_count"],
                        created_at=parse_dt(snap_data["created_at"]),
                        updated_at=parse_dt(snap_data["updated_at"]),
                    )
                    db.add(new_snap)
        try:
            await db.commit()
            typer.echo(f"✅ Данные успешно загружены")   
      
        except Exception as e:
            await db.rollback()
            typer.echo(f"❌ Ошибка при загрузке: {e}")
            raise

    return True

@app.command()
def run():
    """Запустить"""
    typer.echo(f"🔁 Началась загрузка данных {datetime.now()}")     
    asyncio.run(execute())   
    typer.echo(f"🏁 Завершено {datetime.now()}")

if __name__ == "__main__":
    app()
