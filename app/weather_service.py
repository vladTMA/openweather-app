import logging
from typing import Optional, Dict, Any, List, Tuple
import httpx
from pydantic import BaseModel
import os
from datetime import datetime, timedelta
import pytz
import asyncio
from dotenv import load_dotenv
from .database_service import DatabaseService
from .config import MONITORED_CITIES, UPDATE_INTERVAL, ALERT_THRESHOLDS, CITY_NAMES

load_dotenv()

logger = logging.getLogger(__name__)

class WeatherData(BaseModel):
    temperature: float
    feels_like: float
    humidity: int
    description: str
    wind_speed: float
    last_update: Optional[datetime] = None

class WeatherService:
    def __init__(self, api_key: str, database_service: Optional[DatabaseService] = None):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.database_service = database_service
        self._update_task: Optional[asyncio.Task] = None
        self._last_weather_data: Dict[str, WeatherData] = {}
        self._cache_duration = timedelta(minutes=30)
        self._http_client = httpx.AsyncClient(timeout=30.0)  # Создаем один клиент для всего сервиса
        logger.info(f"WeatherService initialized with API key: {api_key[:5]}...")
        
    async def initialize(self) -> None:
        """Initialize the service and start updates"""
        await self.start_updates()
        logger.info("Weather service initialized and updates started")
        
    async def stop(self) -> None:
        """Stop the service and cleanup resources"""
        await self.stop_updates()
        await self._http_client.aclose()  # Закрываем HTTP клиент при остановке сервиса
        logger.info("Weather service stopped")
        
    async def start_updates(self):
        """Start periodic weather updates"""
        if self._update_task is None:
            self._update_task = asyncio.create_task(self._update_loop())
            logger.info("Started periodic weather updates")
            
    async def stop_updates(self):
        """Stop periodic weather updates"""
        if self._update_task:
            self._update_task.cancel()
            try:
                await self._update_task
            except asyncio.CancelledError:
                pass
            self._update_task = None
            logger.info("Stopped periodic weather updates")
        
    async def _update_loop(self):
        """Periodic weather update loop"""
        while True:
            try:
                await self.update_all_cities(force_update=True)
                await asyncio.sleep(UPDATE_INTERVAL)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in update loop: {e}")
                await asyncio.sleep(60)  # Wait before retry
                
    def _is_cache_valid(self, weather_data: Optional[WeatherData]) -> bool:
        """Check if cached weather data is still valid"""
        if not weather_data or not weather_data.last_update:
            return False
        return datetime.now() - weather_data.last_update < self._cache_duration
                
    async def update_all_cities(self, force_update: bool = False) -> List[Tuple[str, Optional[WeatherData]]]:
        """
        Update weather data for all monitored cities
        
        Args:
            force_update: If True, ignore cache and fetch new data
            
        Returns:
            List[Tuple[str, Optional[WeatherData]]]: List of (city_id, weather_data) pairs
        """
        weather_updates = []
        
        for city_id in MONITORED_CITIES:
            # Check memory cache first
            cached_data = self._last_weather_data.get(city_id)
            if not force_update and self._is_cache_valid(cached_data):
                weather_updates.append((city_id, cached_data))
                continue
                
            try:
                weather_data = await self.get_weather_by_city(city_id)
                if weather_data:
                    weather_data.last_update = datetime.now()
                    self._last_weather_data[city_id] = weather_data
                    self._check_weather_alerts(city_id, weather_data)
                weather_updates.append((city_id, weather_data))
            except Exception as e:
                logger.error(f"Failed to update weather for {CITY_NAMES.get(city_id, city_id)}: {e}")
                weather_updates.append((city_id, None))
                    
        return weather_updates
        
    def _check_weather_alerts(self, city_id: str, new_data: WeatherData):
        """Check for significant weather changes and log alerts"""
        old_data = self._last_weather_data.get(city_id)
        city_name = CITY_NAMES.get(city_id, city_id)
        
        if old_data:
            # Check temperature change
            temp_change = abs(new_data.temperature - old_data.temperature)
            if temp_change >= ALERT_THRESHOLDS["TEMPERATURE_CHANGE"]:
                logger.warning(f"Significant temperature change in {city_name}: {temp_change}°C")
                
            # Check wind speed
            if new_data.wind_speed >= ALERT_THRESHOLDS["WIND_SPEED"]:
                logger.warning(f"High wind speed alert in {city_name}: {new_data.wind_speed} m/s")
                
        self._last_weather_data[city_id] = new_data
        
    async def get_weather_by_city(self, city_id: str, units: str = "metric", force_update: bool = False) -> Optional[WeatherData]:
        """
        Get current weather for a city
        
        Args:
            city_id: City name or identifier
            units: Units of measurement ('metric', 'imperial', or 'standard')
            force_update: If True, ignore cache and fetch new data
            
        Returns:
            Optional[WeatherData]: Weather data if successful, None otherwise
        """
        try:
            logger.info(f"Getting weather for city: {city_id}")
            
            # Проверяем кэш
            if not force_update:
                cached_data = self._last_weather_data.get(city_id)
                if self._is_cache_valid(cached_data):
                    logger.info(f"Returning cached data for city: {city_id}")
                    return cached_data

            # Подготавливаем параметры запроса
            params = {
                "q": CITY_NAMES.get(city_id, city_id),  # Используем название города
                "appid": self.api_key,
                "units": units
            }
            
            url = f"{self.base_url}/weather"
            city_name = CITY_NAMES.get(city_id, city_id)
            logger.info(f"Making request to OpenWeather API for {city_name}")
            
            try:
                response = await self._http_client.get(url, params=params)
                
                if response.status_code != 200:
                    logger.error(f"HTTP error fetching weather for {city_name}: {response.text}")
                    return None
                    
                data = response.json()
                logger.info(f"Successfully received weather data for {city_name}")

                weather_data = WeatherData(
                    temperature=data["main"]["temp"],
                    feels_like=data["main"]["feels_like"],
                    humidity=data["main"]["humidity"],
                    description=data["weather"][0]["description"],
                    wind_speed=data["wind"]["speed"],
                    last_update=datetime.now()
                )

                self._last_weather_data[city_id] = weather_data
                
                # Save to database if available
                if self.database_service:
                    try:
                        await self.database_service.save_weather_data(
                            city=city_name,
                            temperature=weather_data.temperature,
                            humidity=weather_data.humidity,
                            wind_speed=weather_data.wind_speed,
                            description=weather_data.description,
                            timezone=str(data.get("timezone", ""))
                        )
                    except Exception as e:
                        logger.error(f"Failed to save weather data to database for {city_name}: {e}")
                
                return weather_data
                
            except httpx.HTTPError as e:
                logger.error(f"HTTP error fetching weather for {city_name}: {e}")
                return None
            except Exception as e:
                logger.error(f"Error processing weather data for {city_name}: {e}")
                logger.exception(e)
                return None

        except Exception as e:
            logger.error(f"Unexpected error getting weather for {city_id}: {e}")
            logger.exception(e)
            return None 