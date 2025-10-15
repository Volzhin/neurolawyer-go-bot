"""Конфигурация приложения."""
import os
from typing import List, Optional
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv("config.env")

class Config:
    """Конфигурация приложения."""
    
    # Telegram Bot
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    
    # Webhooks
    WEBHOOK_DRIVE: str = os.getenv("WEBHOOK_DRIVE", "")
    WEBHOOK_SAMOKATY: str = os.getenv("WEBHOOK_SAMOKATY", "")
    
    # Defaults
    DEFAULT_SERVICE: str = os.getenv("DEFAULT_SERVICE", "drive")
    
    # Admin users
    ADMIN_USER_IDS: List[int] = [
        int(user_id.strip()) 
        for user_id in os.getenv("ADMIN_USER_IDS", "").split(",") 
        if user_id.strip().isdigit()
    ]
    
    # HTTP settings
    HTTP_TIMEOUT_SECONDS: int = int(os.getenv("HTTP_TIMEOUT_SECONDS", "25"))
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Batching settings
    MAX_CREATIVES_PER_BATCH: int = int(os.getenv("MAX_CREATIVES_PER_BATCH", "10"))
    BURST_DEBOUNCE_SECS: float = float(os.getenv("BURST_DEBOUNCE_SECS", "2.0"))
    BURST_HARDCAP_SECS: float = float(os.getenv("BURST_HARDCAP_SECS", "3.5"))
    
    # Webhook mode
    WEBHOOK_MODE: str = os.getenv("WEBHOOK_MODE", "rich")
    
    @classmethod
    def get_webhook_url(cls, service: str) -> Optional[str]:
        """Получить URL вебхука для сервиса."""
        if service == "drive":
            return cls.WEBHOOK_DRIVE
        elif service == "samokaty":
            return cls.WEBHOOK_SAMOKATY
        return None
    
    @classmethod
    def validate(cls) -> bool:
        """Проверить корректность конфигурации."""
        if not cls.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN не установлен")
        if not cls.WEBHOOK_DRIVE:
            raise ValueError("WEBHOOK_DRIVE не установлен")
        if not cls.WEBHOOK_SAMOKATY:
            raise ValueError("WEBHOOK_SAMOKATY не установлен")
        return True

# Создаем глобальный экземпляр конфигурации
config = Config()
