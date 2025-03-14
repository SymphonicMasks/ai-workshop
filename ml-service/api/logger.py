from aiologger import Logger
from aiologger.formatters.base import Formatter
from aiologger.handlers.files import AsyncFileHandler
from aiologger.levels import LogLevel

async def setup_logger():
    logger = Logger(name="api_logger")
    formatter = Formatter(
        fmt="{asctime} | {name} | {levelname} | {message}",
        datefmt="%Y-%m-%d %H:%M:%S",
        style="{",
    )
    
    # Только файловый асинхронный хендлер
    file_handler = AsyncFileHandler(
        filename="logs/api.log",
        mode="a",
        encoding="utf-8",
    )
    file_handler.formatter = formatter
    logger.add_handler(file_handler)

    # Отключаем консольный вывод через StreamHandler
    logger.level = LogLevel.INFO
    return logger