"""Модели базы данных."""
from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, create_engine, Session
from app.utils.env import config

class UserPrefs(SQLModel, table=True):
    """Предпочтения пользователя."""
    __tablename__ = "user_prefs"
    
    user_id: int = Field(primary_key=True)
    service: str = Field(default="drive")
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class LastPayload(SQLModel, table=True):
    """Последний payload для retry."""
    __tablename__ = "last_payload"
    
    user_id: int = Field(primary_key=True)
    json_payload: str = Field()  # JSON строка
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Создаем движок базы данных
engine = create_engine("sqlite:///bot.db", echo=False)

def create_tables():
    """Создать таблицы в базе данных."""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Получить сессию базы данных."""
    return Session(engine)
