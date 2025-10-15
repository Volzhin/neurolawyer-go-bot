# Telegram Bot для приёма креативов

Production-готовый Telegram-бот для приёма креативов и пересылки их на вебхуки с поддержкой альбомов, burst-режима и автоматического батчинга.

## 🚀 Возможности

- **Поддержка рекламных креативов**: фото, видео, GIF/анимации, документы
- **Альбомы фото**: автоматическое объединение нескольких фото в один пакет
- **Burst-режим**: обработка множественных файлов с автоматическим батчингом
- **Выбор сервиса**: переключение между Drive и Samokaty
- **Структурированные логи**: с маскировкой токенов
- **Docker поддержка**: готов к деплою на Railway

## 📋 Поддерживаемые типы рекламных креативов

- 📸 **Фото** - любые изображения (можно загружать несколько штук сразу)
- 🎥 **Видео** - MP4, MOV и другие форматы  
- 🎬 **GIF/анимации** - анимированные изображения
- 📄 **Документы** - PDF, PSD, AI, ZIP и другие

## 🛠 Установка и запуск

### Локальный запуск

1. **Клонируйте репозиторий:**
```bash
git clone <repository-url>
cd neurolawyer_go_bot
```

2. **Установите зависимости:**
```bash
pip install -r requirements.txt
```

3. **Настройте конфигурацию:**
```bash
cp config.env.example config.env
# Отредактируйте config.env с вашими настройками
```

4. **Запустите бота:**
```bash
python -m app.main
```

### Docker

1. **Соберите образ:**
```bash
docker build -t neurolawyer-go-bot .
```

2. **Запустите контейнер:**
```bash
docker run -d --name neurolawyer-go-bot --env-file config.env neurolawyer-go-bot
```

### Docker Compose

```bash
docker-compose up -d
```

## 🚀 Deploy to Railway

1. **Подключите репозиторий к Railway:**
   - Зайдите на [Railway](https://railway.app)
   - Создайте новый проект
   - Подключите GitHub репозиторий

2. **Настройте переменные окружения:**
   - `TELEGRAM_BOT_TOKEN` - токен вашего бота
   - `WEBHOOK_DRIVE` - URL вебхука для Drive
   - `WEBHOOK_SAMOKATY` - URL вебхука для Samokaty
   - Остальные переменные (опционально)

3. **Деплой:**
   - Railway автоматически соберет Dockerfile
   - Бот запустится с помощью Procfile

## ⚙️ Конфигурация

### Переменные окружения

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `TELEGRAM_BOT_TOKEN` | Токен Telegram бота | - |
| `WEBHOOK_DRIVE` | URL вебхука для Drive | - |
| `WEBHOOK_SAMOKATY` | URL вебхука для Samokaty | - |
| `DEFAULT_SERVICE` | Сервис по умолчанию | `drive` |
| `ADMIN_USER_IDS` | ID администраторов (через запятую) | - |
| `HTTP_TIMEOUT_SECONDS` | Таймаут HTTP запросов | `25` |
| `MAX_RETRIES` | Максимум повторов | `3` |
| `LOG_LEVEL` | Уровень логирования | `INFO` |
| `MAX_CREATIVES_PER_BATCH` | Максимум креативов в пакете | `10` |
| `BURST_DEBOUNCE_SECS` | Время ожидания для burst | `2.0` |
| `BURST_HARDCAP_SECS` | Максимальное время burst | `3.5` |
| `WEBHOOK_MODE` | Режим вебхука (`rich`/`urls_only`) | `rich` |

## 🤖 Команды бота

- `/start` - начать работу и выбрать сервис
- `/help` - справка по поддерживаемым типам
- `/service` - выбрать сервис (Drive/Samokaty)
- `/status` - проверить статус вебхука

## 📊 Формат данных

### Полный payload (WEBHOOK_MODE=rich)

```json
{
  "service": "drive",
  "source": "telegram",
  "chat": {
    "chat_id": 123,
    "type": "private",
    "title": null
  },
  "from": {
    "user_id": 456,
    "username": "nick"
  },
  "message": {
    "message_id": 789,
    "date_ts": 1728910000,
    "media_group_id": null
  },
  "message_ids": [789, 790],
  "creatives": [
    {
      "type": "photo",
      "caption": "подпись",
      "file_id": "...",
      "file_unique_id": "...",
      "file_name": "optional",
      "mime_type": "optional",
      "file_size": 1234,
      "width": 1080,
      "height": 1350,
      "duration": 12,
      "is_animated": false,
      "is_video": false,
      "download_url": "https://api.telegram.org/file/bot<token>/<file_path>"
    }
  ],
  "download_urls": [
    "https://api.telegram.org/file/bot<token>/<file_path1>",
    "https://api.telegram.org/file/bot<token>/<file_path2>"
  ],
  "batch": {
    "batch_id": "uuid-v4",
    "seq": 1,
    "total": 2,
    "grouping": "debounce"
  }
}
```

### Упрощенный payload (WEBHOOK_MODE=urls_only)

```json
{
  "service": "drive",
  "source": "telegram",
  "download_urls": [
    "https://api.telegram.org/file/bot<token>/<file_path1>",
    "https://api.telegram.org/file/bot<token>/<file_path2>"
  ]
}
```

## 🧪 Тестирование

```bash
# Запуск тестов
python -m pytest tests/

# Запуск с покрытием
python -m pytest tests/ --cov=app
```

## 📁 Структура проекта

```
app/
├── handlers/          # Обработчики команд и медиа
│   ├── commands.py    # Команды бота
│   └── media.py       # Обработка медиа
├── services/          # Бизнес-логика
│   ├── webhook_client.py  # Отправка на вебхуки
│   ├── tg_files.py        # Работа с файлами Telegram
│   └── prefs.py           # Предпочтения пользователей
├── models/            # Модели данных
│   ├── payload.py     # Модели payload
│   └── database.py    # Модели БД
├── utils/             # Утилиты
│   ├── env.py         # Конфигурация
│   └── logging.py     # Логирование
└── main.py           # Точка входа
```

## 🔧 Разработка

### Установка для разработки

```bash
# Создайте виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows

# Установите зависимости
pip install -r requirements.txt

# Установите dev зависимости
pip install pytest pytest-cov
```

### Линтинг

```bash
# Проверка типов
mypy app/

# Форматирование кода
black app/

# Проверка стиля
flake8 app/
```

## 📝 Логирование

Бот использует структурированное логирование с автоматической маскировкой токенов в URL. Все логи выводятся в консоль в формате:

```
2024-01-15 10:30:45 - app.handlers.commands - INFO - ✅ Пользователь 123456 запустил бота
```

## 🚨 Безопасность

- Токены автоматически маскируются в логах
- Использование non-root пользователя в Docker
- Валидация всех входящих данных
- Ограничение размера файлов через Telegram API

## 📄 Лицензия

MIT License

## 🤝 Поддержка

При возникновении проблем:
1. Проверьте логи бота
2. Убедитесь в корректности конфигурации
3. Проверьте доступность вебхуков
4. Создайте issue в репозитории
