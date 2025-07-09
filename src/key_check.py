import os
from dotenv import load_dotenv

def check_api_key():
    load_dotenv()
    api_key = os.getenv('OPENWEATHER_API_KEY', '')
    
    print("\nПроверка формата API ключа:")
    print("=" * 50)
    
    # Базовые проверки
    print(f"1. Полный ключ: {api_key}")
    print(f"2. Длина ключа: {len(api_key)} символов")
    print(f"3. Последние символы: {api_key[-2:] if len(api_key) >= 2 else 'ключ слишком короткий'}")
    
    # Проверка на специальные символы
    has_special = any(not c.isalnum() for c in api_key)
    print(f"4. Содержит специальные символы: {'Да' if has_special else 'Нет'}")
    
    # Проверка на пробелы
    has_spaces = any(c.isspace() for c in api_key)
    print(f"5. Содержит пробелы: {'Да' if has_spaces else 'Нет'}")
    
    # Проверка регистра
    print(f"6. Все символы в нижнем регистре: {'Да' if api_key.islower() else 'Нет'}")
    
    # Сравнение с известным окончанием
    expected_suffix = "6b"
    if api_key.endswith(expected_suffix):
        print(f"7. ✅ Ключ заканчивается на правильные символы: {expected_suffix}")
    else:
        print(f"7. ❌ Ключ должен заканчиваться на: {expected_suffix}")
        print(f"   Текущее окончание: {api_key[-2:] if len(api_key) >= 2 else 'ключ слишком короткий'}")
    
    print("\nРекомендации:")
    if has_special or has_spaces or not api_key.endswith(expected_suffix):
        print("- Проверьте, что ключ скопирован правильно")
        print("- Убедитесь, что нет лишних пробелов")
        print("- Ключ должен содержать только буквы и цифры")
        print(f"- Ключ должен заканчиваться на {expected_suffix}")
    else:
        print("✅ Формат ключа выглядит правильным")

if __name__ == "__main__":
    check_api_key() 