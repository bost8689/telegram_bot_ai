# python3 app/bot/runner.py

import os
import sys
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from app.core.config import settings
from app.openapi.handler import get_data_from_user_query

from app.core.logging import get_logger
logger = get_logger("bot_runner")

BOT_TOKEN = settings.TG_BOT_TOKEN
if not BOT_TOKEN:
    raise ValueError("NOT FOUND TG_BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Обработчики событий
@dp.message(Command("start"))
async def on_start(message: types.Message):
    logger.info(f"User {message.from_user.id} (@{message.from_user.username}) sent /start")
    await message.answer("Привет! Я готов ответить на твои запросы по Видео.")

@dp.message()
async def on_any_message(message: types.Message):
    user = message.from_user
    text = message.text or message.caption or "non-text content"
    logger.info(f"New event from {user.id} (@{user.username}): {text!r}")   
    
    result = await get_data_from_user_query(text)
    logger.info(f"Результат AI",result=result)
    
    try:        
        await message.answer(str(result))
    except Exception as e:
        logger.error(f"Не удалось отправить сообщение: {e}")
        await message.answer("Произошла ошибка при обработке запроса.")

@dp.error()
async def on_error(event: types.ErrorEvent, exception: Exception):
    logger.error(f"Telegram error: {exception} | Update: {event.update}")

# Функция запуска бота
async def start_polling_with_restart():
    """
    Запускает бота в режиме polling с автоматическим перезапуском при ошибках.
    """
    while True:
        try:
            # Удаляем webhook и сбрасываем очередь
            await bot.delete_webhook(drop_pending_updates=True)            
            # Запускаем polling
            logger.info("Запуск polling...")
            await dp.start_polling(bot)

        except Exception as e:
            logger.error(f"Неизвестная ошибка: {e}. Перезапуск через 15 секунд...")
            await asyncio.sleep(15)

        finally:        
            pass

if __name__ == '__main__':
    asyncio.run(start_polling_with_restart())