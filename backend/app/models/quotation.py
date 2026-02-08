from sqlalchemy import Column, Integer, String, Date, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class Quotation(Base):
    """Quotations / Proforma Invoices."""
    __tablename__ = "quotations"
    
    id = Column(Integer, primary_key=True, index=True)
    quotation_number = Column(String(50), unique=True, nullable=False)  # e.g., PI-2026-0001
    client_id = Column(Integer, ForeignKey("clients.id"), index=True)
    status = Column(String(50), default="draft", index=True)  # draft, sent, confirmed, expired, cancelled
    total_amount = Column(Numeric(15, 2), default=0)
    currency = Column(String(10), default="USD")
    valid_until = Column(Date)
    notes = Column(String)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    client = relationship("Client", back_populates="quotations")
    creator = relationship("User", foreign_keys=[created_by])
    items = relationship("QuotationItem", back_populates="quotation", cascade="all, delete-orphan")
    order = relationship("Order", back_populates="quotation", uselist=False)


class QuotationItem(Base):
    """Line items in quotations."""
    __tablename__ = "quotation_items"
    
    id = Column(Integer, primary_key=True, index=True)
    quotation_id = Column(Integer, ForeignKey("quotations.id", ondelete="CASCADE"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(15, 2), nullable=False)
    discount_percent = Column(Numeric(5, 2), default=0)
    # line_total is computed: quantity * unit_price * (1 - discount_percent / 100)
    notes = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    quotation = relationship("Quotation", back_populates="items")
    product = relationship("Product", back_populates="quotation_items")
    
    @property
    def line_total(self):
        """Calculate line total with discount."""
        return float(self.quantity) * float(self.unit_price) * (1 - float(self.discount_percent) / 100)
