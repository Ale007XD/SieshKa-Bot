"""Import service for importing menu data."""

import json
import csv
import io
from typing import List, Dict, Any, Optional
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.models.product import Product
from app.models.modifier import Modifier, ModifierOption, ProductModifier
from app.utils.exceptions import ValidationException


class ImportService:
    """Service for importing data from various formats."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def import_categories_from_json(
        self,
        json_data: str,
        actor_user_id: int
    ) -> Dict[str, Any]:
        """Import categories from JSON."""
        try:
            data = json.loads(json_data)
        except json.JSONDecodeError as e:
            raise ValidationException(f"Invalid JSON: {str(e)}")
        
        if not isinstance(data, list):
            raise ValidationException("JSON must be an array of categories")
        
        imported = 0
        errors = []
        
        # Use nested transaction for atomic import
        async with self.session.begin_nested() as nested:
            for idx, item in enumerate(data):
                try:
                    await self._import_category(item)
                    imported += 1
                except Exception as e:
                    errors.append(f"Row {idx + 1}: {str(e)}")
            
            # Rollback if any errors occurred
            if errors:
                await nested.rollback()
                imported = 0
            else:
                await self.session.commit()
        
        return {
            "success": len(errors) == 0,
            "imported": imported,
            "errors": errors
        }
    
    async def import_products_from_csv(
        self,
        csv_content: str,
        actor_user_id: int
    ) -> Dict[str, Any]:
        """Import products from CSV."""
        try:
            reader = csv.DictReader(io.StringIO(csv_content))
        except Exception as e:
            raise ValidationException(f"Invalid CSV: {str(e)}")
        
        imported = 0
        errors = []
        
        # Use nested transaction for atomic import
        async with self.session.begin_nested() as nested:
            for idx, row in enumerate(reader):
                try:
                    await self._import_product_from_csv_row(row)
                    imported += 1
                except Exception as e:
                    errors.append(f"Row {idx + 1}: {str(e)}")
            
            # Rollback if any errors occurred
            if errors:
                await nested.rollback()
                imported = 0
            else:
                await self.session.commit()
        
        return {
            "success": len(errors) == 0,
            "imported": imported,
            "errors": errors
        }
    
    async def import_menu_full(
        self,
        data: Dict[str, Any],
        actor_user_id: int
    ) -> Dict[str, Any]:
        """Import full menu structure (categories, products, modifiers)."""
        stats = {
            "categories": {"imported": 0, "errors": []},
            "products": {"imported": 0, "errors": []},
            "modifiers": {"imported": 0, "errors": []}
        }
        
        # Use nested transaction for atomic import
        async with self.session.begin_nested() as nested:
            # Import categories
            if "categories" in data:
                for idx, cat_data in enumerate(data["categories"]):
                    try:
                        await self._import_category_hierarchy(cat_data)
                        stats["categories"]["imported"] += 1
                    except Exception as e:
                        stats["categories"]["errors"].append(f"Category {idx + 1}: {str(e)}")
            
            # Import modifiers
            if "modifiers" in data:
                for idx, mod_data in enumerate(data["modifiers"]):
                    try:
                        await self._import_modifier(mod_data)
                        stats["modifiers"]["imported"] += 1
                    except Exception as e:
                        stats["modifiers"]["errors"].append(f"Modifier {idx + 1}: {str(e)}")
            
            # Import products
            if "products" in data:
                for idx, prod_data in enumerate(data["products"]):
                    try:
                        await self._import_product(prod_data)
                        stats["products"]["imported"] += 1
                    except Exception as e:
                        stats["products"]["errors"].append(f"Product {idx + 1}: {str(e)}")
            
            # Rollback if any errors occurred
            has_errors = any(
                stats[key]["errors"] for key in ["categories", "products", "modifiers"]
            )
            if has_errors:
                await nested.rollback()
                for key in ["categories", "products", "modifiers"]:
                    stats[key]["imported"] = 0
            else:
                await self.session.commit()
        
        return {
            "success": not has_errors,
            "stats": stats
        }
    
    async def _import_category(
        self,
        data: Dict[str, Any],
        parent_id: Optional[int] = None
    ) -> Category:
        """Import a single category."""
        name = data.get("name")
        if not name:
            raise ValidationException("Category name is required")
        
        category = Category(
            name=name,
            description=data.get("description"),
            parent_id=parent_id,
            level=data.get("level", 1 if parent_id is None else 2),
            sort_order=data.get("sort_order", 0),
            image_url=data.get("image_url"),
            is_active=data.get("is_active", True),
            is_archived=False
        )
        
        self.session.add(category)
        await self.session.flush()
        
        # Import children if present
        if "children" in data and isinstance(data["children"], list):
            for child_data in data["children"]:
                await self._import_category(child_data, category.id)
        
        return category
    
    async def _import_category_hierarchy(
        self,
        data: Dict[str, Any]
    ) -> Category:
        """Import category with full hierarchy."""
        return await self._import_category(data, None)
    
    async def _import_product(self, data: Dict[str, Any]) -> Product:
        """Import a single product."""
        name = data.get("name")
        category_id = data.get("category_id")
        price = data.get("price")
        
        if not name:
            raise ValidationException("Product name is required")
        if not category_id:
            raise ValidationException("Product category_id is required")
        if price is None:
            raise ValidationException("Product price is required")
        
        try:
            price = float(price)
        except (TypeError, ValueError):
            raise ValidationException(f"Invalid price: {price}")
        
        product = Product(
            name=name,
            description=data.get("description"),
            price=price,
            category_id=int(category_id),
            stock_quantity=data.get("stock_quantity"),
            track_stock=data.get("track_stock", False),
            sort_order=data.get("sort_order", 0),
            image_url=data.get("image_url"),
            is_active=data.get("is_active", True),
            is_archived=False
        )
        
        self.session.add(product)
        await self.session.flush()
        
        # Assign modifiers if specified
        if "modifier_ids" in data and isinstance(data["modifier_ids"], list):
            for mod_id in data["modifier_ids"]:
                link = ProductModifier(
                    product_id=product.id,
                    modifier_id=int(mod_id)
                )
                self.session.add(link)
        
        return product
    
    async def _import_product_from_csv_row(self, row: Dict[str, str]) -> Product:
        """Import product from CSV row."""
        data = {
            "name": row.get("name"),
            "description": row.get("description"),
            "price": row.get("price"),
            "category_id": row.get("category_id"),
            "stock_quantity": row.get("stock_quantity"),
            "track_stock": row.get("track_stock", "false").lower() == "true",
            "sort_order": row.get("sort_order", "0"),
            "image_url": row.get("image_url"),
            "is_active": row.get("is_active", "true").lower() == "true"
        }
        return await self._import_product(data)
    
    async def _import_modifier(self, data: Dict[str, Any]) -> Modifier:
        """Import a modifier with options."""
        name = data.get("name")
        if not name:
            raise ValidationException("Modifier name is required")
        
        modifier = Modifier(
            name=name,
            description=data.get("description"),
            is_required=data.get("is_required", False),
            is_multiple=data.get("is_multiple", False),
            sort_order=data.get("sort_order", 0),
            is_active=data.get("is_active", True)
        )
        
        self.session.add(modifier)
        await self.session.flush()
        
        # Import options
        if "options" in data and isinstance(data["options"], list):
            for opt_data in data["options"]:
                option = ModifierOption(
                    modifier_id=modifier.id,
                    name=opt_data.get("name", "Option"),
                    price_adjustment=float(opt_data.get("price_adjustment", 0)),
                    sort_order=opt_data.get("sort_order", 0),
                    is_active=opt_data.get("is_active", True)
                )
                self.session.add(option)
        
        return modifier
    
    def validate_import_data(self, data: Dict[str, Any]) -> List[str]:
        """Validate import data structure."""
        errors = []
        
        if not isinstance(data, dict):
            errors.append("Data must be an object")
            return errors
        
        # Validate categories
        if "categories" in data:
            if not isinstance(data["categories"], list):
                errors.append("categories must be an array")
        
        # Validate products
        if "products" in data:
            if not isinstance(data["products"], list):
                errors.append("products must be an array")
        
        # Validate modifiers
        if "modifiers" in data:
            if not isinstance(data["modifiers"], list):
                errors.append("modifiers must be an array")
        
        return errors
