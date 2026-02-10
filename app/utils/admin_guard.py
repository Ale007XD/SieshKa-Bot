from app.config import settings

def is_admin_callback(callback) -> bool:
    uid = getattr(callback.from_user, "id", None)
    admin_ids = getattr(settings, "admin_telegram_ids", [])
    if isinstance(admin_ids, list) and uid is not None:
        try:
            return int(uid) in admin_ids
        except Exception:
            return False
    return False


def is_admin_message(message) -> bool:
    uid = getattr(message.from_user, "id", None)
    admin_ids = getattr(settings, "admin_telegram_ids", [])
    if isinstance(admin_ids, list) and uid is not None:
        try:
            return int(uid) in admin_ids
        except Exception:
            return False
    return False
