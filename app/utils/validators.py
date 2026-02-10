"""Validators for user input."""

import re
from typing import Optional

from app.utils.exceptions import ValidationException


class Validators:
    """Input validation utilities."""
    
    @staticmethod
    def validate_phone(phone: str) -> str:
        """Validate and normalize phone number to plus-prefixed digits."""
        # Remove all non-digit characters
        digits = re.sub(r"\D", "", phone)

        # Check length (should be 10-15 digits)
        if len(digits) < 10 or len(digits) > 15:
            raise ValidationException("Неверный формат телефона")

        # Normalize Russian 8... numbers to 7... with leading +
        if digits.startswith("8") and len(digits) == 11:
            digits = '7' + digits[1:]

        # Always return in E.164-like format with leading +
        return f"+{digits}"
    
    @staticmethod
    def validate_address(address: str) -> str:
        """Validate delivery address."""
        if not address or len(address.strip()) < 5:
            raise ValidationException("Адрес слишком короткий")
        
        if len(address) > 500:
            raise ValidationException("Адрес слишком длинный (макс. 500 символов)")
        
        return address.strip()
    
    @staticmethod
    def validate_comment(comment: Optional[str]) -> Optional[str]:
        """Validate order comment."""
        if not comment:
            return None
        
        comment = comment.strip()
        
        if len(comment) > 1000:
            raise ValidationException("Комментарий слишком длинный (макс. 1000 символов)")
        
        return comment if comment else None
    
    @staticmethod
    def validate_quantity(quantity: int, max_quantity: int = 100) -> int:
        """Validate order item quantity."""
        if not isinstance(quantity, int) or quantity < 1:
            raise ValidationException("Количество должно быть положительным числом")
        
        if quantity > max_quantity:
            raise ValidationException(f"Максимальное количество: {max_quantity}")
        
        return quantity
    
    @staticmethod
    def validate_category_name(name: str) -> str:
        """Validate category name."""
        if not name or len(name.strip()) < 2:
            raise ValidationException("Название категории слишком короткое (мин. 2 символа)")
        
        if len(name) > 255:
            raise ValidationException("Название категории слишком длинное (макс. 255 символов)")
        
        return name.strip()
    
    @staticmethod
    def validate_product_name(name: str) -> str:
        """Validate product name."""
        if not name or len(name.strip()) < 2:
            raise ValidationException("Название товара слишком короткое (мин. 2 символа)")
        
        if len(name) > 255:
            raise ValidationException("Название товара слишком длинное (макс. 255 символов)")
        
        return name.strip()
    
    @staticmethod
    def validate_price(price: float) -> float:
        """Validate product price."""
        if not isinstance(price, (int, float)):
            raise ValidationException("Цена должна быть числом")
        
        if price < 0:
            raise ValidationException("Цена не может быть отрицательной")
        
        if price > 999999.99:
            raise ValidationException("Цена слишком высокая")
        
        return float(price)

    @staticmethod
    def validate_text(text: str, min_len: int = 1, max_len: int = 255, field_name: str = "Поле") -> str:
        """Validate arbitrary text field with length bounds."""
        if text is None:
            raise ValidationException(f"{field_name} обязательно.")
        value = text.strip()
        if len(value) < min_len:
            raise ValidationException(f"{field_name} слишком короткое (мин. {min_len} симв.)")
        if len(value) > max_len:
            raise ValidationException(f"{field_name} слишком длинное (макс. {max_len} симв.)")
        return value
