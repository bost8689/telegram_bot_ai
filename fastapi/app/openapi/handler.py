from app.core.config import settings
from openai import AsyncOpenAI
import json
from app.core.logging import get_logger
logger = get_logger("openai_handler")

import json
import re

async def send_promt_to_ai(user_query):

    promt = """
    Ты — строгий парсер запросов на русском языке. Твоя задача — извлечь из текста параметры фильтрации и вернуть ТОЛЬКО валидный JSON без каких-либо пояснений, markdown или дополнительного текста.
    Доступные поля:
    - date_from: дата начала в формате "YYYY-MM-DD" (если упомянута)
    - date_to: дата окончания в формате "YYYY-MM-DD" (если упомянута)
    - id: целое число (если указано), иначе null

    Примеры:
    Ввод: "Заказы за январь 2025"
    Вывод: {{"date_from": "2025-01-01", "date_to": "2025-01-31", "id": null}}

    Ввод: "Покажи заказ №123"
    Вывод: {{"date_from": null, "date_to": null, "id": 123}}

    Ввод: "С 5 по 10 февраля"
    Вывод: {{"date_from": "2025-02-05", "date_to": "2025-02-10", "id": null}}

    Текущий год: 2025.

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
    logger.info(f"Ответ от AI",data=data,parsed_data=parsed_data)
    return parsed_data