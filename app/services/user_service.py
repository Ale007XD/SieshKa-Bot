"""User service for managing users and roles."""

from typing import List, Optional

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.utils.enums import UserRole
from app.utils.exceptions import NotFoundException, DuplicateException


class UserService:
    """Service for user operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_user_by_id(self, user_id: int) -> User:
        """Get user by ID."""
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise NotFoundException("User", str(user_id))
        return user
    
    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Get user by Telegram ID."""
        result = await self.session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()
    
    async def get_or_create_user(
        self,
        telegram_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None
    ) -> User:
        """Get existing user or create new one."""
        user = await self.get_user_by_telegram_id(telegram_id)
        
        if user:
            # Update user info if changed
            if username and user.username != username:
                user.username = username
            if first_name and user.first_name != first_name:
                user.first_name = first_name
            if last_name and user.last_name != last_name:
                user.last_name = last_name
            await self.session.flush()
            await self.session.commit()
            return user
        
        # Check if this is the first admin
        admin_check = await self.session.execute(
            select(User).where(User.role == UserRole.ADMIN.value)
        )
        is_first_user = admin_check.scalar_one_or_none() is None
        
        # Create new user
        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            role=UserRole.ADMIN.value if is_first_user else UserRole.CLIENT.value,
            is_active=True
        )
        
        self.session.add(user)
        await self.session.flush()
        await self.session.commit()
        return user
    
    async def update_user(
        self,
        user_id: int,
        phone: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None
    ) -> User:
        """Update user information."""
        user = await self.get_user_by_id(user_id)
        
        if phone is not None:
            user.phone = phone
        if first_name is not None:
            user.first_name = first_name
        if last_name is not None:
            user.last_name = last_name
        
        await self.session.flush()
        await self.session.commit()
        return user
    
    async def set_user_role(
        self,
        user_id: int,
        role: UserRole,
        changed_by_id: int
    ) -> User:
        """Set user role."""
        user = await self.get_user_by_id(user_id)
        user.role = role.value
        await self.session.flush()
        await self.session.commit()
        return user
    
    async def deactivate_user(self, user_id: int) -> User:
        """Deactivate user."""
        user = await self.get_user_by_id(user_id)
        user.is_active = False
        await self.session.flush()
        await self.session.commit()
        return user
    
    async def activate_user(self, user_id: int) -> User:
        """Activate user."""
        user = await self.get_user_by_id(user_id)
        user.is_active = True
        await self.session.flush()
        await self.session.commit()
        return user
    
    async def get_users_by_role(
        self,
        role: UserRole,
        active_only: bool = True
    ) -> List[User]:
        """Get users by role."""
        query = select(User).where(User.role == role.value)
        
        if active_only:
            query = query.where(User.is_active == True)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_staff_users(self, active_only: bool = True) -> List[User]:
        """Get all staff users (non-clients)."""
        staff_roles = [
            UserRole.ADMIN.value,
            UserRole.MANAGER.value,
            UserRole.KITCHEN.value,
            UserRole.PACKER.value,
            UserRole.COURIER.value
        ]
        
        query = select(User).where(User.role.in_(staff_roles))
        
        if active_only:
            query = query.where(User.is_active == True)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def is_admin(self, telegram_id: int) -> bool:
        """Check if user with telegram_id is admin."""
        user = await self.get_user_by_telegram_id(telegram_id)
        return user is not None and user.is_admin()
    
    async def is_staff(self, telegram_id: int) -> bool:
        """Check if user with telegram_id is staff."""
        user = await self.get_user_by_telegram_id(telegram_id)
        return user is not None and user.is_staff()
