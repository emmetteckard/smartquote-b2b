from sqlalchemy import Column, Integer, String, Boolean, DateTime, Numeric, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class ProductComponent(Base):
    """
    Represents a component of a bundle product.
    parent_product: The bundle (composite) SKU.
    child_product: The component SKU.
    quantity: How many of child needed for one parent.
    """
    __tablename__ = "product_components"

    id = Column(Integer, primary_key=True, index=True)
    parent_product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    child_product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    quantity = Column(Integer, default=1, nullable=False)

    # Relationships
    # Use string "Product" to avoid circular reference issue since Product is defined below
    parent = relationship("Product", foreign_keys=[parent_product_id], back_populates="components")
    child = relationship("Product", foreign_keys=[child_product_id])

    __table_args__ = (
        UniqueConstraint('parent_product_id', 'child_product_id', name='uq_product_component_parent_child'),
    )


class Product(Base):
    """Product catalog."""
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(100), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(String)
    category = Column(String(100))
    unit = Column(String(50), default="pcs")  # pieces, kg, m, etc.
    min_order_qty = Column(Integer, default=1)
    lingxing_product_id = Column(String(100))  # ERP reference
    
    # Shipping Info
    package_length = Column(Numeric(10, 2), nullable=True) # cm
    package_width = Column(Numeric(10, 2), nullable=True)  # cm
    package_height = Column(Numeric(10, 2), nullable=True) # cm
    package_weight = Column(Numeric(10, 2), nullable=True) # kg
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    base_prices = relationship("BasePrice", back_populates="product", cascade="all, delete-orphan")
    client_prices = relationship("ClientPrice", back_populates="product", cascade="all, delete-orphan")
    inventory = relationship("Inventory", back_populates="product", cascade="all, delete-orphan")
    quotation_items = relationship("QuotationItem", back_populates="product")
    order_items = relationship("OrderItem", back_populates="product")
    
    # Now ProductComponent is defined above, so we can reference it. 
    # Also foreign_keys can refer to the Class attribute directly if needed, or string if strict.
    # User had issue with "ProductComponent.parent_product_id" string lookup failure.
    # Since class is available:
    components = relationship(ProductComponent, foreign_keys=[ProductComponent.parent_product_id], back_populates="parent", cascade="all, delete-orphan")
