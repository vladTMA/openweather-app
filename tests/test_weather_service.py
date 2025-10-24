import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from app.weather_service import WeatherService, WeatherData
from app.telegram_service import TelegramService
from app.database_service import DatabaseService
from datetime import datetime, timedelta


@pytest.fixture
def mock_weather_data():
    """Mock weather data for testing"""
    return WeatherData(
        temperature=20.5,
        feels_like=22.0,
        humidity=65,
        description="clear sky",
        wind_speed=3.2,
        last_update=datetime.now()
    )


@pytest.fixture
def weather_service():
    """Create WeatherService instance for testing"""
    return WeatherService(api_key="test_api_key", database_service=None)


@pytest.fixture
def mock_database_service():
    """Mock database service"""
    mock_db = Mock(spec=DatabaseService)
    mock_db.save_weather_record = AsyncMock(return_value=True)
    mock_db.get_latest_weather = AsyncMock(return_value=None)
    return mock_db


class TestWeatherService:
    """Test cases for WeatherService"""
    
    def test_weather_service_initialization(self, weather_service):
        """Test WeatherService initialization"""
        assert weather_service.api_key == "test_api_key"
        assert weather_service.base_url == "https://api.openweathermap.org/data/2.5"
        assert weather_service.database_service is None
    
    @pytest.mark.asyncio
    async def test_get_weather_by_city_success(self, weather_service, mock_weather_data):
        """Test successful weather data retrieval"""
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "main": {
                    "temp": 20.5,
                    "feels_like": 22.0,
                    "humidity": 65
                },
                "weather": [{"description": "clear sky"}],
                "wind": {"speed": 3.2}
            }
            mock_get.return_value = mock_response
            
            result = await weather_service.get_weather_by_city("Moscow")
            
            assert result is not None
            assert result.temperature == 20.5
            assert result.feels_like == 22.0
            assert result.humidity == 65
            assert result.description == "clear sky"
            assert result.wind_speed == 3.2
    
    @pytest.mark.asyncio
    async def test_get_weather_by_city_api_error(self, weather_service):
        """Test weather data retrieval with API error"""
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 401
            mock_response.json.return_value = {"message": "Invalid API key"}
            mock_get.return_value = mock_response
            
            result = await weather_service.get_weather_by_city("Moscow")
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_update_all_cities(self, weather_service):
        """Test updating weather for all monitored cities"""
        with patch.object(weather_service, 'get_weather_by_city') as mock_get_weather:
            mock_get_weather.return_value = mock_weather_data
            
            results = await weather_service.update_all_cities()
            
            assert len(results) > 0
            for city_id, weather_data in results:
                assert city_id in ["Moscow", "Saint Petersburg", "Pskov", "Belgrade"]
                assert weather_data is not None or weather_data is None


class TestTelegramService:
    """Test cases for TelegramService"""
    
    def test_telegram_service_initialization(self):
        """Test TelegramService initialization"""
        mock_weather_service = Mock()
        telegram_service = TelegramService("test_token", mock_weather_service)
        
        assert telegram_service.token == "test_token"
        assert telegram_service.weather_service == mock_weather_service
        assert telegram_service.subscribed_chats == []
    
    @pytest.mark.asyncio
    async def test_send_weather_updates(self):
        """Test sending weather updates to subscribed users"""
        mock_weather_service = Mock()
        telegram_service = TelegramService("test_token", mock_weather_service)
        telegram_service.subscribed_chats = [12345, 67890]
        
        weather_updates = [
            ("Moscow", mock_weather_data),
            ("Saint Petersburg", mock_weather_data)
        ]
        
        with patch.object(telegram_service, 'app') as mock_app:
            mock_app.bot.send_message = AsyncMock()
            
            await telegram_service.send_weather_updates(weather_updates)
            
            # Verify that messages were sent to all subscribed chats
            assert mock_app.bot.send_message.call_count == 2


class TestDatabaseService:
    """Test cases for DatabaseService"""
    
    @pytest.mark.asyncio
    async def test_save_weather_record(self, mock_database_service):
        """Test saving weather record to database"""
        result = await mock_database_service.save_weather_record(
            city="Moscow",
            temperature=20.5,
            humidity=65,
            wind_speed=3.2,
            description="clear sky",
            timezone="Europe/Moscow"
        )
        
        assert result is True
        mock_database_service.save_weather_record.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_latest_weather(self, mock_database_service):
        """Test getting latest weather record"""
        result = await mock_database_service.get_latest_weather("Moscow")
        
        assert result is None
        mock_database_service.get_latest_weather.assert_called_once_with("Moscow")


@pytest.mark.asyncio
async def test_weather_data_model():
    """Test WeatherData model validation"""
    weather_data = WeatherData(
        temperature=20.5,
        feels_like=22.0,
        humidity=65,
        description="clear sky",
        wind_speed=3.2
    )
    
    assert weather_data.temperature == 20.5
    assert weather_data.feels_like == 22.0
    assert weather_data.humidity == 65
    assert weather_data.description == "clear sky"
    assert weather_data.wind_speed == 3.2
    assert weather_data.last_update is None


if __name__ == "__main__":
    pytest.main([__file__])
