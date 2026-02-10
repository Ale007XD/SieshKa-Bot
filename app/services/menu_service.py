"""Menu service for managing categories and products."""

from typing import List, Optional

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.category import Category
from app.models.product import Product
from app.models.modifier import Modifier, ModifierOption, ProductModifier
from app.utils.exceptions import NotFoundException, ValidationException


class MenuService:
    """Service for menu operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    # Category operations
    
    async def get_category_by_id(self, category_id: int) -> Category:
        """Get category by ID."""
        result = await self.session.execute(
            select(Category).where(Category.id == category_id)
        )
        category = result.scalar_one_or_none()
        if not category:
            raise NotFoundException("Category", str(category_id))
        return category
    
    async def get_category_tree(
        self,
        parent_id: Optional[int] = None,
        include_inactive: bool = False,
        include_archived: bool = False
    ) -> List[Category]:
        """Get category tree starting from parent_id."""
        query = select(Category).where(Category.parent_id == parent_id)
        
        if not include_inactive:
            query = query.where(Category.is_active == True)
        
        if not include_archived:
            query = query.where(Category.is_archived == False)
        
        query = query.order_by(Category.sort_order, Category.name)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_all_categories(
        self,
        include_inactive: bool = False,
        include_archived: bool = False
    ) -> List[Category]:
        """Get all categories."""
        query = select(Category)
        
        if not include_inactive:
            query = query.where(Category.is_active == True)
        
        if not include_archived:
            query = query.where(Category.is_archived == False)
        
        query = query.order_by(Category.sort_order, Category.name)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def create_category(
        self,
        name: str,
        parent_id: Optional[int] = None,
        description: Optional[str] = None,
        sort_order: int = 0,
        image_url: Optional[str] = None
    ) -> Category:
        """Create a new category."""
        # Validate level
        level = 1
        if parent_id:
            parent = await self.get_category_by_id(parent_id)
            if parent.level >= 3:
                raise ValidationException("Maximum category depth (3) reached")
            level = parent.level + 1
        
        category = Category(
            name=name,
            description=description,
            parent_id=parent_id,
            level=level,
            sort_order=sort_order,
            image_url=image_url,
            is_active=True,
            is_archived=False
        )
        
        self.session.add(category)
        await self.session.flush()
        await self.session.commit()
        return category
    
    async def update_category(
        self,
        category_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        sort_order: Optional[int] = None,
        is_active: Optional[bool] = None,
        image_url: Optional[str] = None
    ) -> Category:
        """Update category."""
        category = await self.get_category_by_id(category_id)
        
        if name is not None:
            category.name = name
        if description is not None:
            category.description = description
        if sort_order is not None:
            category.sort_order = sort_order
        if is_active is not None:
            category.is_active = is_active
        if image_url is not None:
            category.image_url = image_url
        
        await self.session.flush()
        await self.session.commit()
        return category
    
    # Product operations
    
    async def get_product_by_id(self, product_id: int) -> Product:
        """Get product by ID."""
        result = await self.session.execute(
            select(Product)
            .options(selectinload(Product.modifiers))
            .where(Product.id == product_id)
        )
        product = result.scalar_one_or_none()
        if not product:
            raise NotFoundException("Product", str(product_id))
        return product
    
    async def get_products_by_category(
        self,
        category_id: int,
        include_inactive: bool = False,
        include_archived: bool = False
    ) -> List[Product]:
        """Get products by category ID."""
        query = select(Product).where(Product.category_id == category_id)
        
        if not include_inactive:
            query = query.where(Product.is_active == True)
        
        if not include_archived:
            query = query.where(Product.is_archived == False)
        
        query = query.order_by(Product.sort_order, Product.name)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_available_products(self) -> List[Product]:
        """Get all available products for clients."""
        query = (
            select(Product)
            .join(Category)
            .where(
                and_(
                    Product.is_active == True,
                    Product.is_archived == False,
                    Category.is_active == True,
                    Category.is_archived == False
                )
            )
            .order_by(Product.sort_order, Product.name)
        )
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def create_product(
        self,
        name: str,
        category_id: int,
        price: float,
        description: Optional[str] = None,
        stock_quantity: Optional[int] = None,
        track_stock: bool = False,
        sort_order: int = 0,
        image_url: Optional[str] = None
    ) -> Product:
        """Create a new product."""
        # Verify category exists and is not archived
        category = await self.get_category_by_id(category_id)
        if category.is_archived:
            raise ValidationException("Cannot add product to archived category")
        
        product = Product(
            name=name,
            description=description,
            price=price,
            category_id=category_id,
            stock_quantity=stock_quantity,
            track_stock=track_stock,
            sort_order=sort_order,
            image_url=image_url,
            is_active=True,
            is_archived=False
        )
        
        self.session.add(product)
        await self.session.flush()
        await self.session.commit()
        return product
    
    async def update_product(
        self,
        product_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        price: Optional[float] = None,
        is_active: Optional[bool] = None,
        stock_quantity: Optional[int] = None,
        track_stock: Optional[bool] = None,
        sort_order: Optional[int] = None,
        image_url: Optional[str] = None
    ) -> Product:
        """Update product."""
        product = await self.get_product_by_id(product_id)
        
        if name is not None:
            product.name = name
        if description is not None:
            product.description = description
        if price is not None:
            product.price = price
        if is_active is not None:
            product.is_active = is_active
        if stock_quantity is not None:
            product.stock_quantity = stock_quantity
        if track_stock is not None:
            product.track_stock = track_stock
        if sort_order is not None:
            product.sort_order = sort_order
        if image_url is not None:
            product.image_url = image_url
        
        await self.session.flush()
        await self.session.commit()
        return product
    
    # Modifier operations
    
    async def get_modifier_by_id(self, modifier_id: int) -> Modifier:
        """Get modifier by ID."""
        result = await self.session.execute(
            select(Modifier)
            .options(selectinload(Modifier.options))
            .where(Modifier.id == modifier_id)
        )
        modifier = result.scalar_one_or_none()
        if not modifier:
            raise NotFoundException("Modifier", str(modifier_id))
        return modifier
    
    async def create_modifier(
        self,
        name: str,
        description: Optional[str] = None,
        is_required: bool = False,
        is_multiple: bool = False,
        sort_order: int = 0
    ) -> Modifier:
        """Create a new modifier."""
        modifier = Modifier(
            name=name,
            description=description,
            is_required=is_required,
            is_multiple=is_multiple,
            sort_order=sort_order,
            is_active=True
        )
        
        self.session.add(modifier)
        await self.session.flush()
        await self.session.commit()
        return modifier
    
    async def add_modifier_option(
        self,
        modifier_id: int,
        name: str,
        price_adjustment: float = 0,
        sort_order: int = 0
    ) -> ModifierOption:
        """Add option to modifier."""
        modifier = await self.get_modifier_by_id(modifier_id)
        
        option = ModifierOption(
            modifier_id=modifier_id,
            name=name,
            price_adjustment=price_adjustment,
            sort_order=sort_order,
            is_active=True
        )
        
        self.session.add(option)
        await self.session.flush()
        await self.session.commit()
        return option
    
    async def assign_modifier_to_product(
        self,
        product_id: int,
        modifier_id: int,
        sort_order: int = 0
    ) -> ProductModifier:
        """Assign modifier to product."""
        product = await self.get_product_by_id(product_id)
        modifier = await self.get_modifier_by_id(modifier_id)
        
        link = ProductModifier(
            product_id=product_id,
            modifier_id=modifier_id,
            sort_order=sort_order
        )
        
        self.session.add(link)
        await self.session.flush()
        await self.session.commit()
        return link
    
    async def remove_modifier_from_product(
        self,
        product_id: int,
        modifier_id: int
    ) -> None:
        """Remove modifier from product."""
        result = await self.session.execute(
            select(ProductModifier).where(
                and_(
                    ProductModifier.product_id == product_id,
                    ProductModifier.modifier_id == modifier_id
                )
            )
        )
        link = result.scalar_one_or_none()
        if link:
            await self.session.delete(link)
