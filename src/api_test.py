import os
import requests
from dotenv import load_dotenv

def check_env_format():
    # Load environment variables
    load_dotenv()
    api_key = os.getenv('OPENWEATHER_API_KEY', '')
    city = os.getenv('CITY_NAME', '')
    
    print("\nПроверка переменных окружения:")
    print("=" * 50)
    
    # Проверка API ключа
    print("\n1. Проверка API ключа:")
    print(f"Значение: {api_key}")
    if api_key.strip() != api_key:
        print("❌ Ошибка: API ключ содержит пробелы в начале или конце")
    if '"' in api_key or "'" in api_key:
        print("❌ Ошибка: API ключ содержит кавычки")
    if '#' in api_key:
        print("❌ Ошибка: API ключ содержит символ комментария")
    if len(api_key) == 32:
        print("✅ Длина API ключа корректная (32 символа)")
    else:
        print(f"❌ Ошибка: Неверная длина API ключа ({len(api_key)} символов вместо 32)")
    
    # Проверка названия города
    print("\n2. Проверка названия города:")
    print(f"Значение: {city}")
    if city.strip() != city:
        print("❌ Ошибка: Название города содержит пробелы в начале или конце")
    if '"' in city or "'" in city:
        print("❌ Ошибка: Название города содержит кавычки")
    if '#' in city:
        print("❌ Ошибка: Название города содержит символ комментария")
    if city:
        print("✅ Название города указано")
    else:
        print("❌ Ошибка: Название города не указано")

def test_api_directly():
    # Load environment variables
    load_dotenv()
    api_key = os.getenv('OPENWEATHER_API_KEY')
    city = os.getenv('CITY_NAME', 'Moscow')
    
    print("\nТестирование API OpenWeather:")
    print("=" * 50)
    
    # Формируем параметры запроса
    params = {
        'q': city,
        'appid': api_key,
        'units': 'metric',
        'lang': 'ru'
    }
    
    # Используем только HTTPS endpoint
    endpoint = "https://api.openweathermap.org/data/2.5/weather"
    
    try:
        # Выполняем запрос
        print(f"\nОтправляем запрос для города: {city}")
        response = requests.get(endpoint, params=params)
        
        # Выводим детали запроса
        print(f"URL запроса: {response.url}")
        print(f"Статус код: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\nУспешный ответ!")
            print(f"Название города: {data.get('name')}")
            print(f"Температура: {data.get('main', {}).get('temp')}°C")
            print(f"Описание: {data.get('weather', [{}])[0].get('description')}")
        else:
            print(f"\nТекст ошибки: {response.text}")
            
    except Exception as e:
        print(f"Ошибка при запросе: {str(e)}")

if __name__ == "__main__":
    check_env_format()
    test_api_directly() 