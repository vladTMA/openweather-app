import asyncio
import os
import sys
from pathlib import Path

# Добавляем корневую директорию проекта в PYTHONPATH
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)

from dotenv import load_dotenv
from app.lifecycle import AppLifecycle
from app.database_service import DatabaseService

async def check_database():
    # Загружаем переменные окружения
    load_dotenv()
    
    # Собираем URL базы данных из компонентов
    db_host = os.getenv('DB_HOST')
    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    
    if not all([db_host, db_name, db_user, db_password]):
        print("❌ Ошибка: Не все переменные окружения для базы данных найдены")
        return
        
    # Формируем URL для асинхронного подключения
    database_url = f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}/{db_name}"
        
    try:
        # Инициализируем сервисы
        lifecycle = AppLifecycle()
        await lifecycle.initialize_database(database_url)
        db_service = DatabaseService(lifecycle.get_session)
        
        # Проверяем последние записи для каждого города
        cities = {
            "524901": "Москва",
            "498817": "Санкт-Петербург",
            "504341": "Псков",
            "792680": "Белград"
        }
        
        print("\n🔍 Проверка последних записей в базе данных:")
        print("=" * 50)
        
        for city_id, city_name in cities.items():
            record = await db_service.get_latest_weather(city_id)
            print(f"\n📍 {city_name} ({city_id}):")
            if record:
                print(f"  🌡 Температура: {record['temperature']}°C")
                print(f"  💧 Влажность: {record['humidity']}%")
                print(f"  💨 Ветер: {record['wind_speed']} м/с")
                print(f"  📝 Описание: {record['description']}")
                print(f"  🕒 Время записи (МСК): {record['recorded_at_moscow'].strftime('%d.%m.%Y %H:%M:%S')}")
            else:
                print("  ❌ Записей не найдено")
                
        print("\n" + "=" * 50)
        
    except Exception as e:
        print(f"\n❌ Ошибка при проверке базы данных: {e}")
    finally:
        if 'lifecycle' in locals():
            await lifecycle.cleanup()

if __name__ == "__main__":
    asyncio.run(check_database()) 