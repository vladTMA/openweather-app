from contextlib import asynccontextmanager
import logging
from typing import Optional, AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from telegram import Bot
from telegram.ext import Application

logger = logging.getLogger(__name__)

class AppLifecycle:
    def __init__(self):
        self.db_engine: Optional[AsyncEngine] = None
        self.session_factory: Optional[sessionmaker[AsyncSession]] = None
        self.bot_app: Optional[Application] = None
        self.is_running = False

    async def initialize_database(self, database_url: str):
        """Initialize database connection pool"""
        try:
            self.db_engine = create_async_engine(
                database_url,
                pool_pre_ping=True,  # Enable connection health checks
                pool_recycle=3600,   # Recycle connections every hour
                echo=False
            )
            
            # Create session factory
            self.session_factory = sessionmaker(
                bind=self.db_engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            # Test the connection
            async with self.db_engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
                
            logger.info("Database connection initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    async def initialize_bot(self, token: str):
        """Initialize Telegram bot"""
        try:
            if self.bot_app:
                logger.warning("Bot application already initialized")
                return

            self.bot_app = Application.builder().token(token).build()
            await self.bot_app.initialize()
            logger.info("Bot application initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize bot: {e}")
            raise

    async def start(self):
        """Start all application components"""
        if self.is_running:
            logger.warning("Application is already running")
            return

        try:
            if self.bot_app:
                await self.bot_app.start()
            self.is_running = True
            logger.info("Application started successfully")
        except Exception as e:
            logger.error(f"Failed to start application: {e}")
            await self.cleanup()
            raise

    async def cleanup(self):
        """Cleanup all resources"""
        try:
            if self.bot_app:
                await self.bot_app.stop()
                await self.bot_app.shutdown()
                self.bot_app = None

            if self.db_engine:
                await self.db_engine.dispose()
                self.db_engine = None

            self.session_factory = None
            self.is_running = False
            logger.info("Application cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            raise

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get database session with automatic cleanup"""
        if not self.session_factory:
            raise RuntimeError("Database not initialized")

        session = self.session_factory()
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise
        finally:
            await session.close()

    async def __aenter__(self):
        """Context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        await self.cleanup() 