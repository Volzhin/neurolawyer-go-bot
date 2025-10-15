"""Обработчики."""
from .commands import router as commands_router
from .media import router as media_router

__all__ = ["commands_router", "media_router"]
