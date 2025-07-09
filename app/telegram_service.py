import logging
from typing import Optional, Dict, List
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from .weather_service import WeatherService, WeatherData
from .config import MONITORED_CITIES, NOTIFICATION_SETTINGS, CITY_COMMANDS, CITY_NAMES
import asyncio
import pytz
from datetime import datetime

logger = logging.getLogger(__name__)

class TelegramService:
    def __init__(self, token: str, weather_service: WeatherService):
        self.token = token
        self.weather_service = weather_service
        self.app: Optional[Application] = None
        self.subscribed_chats: List[int] = []
        self._running = False
        self.moscow_tz = pytz.timezone('Europe/Moscow')

    def _get_moscow_time(self) -> str:
        """Get current Moscow time formatted as string"""
        now = datetime.now(self.moscow_tz)
        return now.strftime("%d.%m.%Y %H:%M:%S")
        
    async def initialize(self) -> None:
        """Initialize the bot application"""
        try:
            logger.info("Starting Telegram bot initialization with token: %s...", self.token[:5] if self.token else None)
            self.app = Application.builder().token(self.token).build()
            if self.app:  # Type guard
                self.app.add_handler(CommandHandler("start", self._start_command))
                self.app.add_handler(CommandHandler("weather", self._weather_command))
                self.app.add_handler(CommandHandler("help", self._help_command))
                self.app.add_handler(CommandHandler("subscribe", self._subscribe_command))
                self.app.add_handler(CommandHandler("unsubscribe", self._unsubscribe_command))
                self.app.add_handler(CommandHandler("cities", self._cities_command))
                
                # Добавляем обработчики для каждого города
                self.app.add_handler(CommandHandler("weather_moscow", self._weather_moscow_command))
                self.app.add_handler(CommandHandler("weather_spb", self._weather_spb_command))
                self.app.add_handler(CommandHandler("weather_pskov", self._weather_pskov_command))
                self.app.add_handler(CommandHandler("weather_belgrade", self._weather_belgrade_command))
                
                logger.info("Telegram bot initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Telegram bot: {e}")
            raise

    async def start(self) -> None:
        """Start the bot"""
        try:
            if not self.app:
                logger.info("Bot not initialized, initializing now...")
                await self.initialize()
            
            if not self.app:  # Double check after initialize
                raise RuntimeError("Failed to initialize Telegram bot")
                
            if not self._running:
                self._running = True
                logger.info("Starting bot polling...")
                # Start the bot in non-blocking mode
                await self.app.initialize()
                await self.app.start()
                # Use the correct polling method with type guard
                if self.app.updater:  # Type guard
                    await self.app.updater.start_polling(
                        allowed_updates=Update.ALL_TYPES,
                        drop_pending_updates=True
                    )
                    logger.info("Telegram bot polling started successfully")
                else:
                    raise RuntimeError("Telegram bot updater not initialized")
        except Exception as e:
            logger.error(f"Failed to start Telegram bot: {e}")
            await self.stop()
            raise

    async def stop(self) -> None:
        """Stop the bot"""
        try:
            if self.app and self._running:
                self._running = False
                # Stop the updater first
                if self.app.updater:
                    await self.app.updater.stop()
                # Then stop and shutdown the application
                await self.app.stop()
                await self.app.shutdown()
                logger.info("Telegram bot stopped successfully")
        except Exception as e:
            logger.error(f"Failed to stop Telegram bot: {e}")
            raise

    async def _start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        if update.message:  # Type guard
            logger.info("Received /start command from chat_id: %s", update.message.chat.id)
            await update.message.reply_text(
                "👋 Привет! Я бот погоды. Доступные команды:\n"
                "/weather - узнать погоду во всех отслеживаемых городах\n"
                "/weather_moscow - погода в Москве\n"
                "/weather_spb - погода в Санкт-Петербурге\n"
                "/weather_pskov - погода в Пскове\n"
                "/weather_belgrade - погода в Белграде\n"
                "/cities - список отслеживаемых городов\n"
                "/subscribe - подписаться на обновления\n"
                "/unsubscribe - отписаться от обновлений\n"
                "/help - показать это сообщение"
            )
            logger.info("Sent welcome message to chat_id: %s", update.message.chat.id)

    async def _help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        if update.message:  # Type guard
            logger.info("Received /help command from chat_id: %s", update.message.chat.id)
            await update.message.reply_text(
                "🌤 Доступные команды:\n"
                "/weather - узнать погоду во всех отслеживаемых городах\n"
                "/weather_moscow - погода в Москве\n"
                "/weather_spb - погода в Санкт-Петербурге\n"
                "/weather_pskov - погода в Пскове\n"
                "/weather_belgrade - погода в Белграде\n"
                "/cities - список отслеживаемых городов\n"
                "/subscribe - подписаться на обновления\n"
                "/unsubscribe - отписаться от обновлений\n"
                "/help - показать это сообщение"
            )
            logger.info("Sent help message to chat_id: %s", update.message.chat.id)

    async def _cities_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /cities command"""
        if update.message:  # Type guard
            logger.info("Received /cities command from chat_id: %s", update.message.chat.id)
            cities_list = "\n".join([f"• {CITY_NAMES[city]}" for city in MONITORED_CITIES])
            await update.message.reply_text(
                f"📍 Отслеживаемые города:\n{cities_list}"
            )
            logger.info("Sent cities list to chat_id: %s", update.message.chat.id)

    async def _subscribe_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /subscribe command"""
        if update.message and update.message.chat.id:  # Type guard
            chat_id = update.message.chat.id
            logger.info(f"Received /subscribe command from chat_id: {chat_id}")
            if chat_id not in self.subscribed_chats:
                self.subscribed_chats.append(chat_id)
                logger.info(f"Chat {chat_id} subscribed to weather updates. Total subscribers: {len(self.subscribed_chats)}")
                await update.message.reply_text(
                    "✅ Вы подписались на обновления погоды"
                )
            else:
                logger.info(f"Chat {chat_id} is already subscribed to weather updates")
                await update.message.reply_text(
                    "ℹ️ Вы уже подписаны на обновления"
                )

    async def _unsubscribe_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /unsubscribe command"""
        if update.message and update.message.chat.id:  # Type guard
            chat_id = update.message.chat.id
            logger.info(f"Received /unsubscribe command from chat_id: {chat_id}")
            if chat_id in self.subscribed_chats:
                self.subscribed_chats.remove(chat_id)
                logger.info(f"Chat {chat_id} unsubscribed from weather updates. Total subscribers: {len(self.subscribed_chats)}")
                await update.message.reply_text(
                    "✅ Вы отписались от обновлений погоды"
                )
            else:
                logger.info(f"Chat {chat_id} was not subscribed to weather updates")
                await update.message.reply_text(
                    "ℹ️ Вы не были подписаны на обновления"
                )

    async def _weather_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /weather command"""
        if not update.message:  # Type guard
            return
            
        try:
            if not context.args:
                # Если город не указан, показываем погоду во всех отслеживаемых городах
                weather_updates = await self.weather_service.update_all_cities()
                moscow_time = self._get_moscow_time()
                response = f"🌤 Текущая погода (МСК: {moscow_time}):\n\n"
                
                for city_id, weather in weather_updates:
                    city_name = CITY_NAMES.get(city_id, city_id)
                    if weather:
                        response += (
                            f"📍 {city_name}:\n"
                            f"🌡 Температура: {weather.temperature}°C\n"
                            f"🌡 Ощущается как: {weather.feels_like}°C\n"
                            f"💧 Влажность: {weather.humidity}%\n"
                            f"💨 Скорость ветра: {weather.wind_speed} м/с\n"
                            f"📝 {weather.description.capitalize()}\n\n"
                        )
                    else:
                        response += f"❌ Не удалось получить данные для {city_name}\n\n"
                        
                await update.message.reply_text(response)
                return

            # Получаем погоду для конкретного города
            city = " ".join(context.args).lower()
            
            # Проверяем, есть ли город в списке команд
            city_id = None
            for cmd, cmd_city_id in CITY_COMMANDS.items():
                if city in cmd.lower():
                    city_id = cmd_city_id
                    break
            
            if not city_id:
                await update.message.reply_text(
                    "❌ Город не найден. Используйте команды:\n"
                    "/weather_moscow - погода в Москве\n"
                    "/weather_spb - погода в Санкт-Петербурге\n"
                    "/weather_pskov - погода в Пскове\n"
                    "/weather_belgrade - погода в Белграде"
                )
                return
            
            weather = await self.weather_service.get_weather_by_city(city_id)
            city_name = CITY_NAMES.get(city_id, city_id)

            if not weather:
                await update.message.reply_text(
                    f"❌ Не удалось получить данные о погоде для города {city_name}"
                )
                return

            response = (
                f"🌤 Погода в {city_name}:\n"
                f"🌡 Температура: {weather.temperature}°C\n"
                f"🌡 Ощущается как: {weather.feels_like}°C\n"
                f"💧 Влажность: {weather.humidity}%\n"
                f"💨 Скорость ветра: {weather.wind_speed} м/с\n"
                f"📝 {weather.description.capitalize()}"
            )
            
            await update.message.reply_text(response)

        except Exception as e:
            logger.error(f"Error in weather command: {e}")
            await update.message.reply_text(
                "❌ Произошла ошибка при получении данных о погоде"
            )

    async def send_weather_updates(self, weather_updates: List[tuple[str, Optional[WeatherData]]]) -> None:
        """Send weather updates to subscribed users"""
        if not self.subscribed_chats:
            return
            
        try:
            moscow_time = self._get_moscow_time()
            message = f"🌤 Обновление погоды (МСК: {moscow_time}):\n\n"
            
            for city_id, weather in weather_updates:
                city_name = CITY_NAMES.get(city_id, city_id)
                if weather:
                    message += (
                        f"📍 {city_name}:\n"
                        f"🌡 Температура: {weather.temperature}°C\n"
                        f"🌡 Ощущается как: {weather.feels_like}°C\n"
                        f"💧 Влажность: {weather.humidity}%\n"
                        f"💨 Скорость ветра: {weather.wind_speed} м/с\n"
                        f"📝 {weather.description.capitalize()}\n\n"
                    )
                else:
                    message += f"❌ Не удалось получить данные для {city_name}\n\n"
            
            if self.app:
                for chat_id in self.subscribed_chats:
                    try:
                        await self.app.bot.send_message(chat_id=chat_id, text=message)
                    except Exception as e:
                        logger.error(f"Failed to send update to chat {chat_id}: {e}")
                        
        except Exception as e:
            logger.error(f"Error sending weather updates: {e}")

    async def send_weather_alert(self, city: str, alert_type: str, message: str) -> None:
        """Send weather alert to subscribed users"""
        if not self.subscribed_chats:
            return
            
        try:
            moscow_time = self._get_moscow_time()
            alert_message = (
                f"⚠️ Погодное предупреждение (МСК: {moscow_time})\n"
                f"📍 {city}\n"
                f"Тип: {alert_type}\n"
                f"Сообщение: {message}"
            )
            
            if self.app:
                for chat_id in self.subscribed_chats:
                    try:
                        await self.app.bot.send_message(chat_id=chat_id, text=alert_message)
                    except Exception as e:
                        logger.error(f"Failed to send alert to chat {chat_id}: {e}")
                        
        except Exception as e:
            logger.error(f"Error sending weather alert: {e}")

    async def _get_city_weather(self, city_id: str, update: Update) -> None:
        """Get weather for specific city"""
        if not update.message:
            return
            
        try:
            weather = await self.weather_service.get_weather_by_city(city_id)
            city_name = CITY_NAMES.get(city_id, city_id)
            moscow_time = self._get_moscow_time()
            
            if weather:
                response = (
                    f"🌤 Погода в {city_name} (МСК: {moscow_time}):\n"
                    f"🌡 Температура: {weather.temperature}°C\n"
                    f"🌡 Ощущается как: {weather.feels_like}°C\n"
                    f"💧 Влажность: {weather.humidity}%\n"
                    f"💨 Скорость ветра: {weather.wind_speed} м/с\n"
                    f"📝 {weather.description.capitalize()}"
                )
            else:
                response = f"❌ Не удалось получить данные для {city_name}"
                
            await update.message.reply_text(response)
            
        except Exception as e:
            logger.error(f"Error getting weather for {city_id}: {e}")
            await update.message.reply_text(
                "❌ Произошла ошибка при получении данных о погоде"
            )

    async def _weather_moscow_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /weather_moscow command"""
        if update.message:  # Type guard
            logger.info("Received /weather_moscow command from chat_id: %s", update.message.chat.id)
            await self._get_city_weather("Moscow", update)

    async def _weather_spb_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /weather_spb command"""
        if update.message:  # Type guard
            logger.info("Received /weather_spb command from chat_id: %s", update.message.chat.id)
            await self._get_city_weather("Saint Petersburg", update)

    async def _weather_pskov_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /weather_pskov command"""
        if update.message:  # Type guard
            logger.info("Received /weather_pskov command from chat_id: %s", update.message.chat.id)
            await self._get_city_weather("Pskov", update)

    async def _weather_belgrade_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /weather_belgrade command"""
        if update.message:  # Type guard
            logger.info("Received /weather_belgrade command from chat_id: %s", update.message.chat.id)
            await self._get_city_weather("Belgrade", update) 