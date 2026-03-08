from sqlalchemy import (
    Column, Integer, String, Boolean, Text, 
    DateTime, ForeignKey, BigInteger, Float, Table
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

# --- USER AUTHENTICATION ---
class User(Base):
    __tablename__ = "users"
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=True)
    role = Column(String(20), server_default="student")
    auth_provider = Column(String(20), server_default="email")
    google_id = Column(String(255), unique=True, nullable=True)
    is_active = Column(Boolean, server_default="true")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)



