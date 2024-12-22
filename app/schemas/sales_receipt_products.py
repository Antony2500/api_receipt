from decimal import Decimal

from pydantic import BaseModel, Field, field_validator

from . import Title, Price, Total


class Quantity(BaseModel):
    quantity: Decimal = Field(gt=0)

class CreateSalesReceiptProduct(Title, Price, Quantity):
    pass

class SalesReceiptProduct(Title, Price, Quantity):
    total: Decimal = Field(gt=0, decimal_places=2)

    @field_validator("total")
    def check_total_matches_price_and_quantity(cls, value, values):
        price = values.get("price")
        quantity = values.get("quantity")

        if value != price * quantity:
            raise ValueError("Total must be equal to price * quantity")

        return value

