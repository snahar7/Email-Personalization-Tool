from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON
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
    email_templates = relationship("EmailTemplate", back_populates="company")

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
    # New fields for engagement tracking
    last_contacted = Column(DateTime(timezone=True))
    engagement_score = Column(Integer, default=0)
    status = Column(String(50), default="new")  # new, contacted, engaged, qualified, converted
    notes = Column(Text)

    company = relationship("Company", back_populates="prospects")
    email_engagements = relationship("EmailEngagement", back_populates="prospect")

class EmailTemplate(Base):
    __tablename__ = "email_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    subject = Column(String(200))
    body = Column(Text)
    company_id = Column(Integer, ForeignKey("companies.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    # A/B testing fields
    variant = Column(String(50))
    performance_metrics = Column(JSON)

    company = relationship("Company", back_populates="email_templates")
    engagements = relationship("EmailEngagement", back_populates="template")

class EmailEngagement(Base):
    __tablename__ = "email_engagements"

    id = Column(Integer, primary_key=True, index=True)
    prospect_id = Column(Integer, ForeignKey("prospects.id"))
    template_id = Column(Integer, ForeignKey("email_templates.id"))
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
    opened_at = Column(DateTime(timezone=True))
    clicked_at = Column(DateTime(timezone=True))
    replied_at = Column(DateTime(timezone=True))
    response_content = Column(Text)
    engagement_score = Column(Integer, default=0)

    prospect = relationship("Prospect", back_populates="email_engagements")
    template = relationship("EmailTemplate", back_populates="engagements") 