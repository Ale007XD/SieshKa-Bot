#!/usr/bin/env python3
"""Create admin user script."""

import asyncio
import argparse
import getpass

from app.database import AsyncSessionLocal, init_db
from app.models.user import User
from app.utils.enums import UserRole


async def create_admin(telegram_id: int, username: str = None, first_name: str = None):
    """Create or update admin user."""
    await init_db()
    
    async with AsyncSessionLocal() as session:
        # Check if user exists
        from sqlalchemy import select
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        
        if user:
            # Update existing user to admin
            user.role = UserRole.ADMIN.value
            user.is_active = True
            print(f"Updated user {telegram_id} to admin role")
        else:
            # Create new admin user
            user = User(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                role=UserRole.ADMIN.value,
                is_active=True
            )
            session.add(user)
            print(f"Created new admin user with telegram_id {telegram_id}")
        
        await session.commit()
        print(f"Admin user: {user.full_name} (ID: {user.id})")


def main():
    parser = argparse.ArgumentParser(description="Create admin user for Food Delivery Bot")
    parser.add_argument("telegram_id", type=int, help="Telegram ID of the admin")
    parser.add_argument("--username", help="Telegram username (optional)")
    parser.add_argument("--first-name", help="First name (optional)")
    
    args = parser.parse_args()
    
    asyncio.run(create_admin(
        telegram_id=args.telegram_id,
        username=args.username,
        first_name=args.first_name
    ))


if __name__ == "__main__":
    main()
