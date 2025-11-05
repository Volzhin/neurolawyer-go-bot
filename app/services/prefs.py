"""Сервис для работы с предпочтениями пользователей."""
from typing import Optional
from sqlmodel import select
from app.models.database import UserPrefs, LastPayload, get_session
from app.utils.logging import get_logger

logger = get_logger(__name__)

class PreferencesService:
    """Сервис для работы с предпочтениями пользователей."""
    
    def get_user_service(self, user_id: int) -> str:
        """Получить выбранный сервис пользователя."""
        with get_session() as session:
            stmt = select(UserPrefs).where(UserPrefs.user_id == user_id)
            user_prefs = session.exec(stmt).first()
            
            if user_prefs:
                return user_prefs.service
            else:
                # Создаем запись с дефолтным сервисом
                from app.utils.env import config
                default_service = config.DEFAULT_SERVICE
                self.set_user_service(user_id, default_service)
                return default_service
    
    def set_user_service(self, user_id: int, service: str) -> None:
        """Установить сервис для пользователя."""
        with get_session() as session:
            stmt = select(UserPrefs).where(UserPrefs.user_id == user_id)
            user_prefs = session.exec(stmt).first()
            
            if user_prefs:
                user_prefs.service = service
            else:
                user_prefs = UserPrefs(user_id=user_id, service=service)
                session.add(user_prefs)
            
            session.commit()
            logger.info(f"✅ Сервис пользователя {user_id} изменен на {service}")
    
    def save_last_payload(self, user_id: int, json_payload: str) -> None:
        """Сохранить последний payload для retry."""
        with get_session() as session:
            stmt = select(LastPayload).where(LastPayload.user_id == user_id)
            last_payload = session.exec(stmt).first()
            
            if last_payload:
                last_payload.json_payload = json_payload
            else:
                last_payload = LastPayload(user_id=user_id, json_payload=json_payload)
                session.add(last_payload)
            
            session.commit()
            logger.info(f"✅ Payload пользователя {user_id} сохранен для retry")
    
    def get_last_payload(self, user_id: int) -> Optional[str]:
        """Получить последний payload пользователя."""
        with get_session() as session:
            stmt = select(LastPayload).where(LastPayload.user_id == user_id)
            last_payload = session.exec(stmt).first()
            
            if last_payload:
                return last_payload.json_payload
            return None
    
    def get_user_placement(self, user_id: int) -> Optional[str]:
        """Получить место размещения пользователя."""
        with get_session() as session:
            stmt = select(UserPrefs).where(UserPrefs.user_id == user_id)
            user_prefs = session.exec(stmt).first()
            
            if user_prefs:
                placement = user_prefs.placement
                logger.debug(f"📍 Placement пользователя {user_id}: {placement}")
                return placement
            logger.debug(f"📍 Placement пользователя {user_id}: не найдено (запись не существует)")
            return None
    
    def set_user_placement(self, user_id: int, placement: str) -> None:
        """Установить место размещения для пользователя."""
        from datetime import datetime
        with get_session() as session:
            stmt = select(UserPrefs).where(UserPrefs.user_id == user_id)
            user_prefs = session.exec(stmt).first()
            
            if user_prefs:
                user_prefs.placement = placement
                user_prefs.updated_at = datetime.utcnow()
            else:
                # Создаем запись с дефолтным сервисом
                from app.utils.env import config
                default_service = config.DEFAULT_SERVICE
                user_prefs = UserPrefs(user_id=user_id, service=default_service, placement=placement)
                session.add(user_prefs)
            
            session.commit()
            logger.info(f"✅ Место размещения пользователя {user_id} установлено: {placement}")