from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class Order(Base):
    """Orders (confirmed quotations)."""
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True, nullable=False)  # e.g., SO-2026-0001
    quotation_id = Column(Integer, ForeignKey("quotations.id"))
    client_id = Column(Integer, ForeignKey("clients.id"), index=True)
    status = Column(String(50), default="pending_payment", index=True)  # pending_payment, paid, processing, shipped, completed, cancelled
    total_amount = Column(Numeric(15, 2), default=0)
    currency = Column(String(10), default="USD")
    payment_status = Column(String(50), default="unpaid")  # unpaid, partial, paid
    stock_locked = Column(Boolean, default=False)
    notes = Column(String)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    quotation = relationship("Quotation", back_populates="order")
    client = relationship("Client", back_populates="orders")
    creator = relationship("User", foreign_keys=[created_by])
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="order", cascade="all, delete-orphan")
    stock_locks = relationship("StockLock", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    """Line items in orders."""
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(15, 2), nullable=False)
    discount_percent = Column(Numeric(5, 2), default=0)
    notes = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")
    
    @property
    def line_total(self):
        """Calculate line total with discount."""
        return float(self.quantity) * float(self.unit_price) * (1 - float(self.discount_percent) / 100)


class Payment(Base):
    """Payment records."""
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    payment_method = Column(String(50))  # wire_transfer, credit_card, paypal, etc.
    amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(10), default="USD")
    payment_date = Column(Date)
    reference_number = Column(String(100))
    status = Column(String(50), default="pending")  # pending, confirmed, failed
    confirmed_by = Column(Integer, ForeignKey("users.id"))
    confirmed_at = Column(DateTime(timezone=True))
    notes = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    order = relationship("Order", back_populates="payments")
    confirmer = relationship("User", foreign_keys=[confirmed_by])


class StockLock(Base):
    """Reserved inventory for orders."""
    __tablename__ = "stock_locks"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"))
    product_id = Column(Integer, ForeignKey("products.id"))
    warehouse_code = Column(String(50))
    quantity = Column(Integer, nullable=False)
    locked_at = Column(DateTime(timezone=True), server_default=func.now())
    locked_by = Column(Integer, ForeignKey("users.id"))
    released_at = Column(DateTime(timezone=True))
    status = Column(String(50), default="locked")  # locked, released, fulfilled
    
    # Relationships
    order = relationship("Order", back_populates="stock_locks")
    product = relationship("Product")
    locker = relationship("User", foreign_keys=[locked_by])
