from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class BasePrice(Base):
    """Base pricing with 3 tiers: X, S, A."""
    __tablename__ = "base_prices"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), index=True)
    tier = Column(String(10), nullable=False)  # 'X', 'S', 'A'
    price = Column(Numeric(15, 2), nullable=False)
    effective_from = Column(Date, nullable=False)
    effective_to = Column(Date, nullable=True)  # NULL means currently active
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    product = relationship("Product", back_populates="base_prices")
    creator = relationship("User", foreign_keys=[created_by])


class ClientPrice(Base):
    """Client-specific pricing overrides."""
    __tablename__ = "client_prices"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), index=True)
    price = Column(Numeric(15, 2), nullable=False)
    is_protected = Column(Boolean, default=False)  # Low-price protection flag
    effective_from = Column(Date, nullable=False)
    effective_to = Column(Date, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    client = relationship("Client", back_populates="client_prices")
    product = relationship("Product", back_populates="client_prices")
    creator = relationship("User", foreign_keys=[created_by])


class PriceHistory(Base):
    """Audit trail for price changes."""
    __tablename__ = "price_history"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    client_id = Column(Integer, nullable=True)  # NULL for base price changes
    tier = Column(String(10), nullable=True)  # NULL for client prices
    old_price = Column(Numeric(15, 2))
    new_price = Column(Numeric(15, 2))
    change_type = Column(String(50))  # 'base_update', 'client_override', 'batch_update'
    reason = Column(String)
    changed_by = Column(Integer, ForeignKey("users.id"))
    changed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    product = relationship("Product")
    changer = relationship("User", foreign_keys=[changed_by])
