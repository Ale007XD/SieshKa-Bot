"""Archive service for managing archived categories and products."""

from typing import List, Optional
from datetime import datetime

from sqlalchemy import select, and_, update
from app.utils.time import utc_now
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.models.product import Product
from app.models.audit_log import AdminAuditLog
from app.utils.exceptions import NotFoundException, ValidationException


class ArchiveService:
    """Service for archiving and unarchiving categories and products."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def archive_category(
        self,
        category_id: int,
        actor_user_id: int,
        cascade: bool = True
    ) -> Category:
        """Archive a category."""
        category = await self._get_category(category_id)
        
        if category.is_archived:
            raise ValidationException("Category is already archived")
        
        now = utc_now()
        
        # Archive the category
        category.is_archived = True
        category.archived_at = now
        category.archived_by_user_id = actor_user_id
        
        # Cascade archive if requested
        if cascade:
            await self._archive_category_children(category_id, actor_user_id, now)
        
        # Log the action
        await self._log_action(
            actor_user_id,
            "archive",
            "category",
            category_id,
            {"cascade": cascade},
            None
        )
        
        await self.session.flush()
        await self.session.commit()
        return category
    
    async def unarchive_category(
        self,
        category_id: int,
        actor_user_id: int,
        cascade_option: str = "self_only"  # or "with_descendants"
    ) -> Category:
        """Unarchive a category."""
        category = await self._get_category(category_id)
        
        if not category.is_archived:
            raise ValidationException("Category is not archived")
        
        # Unarchive the category
        category.is_archived = False
        category.archived_at = None
        category.archived_by_user_id = None
        
        # Cascade unarchive if requested
        if cascade_option == "with_descendants":
            await self._unarchive_category_children(category_id)
        
        # Log the action
        await self._log_action(
            actor_user_id,
            "unarchive",
            "category",
            category_id,
            None,
            {"cascade_option": cascade_option}
        )
        
        await self.session.flush()
        await self.session.commit()
        return category
    
    async def archive_product(
        self,
        product_id: int,
        actor_user_id: int
    ) -> Product:
        """Archive a product."""
        product = await self._get_product(product_id)
        
        if product.is_archived:
            raise ValidationException("Product is already archived")
        
        now = utc_now()
        
        product.is_archived = True
        product.archived_at = now
        product.archived_by_user_id = actor_user_id
        
        # Log the action
        await self._log_action(
            actor_user_id,
            "archive",
            "product",
            product_id,
            None,
            None
        )
        
        await self.session.flush()
        await self.session.commit()
        return product
    
    async def unarchive_product(
        self,
        product_id: int,
        actor_user_id: int
    ) -> Product:
        """Unarchive a product."""
        product = await self._get_product(product_id)
        
        if not product.is_archived:
            raise ValidationException("Product is not archived")
        
        product.is_archived = False
        product.archived_at = None
        product.archived_by_user_id = None
        
        # Log the action
        await self._log_action(
            actor_user_id,
            "unarchive",
            "product",
            product_id,
            None,
            None
        )
        
        await self.session.flush()
        await self.session.commit()
        return product
    
    async def get_archived_categories(self) -> List[Category]:
        """Get all archived categories."""
        result = await self.session.execute(
            select(Category)
            .where(Category.is_archived == True)
            .order_by(Category.archived_at.desc())
        )
        return result.scalars().all()
    
    async def get_archived_products(self) -> List[Product]:
        """Get all archived products."""
        result = await self.session.execute(
            select(Product)
            .where(Product.is_archived == True)
            .order_by(Product.archived_at.desc())
        )
        return result.scalars().all()
    
    # Private helper methods
    
    async def _get_category(self, category_id: int) -> Category:
        """Get category by ID."""
        result = await self.session.execute(
            select(Category).where(Category.id == category_id)
        )
        category = result.scalar_one_or_none()
        if not category:
            raise NotFoundException("Category", str(category_id))
        return category
    
    async def _get_product(self, product_id: int) -> Product:
        """Get product by ID."""
        result = await self.session.execute(
            select(Product).where(Product.id == product_id)
        )
        product = result.scalar_one_or_none()
        if not product:
            raise NotFoundException("Product", str(product_id))
        return product
    
    async def _archive_category_children(
        self,
        parent_id: int,
        actor_user_id: int,
        archived_at: datetime
    ) -> None:
        """Recursively archive all children of a category."""
        # Archive subcategories
        subcategories_result = await self.session.execute(
            select(Category).where(Category.parent_id == parent_id)
        )
        subcategories = subcategories_result.scalars().all()
        
        for subcategory in subcategories:
            subcategory.is_archived = True
            subcategory.archived_at = archived_at
            subcategory.archived_by_user_id = actor_user_id
            
            # Recursively archive children
            await self._archive_category_children(
                subcategory.id,
                actor_user_id,
                archived_at
            )
        
        # Archive products in this category
        await self.session.execute(
            update(Product)
            .where(Product.category_id == parent_id)
            .values(
                is_archived=True,
                archived_at=archived_at,
                archived_by_user_id=actor_user_id
            )
        )
    
    async def _unarchive_category_children(self, parent_id: int) -> None:
        """Recursively unarchive all children of a category."""
        # Unarchive subcategories
        subcategories_result = await self.session.execute(
            select(Category).where(Category.parent_id == parent_id)
        )
        subcategories = subcategories_result.scalars().all()
        
        for subcategory in subcategories:
            subcategory.is_archived = False
            subcategory.archived_at = None
            subcategory.archived_by_user_id = None
            
            # Recursively unarchive children
            await self._unarchive_category_children(subcategory.id)
        
        # Unarchive products in this category
        await self.session.execute(
            update(Product)
            .where(Product.category_id == parent_id)
            .values(
                is_archived=False,
                archived_at=None,
                archived_by_user_id=None
            )
        )
    
    async def _log_action(
        self,
        user_id: int,
        action: str,
        entity_type: str,
        entity_id: int,
        old_values: Optional[dict],
        new_values: Optional[dict]
    ) -> None:
        """Log admin action to audit log."""
        log_entry = AdminAuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            old_values=old_values,
            new_values=new_values
        )
        self.session.add(log_entry)
