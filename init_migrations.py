#!/usr/bin/env python3
"""
Script to initialize Alembic migrations
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def init_migrations():
    """Initialize Alembic migrations"""
    try:
        import alembic
        from alembic.config import Config
        from alembic import command
        
        # Create alembic.ini if it doesn't exist
        alembic_cfg = Config("alembic.ini")
        
        # Initialize migrations
        command.init(alembic_cfg, "migrations")
        
        print("✅ Alembic migrations initialized successfully!")
        print("📁 Migration files created in migrations/ directory")
        
    except ImportError:
        print("❌ Alembic not installed. Please install it first:")
        print("pip install alembic")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error initializing migrations: {e}")
        sys.exit(1)

if __name__ == "__main__":
    init_migrations()
