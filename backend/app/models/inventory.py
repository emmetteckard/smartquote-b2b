from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class Inventory(Base):
    """Inventory synced from Lingxing ERP."""
    __tablename__ = "inventory"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), index=True)
    warehouse_code = Column(String(50))
    available_qty = Column(Integer, default=0)
    reserved_qty = Column(Integer, default=0)  # Locked for orders
    # total_qty is computed: available_qty + reserved_qty
    last_sync_at = Column(DateTime(timezone=True))
    lingxing_warehouse_id = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    product = relationship("Product", back_populates="inventory")
    
    @property
    def total_qty(self):
        """Total quantity = available + reserved."""
        return self.available_qty + self.reserved_qty
