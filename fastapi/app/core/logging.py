# logging_config.py
# Конфигурация структурированного логирования для FastAPI-приложения.
# Использует structlog для гибкого, типизированного и машиночитаемого логирования.
# Поддерживает вывод в консоль и в файл с автоматической ротацией.

import sys
import os
import logging
import structlog
from logging.handlers import RotatingFileHandler
import json
from pathlib import Path
def custom_renderer(logger, name, event_dict):
    # Формат: [logger] event (key=value ...)
    pairs = " ".join(f"{k}={v!r}" for k, v in event_dict.items() if k not in ("logger", "level", "timestamp", "event"))
    return f"[{event_dict.get('logger', 'app')}] {event_dict['event']} {pairs}".rstrip()


def ordered_event_first_processor(_, __, event_dict):
    # Извлекаем event
    event = event_dict.pop("event", None)
    # Создаём новый словарь с event в начале
    ordered = {}
    if event is not None:
        ordered["event"] = event
    # Добавляем остальное
    ordered.update(event_dict)
    return ordered

def get_logger(
    name: str = "app",
    json_logs: bool = True,
    log_level: str = "INFO",
    log_to_file: bool = True,
    log_dir: str = "logs",
    max_bytes: int = 10 * 1024 * 1024,  # Макс. размер одного лог-файла — 10 МБ
    backup_count: int = 5,              # Количество архивных файлов для хранения
):
    """
    Настраивает централизованное логирование для всего приложения.
    
    Параметры:
        json_logs (bool): 
            True — логи в JSON (рекомендуется для production),
            False — читаемый формат (удобно при разработке).
        log_level (str): 
            Уровень логирования: DEBUG, INFO, WARNING, ERROR.
        log_to_file (bool): 
            Записывать ли логи в файл (в дополнение к консоли).
        log_dir (str): 
            Директория для хранения лог-файлов.
        max_bytes (int): 
            Максимальный размер одного файла до ротации.
        backup_count (int): 
            Сколько архивных файлов хранить (например, app.log.1, app.log.2, ...).
    """

    os.makedirs(log_dir, exist_ok=True)

    log_level = getattr(logging, log_level.upper())
    root_logger = logging.getLogger(name)

    if root_logger.handlers:
        return structlog.get_logger(name)

    root_logger.setLevel(log_level)
    root_logger.handlers.clear()

    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    if json_logs:
        renderer = structlog.processors.JSONRenderer(
            serializer=lambda data, **kw: json.dumps(
                data, ensure_ascii=False, separators=(",", ":"), **kw
            )
        )
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    formatter = structlog.stdlib.ProcessorFormatter(
        processor=renderer,
        foreign_pre_chain=shared_processors,
    )


    if log_to_file:
        file_handler = RotatingFileHandler(
            filename=os.path.join(log_dir, f"{name}.log"),
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)


    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    structlog.configure(
        processors=[
            *shared_processors,
            # Затем — ваш кастомный процессор для порядка
            ordered_event_first_processor,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    return structlog.get_logger(name)
