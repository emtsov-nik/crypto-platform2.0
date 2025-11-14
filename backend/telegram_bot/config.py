"""
Telegram Bot Configuration
"""
import os
from typing import List

# Telegram Bot Token (get from @BotFather)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# Backend API URL
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://backend:8000")

# Allowed Telegram User IDs (for authentication)
# Add your Telegram user ID here for access control
ALLOWED_USER_IDS: List[int] = [
    # Add user IDs here, e.g.: 123456789
]

# Get from environment variable (comma-separated list)
allowed_ids_str = os.getenv("TELEGRAM_ALLOWED_USER_IDS", "")
if allowed_ids_str:
    try:
        ALLOWED_USER_IDS = [int(uid.strip()) for uid in allowed_ids_str.split(",") if uid.strip()]
    except ValueError:
        print("⚠️ Warning: Invalid TELEGRAM_ALLOWED_USER_IDS format")

# Bot settings
BOT_USERNAME = os.getenv("TELEGRAM_BOT_USERNAME", "crypto_trading_bot")

# Enable/disable authentication
REQUIRE_AUTH = os.getenv("TELEGRAM_REQUIRE_AUTH", "true").lower() == "true"

# Notification settings
ENABLE_NOTIFICATIONS = os.getenv("TELEGRAM_ENABLE_NOTIFICATIONS", "true").lower() == "true"

# Polling settings
POLLING_INTERVAL = int(os.getenv("TELEGRAM_POLLING_INTERVAL", "1"))

# Logging
LOG_LEVEL = os.getenv("TELEGRAM_LOG_LEVEL", "INFO")
