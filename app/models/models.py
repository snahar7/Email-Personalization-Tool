from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.database import Base

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    industry = Column(String(100))
    website = Column(String(200))
    description = Column(Text)
    # Research fields
    company_bio = Column(Text)
    product_info = Column(Text)
    key_insights = Column(Text)
    market_position = Column(String(200))
    funding_info = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    prospects = relationship("Prospect", back_populates="company")

class Prospect(Base):
    __tablename__ = "prospects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    position = Column(String(100))
    company_id = Column(Integer, ForeignKey("companies.id"))
    linkedin_url = Column(String(200))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    company = relationship("Company", back_populates="prospects") 