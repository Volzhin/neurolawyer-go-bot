"""Настройка логирования."""
import logging
import re
from typing import Any, Dict
from app.utils.env import config

class TokenMaskingFormatter(logging.Formatter):
    """Форматтер для маскировки токенов в логах."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Форматировать запись лога с маскировкой токенов."""
        msg = super().format(record)
        
        # Маскируем токен бота в URL
        token_pattern = r'bot[0-9]+:[A-Za-z0-9_-]+'
        msg = re.sub(token_pattern, 'bot***MASKED***', msg)
        
        return msg

def setup_logging() -> None:
    """Настроить логирование."""
    # Создаем форматтер
    formatter = TokenMaskingFormatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Настраиваем корневой логгер
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, config.LOG_LEVEL.upper()))
    
    # Удаляем существующие обработчики
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Создаем консольный обработчик
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Настраиваем логгеры для внешних библиотек
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("aiogram").setLevel(logging.INFO)

def get_logger(name: str) -> logging.Logger:
    """Получить логгер с указанным именем."""
    return logging.getLogger(name)
