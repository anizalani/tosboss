from . import Company
from backend.utils.db import SessionLocal

def create_company(data):
    db = SessionLocal()
    company = Company(**data)
    db.add(company)
    db.commit()
    db.refresh(company)
    db.close()
    return company

def get_company(company_id):
    db = SessionLocal()
    company = db.query(Company).filter(Company.id == company_id).first()
    db.close()
    return company

def update_company(company_id, updates):
    db = SessionLocal()
    company = db.query(Company).filter(Company.id == company_id).first()
    for key, value in updates.items():
        setattr(company, key, value)
    db.commit()
    db.refresh(company)
    db.close()
    return company

def delete_company(company_id):
    db = SessionLocal()
    company = db.query(Company).filter(Company.id == company_id).first()
    db.delete(company)
    db.commit()
    db.close()