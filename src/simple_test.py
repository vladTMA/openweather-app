import requests
from dotenv import load_dotenv
import os

def test_simple_request():
    load_dotenv()
    api_key = os.getenv('OPENWEATHER_API_KEY')
    
    # Самый простой запрос
    url = f"https://api.openweathermap.org/data/2.5/weather?q=London&appid={api_key}"
    
    print(f"\nТестовый запрос:")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url)
        print(f"Статус код: {response.status_code}")
        print(f"Ответ: {response.text}")
    except Exception as e:
        print(f"Ошибка: {str(e)}")

if __name__ == "__main__":
    test_simple_request() 