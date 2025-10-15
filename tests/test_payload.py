"""Тесты для генерации payload."""
import pytest
from datetime import datetime
from app.models.payload import Creative, WebhookPayload, ChatInfo, UserInfo, MessageInfo, BatchInfo

def test_creative_photo():
    """Тест создания креатива из фото."""
    creative = Creative(
        type="photo",
        caption="Тестовое фото",
        file_id="BAADBAADrwADBREAAYag8mZBqjQBAg",
        file_unique_id="AgADrwADBREAAYag",
        file_size=12345,
        width=1080,
        height=1350,
        download_url="https://api.telegram.org/file/bot***MASKED***/photos/file_123.jpg"
    )
    
    assert creative.type == "photo"
    assert creative.caption == "Тестовое фото"
    assert creative.file_id == "BAADBAADrwADBREAAYag8mZBqjQBAg"
    assert creative.width == 1080
    assert creative.height == 1350

def test_creative_document():
    """Тест создания креатива из документа."""
    creative = Creative(
        type="document",
        file_id="BAADBAADrwADBREAAYag8mZBqjQBAg",
        file_name="test.pdf",
        mime_type="application/pdf",
        file_size=54321
    )
    
    assert creative.type == "document"
    assert creative.file_name == "test.pdf"
    assert creative.mime_type == "application/pdf"

def test_creative_text():
    """Тест создания креатива из текста."""
    creative = Creative(
        type="text",
        caption="Тестовое текстовое сообщение"
    )
    
    assert creative.type == "text"
    assert creative.caption == "Тестовое текстовое сообщение"
    assert creative.file_id is None

def test_webhook_payload():
    """Тест создания webhook payload."""
    chat_info = ChatInfo(chat_id=123, type="private", title=None)
    user_info = UserInfo(user_id=456, username="testuser")
    message_info = MessageInfo(message_id=789, date_ts=1728910000, media_group_id=None)
    
    creative = Creative(
        type="photo",
        file_id="BAADBAADrwADBREAAYag8mZBqjQBAg",
        download_url="https://api.telegram.org/file/bot***MASKED***/photos/file_123.jpg"
    )
    
    batch_info = BatchInfo(
        batch_id="test-batch-id",
        seq=1,
        total=1,
        grouping="debounce"
    )
    
    payload = WebhookPayload(
        service="drive",
        chat=chat_info,
        from_=user_info,
        message=message_info,
        message_ids=[789],
        creatives=[creative],
        download_urls=["https://api.telegram.org/file/bot***MASKED***/photos/file_123.jpg"],
        batch=batch_info
    )
    
    assert payload.service == "drive"
    assert payload.source == "telegram"
    assert payload.chat.chat_id == 123
    assert payload.from_.user_id == 456
    assert len(payload.creatives) == 1
    assert len(payload.download_urls) == 1

def test_batch_info():
    """Тест создания batch info."""
    batch_info = BatchInfo(
        batch_id="test-batch-123",
        seq=2,
        total=3,
        grouping="media_group"
    )
    
    assert batch_info.batch_id == "test-batch-123"
    assert batch_info.seq == 2
    assert batch_info.total == 3
    assert batch_info.grouping == "media_group"
