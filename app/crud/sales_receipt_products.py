from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import SalesReceiptProducts
from app.schemas.sales_receipt_products import CreateSalesReceiptProduct


async def get_all_sales_receipt_products(db_session: AsyncSession) -> List[SalesReceiptProducts]:
    stmt = select(SalesReceiptProducts)
    result = await db_session.execute(stmt)
    sales_receipt_products = result.scalars().all()

    return sales_receipt_products


async def get_sales_receipt_product(db_session: AsyncSession, user_id: UUID) -> SalesReceiptProducts:
    return await db_session.scalar(
        select(SalesReceiptProducts).filter(SalesReceiptProducts.id == user_id)
    )


async def create_sales_receipt_product(
        db_session: AsyncSession,
        create_sl_product: CreateSalesReceiptProduct,
        receipt_id: UUID
) -> SalesReceiptProducts:
    total_slr = create_sl_product.price * create_sl_product.quantity

    new_product = SalesReceiptProducts(
        title=create_sl_product.title,
        price=create_sl_product.price,
        quantity=create_sl_product.quantity,
        total=total_slr,
        receipt_id=receipt_id
    )

    db_session.add(new_product)
    await db_session.commit()
    return new_product