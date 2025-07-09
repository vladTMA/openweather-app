# Weather Notification Bot

A Telegram bot that provides weather updates for multiple cities using the OpenWeather API. The bot sends scheduled notifications twice a day and responds to user requests for current weather conditions.

## 🔧 Core Components

### 1. FastAPI Application (`app/main.py`)
- REST API for weather data
- OpenWeather API integration
- Asynchronous request processing
- Weather data caching

### 2. Telegram Bot (`app/telegram_service.py`)
- Regular notifications
- Current weather commands
- Notification subscription system
- Automatic alerts for weather changes

### 3. Scheduler (`src/scheduler.py`)
- Regular weather data updates
- Scheduled notifications (8:00 AM and 9:30 PM MSK)
- Missed updates checking
- Error handling and retries

### 4. Database (`app/database_service.py`)
- PostgreSQL/SQLite support for weather history
- Asynchronous SQLAlchemy interaction
- Alembic migrations
- Automatic weather data storage

## 📁 Project Structure

```
/app
  - main.py           - Main FastAPI application
  - config.py         - Application configuration
  - weather_service.py - Weather service
  - telegram_service.py - Telegram bot
  - database_service.py - Database operations
  - lifecycle.py      - Lifecycle management

/src
  - scheduler.py      - Task scheduler
  - tests/           - Unit tests
  - templates/       - HTML templates
  
/static             - Static files
/templates          - Page templates
/logs               - Application logs
/migrations         - Database migrations
```

## 🛠 Technologies

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

## 📋 System Requirements

- Docker and Docker Compose
- Python 3.11+
- PostgreSQL (optional, SQLite by default)
- Minimum 1GB RAM
- Stable internet connection

## 🚀 Installation and Launch

1. Clone the repository:
```bash
git clone <repository-url>
cd OpenWeatherApp
```

2. Create `.env` file with parameters:
```env
OPENWEATHER_API_KEY=your_api_key
TELEGRAM_BOT_TOKEN=your_bot_token
DATABASE_URL=postgresql://user:password@db:5432/weather_db  # Optional for PostgreSQL
DEBUG=False
```

3. Run with Docker:
```bash
docker-compose up --build
```

4. Or locally:
```bash
# Create virtual environment:
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies:
pip install -r requirements.txt

# Run application:
python -m uvicorn src.main:app --reload --port 8083
```

## 📊 Monitoring and Logs

- Application logs: `/logs/app_*.log`
- Database logs: `/logs/database.log`
- Scheduler logs: `/logs/scheduler.log`

## 🌐 API Endpoints

### GET /weather/{city}
- Get current weather for city
- Parameters: units (metric/imperial)

### GET /health
- Service health check

### GET /cities
- List of monitored cities

## 🤖 Telegram Commands

| Command | Description |
|---------|-------------|
| `/start` | Start bot and get welcome message |
| `/weather` | Current weather in all cities |
| `/weather_city` | Weather in specific city |
| `/subscribe` | Subscribe to notifications |
| `/unsubscribe` | Unsubscribe from notifications |
| `/help` | List of commands |

## 👨‍💻 Development

1. Create branch for new feature:
```bash
git checkout -b feature/name
```

2. Run tests:
```bash
python -m pytest
```

3. Check with linter:
```bash
flake8 .
```

4. Create database migration:
```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
```

## 🔍 Support

- Monitoring via `/health` endpoint
- Automatic restart on failures
- Log rotation
- Database backup

## 🔒 Security

- All tokens and keys in `.env` file
- HTTPS for API requests
- API access restrictions
- SQL injection protection
- Input validation

## 📈 Scaling

- Horizontal scaling via Docker Swarm
- Weather data caching
- Message queues for notifications
- Load balancing

## ⚠️ Known Limitations

- OpenWeather API limits
- Data update delay up to 30 minutes
- Telegram API restrictions
- External services dependencies

## 📚 Additional Resources

- [API Documentation](http://localhost:8083/docs)
- [Metrics](http://localhost:8083/metrics)
- [Admin Panel](http://localhost:8083/admin) 