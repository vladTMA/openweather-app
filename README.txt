OpenWeather App - Сервис погодных уведомлений

ОПИСАНИЕ ПРОЕКТА
---------------
Сервис для мониторинга погоды с автоматическими уведомлениями через Telegram бота. 
Построен на FastAPI с использованием асинхронного подхода и Docker контейнеризации.

ОСНОВНЫЕ КОМПОНЕНТЫ
------------------
1. FastAPI Приложение (app/main.py)
   - REST API для получения погодных данных
   - Интеграция с OpenWeather API
   - Асинхронная обработка запросов
   - Кэширование погодных данных

2. Telegram Бот (app/telegram_service.py)
   - Отправка регулярных уведомлений
   - Команды для получения текущей погоды
   - Система подписки на уведомления
   - Автоматические оповещения о резких изменениях погоды

3. Планировщик (src/scheduler.py)
   - Регулярные обновления погодных данных
   - Отправка уведомлений по расписанию (8:00 и 21:30 МСК)
   - Проверка пропущенных обновлений
   - Обработка ошибок и повторные попытки

4. База данных (app/database_service.py)
   - PostgreSQL для хранения истории погоды
   - Асинхронное взаимодействие через SQLAlchemy
   - Миграции через Alembic
   - Автоматическое сохранение погодных данных

СТРУКТУРА ПРОЕКТА
----------------
/app
  - main.py           - Основное FastAPI приложение
  - config.py         - Конфигурация приложения
  - weather_service.py - Сервис работы с погодой
  - telegram_service.py - Telegram бот
  - database_service.py - Работа с базой данных
  - lifecycle.py      - Управление жизненным циклом

/src
  - scheduler.py      - Планировщик задач
  - tests/           - Модульные тесты
  - templates/       - HTML шаблоны
  
/static             - Статические файлы
/templates          - Шаблоны страниц
/logs               - Логи приложения
/migrations         - Миграции базы данных

ТЕХНОЛОГИИ
----------
- Python 3.12
- FastAPI
- SQLAlchemy
- python-telegram-bot
- PostgreSQL
- Docker & Docker Compose
- Uvicorn
- Alembic
- Pydantic
- httpx

ТРЕБОВАНИЯ К СИСТЕМЕ
-------------------
- Docker и Docker Compose
- Python 3.12+
- PostgreSQL 16+
- Не менее 1GB RAM
- Стабильное интернет-соединение

УСТАНОВКА И ЗАПУСК
-----------------
1. Клонировать репозиторий:
   git clone <repository-url>
   cd OpenWeatherApp

2. Создать файл .env со следующими параметрами:
   OPENWEATHER_API_KEY=your_api_key
   TELEGRAM_BOT_TOKEN=your_bot_token
   DATABASE_URL=postgresql://user:password@db:5432/weather_db
   DEBUG=False

3. Запустить через Docker:
   docker-compose up --build

4. Или локально:
   - Создать виртуальное окружение:
     python -m venv venv
     source venv/bin/activate (Linux/Mac) или venv\Scripts\activate (Windows)
   
   - Установить зависимости:
     pip install -r requirements.txt
   
   - Запустить приложение:
     python -m uvicorn app.main:app --reload

МОНИТОРИНГ И ЛОГИ
----------------
- Логи приложения: /logs/app_*.log
- Логи базы данных: /logs/database.log
- Логи планировщика: /logs/scheduler.log

API ENDPOINTS
------------
GET /weather/{city}
  - Получение текущей погоды для города
  - Параметры: units (metric/imperial)

GET /health
  - Проверка состояния сервиса

GET /cities
  - Список отслеживаемых городов

TELEGRAM КОМАНДЫ
---------------
/start         - Начало работы с ботом
/weather       - Текущая погода во всех городах
/weather_city  - Погода в конкретном городе
/subscribe     - Подписка на уведомления
/unsubscribe   - Отписка от уведомлений
/help          - Список команд

РАЗРАБОТКА
----------
1. Создать ветку для новой функциональности:
   git checkout -b feature/name

2. Запустить тесты:
   python -m pytest

3. Проверить линтером:
   flake8 .

4. Создать миграцию базы данных:
   alembic revision --autogenerate -m "description"
   alembic upgrade head

ПОДДЕРЖКА
---------
- Мониторинг через /health endpoint
- Автоматический перезапуск при сбоях
- Ротация логов
- Резервное копирование базы данных

БЕЗОПАСНОСТЬ
-----------
- Все токены и ключи в .env файле
- HTTPS для API запросов
- Ограничение доступа к API
- Защита от SQL-инъекций
- Валидация входных данных

МАСШТАБИРОВАНИЕ
--------------
- Горизонтальное масштабирование через Docker Swarm
- Кэширование погодных данных
- Очереди сообщений для уведомлений
- Балансировка нагрузки

ИЗВЕСТНЫЕ ОГРАНИЧЕНИЯ
-------------------
- Лимиты API OpenWeather
- Задержка обновления данных до 30 минут
- Ограничения Telegram API
- Зависимость от внешних сервисов

ДОПОЛНИТЕЛЬНО
------------
Документация API: http://localhost:8000/docs
Метрики: http://localhost:8000/metrics
Административная панель: http://localhost:8000/admin 