from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime

class CompanyBase(BaseModel):
    name: str
    domain: str
    description: Optional[str] = None
    website_url: HttpUrl
    industry_category: str

class CompanyCreate(CompanyBase):
    pass

class CompanyUpdate(CompanyBase):
    pass

class Company(CompanyBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True