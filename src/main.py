import os
import time
from typing import List, Optional
from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from src.weather_service import WeatherService
from src.database_service import DatabaseService
import logging
import sys
import asyncio
from app.telegram_service import TelegramService
from src.scheduler import WeatherScheduler
import signal
from datetime import datetime
import pytz

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app_20250707.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="OpenWeather Dashboard")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize database service with error handling
try:
    db_service = DatabaseService()
    db_enabled = True
    logger.info("Database connection successful")
except Exception as e:
    db_enabled = False
    db_service = None
    logger.warning(f"Database connection failed: {e}. Running without database.")

# Initialize weather service with database
weather_service = WeatherService(database_service=db_service)

# Initialize telegram bot
telegram_service = None
if os.getenv("TELEGRAM_BOT_TOKEN"):
    try:
        logger.info("Attempting to initialize Telegram bot...")
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        logger.info(f"Using Telegram bot token: {bot_token[:5]}...")
        telegram_service = TelegramService(bot_token, weather_service)
        logger.info("Telegram bot service created")
    except Exception as e:
        logger.error(f"Failed to initialize Telegram bot: {e}")
        telegram_service = None
else:
    logger.warning("TELEGRAM_BOT_TOKEN not found in environment variables")

# Initialize database if enabled
@app.on_event("startup")
async def startup_event():
    if db_enabled:
        try:
            await db_service.initialize_database()
            logger.info("Database initialized successfully")
            # Start weather updates after database is initialized
            await weather_service.start_updates()
            logger.info("Weather updates started")
            
            # Initialize and start telegram bot if available
            if telegram_service:
                try:
                    logger.info("Initializing Telegram bot...")
                    await telegram_service.initialize()
                    logger.info("Starting Telegram bot...")
                    await telegram_service.start()
                    logger.info("Telegram bot started successfully")
                    
                    # Initialize and start the scheduler
                    logger.info("Starting weather scheduler...")
                    scheduler = WeatherScheduler(weather_service, telegram_service)
                    asyncio.create_task(scheduler.start_scheduler())
                    logger.info("Weather scheduler started successfully")
                    
                except Exception as e:
                    logger.error(f"Failed to start Telegram bot or scheduler: {e}")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            
@app.on_event("shutdown")
async def shutdown_event():
    if hasattr(weather_service, 'stop_updates'):
        await weather_service.stop_updates()
        logger.info("Weather updates stopped")
    
    if telegram_service:
        try:
            await telegram_service.stop()
            logger.info("Telegram bot stopped")
        except Exception as e:
            logger.error(f"Error stopping Telegram bot: {e}")

# Mount templates directory
templates = Jinja2Templates(directory="templates")

LOCK_FILE = "bot.lock"
should_stop = False

def signal_handler(signum, frame):
    """
    Handle termination signals
    """
    global should_stop
    logger.info(f"Received signal {signum}. Shutting down gracefully...")
    should_stop = True

def is_process_running(pid):
    """
    Check if a process with given PID is running
    """
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False

async def cleanup():
    """
    Cleanup function to be called before shutdown
    """
    global telegram_service
    if telegram_service:
        try:
            await telegram_service.stop_bot()
        except Exception as e:
            logger.error(f"Error stopping telegram service: {e}")
    
    try:
        if os.path.exists(LOCK_FILE):
            os.remove(LOCK_FILE)
            logger.info("Lock file removed during cleanup")
    except Exception as e:
        logger.error(f"Error removing lock file during cleanup: {e}")

async def run_bot() -> None:
    """
    Main function to start the bot and scheduler
    """
    global should_stop
    
    # Check if bot is already running
    if os.path.exists(LOCK_FILE):
        try:
            with open(LOCK_FILE, 'r') as f:
                pid = int(f.read().strip())
            
            if is_process_running(pid):
                logger.error(f"Bot is already running with PID {pid}")
                return
            else:
                logger.info("Found stale lock file, removing it")
                os.remove(LOCK_FILE)
        except (ValueError, IOError) as e:
            logger.error(f"Error reading lock file: {e}")
            try:
                os.remove(LOCK_FILE)
            except OSError as e:
                logger.error(f"Error removing stale lock file: {e}")
                return

    # Create lock file with timestamp
    try:
        with open(LOCK_FILE, 'w') as f:
            f.write(f"{os.getpid()}\n{int(time.time())}")
    except IOError as e:
        logger.error(f"Could not create lock file: {e}")
        return

    # Initialize services
    # The TelegramService is now initialized in startup_event
    scheduler = WeatherScheduler(weather_service, telegram_service)
    scheduler_task = None
    
    try:
        # Start the scheduler
        scheduler_task = asyncio.create_task(scheduler.start_scheduler())
        
        # Run the bot with proper lifecycle management
        # The bot is now started in startup_event
        # await telegram_service.run_bot() # This line is no longer needed here
        
    except Exception as e:
        logger.error(f"Error in run_bot function: {e}")
        raise
    finally:
        # Cancel scheduler task if it exists
        if scheduler_task is not None:
            scheduler_task.cancel()
            try:
                await scheduler_task
            except asyncio.CancelledError:
                pass
        
        # Remove lock file
        try:
            if os.path.exists(LOCK_FILE):
                os.remove(LOCK_FILE)
                logger.info("Lock file removed during cleanup")
        except Exception as e:
            logger.error(f"Error removing lock file during cleanup: {e}")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, cities: Optional[str] = None):
    weather_data = await weather_service.update_all_cities()
    
    # Convert weather data to format expected by template
    formatted_data = []
    for city, data in weather_data:
        if data:
            formatted_data.append({
                "name": city,
                "main": {
                    "temp": data.temperature,
                    "humidity": data.humidity
                },
                "weather": [{"description": data.description}],
                "wind": {"speed": data.wind_speed},
                "sys": {"country": ""},  # Add country code if available
                "recorded_at_moscow": datetime.now(pytz.timezone('Europe/Moscow'))
            })
        else:
            formatted_data.append({"error": f"Failed to get weather data for {city}"})
    
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request, 
            "weather_list": formatted_data,
            "db_enabled": db_enabled
        }
    )

@app.get("/api/weather")
async def get_weather(city: Optional[str] = None):
    if not city:
        return {"error": "City parameter is required"}
    
    weather_data = await weather_service.get_weather_by_city(city)
    if weather_data:
        return {
            "name": city,
            "main": {
                "temp": weather_data.temperature,
                "humidity": weather_data.humidity
            },
            "weather": [{"description": weather_data.description}],
            "wind": {"speed": weather_data.wind_speed},
            "recorded_at_moscow": datetime.now(pytz.timezone('Europe/Moscow'))
        }
    else:
        return {"error": f"Failed to get weather data for {city}"}

@app.get("/api/weather/multiple")
async def get_weather_multiple(cities: List[str] = Query(None)):
    if not cities:
        # Если города не указаны, получаем погоду для всех отслеживаемых городов
        weather_data = await weather_service.update_all_cities()
    else:
        # Если указаны конкретные города, получаем погоду только для них
        tasks = [weather_service.get_weather_by_city(city) for city in cities]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        weather_data = list(zip(cities, results))
    
    formatted_data = []
    for city, data in weather_data:
        if isinstance(data, Exception):
            formatted_data.append({"error": f"Failed to get weather data for {city}: {str(data)}"})
        elif data:
            formatted_data.append({
                "name": city,
                "main": {
                    "temp": data.temperature,
                    "humidity": data.humidity
                },
                "weather": [{"description": data.description}],
                "wind": {"speed": data.wind_speed},
                "recorded_at_moscow": datetime.now(pytz.timezone('Europe/Moscow'))
            })
        else:
            formatted_data.append({"error": f"Failed to get weather data for {city}"})
    
    return formatted_data

@app.get("/api/weather/history")
async def get_weather_history(city: Optional[str] = None, limit: int = 10):
    if not db_enabled:
        return {"error": "Database is not enabled"}
    try:
        history = await db_service.get_weather_history(city, limit)
        return history
    except Exception as e:
        logger.error(f"Error getting weather history: {e}")
        return {"error": "Failed to get weather history"}

if __name__ == '__main__':
    loop = None
    try:
        # Set up signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Create and set event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Run the bot
        loop.run_until_complete(run_bot())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot stopped due to error: {e}")
    finally:
        if loop is not None:
            try:
                # Cancel all running tasks
                for task in asyncio.all_tasks(loop):
                    task.cancel()
                
                # Wait for tasks to be cancelled
                loop.run_until_complete(asyncio.gather(*asyncio.all_tasks(loop), return_exceptions=True))
                
                # Stop and close the loop
                loop.stop()
                loop.close()
                
                logger.info("Event loop closed successfully")
            except Exception as e:
                logger.error(f"Error during event loop cleanup: {e}")
            finally:
                # Ensure we remove the lock file
                if os.path.exists(LOCK_FILE):
                    try:
                        os.remove(LOCK_FILE)
                        logger.info("Lock file removed")
                    except OSError as e:
                        logger.error(f"Error removing lock file: {e}") 