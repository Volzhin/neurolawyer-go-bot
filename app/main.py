"""Основной файл приложения."""
import asyncio
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from aiogram.fsm.storage.memory import MemoryStorage
from app.utils.env import config
from app.utils.logging import setup_logging, get_logger
from app.handlers import commands_router, media_router
from app.models.database import create_tables

logger = get_logger(__name__)

async def main():
    """Основная функция."""
    # Настраиваем логирование
    setup_logging()
    
    # Проверяем конфигурацию
    try:
        config.validate()
    except ValueError as e:
        logger.error(f"❌ Ошибка конфигурации: {e}")
        sys.exit(1)
    
    # Создаем таблицы БД
    create_tables()
    logger.info("✅ База данных инициализирована")
    
    # Создаем бота
    bot = Bot(
        token=config.TELEGRAM_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
    )
    
    # Инициализируем сервис файлов
    from app.handlers.media import tg_files_service
    tg_files_service.bot = bot
    
    # Настраиваем команды бота
    commands = [
        BotCommand(command="start", description="🚀 Запустить бота"),
        BotCommand(command="help", description="ℹ️ Справка по боту"),
        BotCommand(command="service", description="🔧 Выбрать сервис"),
        BotCommand(command="status", description="🔍 Статус вебхука")
    ]
    await bot.set_my_commands(commands)
    logger.info("✅ Команды бота настроены")
    
    # Создаем диспетчер с хранилищем FSM
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Регистрируем обработчики
    dp.include_router(commands_router)
    dp.include_router(media_router)
    
    logger.info("🚀 Бот запущен")
    
    try:
        # Запускаем бота
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("⏹️ Получен сигнал остановки")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
    finally:
        await bot.session.close()
        logger.info("👋 Бот остановлен")

if __name__ == "__main__":
    asyncio.run(main())
