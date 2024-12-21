import decimal
from datetime import datetime

from sqlalchemy import ForeignKey, Enum, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID

from .base import Base
from .enums.payment import PaymentType


class Payment(Base):
    __tablename__ = "payments"

    payment_type: Mapped[PaymentType] = mapped_column(Enum(PaymentType), nullable=False)
    amount: Mapped[decimal] = mapped_column(Numeric(10, 2))
    created_at: Mapped[datetime]

    receipt_id = mapped_column(ForeignKey("sales_receipts.id"))
    receipt: Mapped["SalesReceipt"] = relationship("SalesReceipt", back_populates="payments")