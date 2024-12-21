from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.models import User as DBModelUser
from app.models.log import Log
from app.utils.auth import utc_now


async def create_log(
        session: AsyncSession,
        log_type: str,
        user: DBModelUser | None,
        target_id: UUID | None = None,
        data: dict = None
):
    now = utc_now()

    log = Log(
        **{
            "created": now,
            "target_id": target_id,
            "log_type": log_type,
            "user": user,
            "data": data,
        }
    )

    session.add(log)
    await session.commit()

    return log