"""Custom exceptions for the application."""


class AppException(Exception):
    """Base application exception."""
    
    def __init__(self, message: str, code: str = None):
        self.message = message
        self.code = code
        super().__init__(self.message)


class NotFoundException(AppException):
    """Resource not found exception."""
    
    def __init__(self, resource: str, identifier: str = None):
        message = f"{resource} not found"
        if identifier:
            message += f": {identifier}"
        super().__init__(message, "NOT_FOUND")


class ValidationException(AppException):
    """Validation error exception."""
    
    def __init__(self, message: str):
        super().__init__(message, "VALIDATION_ERROR")


class PermissionDeniedException(AppException):
    """Permission denied exception."""
    
    def __init__(self, message: str = "Permission denied"):
        super().__init__(message, "PERMISSION_DENIED")


class InvalidStateTransitionException(AppException):
    """Invalid order state transition exception."""
    
    def __init__(self, from_status: str, to_status: str):
        message = f"Cannot transition from {from_status} to {to_status}"
        super().__init__(message, "INVALID_STATE_TRANSITION")


class InsufficientStockException(AppException):
    """Insufficient stock exception."""
    
    def __init__(self, product_name: str, available: int, requested: int):
        message = f"Insufficient stock for {product_name}: {available} available, {requested} requested"
        super().__init__(message, "INSUFFICIENT_STOCK")


class PromoCodeException(AppException):
    """Promo code related exception."""
    
    def __init__(self, message: str):
        super().__init__(message, "PROMO_CODE_ERROR")


class DuplicateException(AppException):
    """Duplicate resource exception."""
    
    def __init__(self, resource: str, field: str):
        message = f"{resource} with this {field} already exists"
        super().__init__(message, "DUPLICATE_ERROR")
