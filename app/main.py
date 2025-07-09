import asyncio
import logging
import os
from typing import Optional, List
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from app.lifecycle import AppLifecycle
from app.weather_service import WeatherService
from app.database_service import DatabaseService
from app.telegram_service import TelegramService
from app.config import UPDATE_INTERVAL, MONITORED_CITIES, CITY_NAMES
import pytz
from datetime import datetime

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI()
templates = Jinja2Templates(directory="templates")  # Используем корневой каталог templates
app.mount("/static", StaticFiles(directory="static"), name="static")

class WeatherBot:
    def __init__(self):
        self.lifecycle = AppLifecycle()
        self.database_service: Optional[DatabaseService] = None
        self.weather_service: Optional[WeatherService] = None
        self.telegram_service: Optional[TelegramService] = None
        self._stop_event = asyncio.Event()

    async def initialize(self) -> None:
        """Initialize all services"""
        try:
            # Initialize database if URL is provided
            database_url = os.getenv('DATABASE_URL')
            if database_url:
                await self.lifecycle.initialize_database(database_url)
                self.database_service = DatabaseService(self.lifecycle.get_session)
                logger.info("Database service initialized")
            else:
                logger.warning("DATABASE_URL not set, running without database")

            # Initialize weather service
            api_key = os.getenv('OPENWEATHER_API_KEY')
            if not api_key:
                raise ValueError("OPENWEATHER_API_KEY environment variable is not set")
            
            logger.info(f"Using OpenWeather API key: {api_key[:5]}...")
            
            # Проверяем, что ключ не пустой и имеет правильный формат
            if len(api_key.strip()) < 20:  # OpenWeather API ключи обычно длиннее 20 символов
                raise ValueError("OPENWEATHER_API_KEY seems invalid (too short)")
            
            self.weather_service = WeatherService(
                api_key=api_key,
                database_service=self.database_service
            )
            await self.weather_service.initialize()
            logger.info("Weather service initialized")

            # Initialize telegram service
            bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
            logger.info("Attempting to initialize Telegram bot...")
            if not bot_token:
                logger.error("TELEGRAM_BOT_TOKEN environment variable is not set")
                raise ValueError("TELEGRAM_BOT_TOKEN environment variable is not set")
            
            logger.info(f"Using Telegram bot token: {bot_token[:5]}...")
            
            self.telegram_service = TelegramService(
                token=bot_token,
                weather_service=self.weather_service
            )
            await self.telegram_service.initialize()
            logger.info("Telegram service initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize services: {e}")
            await self.stop()
            raise

    async def start(self) -> None:
        """Start all services"""
        try:
            await self.initialize()
            if not self.telegram_service:
                raise RuntimeError("Telegram service was not initialized")
            await self.telegram_service.start()
            logger.info("All services started successfully")
        except Exception as e:
            logger.error(f"Failed to start services: {e}")
            await self.stop()
            raise

    async def stop(self) -> None:
        """Stop all services"""
        try:
            self._stop_event.set()
            if self.telegram_service:
                await self.telegram_service.stop()
            if self.weather_service:
                await self.weather_service.stop()
            if self.database_service:
                await self.database_service.stop()
            logger.info("All services stopped successfully")
        except Exception as e:
            logger.error(f"Failed to stop services: {e}")
            raise

# Create bot instance
bot = WeatherBot()

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    await bot.initialize()
    await bot.start()  # Start the bot after initialization

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await bot.stop()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Render main page"""
    # Получаем данные о погоде для всех отслеживаемых городов
    weather_list = []
    if bot.weather_service:
        for city_id in MONITORED_CITIES:
            try:
                weather = await bot.weather_service.get_weather_by_city(city_id)
                if weather:
                    # Получаем текущее время в Москве
                    moscow_tz = pytz.timezone('Europe/Moscow')
                    current_time = datetime.now(moscow_tz)
                    
                    weather_list.append({
                        "name": CITY_NAMES.get(city_id, city_id),
                        "main": {
                            "temp": weather.temperature,
                            "humidity": weather.humidity
                        },
                        "weather": [{"description": weather.description}],
                        "wind": {"speed": weather.wind_speed},
                        "sys": {"country": "RU"},
                        "recorded_at_moscow": current_time
                    })
            except Exception as e:
                weather_list.append({"error": str(e)})

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "weather_list": weather_list,
            "db_enabled": bot.database_service is not None
        }
    )

@app.get("/weather")
async def get_weather(cities: str = ""):
    """Get weather data for cities"""
    if not bot.weather_service:
        return {"error": "Weather service not initialized"}
        
    city_list = [city.strip() for city in cities.split(",") if city.strip()]
    if not city_list:
        return {"error": "No cities provided"}
        
    results = []
    for city in city_list:
        try:
            weather = await bot.weather_service.get_weather_by_city(city)
            if weather:
                results.append({
                    "city": city,
                    "temperature": weather.temperature,
                    "feels_like": weather.feels_like,
                    "humidity": weather.humidity,
                    "wind_speed": weather.wind_speed,
                    "description": weather.description
                })
            else:
                results.append({
                    "city": city,
                    "error": "Failed to get weather data"
                })
        except Exception as e:
            results.append({
                "city": city,
                "error": str(e)
            })
            
    return {"results": results}

async def start_bot():
    """Start the bot"""
    await bot.start()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8083, reload=True) 