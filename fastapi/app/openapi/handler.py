from app.core.config import settings
from openai import AsyncOpenAI
import json
from app.core.logging import get_logger
logger = get_logger("openai_handler")
from app.db.session import AsyncSessionLocal
from app.video.models import *
import json
import re

from datetime import datetime, date
from sqlalchemy import select, func, and_

async def execute_query_from_json(query_json: dict) -> int:

    async with AsyncSessionLocal() as db:

        q_type = query_json["type"]
        filters = query_json.get("filters", {})

        if q_type == "total_count":
            result = await db.execute(select(func.count()).select_from(Video))
            return result.scalar_one()

        elif q_type == "count_by_creator_and_date":
            creator_id = filters["creator_id"]
            start = datetime.fromisoformat(filters["start_date"])
            end = datetime.fromisoformat(filters["end_date"])
            stmt = (
                select(func.count())
                .select_from(Video)
                .where(
                    and_(
                        Video.creator_id == creator_id,
                        Video.video_created_at >= start,
                        Video.video_created_at <= end,
                    )
                )
            )
            result = await db.execute(stmt)
            return result.scalar_one()

        elif q_type == "count_by_views_threshold":
            threshold = filters["views_threshold"]
            stmt = select(func.count()).select_from(Video).where(Video.views_count > threshold)
            result = await db.execute(stmt)
            return result.scalar_one()

        elif q_type == "total_delta_views_on_date":
            target_date = date.fromisoformat(filters["target_date"])  # "2025-11-28"
            start = datetime.combine(target_date, datetime.min.time())
            end = datetime.combine(target_date, datetime.max.time())
            stmt = (
                select(func.sum(VideoSnapshot.delta_views_count))
                .where(
                    and_(
                        VideoSnapshot.created_at >= start,
                        VideoSnapshot.created_at <= end,
                    )
                )
            )
            result = await db.execute(stmt)
            return result.scalar_one() or 0

        elif q_type == "distinct_videos_with_views_on_date":
            target_date = date.fromisoformat(filters["target_date"])  # "2025-11-27"
            start = datetime.combine(target_date, datetime.min.time())
            end = datetime.combine(target_date, datetime.max.time())
            stmt = (
                select(func.count(func.distinct(VideoSnapshot.video_id)))
                .where(
                    and_(
                        VideoSnapshot.created_at >= start,
                        VideoSnapshot.created_at <= end,
                        VideoSnapshot.delta_views_count > 0,
                    )
                )
            )
            result = await db.execute(stmt)
            return result.scalar_one() or 0

        else:
            logger.error(f"Неизвестный тип запроса ",q_type=q_type)
            raise ValueError(f"Неизвестный тип запроса: {q_type}")

# Примеры запросов:
#     «Сколько всего видео есть в системе?»
#     «Сколько видео у креатора с id X вышло с 2025-11-01 по 2025-11-05 включительно?»
#     «Сколько видео набрало больше 100000 просмотров за всё время?»
#     «На сколько просмотров в сумме выросли все видео 2025-11-28?»
#     «Сколько разных видео получали новые просмотры 2025-11-27?»

async def send_promt_to_ai(user_query):

    promt = """

    Ты — строгий парсер запросов на русском языке. Твоя задача — извлечь из текста параметры фильтрации и вернуть ТОЛЬКО валидный JSON без каких-либо пояснений, markdown или дополнительного текста.
    videos
    id: str — уникальный ID видео
    creator_id: str — ID креатора
    video_created_at: datetime — дата публикации видео
    views_count: int — текущее (финальное) число просмотров
    likes_count, comments_count, reports_count: int
    created_at, updated_at: datetime
    video_snapshots

    id: str — ID снапшота
    video_id: str → ссылка на videos.id
    views_count, likes_count, и т.д. — значения на момент замера
    delta_views_count, delta_likes_count, и т.д. — прирост с предыдущего замера
    created_at: datetime — время замера (обычно каждый час)
    updated_at: datetime
    Правила:

    Никогда не выдумывай поля — используй только указанные.
    Для агрегации по дате используй video_created_at из videos (для даты выхода видео) или created_at из video_snapshots (для даты замера).
    Прирост просмотров за день = сумма delta_views_count по всем снапшотам с created_at в этот день.
    Возвращай только валидный JSON вида:    
    где:
    type — одно из: "total_count", "count_by_creator_and_date", "count_by_views_threshold", "total_delta_views_on_date", "distinct_videos_with_views_on_date"
    sql_intent — краткое описание на английском
    filters — только те параметры, что есть в запросе (даты в ISO 8601, числа — как есть)

    Ответь только JSON, без пояснений, без ```, только валидный JSON.
    Теперь обработай этот запрос:{user_query}"""

    full_prompt = promt.format(user_query=user_query) 

    client = AsyncOpenAI(
        api_key=settings.AI_TOKEN,
        base_url=settings.AI_API_URL, 
    )
    response = await client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": full_prompt}],
        temperature=0.1
    )
    data = response.choices[0].message.content
    parsed_data = json.loads(data)

    answer = await execute_query_from_json(parsed_data)
    logger.info(f"Ответ от AI",data=data)

    return answer

