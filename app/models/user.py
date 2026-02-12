from __future__ import annotations

"""User model for all roles (client, admin, manager, kitchen, packer, courier)."""

from typing import List, Optional

from sqlalchemy import Boolean, BigInteger, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.utils.enums import UserRole, STAFF_ROLES, ADMIN_ROLES, MANAGER_ROLES, CLIENT_ROLES


class User(BaseModel):
    """User model representing all roles in the system."""

    __tablename__ = "users"

    # Roles are defined in enums and imported as STAFF_ROLES, ADMIN_ROLES, MANAGER_ROLES, CLIENT_ROLES

    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True, nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Role
    role: Mapped[str] = mapped_column(String(20), default=UserRole.CLIENT.value, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Staff fields
    employee_code: Mapped[Optional[str]] = mapped_column(String(50), unique=True, nullable=True)

    # Relationships
    orders: Mapped[List["Order"]] = relationship(
        "Order",
        back_populates="user",
        primaryjoin="User.id == Order.user_id",
        lazy="dynamic",
    )
    archived_categories: Mapped[List["Category"]] = relationship(
        "Category",
        foreign_keys="Category.archived_by_user_id",
        back_populates="archived_by_user",
        lazy="dynamic",
    )
    archived_products: Mapped[List["Product"]] = relationship(
        "Product",
        foreign_keys="Product.archived_by_user_id",
        back_populates="archived_by_user",
        lazy="dynamic",
    )
    audit_logs: Mapped[List["AdminAuditLog"]] = relationship("AdminAuditLog", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, role={self.role})>"

    @property
    def full_name(self) -> str:
        """Get user's full name."""
        parts = [self.first_name or "", self.last_name or ""]
        name = " ".join(p for p in parts if p)
        return name or self.username or f"User_{self.telegram_id}"

    def is_admin(self) -> bool:
        """Check if user is admin."""
        return self._in_roles(*ADMIN_ROLES)

    def is_manager(self) -> bool:
        """Check if user is manager."""
        return self._in_roles(*MANAGER_ROLES)

    def is_staff(self) -> bool:
        """Check if user is any staff member."""
        return self._in_roles(*STAFF_ROLES)

    def is_client(self) -> bool:
        """Check if user is a client."""
        return self._in_roles(*CLIENT_ROLES)

    def _in_roles(self, *roles: str) -> bool:
        """Helper to check if current role is among given roles."""
        return self.role in set(roles)
