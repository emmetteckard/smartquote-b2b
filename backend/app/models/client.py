from sqlalchemy import Column, Integer, String, Boolean, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class Client(Base):
    """Client company information."""
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(255), nullable=False)
    contact_person = Column(String(255))
    email = Column(String(255))
    phone = Column(String(50))
    address = Column(String)
    tax_id = Column(String(100))
    payment_terms = Column(Integer, default=30)  # days
    credit_limit = Column(Numeric(15, 2))
    tier = Column(String(10), default="A")  # 'X', 'S', 'A' pricing tier
    sales_rep_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    users = relationship("User", foreign_keys="[User.client_id]", back_populates="client")
    sales_rep = relationship("User", foreign_keys=[sales_rep_id], back_populates="assigned_clients")
    client_prices = relationship("ClientPrice", back_populates="client", cascade="all, delete-orphan")
    quotations = relationship("Quotation", back_populates="client")
    orders = relationship("Order", back_populates="client")
