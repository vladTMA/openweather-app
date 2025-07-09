import logging
from datetime import datetime
from typing import Optional, Callable, AsyncContextManager, AsyncGenerator
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from contextlib import asynccontextmanager
import pytz

logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self, get_session: Callable[[], AsyncContextManager[AsyncSession]]):
        self.get_session = get_session
        self.moscow_tz = pytz.timezone('Europe/Moscow')
        
    def _convert_to_moscow_time(self, utc_dt: datetime) -> datetime:
        """Convert UTC datetime to Moscow time"""
        if utc_dt.tzinfo is None:
            utc_dt = pytz.UTC.localize(utc_dt)
        return utc_dt.astimezone(self.moscow_tz)
        
    async def stop(self) -> None:
        """Stop the database service"""
        # Nothing to do here since we're using a session factory
        # and sessions are managed by the context manager
        logger.info("Database service stopped")
        
    @asynccontextmanager
    async def _transaction(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Transaction context manager that ensures proper commit/rollback handling
        """
        async with self.get_session() as session:
            try:
                yield session
                await session.commit()
                logger.debug("Transaction committed successfully")
            except SQLAlchemyError as e:
                await session.rollback()
                logger.error(f"Transaction rolled back due to error: {e}")
                raise
            except Exception as e:
                await session.rollback()
                logger.error(f"Transaction rolled back due to unexpected error: {e}")
                raise
            finally:
                await session.close()
                logger.debug("Database session closed")

    async def save_weather_record(self, city: str, temperature: float, humidity: int,
                                wind_speed: float, description: str, timezone: str) -> bool:
        """
        Save weather record to database
        
        Returns:
            bool: True if save was successful, False otherwise
        """
        try:
            async with self._transaction() as session:
                query = text("""
                    INSERT INTO weather_records 
                    (city, temperature, humidity, wind_speed, description, recorded_at, timezone)
                    VALUES (:city, :temp, :humidity, :wind, :descr, :recorded, :tz)
                    RETURNING id
                """)
                
                result = await session.execute(query, {
                    "city": city,
                    "temp": temperature,
                    "humidity": humidity,
                    "wind": wind_speed,
                    "descr": description,
                    "recorded": datetime.utcnow(),
                    "tz": timezone
                })
                
                record_id = result.scalar_one()
                logger.info(f"Saved weather record for {city} with id {record_id}")
                return True
                
        except SQLAlchemyError as e:
            logger.error(f"Database error saving weather record: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error saving weather record: {e}")
            return False

    async def get_latest_weather(self, city: str) -> Optional[dict]:
        """
        Get latest weather record for city
        
        Returns:
            Optional[dict]: Weather data if found, None otherwise
        """
        try:
            # Преобразуем ID города в название
            city_names = {
                "524901": "Moscow",
                "498817": "Saint Petersburg",
                "504341": "Pskov",
                "792680": "Belgrade"
            }
            city_name = city_names.get(city)
            if not city_name:
                print(f"Unknown city ID: {city}")
                return None

            async with self._transaction() as session:
                # Сначала проверим все записи в таблице
                check_query = text("SELECT DISTINCT city FROM weather_records")
                result = await session.execute(check_query)
                cities = result.fetchall()
                print(f"\nAvailable cities in database: {[city[0] for city in cities]}")
                print(f"Looking for city: {city_name}")
                
                query = text("""
                    SELECT id, temperature, humidity, wind_speed, description, recorded_at, timezone
                    FROM weather_records
                    WHERE city = :city
                    ORDER BY recorded_at DESC
                    LIMIT 1
                    FOR UPDATE SKIP LOCKED
                """)
                
                result = await session.execute(query, {"city": city_name})
                record = result.fetchone()
                
                if record:
                    moscow_time = self._convert_to_moscow_time(record.recorded_at)
                    return {
                        "id": record.id,
                        "temperature": record.temperature,
                        "humidity": record.humidity,
                        "wind_speed": record.wind_speed,
                        "description": record.description,
                        "recorded_at": record.recorded_at,
                        "recorded_at_moscow": moscow_time,
                        "timezone": record.timezone
                    }
                return None
                
        except SQLAlchemyError as e:
            logger.error(f"Database error retrieving weather history: {e}")
            print(f"SQL Error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error retrieving weather history: {e}")
            print(f"Error: {str(e)}")
            return None

    async def cleanup_old_records(self, days: int = 7) -> bool:
        """
        Remove weather records older than specified days
        
        Args:
            days: Number of days to keep records for
            
        Returns:
            bool: True if cleanup was successful, False otherwise
        """
        try:
            async with self._transaction() as session:
                query = text("""
                    DELETE FROM weather_records
                    WHERE recorded_at < NOW() - INTERVAL ':days days'
                    RETURNING id
                """)
                
                result = await session.execute(query, {"days": days})
                deleted_count = len(result.fetchall())
                logger.info(f"Cleaned up {deleted_count} old weather records")
                return True
                
        except SQLAlchemyError as e:
            logger.error(f"Database error during cleanup: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during cleanup: {e}")
            return False 