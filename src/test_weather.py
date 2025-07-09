from weather_service import WeatherService
import logging
import os
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_weather_service():
    try:
        # Load and check environment variables
        load_dotenv()
        api_key = os.getenv('OPENWEATHER_API_KEY')
        cities = [city.strip() for city in os.getenv('CITY_NAME', 'Moscow').split(',')]
        
        print("\nПроверка конфигурации:")
        print("=" * 40)
        print(f"API ключ существует: {'Да' if api_key else 'Нет'}")
        print(f"Длина API ключа: {len(api_key) if api_key else 'Ключ отсутствует'}")
        print(f"Города: {', '.join(cities)}")
        print("=" * 40)
        
        # Initialize weather service
        weather_service = WeatherService()
        
        # Test each city
        for city in cities:
            print(f"\nТестирование города: {city}")
            print("=" * 40)
            
            # Get weather data
            print("Запрос данных о погоде...")
            weather_data = weather_service.get_current_weather(city)
            
            # Print formatted results
            print("\nПолученные данные о погоде:")
            print("=" * 40)
            print(f"🌡 Температура: {weather_data['temperature']}°C")
            print(f"💧 Влажность: {weather_data['humidity']}%")
            print(f"🌪 Скорость ветра: {weather_data['wind_speed']} м/с")
            print(f"☁️ Описание: {weather_data['description']}")
            print(f"📅 Время записи: {weather_data['recorded_at']}")
            print(f"🌍 Часовой пояс: {weather_data['timezone']}")
            print("=" * 40)
            
            # Test caching
            print("\nПроверка кэширования...")
            cached_data = weather_service.get_current_weather(city)
            if cached_data == weather_data:
                print("✅ Кэширование работает: получены данные из кэша")
            print("=" * 40)
        
    except Exception as e:
        logger.error(f"Ошибка при тестировании: {str(e)}")
        raise

if __name__ == "__main__":
    print("Начинаем тестирование сервиса погоды...")
    test_weather_service() 