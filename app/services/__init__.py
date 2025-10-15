"""Сервисы."""
from .webhook_client import WebhookClient
from .tg_files import TelegramFileService
from .prefs import PreferencesService

__all__ = ["WebhookClient", "TelegramFileService", "PreferencesService"]
