"""Services package."""

from app.services.menu_service import MenuService
from app.services.archive_service import ArchiveService
from app.services.cart_service import CartService, CartItem
from app.services.order_service import OrderService
from app.services.user_service import UserService
from app.services.notification_service import NotificationService
from app.services.stats_service import StatsService
from app.services.import_service import ImportService
from app.services.settings_service import SettingsService

# v1.1 Services (safe no-op)
from app.services.promo_code_service import PromoCodeService
from app.services.delivery_zone_service import DeliveryZoneService
from app.services.review_service import ReviewService
from app.services.payment_service import PaymentService
from app.services.backup_storage_service import BackupStorageService

__all__ = [
    "MenuService",
    "ArchiveService",
    "CartService",
    "CartItem",
    "OrderService",
    "UserService",
    "NotificationService",
    "StatsService",
    "ImportService",
    "SettingsService",
    # v1.1
    "PromoCodeService",
    "DeliveryZoneService",
    "ReviewService",
    "PaymentService",
    "BackupStorageService",
]
