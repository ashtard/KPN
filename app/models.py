from __future__ import annotations
from sqlalchemy import Column, Integer, String, DateTime, func
from .db import Base


class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(200), nullable=False, index=True)
    email = Column(String(254), nullable=False, unique=True, index=True)
    phone = Column(String(50), nullable=True, unique=True, index=True)
    address = Column(String(400), nullable=True)
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True),
                        server_default=func.now(), onupdate=func.now(), nullable=False)