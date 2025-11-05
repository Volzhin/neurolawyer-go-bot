"""Модели для payload вебхуков."""
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime

class ChatInfo(BaseModel):
    """Информация о чате."""
    chat_id: int
    type: str
    title: Optional[str] = None

class UserInfo(BaseModel):
    """Информация о пользователе."""
    user_id: int
    username: Optional[str] = None

class MessageInfo(BaseModel):
    """Информация о сообщении."""
    message_id: int
    date_ts: int
    media_group_id: Optional[str] = None

class Creative(BaseModel):
    """Креатив (файл или текст)."""
    type: str  # photo, video, document, text, audio, voice, sticker, animation
    caption: Optional[str] = None
    file_id: Optional[str] = None
    file_unique_id: Optional[str] = None
    file_name: Optional[str] = None
    mime_type: Optional[str] = None
    file_size: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    duration: Optional[int] = None
    is_animated: bool = False
    is_video: bool = False
    download_url: Optional[str] = None

class BatchInfo(BaseModel):
    """Информация о батче."""
    batch_id: str
    seq: int
    total: int
    grouping: str  # debounce, media_group

class WebhookPayload(BaseModel):
    """Payload для отправки на вебхук."""
    service: str
    source: str = "telegram"
    chat: ChatInfo
    from_: UserInfo = Field(alias="from")
    message: MessageInfo
    message_ids: List[int]
    creatives: List[Creative]
    download_urls: List[str]
    batch: BatchInfo
    placement: Optional[str] = None  # Место размещения креатива

    class Config:
        populate_by_name = True

class UrlsOnlyPayload(BaseModel):
    """Упрощенный payload только с URL."""
    service: str
    source: str = "telegram"
    download_urls: List[str]

class TextsPayload(BaseModel):
    """Payload для отправки массива текстов с контекстом чата."""
    service: str
    source: str = "telegram"
    texts: List[str]
    chat_id: int
    chat: ChatInfo
    from_: UserInfo = Field(alias="from")
    placement: Optional[str] = None  # Место размещения креатива

    class Config:
        populate_by_name = True
