from decimal import Decimal
from pydantic import BaseModel, Field


from . import Total


class Rest(BaseModel):
    rest: Decimal = Field(gt=0, decimal_places=2)


class CreateSalesReceipt(Total, Rest):
    pass

