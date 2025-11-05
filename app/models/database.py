"""Модели базы данных."""
from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, create_engine, Session, text
from app.utils.env import config
from app.utils.logging import get_logger

logger = get_logger(__name__)

class UserPrefs(SQLModel, table=True):
    """Предпочтения пользователя."""
    __tablename__ = "user_prefs"
    
    user_id: int = Field(primary_key=True)
    service: str = Field(default="drive")
    placement: Optional[str] = Field(default=None)  # Место размещения креатива
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
    # Миграция: добавляем колонку placement если её нет
    _migrate_add_placement_column()


def _migrate_add_placement_column():
    """Миграция: добавить колонку placement в таблицу user_prefs если её нет."""
    try:
        with get_session() as session:
            # Проверяем, существует ли колонка placement
            result = session.exec(
                text("PRAGMA table_info(user_prefs)")
            ).fetchall()
            
            # PRAGMA table_info возвращает список кортежей
            # Ищем колонку placement
            has_placement = any(
                row[1] == "placement" for row in result
            )
            
            if not has_placement:
                # Добавляем колонку
                session.exec(text("ALTER TABLE user_prefs ADD COLUMN placement TEXT"))
                session.commit()
                logger.info("✅ Миграция: добавлена колонка placement в user_prefs")
            else:
                logger.debug("✅ Колонка placement уже существует")
    except Exception as e:
        logger.warning(f"⚠️ Ошибка при миграции placement: {e}")
        # Игнорируем - возможно таблица ещё не создана

def get_session():
    """Получить сессию базы данных."""
    return Session(engine)
