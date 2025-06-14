from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ..schemas.company import Company, CompanyCreate, CompanyUpdate
from ..auth.auth import get_current_user
from backend.models import crud

router = APIRouter()

@router.get("/", response_model=List[Company])
async def list_companies():
    """Get list of all companies"""
    return crud.get_companies()

@router.get("/{company_id}", response_model=Company)
async def get_company(company_id: str):
    """Get company details by ID"""
    company = crud.get_company(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company

@router.post("/", response_model=Company)
async def create_company(company: CompanyCreate):
    """Create a new company"""
    return crud.create_company(company.dict())

@router.put("/{company_id}", response_model=Company)
async def update_company(company_id: str, company: CompanyUpdate):
    """Update company details"""
    updated = crud.update_company(company_id, company.dict())
    if not updated:
        raise HTTPException(status_code=404, detail="Company not found")
    return updated