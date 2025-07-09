import asyncio
import logging
import os
from datetime import datetime, timedelta
from typing import Optional, List
from dotenv import load_dotenv
from app.weather_service import WeatherService
from app.database_service import DatabaseService
from app.telegram_service import TelegramService
from app.config import TIMEZONE, SCHEDULED_HOURS, SCHEDULED_MINUTES

# Загружаем переменные окружения
load_dotenv()

# Получаем токены
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")
if not OPENWEATHER_API_KEY:
    raise ValueError("OPENWEATHER_API_KEY not found in environment variables")

logger = logging.getLogger(__name__)

class WeatherScheduler:
    def __init__(self, weather_service: WeatherService, telegram_service: Optional[TelegramService] = None):
        self.weather_service = weather_service
        self.telegram_service = telegram_service
        self.last_update = {}  # Хранение времени последнего обновления для каждого города
        
    async def start_scheduler(self) -> None:
        """
        Start the scheduler for periodic weather updates
        """
        while True:
            try:
                now = datetime.now(TIMEZONE)
                current_time = now.time()
                
                # Проверяем, нужно ли отправить уведомление
                if (current_time.hour in SCHEDULED_HOURS and 
                    current_time.minute == SCHEDULED_MINUTES[current_time.hour] and 
                    current_time.second < 30):  # Даем 30 секунд окно для отправки
                    
                    logger.info(f"Starting scheduled weather data collection at {current_time.strftime('%H:%M:%S')} (Moscow time)")
                    
                    # Собираем данные и отправляем уведомления
                    await self.collect_and_store_weather_data(force_notify=True)
                    
                    # Ждем 31 секунду, чтобы гарантированно пропустить текущее окно
                    await asyncio.sleep(31)
                else:
                    # Логируем текущее время и следующее запланированное обновление
                    next_update = None
                    for hour in SCHEDULED_HOURS:
                        scheduled_time = now.replace(
                            hour=hour, 
                            minute=SCHEDULED_MINUTES[hour], 
                            second=0, 
                            microsecond=0
                        )
                        if scheduled_time > now:
                            next_update = scheduled_time
                            break
                    if not next_update:
                        # Если сегодня больше нет обновлений, берем первое время на завтра
                        tomorrow = now + timedelta(days=1)
                        next_update = tomorrow.replace(
                            hour=SCHEDULED_HOURS[0], 
                            minute=SCHEDULED_MINUTES[SCHEDULED_HOURS[0]], 
                            second=0, 
                            microsecond=0
                        )
                    
                    if current_time.minute == 0 and current_time.second == 0:  # Логируем только в начале каждого часа
                        logger.info(f"Current time: {current_time.strftime('%H:%M:%S')} (Moscow time), next update scheduled for: {next_update.strftime('%Y-%m-%d %H:%M:%S')}")
                    
                    # Проверяем пропущенные обновления каждые 30 секунд
                    await self.check_missed_updates()
                    await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"Error in scheduler: {e}")
                await asyncio.sleep(60)  # Ждем минуту перед повторной попыткой
                
    async def check_missed_updates(self) -> None:
        """
        Check if we missed any scheduled updates
        """
        now = datetime.now(TIMEZONE)
        
        for hour in SCHEDULED_HOURS:
            # Создаем datetime для запланированного времени
            scheduled_time = now.replace(
                hour=hour, 
                minute=SCHEDULED_MINUTES[hour], 
                second=0, 
                microsecond=0
            )
            
            # Если запланированное время прошло, но не более 30 минут назад
            if now > scheduled_time and now - scheduled_time <= timedelta(minutes=30):
                # Проверяем, было ли уже обновление
                if not any(last_time > scheduled_time for last_time in self.last_update.values()):
                    logger.info(f"Detected missed update for {hour}:{SCHEDULED_MINUTES[hour]:02d} (Moscow time)")
                    await self.collect_and_store_weather_data(force_notify=True)
                    
    async def collect_and_store_weather_data(self, force_notify: bool = False) -> None:
        """
        Collect and store weather data for all cities
        Args:
            force_notify: If True, always send notification regardless of the time
        """
        try:
            current_time = datetime.now(TIMEZONE)
            logger.info(f"Starting weather data collection at {current_time.strftime('%H:%M:%S')} (Moscow time)")
            
            # Получаем данные о погоде для всех городов
            weather_updates = await self.weather_service.update_all_cities()
            logger.info(f"Weather data collected for {len(weather_updates)} cities")
            
            # Обновляем время последнего обновления
            for city, weather_data in weather_updates:
                if weather_data:
                    self.last_update[city] = current_time
                    logger.info(f"Updated weather data for {city}")
                else:
                    logger.warning(f"Failed to get weather data for {city}")
            
            # Отправляем уведомления, если есть Telegram сервис и это запланированное время
            if self.telegram_service:
                if force_notify or (current_time.hour in SCHEDULED_HOURS and 
                                  current_time.minute == SCHEDULED_MINUTES[current_time.hour]):
                    logger.info(f"Sending weather notifications (force_notify={force_notify}, hour={current_time.hour})")
                    await self.telegram_service.send_weather_updates(weather_updates)
                    logger.info("Weather notifications sent successfully")
                else:
                    logger.info("Skipping notifications - not a scheduled time")
            else:
                logger.warning("Telegram service not available - skipping notifications")
            
            logger.info("Weather data collection and notification process completed")
            
        except Exception as e:
            logger.error(f"Error in collect_and_store_weather_data: {str(e)}")

if __name__ == "__main__":
    # Создаем сервисы
    weather_service = WeatherService(api_key=OPENWEATHER_API_KEY)
    telegram_service = TelegramService(token=TELEGRAM_BOT_TOKEN, weather_service=weather_service)
    
    # Создаем и запускаем планировщик
    scheduler = WeatherScheduler(weather_service, telegram_service)
    asyncio.run(scheduler.start_scheduler()) 