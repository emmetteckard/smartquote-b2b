from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr

class ClientBase(BaseModel):
    company_name: str
    contact_person: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    tax_id: Optional[str] = None
    payment_terms: Optional[int] = 30
    credit_limit: Optional[float] = None
    tier: Optional[str] = "A"
    is_active: Optional[bool] = True
    sales_rep_id: Optional[int] = None

class ClientCreate(ClientBase):
    pass

class ClientUpdate(BaseModel):
    company_name: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    tax_id: Optional[str] = None
    payment_terms: Optional[int] = None
    credit_limit: Optional[float] = None
    tier: Optional[str] = None
    is_active: Optional[bool] = None
    sales_rep_id: Optional[int] = None

class ClientResponse(ClientBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
