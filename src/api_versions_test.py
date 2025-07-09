import requests
from dotenv import load_dotenv
import os

def test_api_versions():
    load_dotenv()
    api_key = os.getenv('OPENWEATHER_API_KEY')
    
    # Список разных версий API для тестирования
    endpoints = [
        "https://api.openweathermap.org/data/2.5/weather",  # Current weather data
        "https://api.openweathermap.org/data/2.5/forecast", # 5 day forecast
        "https://api.openweathermap.org/data/3.0/weather",  # New API version
        "http://api.openweathermap.org/data/2.5/weather"    # HTTP version
    ]
    
    print("\nТестирование разных версий API:")
    print("=" * 50)
    
    for endpoint in endpoints:
        print(f"\nПробуем endpoint: {endpoint}")
        url = f"{endpoint}?q=London&appid={api_key}"
        
        try:
            response = requests.get(url)
            print(f"Статус: {response.status_code}")
            print(f"Ответ: {response.text[:200]}...")  # Показываем только начало ответа
        except Exception as e:
            print(f"Ошибка: {str(e)}")
        
        print("-" * 50)

if __name__ == "__main__":
    test_api_versions() 