import requests
from dotenv import load_dotenv
import os

def test_sample_api():
    load_dotenv()
    api_key = os.getenv('OPENWEATHER_API_KEY', '')
    
    print("\nТестирование API по официальному примеру:")
    print("=" * 50)
    
    # Пример из документации OpenWeather
    sample_url = f"https://samples.openweathermap.org/data/2.5/weather?q=London,uk&appid={api_key}"
    print(f"Тестовый URL: {sample_url}")
    
    try:
        response = requests.get(sample_url)
        print(f"\nСтатус код: {response.status_code}")
        print(f"Ответ: {response.text}")
        
        if response.status_code == 401:
            print("\nПроверьте в личном кабинете:")
            print("1. Перейдите на https://home.openweathermap.org/api_keys")
            print("2. Убедитесь, что ключ активен")
            print("3. Попробуйте сгенерировать новый ключ")
            print("4. Проверьте статистику использования")
    except Exception as e:
        print(f"Ошибка при запросе: {str(e)}")

if __name__ == "__main__":
    test_sample_api() 