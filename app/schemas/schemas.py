from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

# Company Schemas
class CompanyBase(BaseModel):
    name: str
    industry: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    company_bio: Optional[str] = None
    product_info: Optional[str] = None
    key_insights: Optional[str] = None
    market_position: Optional[str] = None
    funding_info: Optional[str] = None

class CompanyCreate(CompanyBase):
    pass

class Company(CompanyBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Prospect Schemas
class ProspectBase(BaseModel):
    name: str
    email: EmailStr
    position: Optional[str] = None
    company_id: Optional[int] = None
    linkedin_url: Optional[str] = None

class ProspectCreate(ProspectBase):
    pass

class Prospect(ProspectBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    company: Optional[Company] = None

    class Config:
        from_attributes = True 