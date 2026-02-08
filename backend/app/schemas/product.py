from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime


class ProductBase(BaseModel):
    sku: str
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    unit: str = "pcs"
    min_order_qty: int = 1
    lingxing_product_id: Optional[str] = None
    package_length: Optional[float] = None
    package_width: Optional[float] = None
    package_height: Optional[float] = None
    package_weight: Optional[float] = None
    is_active: Optional[bool] = True


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    sku: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    unit: Optional[str] = None
    min_order_qty: Optional[int] = None
    lingxing_product_id: Optional[str] = None
    package_length: Optional[float] = None
    package_width: Optional[float] = None
    package_height: Optional[float] = None
    package_weight: Optional[float] = None
    is_active: Optional[bool] = None


class ProductComponentSchema(BaseModel):
    child_product_id: int
    quantity: int
    child_sku: Optional[str] = None # For display
    
    class Config:
        from_attributes = True

class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Extra fields for UI display
    current_price: Optional[float] = None
    tier_prices: Optional[dict] = None
    
    # Components
    components_list: Optional[List[ProductComponentSchema]] = None

    class Config:
        from_attributes = True
