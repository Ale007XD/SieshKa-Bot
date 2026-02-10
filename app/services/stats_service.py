"""Stats service for generating statistics and reports."""

from typing import Dict, List, Optional
from datetime import datetime, date, timedelta

from sqlalchemy import select, func, and_, cast, Date
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.utils.enums import OrderStatus


class StatsService:
    """Service for statistics and reporting."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_daily_stats(self, target_date: Optional[date] = None) -> Dict:
        """Get statistics for a specific day."""
        if target_date is None:
            target_date = date.today()
        
        # Orders count and revenue
        orders_result = await self.session.execute(
            select(
                func.count(Order.id).label("total_orders"),
                func.sum(Order.total).label("total_revenue"),
                func.avg(Order.total).label("avg_order_value")
            )
            .where(
                and_(
                    cast(Order.created_at, Date) == target_date,
                    Order.status != OrderStatus.CANCELLED.value
                )
            )
        )
        orders_stats = orders_result.one()
        
        # Cancelled orders
        cancelled_result = await self.session.execute(
            select(func.count(Order.id))
            .where(
                and_(
                    cast(Order.created_at, Date) == target_date,
                    Order.status == OrderStatus.CANCELLED.value
                )
            )
        )
        cancelled_count = cancelled_result.scalar() or 0
        
        return {
            "date": target_date.isoformat(),
            "total_orders": orders_stats.total_orders or 0,
            "cancelled_orders": cancelled_count,
            "total_revenue": float(orders_stats.total_revenue or 0),
            "average_order_value": float(orders_stats.avg_order_value or 0)
        }
    
    async def get_period_stats(
        self,
        start_date: date,
        end_date: date
    ) -> Dict:
        """Get statistics for a date period."""
        # Daily breakdown
        daily_result = await self.session.execute(
            select(
                cast(Order.created_at, Date).label("day"),
                func.count(Order.id).label("orders"),
                func.sum(Order.total).label("revenue")
            )
            .where(
                and_(
                    cast(Order.created_at, Date) >= start_date,
                    cast(Order.created_at, Date) <= end_date,
                    Order.status != OrderStatus.CANCELLED.value
                )
            )
            .group_by(cast(Order.created_at, Date))
            .order_by(cast(Order.created_at, Date))
        )
        
        daily_stats = [
            {
                "date": row.day.isoformat(),
                "orders": row.orders,
                "revenue": float(row.revenue or 0)
            }
            for row in daily_result.all()
        ]
        
        # Overall totals
        total_result = await self.session.execute(
            select(
                func.count(Order.id).label("total_orders"),
                func.sum(Order.total).label("total_revenue")
            )
            .where(
                and_(
                    cast(Order.created_at, Date) >= start_date,
                    cast(Order.created_at, Date) <= end_date,
                    Order.status != OrderStatus.CANCELLED.value
                )
            )
        )
        totals = total_result.one()
        
        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "daily": daily_stats,
            "total_orders": totals.total_orders or 0,
            "total_revenue": float(totals.total_revenue or 0)
        }
    
    async def get_top_products(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 10
    ) -> List[Dict]:
        """Get top selling products."""
        if end_date is None:
            end_date = date.today()
        if start_date is None:
            start_date = end_date - timedelta(days=30)
        
        result = await self.session.execute(
            select(
                OrderItem.product_id,
                OrderItem.product_name,
                func.sum(OrderItem.quantity).label("total_quantity"),
                func.sum(OrderItem.item_total).label("total_revenue")
            )
            .join(Order)
            .where(
                and_(
                    cast(Order.created_at, Date) >= start_date,
                    cast(Order.created_at, Date) <= end_date,
                    Order.status != OrderStatus.CANCELLED.value
                )
            )
            .group_by(OrderItem.product_id, OrderItem.product_name)
            .order_by(func.sum(OrderItem.quantity).desc())
            .limit(limit)
        )
        
        return [
            {
                "product_id": row.product_id,
                "product_name": row.product_name,
                "total_quantity": row.total_quantity,
                "total_revenue": float(row.total_revenue or 0)
            }
            for row in result.all()
        ]
    
    async def get_order_status_distribution(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, int]:
        """Get distribution of orders by status."""
        if end_date is None:
            end_date = date.today()
        if start_date is None:
            start_date = end_date - timedelta(days=30)
        
        result = await self.session.execute(
            select(
                Order.status,
                func.count(Order.id).label("count")
            )
            .where(
                and_(
                    cast(Order.created_at, Date) >= start_date,
                    cast(Order.created_at, Date) <= end_date
                )
            )
            .group_by(Order.status)
        )
        
        return {row.status: row.count for row in result.all()}
