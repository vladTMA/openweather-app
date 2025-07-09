import requests
import time
from datetime import datetime
import os
from dotenv import load_dotenv

def check_api_status():
    load_dotenv()
    api_key = os.getenv('OPENWEATHER_API_KEY', '')
    
    # Правильный URL для бесплатного API
    base_url = "api.openweathermap.org/data/2.5/weather"
    url = f"http://{base_url}"
    
    params = {
        'q': 'London',
        'appid': api_key,
        'units': 'metric'
    }
    
    try:
        response = requests.get(url, params=params)
        current_time = datetime.now().strftime('%H:%M:%S')
        
        if response.status_code == 200:
            print(f"✅ [{current_time}] API ключ активен! Получен успешный ответ.")
            print("\nПример данных:")
            data = response.json()
            print(f"Город: {data.get('name')}")
            print(f"Температура: {data.get('main', {}).get('temp')}°C")
            return True
        else:
            print(f"❌ [{current_time}] API ключ еще не активен (Статус: {response.status_code})")
            print(f"Ответ сервера: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ [{current_time}] Ошибка при проверке: {str(e)}")
        return False

def monitor_activation(check_interval=300):  # 300 секунд = 5 минут
    print("\nЗапуск мониторинга активации API ключа")
    print("=" * 50)
    print("Проверка будет выполняться каждые 5 минут")
    print("Для остановки нажмите Ctrl+C")
    print("=" * 50)
    
    attempt = 1
    
    try:
        while True:
            print(f"\nПопытка #{attempt}")
            if check_api_status():
                print("\n✨ API ключ успешно активирован!")
                break
                
            print(f"Следующая проверка через {check_interval // 60} минут...")
            time.sleep(check_interval)
            attempt += 1
            
    except KeyboardInterrupt:
        print("\n\nМониторинг остановлен пользователем")
    except Exception as e:
        print(f"\n\nОшибка в процессе мониторинга: {str(e)}")

if __name__ == "__main__":
    monitor_activation() 