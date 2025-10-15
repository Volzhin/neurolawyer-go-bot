# 🚀 Быстрый старт

## 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

## 2. Настройка конфигурации

```bash
cp config.env.example config.env
# Отредактируйте config.env с вашими настройками
```

## 3. Запуск

```bash
python run.py
# или
python -m app.main
```

## 4. Docker

```bash
docker-compose up -d
```

## 5. Тестирование

```bash
python -m pytest tests/
```

## 📋 Обязательные настройки

В файле `config.env` обязательно укажите:

- `TELEGRAM_BOT_TOKEN` - токен вашего бота
- `WEBHOOK_DRIVE` - URL вебхука для Drive  
- `WEBHOOK_SAMOKATY` - URL вебхука для Samokaty

## 🤖 Команды бота

- `/start` - начать работу
- `/help` - справка
- `/service` - выбрать сервис
- `/status` - проверить статус
- `/retry` - повторить отправку

## 📊 Поддерживаемые типы

Рекламные креативы: фото (можно несколько сразу), видео, GIF, документы.
