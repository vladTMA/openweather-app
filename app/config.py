from typing import List, Dict
import pytz

# Настройки времени
TIMEZONE = pytz.timezone('Europe/Moscow')  # Московское время
SCHEDULED_HOURS: List[int] = [8, 21]  # Часы для отправки уведомлений (по московскому времени)
SCHEDULED_MINUTES: Dict[int, int] = {
    8: 0,   # 8:00
    21: 30  # 21:30
}

# Список городов для мониторинга
MONITORED_CITIES: List[str] = [
    "Moscow",        # Москва
    "Saint Petersburg",  # Санкт-Петербург
    "Pskov",        # Псков
    "Belgrade"      # Белград
]

# Словарь для отображения ключей в названия городов для отображения
CITY_NAMES: Dict[str, str] = {
    "Moscow": "Москва",
    "Saint Petersburg": "Санкт-Петербург",
    "Pskov": "Псков",
    "Belgrade": "Белград"
}

# Интервал обновления данных в секундах
UPDATE_INTERVAL: int = 1800  # 30 минут

# Настройки уведомлений
NOTIFICATION_SETTINGS: Dict[str, bool] = {
    "SEND_REGULAR_UPDATES": True,  # Отправлять регулярные обновления
    "SEND_ALERTS": True,  # Отправлять уведомления о резких изменениях погоды
}

# Пороговые значения для уведомлений
ALERT_THRESHOLDS: Dict[str, float] = {
    "TEMPERATURE_CHANGE": 5.0,  # Изменение температуры на 5 градусов
    "WIND_SPEED": 15.0,  # Сильный ветер более 15 м/с
}

# Маппинг команд в названия городов
CITY_COMMANDS: Dict[str, str] = {
    "moscow": "Moscow",
    "spb": "Saint Petersburg",
    "pskov": "Pskov",
    "belgrade": "Belgrade"
} 