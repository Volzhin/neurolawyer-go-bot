"""Обработчики команд."""
from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
from app.utils.logging import get_logger
from app.services.prefs import PreferencesService
from app.services.webhook_client import WebhookClient
from app.utils.env import config

logger = get_logger(__name__)
router = Router()

prefs_service = PreferencesService()
webhook_client = WebhookClient()

@router.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start."""
    user_id = message.from_user.id
    username = message.from_user.username or "пользователь"
    
    # Получаем текущий сервис
    current_service = prefs_service.get_user_service(user_id)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=f"🚗 Drive {'✅' if current_service == 'drive' else ''}",
                callback_data="service_drive"
            ),
            InlineKeyboardButton(
                text=f"🛵 Samokaty {'✅' if current_service == 'samokaty' else ''}",
                callback_data="service_samokaty"
            )
        ],
        [InlineKeyboardButton(text="ℹ️ Помощь", callback_data="help")]
    ])
    
    text = f"""👋 Привет, {username}!

Я бот для приёма рекламных креативов и пересылки их на вебхуки.

📋 Поддерживаемые типы:
• 📸 Фото (можно загружать несколько штук сразу)

🎯 Текущий сервис: {current_service.title()}

Выберите сервис или отправьте рекламный креатив!"""
    
    await message.answer(text, reply_markup=keyboard)
    logger.info(f"✅ Пользователь {user_id} ({username}) запустил бота")

@router.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help."""
    text = """ℹ️ Справка по боту

📋 Поддерживаемые типы рекламных креативов:
• 📸 Фото - любые изображения (можно загружать несколько штук сразу)

📦 Альбомы фото: Отправьте несколько фото подряд - они будут объединены в один пакет.

⚡ Burst-режим: Отправьте много файлов подряд - они будут автоматически разбиты на пакеты.

🔧 Команды:
• /start - начать работу
• /service - выбрать сервис
• /status - проверить статус вебхука
• /help - эта справка

Просто отправьте рекламный креатив, и я перешлю его на выбранный вебхук!"""
    
    await message.answer(text)
    logger.info(f"ℹ️ Пользователь {message.from_user.id} запросил справку")

@router.message(Command("service"))
async def cmd_service(message: Message):
    """Обработчик команды /service."""
    user_id = message.from_user.id
    current_service = prefs_service.get_user_service(user_id)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=f"🚗 Drive {'✅' if current_service == 'drive' else ''}",
                callback_data="service_drive"
            ),
            InlineKeyboardButton(
                text=f"🛵 Samokaty {'✅' if current_service == 'samokaty' else ''}",
                callback_data="service_samokaty"
            )
        ]
    ])
    
    text = f"""🔧 Выбор сервиса

Текущий сервис: {current_service.title()}

Выберите сервис для отправки креативов:
• 🚗 Drive - для файлов Drive
• 🛵 Samokaty - для файлов Samokaty"""
    
    await message.answer(text, reply_markup=keyboard)
    logger.info(f"🔧 Пользователь {user_id} запросил выбор сервиса")

@router.message(Command("status"))
async def cmd_status(message: Message):
    """Обработчик команды /status."""
    user_id = message.from_user.id
    current_service = prefs_service.get_user_service(user_id)
    
    webhook_url = config.get_webhook_url(current_service)
    if not webhook_url:
        await message.answer("❌ Не удалось определить URL вебхука")
        return
    
    await message.answer("🔄 Проверяю статус вебхука...")
    
    success = await webhook_client.send_ping(webhook_url)
    
    if success:
        await message.answer(f"✅ Вебхук {current_service.title()} работает корректно")
    else:
        await message.answer(f"❌ Проблемы с вебхуком {current_service.title()}")
    
    logger.info(f"🔍 Пользователь {user_id} проверил статус вебхука {current_service}")


@router.callback_query(F.data.startswith("service_"))
async def callback_service(callback: CallbackQuery):
    """Обработчик выбора сервиса."""
    user_id = callback.from_user.id
    service = callback.data.split("_")[1]
    
    prefs_service.set_user_service(user_id, service)
    
    await callback.message.edit_text(
        f"✅ Сервис изменен на **{service.title()}**\n\nТеперь все креативы будут отправляться на этот вебхук.",
        reply_markup=None
    )
    
    await callback.answer(f"Сервис изменен на {service.title()}")
    logger.info(f"✅ Пользователь {user_id} изменил сервис на {service}")

@router.callback_query(F.data == "help")
async def callback_help(callback: CallbackQuery):
    """Обработчик кнопки помощи."""
    await cmd_help(callback.message)
    await callback.answer()
