"""Admin audit log model for tracking admin actions."""

from typing import Optional

from sqlalchemy import String, Integer, ForeignKey, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSON

from app.models.base import BaseModel


class AdminAuditLog(BaseModel):
    """Audit log for admin actions."""
    
    __tablename__ = "admin_audit_logs"
    
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., 'archive', 'unarchive', 'create', 'update', 'delete'
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., 'category', 'product', 'order'
    entity_id: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Details of the change
    old_values: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    new_values: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Reason for the action
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # IP address and user agent (if available)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="audit_logs")
    
    def __repr__(self):
        return f"<AdminAuditLog(id={self.id}, action={self.action}, entity={self.entity_type}:{self.entity_id})>"
