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
OpenWeatherApp/
├── app/                    # Main application
│   ├── main.py            # FastAPI application
│   ├── config.py          # Application configuration
│   ├── weather_service.py # Weather service
│   ├── telegram_service.py # Telegram bot
│   ├── database_service.py # Database operations
│   └── lifecycle.py      # Lifecycle management
├── tests/                 # Structured tests
│   ├── test_weather_service.py
│   ├── test_api.py
│   └── test_config.py
├── migrations/            # Database migrations
│   ├── env.py
│   └── versions/
├── docs/                  # Documentation
├── .github/workflows/     # GitHub Actions CI/CD
├── static/               # Static files
├── templates/            # HTML templates
├── logs/                 # Application logs
├── docker-compose.yml    # Docker configuration
├── Dockerfile           # Docker image
├── requirements.txt     # Python dependencies
├── alembic.ini         # Migration configuration
├── pytest.ini         # Test configuration
├── LICENSE             # MIT license
├── CONTRIBUTING.md     # Developer guide
└── EnvExample          # Environment variables example
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

2. Create `.env` file based on example:
```bash
cp EnvExample .env
```

Then edit `.env` file with parameters:
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

### Setting up development environment

1. Create branch for new feature:
```bash
git checkout -b feature/name
```

2. Install development dependencies:
```bash
pip install -r requirements.txt
```

### Testing

3. Run all tests:
```bash
pytest
```

4. Run tests with coverage:
```bash
pytest --cov=app --cov-report=html
```

5. Run specific tests:
```bash
pytest tests/test_weather_service.py
pytest tests/test_api.py
pytest tests/test_config.py
```

### Code quality checks

6. Check with linter:
```bash
flake8 .
```

7. Check security:
```bash
bandit -r app/
safety check
```

### Database management

8. Initialize migrations (if needed):
```bash
python init_migrations.py
```

9. Create new migration:
```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
```

### CI/CD

The project uses GitHub Actions for automated testing:
- Tests run on Python 3.11 and 3.12
- Linter and security checks
- Docker image building
- Code coverage reporting

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