import logging
from typing import Optional, Dict, Any, List, Tuple
import httpx
from pydantic import BaseModel
import os
from datetime import datetime
import pytz
import asyncio
from dotenv import load_dotenv
from src.database_service import DatabaseService

load_dotenv()

logger = logging.getLogger(__name__)

class WeatherData(BaseModel):
    temperature: float
    feels_like: float
    humidity: int
    description: str
    wind_speed: float

class WeatherService:
    def __init__(self, database_service: Optional[DatabaseService] = None):
        self.api_key = os.getenv("OPENWEATHER_API_KEY")
        self.base_url = os.getenv("OPENWEATHER_BASE_URL", "https://api.openweathermap.org/data/2.5")
        self.database_service = database_service
        self._last_weather_data: Dict[str, WeatherData] = {}
        
    async def start_updates(self):
        """Start periodic weather updates"""
        if self.database_service:
            await self.database_service.initialize_database()
        self._update_task = asyncio.create_task(self._update_loop())
        logger.info("Started periodic weather updates")
            
    async def stop_updates(self):
        """Stop periodic weather updates"""
        if hasattr(self, '_update_task'):
            self._update_task.cancel()
            try:
                await self._update_task
            except asyncio.CancelledError:
                pass
            logger.info("Stopped periodic weather updates")
        
    async def _update_loop(self):
        """Periodic weather update loop"""
        while True:
            try:
                await self.update_all_cities()
                await asyncio.sleep(1800)  # 30 минут
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in update loop: {e}")
                await asyncio.sleep(60)  # Wait before retry
                
    async def update_all_cities(self) -> List[Tuple[str, Optional[WeatherData]]]:
        """
        Update weather data for all monitored cities
        
        Returns:
            List[Tuple[str, Optional[WeatherData]]]: List of (city, weather_data) pairs
        """
        cities = ["Moscow", "Saint Petersburg", "Belgrade", "Pskov"]
        tasks = []
        for city in cities:
            tasks.append(self.get_weather_by_city(city))
            
        results = await asyncio.gather(*tasks, return_exceptions=True)
        weather_updates = []
        
        for city, result in zip(cities, results):
            if isinstance(result, Exception):
                logger.error(f"Failed to update weather for {city}: {result}")
                weather_updates.append((city, None))
            else:
                weather_updates.append((city, result))
                # Only check alerts for valid weather data
                if isinstance(result, WeatherData):
                    self._check_weather_alerts(city, result)
                    
        return weather_updates
        
    def _check_weather_alerts(self, city: str, new_data: WeatherData):
        """Check for significant weather changes and log alerts"""
        old_data = self._last_weather_data.get(city)
        if old_data:
            # Check temperature change
            temp_change = abs(new_data.temperature - old_data.temperature)
            if temp_change >= 5.0:  # Изменение температуры на 5 градусов
                logger.warning(f"Significant temperature change in {city}: {temp_change}°C")
                
            # Check wind speed
            if new_data.wind_speed >= 15.0:  # Сильный ветер более 15 м/с
                logger.warning(f"High wind speed alert in {city}: {new_data.wind_speed} m/s")
                
        self._last_weather_data[city] = new_data
        
    async def get_weather_by_city(self, city: str, units: str = "metric") -> Optional[WeatherData]:
        """
        Get current weather for a city
        
        Args:
            city: Name of the city
            units: Units of measurement ('metric', 'imperial', or 'standard')
            
        Returns:
            Optional[WeatherData]: Weather data if successful, None otherwise
        """
        try:
            # First try to get cached data from database
            if self.database_service:
                cached_data = await self.database_service.get_latest_weather(city)
                if cached_data:
                    # Check if data is fresh (less than 30 minutes old)
                    cache_time = cached_data["recorded_at"]
                    if (datetime.utcnow() - cache_time).total_seconds() < 1800:
                        logger.info(f"Using cached weather data for {city}")
                        return WeatherData(
                            temperature=cached_data["temperature"],
                            feels_like=cached_data["temperature"],  # Approximation
                            humidity=cached_data["humidity"],
                            description=cached_data["description"],
                            wind_speed=cached_data["wind_speed"]
                        )

            # If no fresh cache, fetch from API
            params = {
                "q": city,
                "appid": self.api_key,
                "units": units
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{self.base_url}/weather", params=params)
                response.raise_for_status()
                data = response.json()

            weather_data = WeatherData(
                temperature=data["main"]["temp"],
                feels_like=data["main"]["feels_like"],
                humidity=data["main"]["humidity"],
                description=data["weather"][0]["description"],
                wind_speed=data["wind"]["speed"]
            )

            # Cache the new data
            if self.database_service:
                now = datetime.utcnow()
                weather_record = {
                    'city': city,
                    'temp': weather_data.temperature,
                    'humidity': weather_data.humidity,
                    'wind_speed': weather_data.wind_speed,
                    'description': weather_data.description,
                    'recorded_at': now.strftime('%Y-%m-%d %H:%M:%S'),
                    'timezone': str(data.get("timezone", "UTC"))
                }
                
                success = await self.database_service.save_weather_data(weather_record)
                if not success:
                    logger.warning(f"Failed to cache weather data for {city}")

            return weather_data

        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching weather for {city}: {e}")
            # Try to get data from cache even if it's old
            if self.database_service:
                cached_data = await self.database_service.get_latest_weather(city)
                if cached_data:
                    logger.info(f"Using stale cached weather data for {city} due to API error")
                    return WeatherData(
                        temperature=cached_data["temperature"],
                        feels_like=cached_data["temperature"],
                        humidity=cached_data["humidity"],
                        description=cached_data["description"],
                        wind_speed=cached_data["wind_speed"]
                    )
            return None
            
        except Exception as e:
            logger.error(f"Error fetching weather for {city}: {e}")
            return None 