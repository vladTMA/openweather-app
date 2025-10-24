# 🌤️ OpenWeather App

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](docker-compose.yml)

Сервис для мониторинга погоды с автоматическими уведомлениями через Telegram бота. Построен на FastAPI с использованием асинхронного подхода и Docker контейнеризации.

## ✨ Основные возможности

- 🌡️ **Мониторинг погоды** для нескольких городов
- 🤖 **Telegram бот** с командами и уведомлениями
- 📊 **REST API** для получения погодных данных
- 🗄️ **База данных** для хранения истории погоды
- ⏰ **Планировщик** для автоматических обновлений
- 🐳 **Docker** контейнеризация
- 🧪 **Полное тестирование** с pytest
- 🔄 **CI/CD** с GitHub Actions

## 🚀 Быстрый старт

### 1. Клонирование репозитория
```bash
git clone https://github.com/YOUR_USERNAME/OpenWeatherApp.git
cd OpenWeatherApp
```

### 2. Настройка переменных окружения
```bash
# Скопируйте пример конфигурации
cp EnvExample .env

# Отредактируйте .env файл с вашими API ключами
```

### 3. Запуск через Docker (рекомендуется)
```bash
docker-compose up --build
```

### 4. Или локальный запуск
```bash
# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Установка зависимостей
pip install -r requirements.txt

# Запуск приложения
python -m uvicorn app.main:app --reload --port 8083
```

## 📋 Требования

- Python 3.11+
- Docker и Docker Compose
- API ключ OpenWeather (бесплатный)
- Telegram Bot Token

## 🌐 API Endpoints

| Endpoint | Описание |
|----------|----------|
| `GET /` | Главная страница |
| `GET /health` | Проверка состояния сервиса |
| `GET /weather?cities=Moscow,SPB` | Погода для указанных городов |
| `GET /cities` | Список отслеживаемых городов |

## 🤖 Telegram команды

| Команда | Описание |
|---------|----------|
| `/start` | Начало работы с ботом |
| `/weather` | Текущая погода во всех городах |
| `/weather_moscow` | Погода в Москве |
| `/weather_spb` | Погода в Санкт-Петербурге |
| `/subscribe` | Подписка на уведомления |
| `/unsubscribe` | Отписка от уведомлений |
| `/help` | Список команд |

## 🛠 Технологии

- **Backend**: FastAPI, Python 3.11+
- **Database**: PostgreSQL/SQLite, SQLAlchemy, Alembic
- **Bot**: python-telegram-bot
- **Weather API**: OpenWeather API
- **Containerization**: Docker, Docker Compose
- **Testing**: pytest, pytest-asyncio
- **CI/CD**: GitHub Actions

## 📁 Структура проекта

```
OpenWeatherApp/
├── app/                    # Основное приложение
│   ├── main.py            # FastAPI приложение
│   ├── config.py          # Конфигурация
│   ├── weather_service.py # Сервис погоды
│   ├── telegram_service.py # Telegram бот
│   ├── database_service.py # База данных
│   └── lifecycle.py       # Управление жизненным циклом
├── tests/                 # Тесты
├── migrations/            # Миграции базы данных
├── docs/                  # Документация
├── .github/workflows/     # GitHub Actions
├── docker-compose.yml     # Docker конфигурация
├── Dockerfile            # Docker образ
├── requirements.txt       # Python зависимости
├── alembic.ini           # Конфигурация миграций
├── pytest.ini           # Конфигурация тестов
├── LICENSE               # MIT лицензия
└── CONTRIBUTING.md       # Руководство для разработчиков
```

## 🧪 Тестирование

```bash
# Запуск всех тестов
pytest

# Запуск с покрытием
pytest --cov=app

# Запуск конкретного теста
pytest tests/test_weather_service.py
```

## 📊 Мониторинг

- **Логи**: `/logs/app_*.log`
- **Health Check**: `GET /health`
- **API Docs**: `http://localhost:8083/docs`

## 🔧 Разработка

1. Форкните репозиторий
2. Создайте ветку: `git checkout -b feature/amazing-feature`
3. Внесите изменения и добавьте тесты
4. Запустите тесты: `pytest`
5. Создайте Pull Request

Подробное руководство: [CONTRIBUTING.md](CONTRIBUTING.md)

## 📚 Документация

- 🇷🇺 [Русская версия](docs/README-ru.md)
- 🇬🇧 [English version](docs/README-en.md)

## 🤝 Вклад в проект

Мы приветствуем вклад от сообщества! Пожалуйста, прочитайте [CONTRIBUTING.md](CONTRIBUTING.md) для получения подробной информации.

## 📄 Лицензия

Этот проект распространяется под лицензией MIT. См. [LICENSE](LICENSE) для получения дополнительной информации.

## ⚠️ Известные ограничения

- Лимиты API OpenWeather (1000 запросов/день для бесплатного плана)
- Задержка обновления данных до 30 минут
- Ограничения Telegram API
- Зависимость от внешних сервисов

## 🆘 Поддержка

Если у вас есть вопросы или проблемы:

1. Проверьте [Issues](https://github.com/YOUR_USERNAME/OpenWeatherApp/issues)
2. Создайте новый Issue
3. Свяжитесь с maintainers

## 🌟 Звезды

Если проект вам понравился, поставьте звезду! ⭐ 