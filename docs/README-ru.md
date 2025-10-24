# OpenWeather App - Сервис погодных уведомлений

Сервис для мониторинга погоды с автоматическими уведомлениями через Telegram бота. 
Построен на FastAPI с использованием асинхронного подхода и Docker контейнеризации.

## 🔧 Основные компоненты

### 1. FastAPI Приложение (`app/main.py`)
- REST API для получения погодных данных
- Интеграция с OpenWeather API
- Асинхронная обработка запросов
- Кэширование погодных данных

### 2. Telegram Бот (`app/telegram_service.py`)
- Отправка регулярных уведомлений
- Команды для получения текущей погоды
- Система подписки на уведомления
- Автоматические оповещения о резких изменениях погоды

### 3. Планировщик (`src/scheduler.py`)
- Регулярные обновления погодных данных
- Отправка уведомлений по расписанию (8:00 и 21:30 МСК)
- Проверка пропущенных обновлений
- Обработка ошибок и повторные попытки

### 4. База данных (`app/database_service.py`)
- PostgreSQL/SQLite для хранения истории погоды
- Асинхронное взаимодействие через SQLAlchemy
- Миграции через Alembic
- Автоматическое сохранение погодных данных

## 📁 Структура проекта

```
OpenWeatherApp/
├── app/                    # Основное приложение
│   ├── main.py            # FastAPI приложение
│   ├── config.py          # Конфигурация приложения
│   ├── weather_service.py # Сервис работы с погодой
│   ├── telegram_service.py # Telegram бот
│   ├── database_service.py # Работа с базой данных
│   └── lifecycle.py       # Управление жизненным циклом
├── tests/                 # Структурированные тесты
│   ├── test_weather_service.py
│   ├── test_api.py
│   └── test_config.py
├── migrations/            # Миграции базы данных
│   ├── env.py
│   └── versions/
├── docs/                  # Документация
├── .github/workflows/     # GitHub Actions CI/CD
├── static/               # Статические файлы
├── templates/            # HTML шаблоны
├── logs/                 # Логи приложения
├── docker-compose.yml    # Docker конфигурация
├── Dockerfile           # Docker образ
├── requirements.txt     # Python зависимости
├── alembic.ini         # Конфигурация миграций
├── pytest.ini         # Конфигурация тестов
├── LICENSE             # MIT лицензия
├── CONTRIBUTING.md     # Руководство для разработчиков
└── EnvExample          # Пример переменных окружения
```

## 🛠 Технологии

- Python 3.11
- FastAPI (0.109.0)
- SQLAlchemy (2.0.25)
- python-telegram-bot (20.7)
- PostgreSQL/SQLite
- Docker & Docker Compose
- Uvicorn (0.27.0)
- Alembic (1.13.1)
- Pydantic (2.4.2)
- httpx (0.25.2+)

## 📋 Требования к системе

- Docker и Docker Compose
- Python 3.11+
- PostgreSQL (опционально, по умолчанию SQLite)
- Не менее 1GB RAM
- Стабильное интернет-соединение

## 🚀 Установка и запуск

1. Клонировать репозиторий:
```bash
git clone <repository-url>
cd OpenWeatherApp
```

2. Создать файл `.env` на основе примера:
```bash
cp EnvExample .env
```

Затем отредактировать `.env` файл со следующими параметрами:
```env
OPENWEATHER_API_KEY=your_api_key
TELEGRAM_BOT_TOKEN=your_bot_token
DATABASE_URL=postgresql://user:password@db:5432/weather_db  # Опционально для PostgreSQL
DEBUG=False
```

3. Запустить через Docker:
```bash
docker-compose up --build
```

4. Или локально:
```bash
# Создать виртуальное окружение:
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Установить зависимости:
pip install -r requirements.txt

# Запустить приложение:
python -m uvicorn src.main:app --reload --port 8083
```

## 📊 Мониторинг и логи

- Логи приложения: `/logs/app_*.log`
- Логи базы данных: `/logs/database.log`
- Логи планировщика: `/logs/scheduler.log`

## 🌐 API Endpoints

### GET /weather/{city}
- Получение текущей погоды для города
- Параметры: units (metric/imperial)

### GET /health
- Проверка состояния сервиса

### GET /cities
- Список отслеживаемых городов

## 🤖 Telegram команды

| Команда | Описание |
|---------|----------|
| `/start` | Начало работы с ботом |
| `/weather` | Текущая погода во всех городах |
| `/weather_city` | Погода в конкретном городе |
| `/subscribe` | Подписка на уведомления |
| `/unsubscribe` | Отписка от уведомлений |
| `/help` | Список команд |

## 👨‍💻 Разработка

### Настройка окружения разработки

1. Создать ветку для новой функциональности:
```bash
git checkout -b feature/name
```

2. Установить зависимости разработки:
```bash
pip install -r requirements.txt
```

### Тестирование

3. Запустить все тесты:
```bash
pytest
```

4. Запустить тесты с покрытием:
```bash
pytest --cov=app --cov-report=html
```

5. Запустить конкретные тесты:
```bash
pytest tests/test_weather_service.py
pytest tests/test_api.py
pytest tests/test_config.py
```

### Проверка качества кода

6. Проверить линтером:
```bash
flake8 .
```

7. Проверить безопасность:
```bash
bandit -r app/
safety check
```

### Работа с базой данных

8. Инициализировать миграции (если нужно):
```bash
python init_migrations.py
```

9. Создать новую миграцию:
```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
```

### CI/CD

Проект использует GitHub Actions для автоматического тестирования:
- Тесты запускаются на Python 3.11 и 3.12
- Проверка линтера и безопасности
- Сборка Docker образа
- Покрытие кода

## 🔍 Поддержка

- Мониторинг через `/health` endpoint
- Автоматический перезапуск при сбоях
- Ротация логов
- Резервное копирование базы данных

## 🔒 Безопасность

- Все токены и ключи в `.env` файле
- HTTPS для API запросов
- Ограничение доступа к API
- Защита от SQL-инъекций
- Валидация входных данных

## 📈 Масштабирование

- Горизонтальное масштабирование через Docker Swarm
- Кэширование погодных данных
- Очереди сообщений для уведомлений
- Балансировка нагрузки

## ⚠️ Известные ограничения

- Лимиты API OpenWeather
- Задержка обновления данных до 30 минут
- Ограничения Telegram API
- Зависимость от внешних сервисов

## 📚 Дополнительно

- [Документация API](http://localhost:8083/docs)
- [Метрики](http://localhost:8083/metrics)
- [Административная панель](http://localhost:8083/admin) 