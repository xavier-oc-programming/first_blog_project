from pathlib import Path

from dotenv import load_dotenv
import os

load_dotenv(Path(__file__).parent / ".env")

# Server
SECRET_KEY = os.getenv("SECRET_KEY", "dev-fallback-key-change-in-production")

# Data / paths
# DB_URI: set to a PostgreSQL URL on the host (e.g. Render), falls back to SQLite locally
DB_URI = os.getenv("DB_URI", "sqlite:///posts.db")
