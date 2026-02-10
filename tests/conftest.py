"""Test configuration helpers."""
import os

# Ensure admin telegram IDs env var is JSON array to satisfy dotenv parsing in tests
os.environ.setdefault("ADMIN_TELEGRAM_IDS", "[]")
