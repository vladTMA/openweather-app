import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy import Column, Integer, Float, String, DateTime, text, select
from sqlalchemy.ext.declarative import declarative_base
from logging.handlers import RotatingFileHandler
from typing import Optional, List, Dict

# Get logger
logger = logging.getLogger(__name__)

# Configure logging format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler('logs/database.log', maxBytes=10485760, backupCount=5),
        logging.StreamHandler()
    ]
)

# Load environment variables
load_dotenv()
logger.info("Environment variables loaded")

Base = declarative_base()

class WeatherRecord(Base):
    __tablename__ = 'weather_records'
    
    id = Column(Integer, primary_key=True)
    city = Column(String, nullable=False)
    temperature = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)
    wind_speed = Column(Float, nullable=False)
    description = Column(String, nullable=False)
    recorded_at = Column(DateTime, nullable=False)
    timezone = Column(String, nullable=False)

class DatabaseService:
    def __init__(self):
        try:
            # Получаем параметры подключения
            db_host = os.getenv('DB_HOST')
            db_name = os.getenv('DB_NAME')
            db_user = os.getenv('DB_USER')
            db_password = os.getenv('DB_PASSWORD')
            
            # Логируем параметры (без пароля)
            logger.info("Database configuration:")
            logger.info(f"Host: {db_host}")
            logger.info(f"Database: {db_name}")
            logger.info(f"User: {db_user}")
            logger.info(f"Password: {'*' * (len(db_password) if db_password else 0)}")
        
            if not all([db_host, db_name, db_user, db_password]):
                missing = []
                if not db_host: missing.append('DB_HOST')
                if not db_name: missing.append('DB_NAME')
                if not db_user: missing.append('DB_USER')
                if not db_password: missing.append('DB_PASSWORD')
                error_msg = f"Missing database configuration: {', '.join(missing)}"
                logger.error(error_msg)
                raise ValueError(error_msg)
        
            # Create database URL for async connection
            db_url = f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}/{db_name}"
            logger.info(f"Database URL constructed (without password): postgresql+asyncpg://{db_user}:***@{db_host}/{db_name}")
        
            try:
                # Create async engine with connection pooling
                logger.info("Creating async database engine with connection pooling...")
                self.engine = create_async_engine(
                    db_url,
                    echo=True,
                    pool_size=5,
                    max_overflow=10,
                    pool_timeout=30,
                    pool_recycle=1800  # Recycle connections after 30 minutes
                )
                
                logger.info("Creating async session factory...")
                self.async_session = async_sessionmaker(
                    self.engine,
                    class_=AsyncSession,
                    expire_on_commit=False
                )
            
            except Exception as e:
                error_msg = f"Error during database setup: {str(e)}"
                logger.error(error_msg)
                raise Exception(error_msg)
                
        except Exception as e:
            error_msg = f"Error in DatabaseService initialization: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    async def initialize_database(self):
        """Initialize database tables and test connection"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            
        async with self.async_session() as session:
            logger.info("Testing database connection...")
            result = await session.execute(text("SELECT version()"))
            version = result.scalar()
            logger.info(f"Database connection successful. PostgreSQL version: {version}")

    def get_session(self) -> AsyncSession:
        """
        Get a new async database session
        """
        return self.async_session()

    async def save_weather_data(self, weather_data: Dict) -> bool:
        """
        Saves weather data to the database
        Args:
            weather_data (dict): Weather data to save
        Returns:
            bool: True if save was successful, False otherwise
        """
        async with self.get_session() as session:
            try:
                # Parse the date and time strings into a datetime object
                recorded_at = datetime.strptime(weather_data['recorded_at'], '%Y-%m-%d %H:%M:%S')

                record = WeatherRecord(
                    city=weather_data['city'],
                    temperature=weather_data['temp'],
                    humidity=weather_data['humidity'],
                    wind_speed=weather_data['wind_speed'],
                    description=weather_data['description'],
                    recorded_at=recorded_at,
                    timezone=weather_data['timezone']
                )
                
                session.add(record)
                await session.commit()
                
                logger.info(f"Weather data saved successfully for {weather_data['city']}")
                return True
            except Exception as e:
                await session.rollback()
                logger.error(f"Error saving weather data: {str(e)}")
                return False

    async def get_weather_history(self, city: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """
        Retrieves weather history from the database
        Args:
            city (str): Optional city filter
            limit (int): Maximum number of records to return
        Returns: list of weather records
        """
        async with self.get_session() as session:
            try:
                query = select(WeatherRecord).order_by(WeatherRecord.recorded_at.desc())
                if city:
                    query = query.filter(WeatherRecord.city == city)
                query = query.limit(limit)
                
                result = await session.execute(query)
                records = result.scalars().all()
                
                return [{
                    'city': record.city,
                    'temp': record.temperature,
                    'humidity': record.humidity,
                    'wind_speed': record.wind_speed,
                    'description': record.description,
                    'recorded_at': record.recorded_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'timezone': record.timezone
                } for record in records]
                
            except Exception as e:
                logger.error(f"Error retrieving weather history: {str(e)}")
                return []

    async def get_latest_weather(self, city: str) -> Optional[Dict]:
        """
        Get the latest weather record for a specific city
        """
        async with self.get_session() as session:
            try:
                query = (
                    select(WeatherRecord)
                    .filter(WeatherRecord.city == city)
                    .order_by(WeatherRecord.recorded_at.desc())
                    .limit(1)
                )
                
                result = await session.execute(query)
                record = result.scalar_one_or_none()
                
                if record:
                    return {
                        'city': record.city,
                        'temperature': record.temperature,
                        'humidity': record.humidity,
                        'wind_speed': record.wind_speed,
                        'description': record.description,
                        'recorded_at': record.recorded_at,
                        'timezone': record.timezone
                    }
                return None
            except Exception as e:
                logger.error(f"Error retrieving latest weather: {str(e)}")
                return None 