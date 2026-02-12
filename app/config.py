"""Application configuration using Pydantic Settings."""

from typing import List, Optional
import json
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Bot Configuration
    bot_token: Optional[str] = Field(default=None, description="Telegram bot token from @BotFather")

    # Database Configuration
    database_url: Optional[str] = Field(default=None, description="PostgreSQL connection URL")

    # Redis Configuration
    redis_url: Optional[str] = Field(default=None, description="Redis connection URL")

    # Security
    secret_key: Optional[str] = Field(default=None, min_length=32, description="Secret key for JWT and encryption")
    allowed_origins: List[str] = Field(default_factory=lambda: ["http://localhost:3000"], description="Allowed CORS origins")

    # Admin Configuration
    admin_telegram_ids: List[int] = Field(default_factory=list, description="List of admin Telegram IDs")

    # Optional: Telegram-based order notifications (for guest orders)
    telegram_bot_token: Optional[str] = Field(default=None, description="Telegram bot token for notifications")
    order_telegram_chat_id: Optional[int] = Field(default=None, description="Telegram chat_id to send new order notifications")

    # Timezone
    timezone: str = Field(default="Europe/Moscow", description="Application timezone")

    # Backup Configuration
    backup_enabled: bool = Field(default=True)
    backup_cron: str = Field(default="0 2 * * *")
    backup_retention_days: int = Field(default=7)
    backup_dir: str = Field(default="/app/backups")
    backup_tg_chat_id: Optional[str] = Field(default=None)
    backup_tg_thread_id: Optional[int] = Field(default=None)
    backup_max_tg_mb: int = Field(default=45)
    backup_compress_level: int = Field(default=6)

    # Feature Flags (v1.1)
    feature_promo_codes: bool = Field(default=False)
    feature_delivery_zones: bool = Field(default=False)
    feature_reviews: bool = Field(default=False)
    feature_online_payments: bool = Field(default=False)
    feature_external_backup: bool = Field(default=False)

    @field_validator("admin_telegram_ids", mode="before")
    @classmethod
    def parse_admin_ids(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            s = v.strip()
            if s.startswith("[") and s.endswith("]"):
                try:
                    data = json.loads(s)
                    return [int(x) for x in data if isinstance(x, int) or (isinstance(x, str) and x.isdigit())]
                except Exception:
                    pass
            return [int(x.strip()) for x in s.split(",") if x.strip()]
        return v

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v):
        if v is None:
            return v
        if len(v) < 32:
            raise ValueError("Secret key must be at least 32 characters")
        return v


# Global settings instance
settings = Settings()
