from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.models import SalesReceipt
from app.schemas.sales_receipt import CreateSalesReceipt
from app.utils.auth import utc_now


async def create_sales_receipt(
        db_session: AsyncSession,
        user_id: UUID
) -> SalesReceipt:
    now = utc_now()
    new_receipt = SalesReceipt(
        total=0,
        rest=0,
        created_at=now,
        user_id=user_id,
    )

    db_session.add(new_receipt)
    await db_session.commit()
    return new_receipt