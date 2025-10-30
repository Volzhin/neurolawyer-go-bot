"""Клиент для отправки данных на вебхуки."""
import asyncio
import json
import uuid
from typing import Optional, Dict, Any
import httpx
from app.utils.env import config
from app.utils.logging import get_logger
from app.models.payload import WebhookPayload, UrlsOnlyPayload, TextsPayload

logger = get_logger(__name__)

class WebhookClient:
    """Клиент для отправки данных на вебхуки."""
    
    def __init__(self):
        self.timeout = httpx.Timeout(config.HTTP_TIMEOUT_SECONDS)
        self.max_retries = config.MAX_RETRIES
        self.retry_backoff = 2  # Фиксированная задержка в 2 секунды
    
    async def send_payload(
        self, 
        payload: WebhookPayload, 
        webhook_url: str,
        idempotency_key: Optional[str] = None
    ) -> bool:
        """Отправить payload на вебхук."""
        if config.WEBHOOK_MODE == "urls_only":
            # Отправляем только URLs
            urls_payload = UrlsOnlyPayload(
                service=payload.service,
                download_urls=payload.download_urls
            )
            data = urls_payload.model_dump()
        else:
            # Отправляем полный payload
            data = payload.model_dump(by_alias=True)
        
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "TelegramBot/1.0"
        }
        
        if idempotency_key:
            headers["X-Idempotency-Key"] = idempotency_key
        
        for attempt in range(self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        webhook_url,
                        json=data,
                        headers=headers
                    )
                    
                    if response.status_code == 200:
                        logger.info(f"✅ Payload успешно отправлен на {webhook_url}")
                        return True
                    else:
                        logger.warning(
                            f"⚠️ Неожиданный статус {response.status_code} от {webhook_url}: {response.text}"
                        )
                        
            except httpx.TimeoutException:
                logger.warning(f"⏰ Таймаут при отправке на {webhook_url} (попытка {attempt + 1})")
            except httpx.RequestError as e:
                logger.error(f"❌ Ошибка запроса к {webhook_url}: {e}")
            except Exception as e:
                logger.error(f"❌ Неожиданная ошибка при отправке на {webhook_url}: {e}")
            
            if attempt < self.max_retries:
                wait_time = self.retry_backoff * (2 ** attempt)
                logger.info(f"⏳ Повторная попытка через {wait_time}с...")
                await asyncio.sleep(wait_time)
        
        logger.error(f"❌ Не удалось отправить payload на {webhook_url} после {self.max_retries + 1} попыток")
        return False
    
    async def send_ping(self, webhook_url: str) -> bool:
        """Отправить ping на вебхук."""
        ping_data = {"ping": "ok"}
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    webhook_url,
                    json=ping_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    logger.info(f"✅ Ping успешно отправлен на {webhook_url}")
                    return True
                else:
                    logger.warning(f"⚠️ Ping вернул статус {response.status_code}: {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Ошибка при отправке ping на {webhook_url}: {e}")
            return False
    
    def generate_idempotency_key(self, batch_id: str, seq: int) -> str:
        """Сгенерировать ключ идемпотентности."""
        return f"{batch_id}.{seq}"

    async def send_texts(
        self,
        texts: list[str],
        webhook_url: str,
        service: str,
        idempotency_key: Optional[str] = None
    ) -> bool:
        """Отправить массив текстов на вебхук."""
        payload = TextsPayload(service=service, texts=texts)
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "TelegramBot/1.0"
        }
        if idempotency_key:
            headers["X-Idempotency-Key"] = idempotency_key
        for attempt in range(self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        webhook_url,
                        json=payload.model_dump(),
                        headers=headers
                    )
                    if response.status_code == 200:
                        logger.info(f"✅ Тексты успешно отправлены на {webhook_url}")
                        return True
                    else:
                        logger.warning(
                            f"⚠️ Неожиданный статус {response.status_code} от {webhook_url}: {response.text}"
                        )
            except httpx.TimeoutException:
                logger.warning(f"⏰ Таймаут при отправке на {webhook_url} (попытка {attempt + 1})")
            except httpx.RequestError as e:
                logger.error(f"❌ Ошибка запроса к {webhook_url}: {e}")
            except Exception as e:
                logger.error(f"❌ Неожиданная ошибка при отправке на {webhook_url}: {e}")
            if attempt < self.max_retries:
                wait_time = self.retry_backoff * (2 ** attempt)
                logger.info(f"⏳ Повторная попытка через {wait_time}с...")
                await asyncio.sleep(wait_time)
        logger.error(f"❌ Не удалось отправить тексты на {webhook_url} после {self.max_retries + 1} попыток")
        return False
