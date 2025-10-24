# Руководство по внесению вклада в проект

Спасибо за интерес к проекту OpenWeather App! Мы приветствуем вклад от сообщества.

## 🚀 Быстрый старт

1. **Форкните репозиторий** на GitHub
2. **Клонируйте ваш форк** локально:
   ```bash
   git clone https://github.com/YOUR_USERNAME/OpenWeatherApp.git
   cd OpenWeatherApp
   ```

3. **Создайте виртуальное окружение**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

4. **Установите зависимости**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Создайте файл .env** на основе EnvExample:
   ```bash
   cp EnvExample .env
   # Отредактируйте .env файл с вашими API ключами
   ```

## 🛠 Разработка

### Структура проекта

```
OpenWeatherApp/
├── app/                    # Основное приложение
│   ├── main.py            # FastAPI приложение
│   ├── config.py          # Конфигурация
│   ├── weather_service.py # Сервис погоды
│   ├── telegram_service.py # Telegram бот
│   ├── database_service.py # База данных
│   └── lifecycle.py       # Управление жизненным циклом
├── tests/                 # Тесты
├── migrations/            # Миграции базы данных
├── docs/                  # Документация
└── static/                # Статические файлы
```

### Запуск в режиме разработки

```bash
# Запуск через Docker
docker-compose up --build

# Или локально
python -m uvicorn app.main:app --reload --port 8083
```

### Тестирование

```bash
# Запуск всех тестов
pytest

# Запуск с покрытием
pytest --cov=app

# Запуск конкретного теста
pytest tests/test_weather_service.py
```

## 📝 Процесс внесения изменений

### 1. Создание ветки

```bash
git checkout -b feature/your-feature-name
# или
git checkout -b fix/your-bug-fix
```

### 2. Внесение изменений

- Следуйте стилю кода проекта
- Добавляйте тесты для новой функциональности
- Обновляйте документацию при необходимости
- Убедитесь, что все тесты проходят

### 3. Коммиты

Используйте понятные сообщения коммитов:

```bash
git commit -m "feat: add new weather alert functionality"
git commit -m "fix: resolve database connection issue"
git commit -m "docs: update API documentation"
```

**Типы коммитов:**
- `feat:` - новая функциональность
- `fix:` - исправление ошибки
- `docs:` - изменения в документации
- `style:` - форматирование кода
- `refactor:` - рефакторинг кода
- `test:` - добавление тестов
- `chore:` - обновление зависимостей, конфигурации

### 4. Push и Pull Request

```bash
git push origin feature/your-feature-name
```

Затем создайте Pull Request на GitHub с описанием изменений.

## 🧪 Тестирование

### Типы тестов

1. **Unit тесты** - тестирование отдельных компонентов
2. **Integration тесты** - тестирование взаимодействия компонентов
3. **API тесты** - тестирование REST API

### Запуск тестов

```bash
# Все тесты
pytest

# Только unit тесты
pytest -m unit

# Только integration тесты
pytest -m integration

# Пропустить медленные тесты
pytest -m "not slow"
```

### Покрытие кода

```bash
pytest --cov=app --cov-report=html
```

## 📋 Стандарты кода

### Python

- Следуйте PEP 8
- Используйте type hints
- Документируйте функции и классы
- Максимальная длина строки: 88 символов

### Пример хорошего кода:

```python
async def get_weather_by_city(
    self, 
    city_id: str, 
    units: str = "metric", 
    force_update: bool = False
) -> Optional[WeatherData]:
    """
    Get current weather for a city
    
    Args:
        city_id: City name or identifier
        units: Units of measurement ('metric', 'imperial', or 'standard')
        force_update: If True, ignore cache and fetch new data
        
    Returns:
        Optional[WeatherData]: Weather data if successful, None otherwise
    """
    # Implementation here
```

## 🐛 Сообщения об ошибках

При сообщении об ошибке укажите:

1. **Описание проблемы**
2. **Шаги для воспроизведения**
3. **Ожидаемое поведение**
4. **Фактическое поведение**
5. **Версия Python и зависимости**
6. **Логи ошибок**

## 💡 Предложения по улучшению

Мы приветствуем предложения по улучшению! Пожалуйста:

1. Проверьте существующие Issues
2. Создайте новый Issue с описанием предложения
3. Обсудите идею с сообществом
4. Создайте Pull Request с реализацией

## 📚 Документация

- Обновляйте README при изменении API
- Добавляйте примеры использования
- Документируйте новые функции
- Обновляйте комментарии в коде

## 🔒 Безопасность

- Не коммитьте API ключи или пароли
- Используйте файл .env для конфиденциальных данных
- Проверяйте входные данные
- Используйте HTTPS для API запросов

## 📞 Поддержка

Если у вас есть вопросы:

1. Проверьте документацию
2. Поищите в Issues
3. Создайте новый Issue
4. Свяжитесь с maintainers

## 🎉 Спасибо!

Ваш вклад помогает сделать проект лучше для всех. Спасибо за участие!
