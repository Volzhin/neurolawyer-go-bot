"""Сервис для работы с файлами Telegram."""
from typing import Optional, Dict, Any, List
from aiogram import Bot
from aiogram.types import Message, PhotoSize, Video, Document, Audio, Voice, Sticker, Animation
from app.utils.logging import get_logger
from app.models.payload import Creative

logger = get_logger(__name__)

class TelegramFileService:
    """Сервис для работы с файлами Telegram."""
    
    def __init__(self, bot: Bot):
        self.bot = bot
    
    async def get_file_url(self, file_id: str) -> Optional[str]:
        """Получить URL для скачивания файла."""
        try:
            file = await self.bot.get_file(file_id)
            return f"https://api.telegram.org/file/bot{self.bot.token}/{file.file_path}"
        except Exception as e:
            logger.error(f"❌ Ошибка получения URL файла {file_id}: {e}")
            return None
    
    async def extract_creative_from_message(self, message: Message) -> Optional[Creative]:
        """Извлечь креатив из сообщения."""
        creative_type = None
        file_id = None
        file_unique_id = None
        file_name = None
        mime_type = None
        file_size = None
        width = None
        height = None
        duration = None
        is_animated = False
        is_video = False
        
        # Определяем тип контента
        if message.photo:
            # Фото
            creative_type = "photo"
            # Берем фото наибольшего размера
            largest_photo = max(message.photo, key=lambda p: p.file_size or 0)
            file_id = largest_photo.file_id
            file_unique_id = largest_photo.file_unique_id
            file_size = largest_photo.file_size
            width = largest_photo.width
            height = largest_photo.height
            
        else:
            # Неподдерживаемый тип
            logger.warning(f"⚠️ Неподдерживаемый тип сообщения: {message.content_type}")
            return None
        
        # Получаем URL для скачивания (если есть файл)
        download_url = None
        if file_id:
            download_url = await self.get_file_url(file_id)
        
        return Creative(
            type=creative_type,
            caption=message.caption,
            file_id=file_id,
            file_unique_id=file_unique_id,
            file_name=file_name,
            mime_type=mime_type,
            file_size=file_size,
            width=width,
            height=height,
            duration=duration,
            is_animated=is_animated,
            is_video=is_video,
            download_url=download_url
        )
    
    async def extract_creatives_from_messages(self, messages: List[Message]) -> List[Creative]:
        """Извлечь креативы из списка сообщений."""
        creatives = []
        
        for message in messages:
            creative = await self.extract_creative_from_message(message)
            if creative:
                creatives.append(creative)
        
        return creatives
