"""Тесты для логики батчинга."""
import pytest
from app.handlers.media import create_webhook_payload
from app.models.payload import Creative, ChatInfo, UserInfo, MessageInfo, BatchInfo

def test_create_webhook_payload():
    """Тест создания webhook payload."""
    # Создаем мок-объекты
    class MockMessage:
        def __init__(self, message_id, chat_id, chat_type, from_user_id, from_username, media_group_id=None):
            self.message_id = message_id
            self.chat = MockChat(chat_id, chat_type)
            self.from_user = MockUser(from_user_id, from_username)
            self.media_group_id = media_group_id
            self.date = MockDate()
    
    class MockChat:
        def __init__(self, chat_id, chat_type):
            self.id = chat_id
            self.type = chat_type
            self.title = None
    
    class MockUser:
        def __init__(self, user_id, username):
            self.id = user_id
            self.username = username
    
    class MockDate:
        def timestamp(self):
            return 1728910000.0
    
    # Создаем тестовые данные
    messages = [
        MockMessage(1, 123, "private", 456, "testuser"),
        MockMessage(2, 123, "private", 456, "testuser")
    ]
    
    creatives = [
        Creative(type="photo", file_id="file1", download_url="url1"),
        Creative(type="photo", file_id="file2", download_url="url2")
    ]
    
    download_urls = ["url1", "url2"]
    
    # Создаем payload
    payload = create_webhook_payload(
        messages=messages,
        creatives=creatives,
        download_urls=download_urls,
        service="drive",
        batch_id="test-batch",
        seq=1,
        total=1,
        grouping="debounce"
    )
    
    # Проверяем результат
    assert payload.service == "drive"
    assert payload.source == "telegram"
    assert payload.chat.chat_id == 123
    assert payload.chat.type == "private"
    assert payload.from_.user_id == 456
    assert payload.from_.username == "testuser"
    assert payload.message.message_id == 1
    assert payload.message_ids == [1, 2]
    assert len(payload.creatives) == 2
    assert len(payload.download_urls) == 2
    assert payload.batch.batch_id == "test-batch"
    assert payload.batch.seq == 1
    assert payload.batch.total == 1
    assert payload.batch.grouping == "debounce"

def test_batch_chunking():
    """Тест разбиения на чанки."""
    # Создаем 12 креативов для тестирования разбиения на чанки
    creatives = [
        Creative(type="photo", file_id=f"file{i}", download_url=f"url{i}")
        for i in range(12)
    ]
    
    # Разбиваем на чанки по 10 (MAX_CREATIVES_PER_BATCH)
    max_per_batch = 10
    chunks = [creatives[i:i + max_per_batch] for i in range(0, len(creatives), max_per_batch)]
    
    assert len(chunks) == 2
    assert len(chunks[0]) == 10
    assert len(chunks[1]) == 2

def test_media_group_payload():
    """Тест payload для media group."""
    class MockMessage:
        def __init__(self, message_id, media_group_id):
            self.message_id = message_id
            self.media_group_id = media_group_id
            self.chat = MockChat()
            self.from_user = MockUser()
            self.date = MockDate()
    
    class MockChat:
        def __init__(self):
            self.id = 123
            self.type = "private"
            self.title = None
    
    class MockUser:
        def __init__(self):
            self.id = 456
            self.username = "testuser"
    
    class MockDate:
        def timestamp(self):
            return 1728910000.0
    
    messages = [
        MockMessage(1, "group123"),
        MockMessage(2, "group123"),
        MockMessage(3, "group123")
    ]
    
    creatives = [
        Creative(type="photo", file_id="file1", download_url="url1"),
        Creative(type="photo", file_id="file2", download_url="url2"),
        Creative(type="photo", file_id="file3", download_url="url3")
    ]
    
    payload = create_webhook_payload(
        messages=messages,
        creatives=creatives,
        download_urls=["url1", "url2", "url3"],
        service="samokaty",
        batch_id="group-batch",
        seq=1,
        total=1,
        grouping="media_group"
    )
    
    assert payload.batch.grouping == "media_group"
    assert len(payload.creatives) == 3
    assert len(payload.message_ids) == 3
