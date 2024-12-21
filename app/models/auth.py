from sqlalchemy import String, ForeignKey, Enum
from sqlalchemy.orm import mapped_column, relationship, Mapped
from datetime import datetime
from .base import Base


class AuthToken(Base):
    __tablename__ = "service_auth_tokens"

    secret: Mapped[str] = mapped_column(String(1024), unique=True, index=True)
    expiration: Mapped[datetime]
    created: Mapped[datetime]

    token_type: Mapped[str] = mapped_column(Enum("refresh", name="token_types"))

    user_id = mapped_column(ForeignKey("service_users.id", ondelete="CASCADE"))
    user: Mapped["User"] = relationship("User", back_populates="refresh_tokens")