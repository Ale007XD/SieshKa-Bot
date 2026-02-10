"""Time utilities."""

from datetime import datetime, time, timezone as dt_timezone
from typing import Optional
import pytz

from app.config import settings


def get_timezone() -> pytz.timezone:
    """Get configured timezone."""
    return pytz.timezone(settings.timezone)


def now() -> datetime:
    """Get current datetime in configured timezone."""
    return datetime.now(get_timezone())


def utc_now() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(dt_timezone.utc)


def to_timezone(dt: datetime, tz: Optional[str] = None) -> datetime:
    """Convert datetime to timezone."""
    if tz is None:
        tz = settings.timezone
    
    timezone = pytz.timezone(tz)
    
    if dt.tzinfo is None:
        dt = pytz.utc.localize(dt)
    
    return dt.astimezone(timezone)


def is_working_hours(
    working_start: str = "09:00",
    working_end: str = "22:00"
) -> bool:
    """Check if current time is within working hours."""
    current = now()
    
    # Parse working hours
    start_hour, start_minute = map(int, working_start.split(':'))
    end_hour, end_minute = map(int, working_end.split(':'))
    
    start_time = time(start_hour, start_minute)
    end_time = time(end_hour, end_minute)
    
    current_time = current.time()
    
    if start_time <= end_time:
        return start_time <= current_time <= end_time
    else:
        # Working hours span midnight
        return current_time >= start_time or current_time <= end_time


def format_duration(minutes: int) -> str:
    """Format duration in minutes to human-readable string."""
    if minutes < 60:
        return f"{minutes} мин"
    
    hours = minutes // 60
    mins = minutes % 60
    
    if mins == 0:
        return f"{hours} ч"
    
    return f"{hours} ч {mins} мин"
