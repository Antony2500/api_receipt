import decimal
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class SalesReceipt(Base):
    __tablename__ = "sales_receipts"

    total: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    rest: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    created_at: Mapped[datetime]

    user_id = mapped_column(ForeignKey("service_users.id"))
    user: Mapped["User"] = relationship("User", back_populates="sales_receipts")

    sales_receipt_products: Mapped[list["SalesReceiptProducts"]] = relationship("SalesReceiptProducts", back_populates="receipt")
    payments: Mapped["Payment"] = relationship("Payment", back_populates="receipt")