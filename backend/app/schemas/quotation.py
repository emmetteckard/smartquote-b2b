from typing import Optional, List
from pydantic import BaseModel
from datetime import date, datetime
from decimal import Decimal


class QuotationItemBase(BaseModel):
    product_id: int
    quantity: int
    unit_price: Decimal
    discount_percent: Decimal = Decimal(0)
    notes: Optional[str] = None


class QuotationItemCreate(QuotationItemBase):
    pass


class QuotationItemResponse(QuotationItemBase):
    id: int
    line_total: float

    class Config:
        from_attributes = True


class QuotationBase(BaseModel):
    client_id: int
    valid_until: Optional[date] = None
    notes: Optional[str] = None
    currency: str = "USD"


class QuotationCreate(QuotationBase):
    items: List[QuotationItemCreate]


class QuotationUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None
    valid_until: Optional[date] = None


class QuotationResponse(QuotationBase):
    id: int
    quotation_number: str
    status: str
    total_amount: Decimal
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: List[QuotationItemResponse] = []

    class Config:
        from_attributes = True
