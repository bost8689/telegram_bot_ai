from app.core.config import settings
from openai import AsyncOpenAI
import json
from app.core.logging import get_logger
logger = get_logger("openai_handler")
from app.db.session import AsyncSessionLocal
from app.video.models import *
import json
from datetime import datetime, date, time

from datetime import datetime, date
from sqlalchemy import select, func, and_, distinct

async def get_data_from_user_query(user_query_text: str) -> int:
    logger.info(f"входные данные",user_query_text=user_query_text)
    query_json = await _send_promt_to_ai(user_query_text)
    logger.info(f"ответ от ai",query_json=query_json)
    result = await _execute_query_from_json(query_json)
    logger.info(f"данные из бд для ответа в тг",result=result)
    return result

def _parse_date_to_datetime_range(dt_input) -> tuple[datetime, datetime]:
    """Преобразует строку 'YYYY-MM-DD' в (start, end) с часовым поясом UTC."""
    if isinstance(dt_input, str):
        d = date.fromisoformat(dt_input)
    elif isinstance(dt_input, date):
        d = dt_input
    else:
        raise ValueError("Ожидалась строка вида 'YYYY-MM-DD' или date")
    start = datetime.combine(d, time.min) 
    end = datetime.combine(d, time.max) 
    return start, end

async def _execute_query_from_json(query: dict) -> int:
    """
    Выполняет аналитический запрос к БД на основе типа и фильтров.
    Возвращает целое число — результат агрегации.
    """
    async with AsyncSessionLocal() as db:
        query_type = query["type"]
        filters = query.get("filters", {})
        # Подсчёт видео
        if query_type is None:
            logger.error(f"Неверный формат запроса")
            return f"Неверный формат запроса"
        if query_type == "total_videos":
            stmt = select(func.count()).select_from(Video)
            conditions = []

            if "creator_id" in filters:
                conditions.append(Video.creator_id == filters["creator_id"])

            if "date" in filters:
                start, end = _parse_date_to_datetime_range(filters["date"])
                conditions.append(Video.video_created_at >= start)
                conditions.append(Video.video_created_at <= end)
            elif "start_date" in filters and "end_date" in filters:
                start = datetime.fromisoformat(filters["start_date"])
                end = datetime.fromisoformat(filters["end_date"])
                # Или, если передаются без времени:
                if "T" not in filters["start_date"]:
                    start, _ = _parse_date_to_datetime_range(filters["start_date"])
                if "T" not in filters["end_date"]:
                    _, end = _parse_date_to_datetime_range(filters["end_date"])
                conditions.append(Video.video_created_at >= start)
                conditions.append(Video.video_created_at <= end)

            if conditions:
                stmt = stmt.where(and_(*conditions))
            result = await db.execute(stmt)
            return result.scalar_one()

        # Рост просмотров (по снапшотам)
        elif query_type == "total_views_growth_on_date":
            stmt = select(func.coalesce(func.sum(VideoSnapshot.delta_views_count), 0))
            conditions = []

            if "date" in filters:
                start, end = _parse_date_to_datetime_range(filters["date"])
                conditions.append(VideoSnapshot.created_at >= start)
                conditions.append(VideoSnapshot.created_at <= end)
            elif "start_date" in filters and "end_date" in filters:
                start = datetime.fromisoformat(filters["start_date"])
                end = datetime.fromisoformat(filters["end_date"])
                if "T" not in filters["start_date"]:
                    start, _ = _parse_date_to_datetime_range(filters["start_date"])
                if "T" not in filters["end_date"]:
                    _, end = _parse_date_to_datetime_range(filters["end_date"])
                conditions.append(VideoSnapshot.created_at >= start)
                conditions.append(VideoSnapshot.created_at <= end)

            if "creator_id" in filters:
                stmt = stmt.join(Video, Video.id == VideoSnapshot.video_id)
                conditions.append(Video.creator_id == filters["creator_id"])

            if conditions:
                stmt = stmt.where(and_(*conditions))
            result = await db.execute(stmt)
            return result.scalar_one()

        # Видео с новыми просмотрами (delta > 0)
        elif query_type == "videos_with_new_views_on_date":
            stmt = select(func.count(distinct(VideoSnapshot.video_id)))
            conditions = [
                VideoSnapshot.delta_views_count > 0
            ]

            if "date" in filters:
                start, end = _parse_date_to_datetime_range(filters["date"])
                conditions.append(VideoSnapshot.created_at >= start)
                conditions.append(VideoSnapshot.created_at <= end)
            elif "start_date" in filters and "end_date" in filters:
                start = datetime.fromisoformat(filters["start_date"])
                end = datetime.fromisoformat(filters["end_date"])
                if "T" not in filters["start_date"]:
                    start, _ = _parse_date_to_datetime_range(filters["start_date"])
                if "T" not in filters["end_date"]:
                    _, end = _parse_date_to_datetime_range(filters["end_date"])
                conditions.append(VideoSnapshot.created_at >= start)
                conditions.append(VideoSnapshot.created_at <= end)

            if "creator_id" in filters:
                stmt = stmt.join(Video, Video.id == VideoSnapshot.video_id)
                conditions.append(Video.creator_id == filters["creator_id"])

            stmt = stmt.where(and_(*conditions))
            result = await db.execute(stmt)
            return result.scalar_one()

        # Видео с просмотрами выше порога
        elif query_type == "videos_with_views_over":
            threshold = filters["threshold"]

            # Если есть временные фильтры — работаем через снапшоты
            if "date" in filters or "start_date" in filters:
                # Подзапрос: последний снапшот для каждого видео в указанный период
                snap_subq = select(
                    VideoSnapshot.video_id,
                    VideoSnapshot.views_count,
                    VideoSnapshot.created_at
                )

                if "date" in filters:
                    start, end = _parse_date_to_datetime_range(filters["date"])
                    snap_subq = snap_subq.where(
                        and_(
                            VideoSnapshot.created_at >= start,
                            VideoSnapshot.created_at <= end
                        )
                    )
                elif "start_date" in filters and "end_date" in filters:
                    start = datetime.fromisoformat(filters["start_date"])
                    end = datetime.fromisoformat(filters["end_date"])
                    if "T" not in filters["start_date"]:
                        start, _ = _parse_date_to_datetime_range(filters["start_date"])
                    if "T" not in filters["end_date"]:
                        _, end = _parse_date_to_datetime_range(filters["end_date"])
                    snap_subq = snap_subq.where(
                        and_(
                            VideoSnapshot.created_at >= start,
                            VideoSnapshot.created_at <= end
                        )
                    )

                # Берём последний снапшот на видео в периоде
                snap_subq = (
                    snap_subq.add_columns(
                        func.row_number().over(
                            partition_by=VideoSnapshot.video_id,
                            order_by=VideoSnapshot.created_at.desc()
                        ).label("rn")
                    )
                    .subquery()
                )

                stmt = select(func.count()).select_from(snap_subq).where(
                    and_(
                        snap_subq.c.rn == 1,
                        snap_subq.c.views_count > threshold
                    )
                )

                if "creator_id" in filters:
                    stmt = stmt.join(Video, Video.id == snap_subq.c.video_id)
                    stmt = stmt.where(Video.creator_id == filters["creator_id"])

                result = await db.execute(stmt)
                return result.scalar_one()

            # Если нет даты — используем основную таблицу videos
            else:
                stmt = select(func.count()).select_from(Video).where(
                    Video.views_count > threshold
                )
                if "creator_id" in filters:
                    stmt = stmt.where(Video.creator_id == filters["creator_id"])
                result = await db.execute(stmt)
                return result.scalar_one()

        else:
            logger.error(f"Неизвестный тип запроса: {query_type}")
            return f"Неизвестный тип запроса"
 

async def _send_promt_to_ai(user_query)->json:

    promt = """
    Твоя задача — извлечь из текста на русском языке параметры фильтрации и вернуть JSON.
    Возможные значения type:
    "total_videos" -creator_id-если указан id, date - если указана дата, (start_date, end_date) - если указан диапазон
    "videos_with_views_over" → требует threshold, date - если указана дата, (start_date, end_date) - если указан диапазон
    "total_views_growth_on_date" → creator_id - если указан id, date - если указана дата, (start_date, end_date) - если указан диапазон
    "videos_with_new_views_on_date" → требует date
    Используй только поля:    
    Все даты в filters — в формате YYYY-MM-DD (без времени)    
    Json должен быть валидный строго без ``` и дополнительного текста и символов.
    Ечсли запро не относится к запросам видео, то type=null
    Формат вывода {format_json}
    Теперь обработай этот запрос:{user_query}"""

    full_prompt = promt.format(format_json='без ``` {"type": "...", "filters": ... }',user_query=user_query) 

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

    return parsed_data
 
