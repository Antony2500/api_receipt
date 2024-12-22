from decimal import Decimal

from sqlalchemy import String, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class SalesReceiptProducts(Base):
    __tablename__ = "sales_receipt_products"

    title: Mapped[str] = mapped_column(String(255))
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    quantity: Mapped[Decimal] = mapped_column(Numeric(10, 0))
    total: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    product_id = mapped_column(ForeignKey("products.id"))
    product: Mapped["Products"] = relationship("Products")

    receipt_id = mapped_column(ForeignKey("sales_receipts.id"))
    receipt: Mapped["SalesReceipt"] = relationship("SalesReceipt", back_populates="sales_receipt_products")