import requests
from dotenv import load_dotenv
import os

def test_official_format():
    load_dotenv()
    api_key = os.getenv('OPENWEATHER_API_KEY', '')  # Default to empty string if not found
    
    print("\nПроверка API ключа:")
    print(f"Ключ: {api_key}")
    print(f"Длина ключа: {len(api_key)} символов")
    
    if not api_key:
        print("❌ Ошибка: API ключ не найден в .env файле")
        return
    
    # Тест 1: Формат из официальной документации
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    
    # Тест с разными форматами параметров
    test_cases = [
        {
            "name": "Базовый запрос (только город)",
            "params": {"q": "London", "appid": api_key}
        },
        {
            "name": "Запрос с метрической системой",
            "params": {"q": "London", "appid": api_key, "units": "metric"}
        },
        {
            "name": "Запрос с ID города (London)",
            "params": {"id": "2643743", "appid": api_key}  # London city ID
        },
        {
            "name": "Запрос с координатами (London)",
            "params": {"lat": "51.5085", "lon": "-0.1257", "appid": api_key}
        }
    ]
    
    print("\nТестирование разных форматов запроса:")
    print("=" * 50)
    
    for test in test_cases:
        print(f"\n{test['name']}:")
        try:
            response = requests.get(base_url, params=test['params'])
            print(f"URL: {response.url}")
            print(f"Статус: {response.status_code}")
            print(f"Ответ: {response.text[:200]}...")
        except Exception as e:
            print(f"Ошибка: {str(e)}")
        print("-" * 50)

if __name__ == "__main__":
    test_official_format() 