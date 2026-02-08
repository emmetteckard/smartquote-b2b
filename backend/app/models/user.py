from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class Role(Base):
    """User roles: super_admin, admin, sales, client."""
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    users = relationship("User", back_populates="role")


class User(Base):
    """User accounts with role-based access."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"))
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    role = relationship("Role", back_populates="users")
    client = relationship("Client", back_populates="users", foreign_keys=[client_id])
    assigned_clients = relationship("Client", back_populates="sales_rep", foreign_keys="[Client.sales_rep_id]")
