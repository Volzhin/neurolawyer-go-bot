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

# Память: последнее информационное сообщение бота на пользователя
last_info_message_id: dict[int, int] = {}


def get_service_menu() -> InlineKeyboardMarkup:
    """Создать меню выбора сервиса."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🚗 Drive", callback_data="service_drive"),
            InlineKeyboardButton(text="🛵 Samokaty", callback_data="service_samokaty")
        ]
    ])


def build_full_instructions(current_service: str) -> str:
    """Сформировать полные инструкции по всем форматам."""
    return f"""✅ Сервис: {current_service.title()}\n\nКак пользоваться:\n1) Выберите сервис (Drive или Samokaty) — и просто отправляйте материалы. Бот сам определит тип и отправит на нужный вебхук.\n\nПоддерживаемые форматы:\n• 📸 Фото (одиночные и альбомы) — объединяются и батчатся\n• 📝 Тексты (многострочные) — каждая непустая строка как отдельный текст\n• 📊 Excel (.xlsx) — все непустые ячейки со всех листов, первая строка игнорируется\n\nПодсказки:\n• Чтобы сменить сервис: /service\n• Проверить статус вебхука: /status\n"""


async def send_instruction(message: Message, text: str, reply_markup: InlineKeyboardMarkup | None = None) -> None:
    """Обновить предыдущее инфо-сообщение, а при отсутствии — отправить новое.
    Это устраняет дублирование длинных инструкций в чате.
    """
    user_id = message.from_user.id
    old_id = last_info_message_id.get(user_id)
    # Пытаемся отредактировать предыдущее сообщение
    if old_id:
        try:
            await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=old_id,
                text=text,
                reply_markup=reply_markup
            )
            return
        except Exception:
            # Если редактирование не удалось (удалено/устарело) — пошлём новое
            try:
                await message.bot.delete_message(chat_id=message.chat.id, message_id=old_id)
            except Exception:
                pass
    sent = await message.answer(text, reply_markup=reply_markup)
    last_info_message_id[user_id] = sent.message_id


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start."""
    user_id = message.from_user.id
    username = message.from_user.username or "пользователь"
    
    # Получаем текущий сервис
    current_service = prefs_service.get_user_service(user_id)
    
    greeting = f"👋 Привет, {username}!\n\nЯ помогу проверить и переслать материалы на выбранный сервис."
    await send_instruction(message, greeting + "\n\n" + build_full_instructions(current_service))
    logger.info(f"✅ Пользователь {user_id} ({username}) запустил бота")


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help."""
    text = """ℹ️ Справка по боту

📋 Поддерживаемые форматы:
• 📸 Фото (в т.ч. альбомы)
• 📝 Тексты (многострочные) и Excel (.xlsx)

📦 Альбомы фото: отправьте несколько фото подряд — будут объединены в один пакет.
⚡ Burst-режим: при потоке одиночных фото — авто-батчинг.

📝 Тексты:
• Введите несколько строк — каждая строка будет отправлена как отдельный текст
• Прикрепите .xlsx — возьмём все непустые ячейки, кроме первой строки (заголовка)

🔧 Команды:
• /start — начать работу
• /service — выбрать сервис (Drive/Samokaty)
• /text — инструкция по текстам
• /status — проверить статус вебхука
• /help — эта справка
"""
    
    await send_instruction(message, text)
    logger.info(f"ℹ️ Пользователь {message.from_user.id} запросил справку")


@router.message(Command("text"))
async def cmd_text(message: Message):
    """Инструкция по работе с текстами и Excel."""
    current_service = prefs_service.get_user_service(message.from_user.id)
    text = f"""📝 Инструкция по текстам

Текущий сервис: {current_service.title()}

• Отправьте многострочный текст — каждая непустая строка уйдёт как отдельный текст
• Пришлите Excel (.xlsx) — соберём все непустые ячейки по всем листам, игнорируя первую строку

Для текста и Excel используются специальные вебхуки сервиса.
Вы можете поменять сервис командой /service.
"""
    await send_instruction(message, text)
    logger.info(f"📝 Пользователь {message.from_user.id} открыл инструкцию по текстам")


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
    
    intro = f"🔧 Выбор сервиса\n\nТекущий сервис: {current_service.title()}\n\n" + build_full_instructions(current_service)
    await send_instruction(message, intro, reply_markup=keyboard)
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
        f"✅ Сервис изменен на **{service.title()}**\n\n" + build_full_instructions(service),
        reply_markup=None
    )
    
    await callback.answer(f"Сервис изменен на {service.title()}")
    logger.info(f"✅ Пользователь {user_id} изменил сервис на {service}")


@router.callback_query(F.data == "help")
async def callback_help(callback: CallbackQuery):
    """Обработчик кнопки помощи."""
    await cmd_help(callback.message)
    await callback.answer()

