import pytest
import os
from unittest.mock import patch, Mock
from app.config import (
    MONITORED_CITIES,
    CITY_NAMES,
    CITY_COMMANDS,
    SCHEDULED_HOURS,
    SCHEDULED_MINUTES,
    UPDATE_INTERVAL,
    ALERT_THRESHOLDS,
    NOTIFICATION_SETTINGS
)


class TestConfig:
    """Test cases for configuration settings"""
    
    def test_monitored_cities(self):
        """Test monitored cities configuration"""
        assert isinstance(MONITORED_CITIES, list)
        assert len(MONITORED_CITIES) > 0
        assert "Moscow" in MONITORED_CITIES
        assert "Saint Petersburg" in MONITORED_CITIES
    
    def test_city_names_mapping(self):
        """Test city names mapping"""
        assert isinstance(CITY_NAMES, dict)
        assert "Moscow" in CITY_NAMES
        assert CITY_NAMES["Moscow"] == "Москва"
        assert CITY_NAMES["Saint Petersburg"] == "Санкт-Петербург"
    
    def test_city_commands_mapping(self):
        """Test city commands mapping"""
        assert isinstance(CITY_COMMANDS, dict)
        assert "moscow" in CITY_COMMANDS
        assert CITY_COMMANDS["moscow"] == "Moscow"
        assert CITY_COMMANDS["spb"] == "Saint Petersburg"
    
    def test_scheduled_hours(self):
        """Test scheduled hours configuration"""
        assert isinstance(SCHEDULED_HOURS, list)
        assert 8 in SCHEDULED_HOURS
        assert 21 in SCHEDULED_HOURS
    
    def test_scheduled_minutes(self):
        """Test scheduled minutes configuration"""
        assert isinstance(SCHEDULED_MINUTES, dict)
        assert 8 in SCHEDULED_MINUTES
        assert 21 in SCHEDULED_MINUTES
        assert SCHEDULED_MINUTES[8] == 0
        assert SCHEDULED_MINUTES[21] == 30
    
    def test_update_interval(self):
        """Test update interval configuration"""
        assert isinstance(UPDATE_INTERVAL, int)
        assert UPDATE_INTERVAL > 0
        assert UPDATE_INTERVAL == 1800  # 30 minutes
    
    def test_alert_thresholds(self):
        """Test alert thresholds configuration"""
        assert isinstance(ALERT_THRESHOLDS, dict)
        assert "TEMPERATURE_CHANGE" in ALERT_THRESHOLDS
        assert "WIND_SPEED" in ALERT_THRESHOLDS
        assert ALERT_THRESHOLDS["TEMPERATURE_CHANGE"] == 5.0
        assert ALERT_THRESHOLDS["WIND_SPEED"] == 15.0
    
    def test_notification_settings(self):
        """Test notification settings configuration"""
        assert isinstance(NOTIFICATION_SETTINGS, dict)
        assert "SEND_REGULAR_UPDATES" in NOTIFICATION_SETTINGS
        assert "SEND_ALERTS" in NOTIFICATION_SETTINGS
        assert NOTIFICATION_SETTINGS["SEND_REGULAR_UPDATES"] is True
        assert NOTIFICATION_SETTINGS["SEND_ALERTS"] is True


if __name__ == "__main__":
    pytest.main([__file__])
