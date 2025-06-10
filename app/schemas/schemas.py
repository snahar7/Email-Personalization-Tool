from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List, Dict

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
    company_id: int
    linkedin_url: Optional[str] = None
    status: Optional[str] = "new"
    notes: Optional[str] = None

class ProspectCreate(ProspectBase):
    pass

class Prospect(ProspectBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_contacted: Optional[datetime] = None
    engagement_score: int = 0

    class Config:
        from_attributes = True

class EmailTemplateBase(BaseModel):
    name: str
    subject: str
    body: str
    company_id: int
    is_active: bool = True
    variant: Optional[str] = None
    performance_metrics: Optional[Dict] = None

class EmailTemplateCreate(EmailTemplateBase):
    pass

class EmailTemplate(EmailTemplateBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class EmailEngagementBase(BaseModel):
    prospect_id: int
    template_id: int
    response_content: Optional[str] = None
    engagement_score: int = 0

class EmailEngagementCreate(EmailEngagementBase):
    pass

class EmailEngagement(EmailEngagementBase):
    id: int
    sent_at: datetime
    opened_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None
    replied_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Response models for analytics
class EngagementMetrics(BaseModel):
    total_sent: int
    total_opened: int
    total_clicked: int
    total_replied: int
    average_engagement_score: float
    best_performing_template: Optional[str] = None
    best_sending_time: Optional[str] = None

class ProspectEngagement(BaseModel):
    prospect: Prospect
    total_emails: int
    last_engagement: Optional[datetime] = None
    engagement_trend: List[Dict[str, datetime]] 