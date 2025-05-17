from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class ProspectBase(BaseModel):
    name: str
    email: EmailStr
    company: Optional[str] = None
    position: Optional[str] = None
    company_info: Optional[str] = None

class ProspectCreate(ProspectBase):
    pass

class Prospect(ProspectBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True 