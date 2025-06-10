from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import pandas as pd
import io

from app.database.database import get_db
from app.models.models import Company, Prospect
from app.schemas.schemas import CompanyCreate, Company as CompanySchema, ProspectCreate, Prospect as ProspectSchema

router = APIRouter()

# Company endpoints
@router.post("/companies/", response_model=CompanySchema)
def create_company(company: CompanyCreate, db: Session = Depends(get_db)):
    db_company = Company(**company.model_dump())
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company

@router.get("/companies/{company_id}", response_model=CompanySchema)
def get_company(company_id: int, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == company_id).first()
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return company

@router.put("/companies/{company_id}", response_model=CompanySchema)
def update_company(company_id: int, company_update: CompanyCreate, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == company_id).first()
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    
    for key, value in company_update.model_dump(exclude_unset=True).items():
        setattr(company, key, value)
    
    db.commit()
    db.refresh(company)
    return company

# CSV Upload endpoint
@router.post("/companies/upload-csv")
async def upload_companies_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        # Process each row
        for _, row in df.iterrows():
            # Create or get company
            company = db.query(Company).filter(Company.name == row['company']).first()
            if not company:
                company = Company(
                    name=row['company'],
                    industry=row.get('industry'),
                    website=row.get('website'),
                    description=row.get('company_description')
                )
                db.add(company)
                db.commit()
                db.refresh(company)
            
            # Create prospect
            prospect = Prospect(
                name=row['name'],
                email=row['email'],
                position=row['title'],
                company_id=company.id,
                linkedin_url=row.get('linkedin')
            )
            db.add(prospect)
        
        db.commit()
        return {"message": "CSV processed successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Prospect endpoints
@router.post("/prospects/", response_model=ProspectSchema)
def create_prospect(prospect: ProspectCreate, db: Session = Depends(get_db)):
    db_prospect = Prospect(**prospect.model_dump())
    db.add(db_prospect)
    db.commit()
    db.refresh(db_prospect)
    return db_prospect

@router.get("/prospects/{prospect_id}", response_model=ProspectSchema)
def get_prospect(prospect_id: int, db: Session = Depends(get_db)):
    prospect = db.query(Prospect).filter(Prospect.id == prospect_id).first()
    if prospect is None:
        raise HTTPException(status_code=404, detail="Prospect not found")
    return prospect

@router.get("/prospects/", response_model=List[ProspectSchema])
def list_prospects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    prospects = db.query(Prospect).offset(skip).limit(limit).all()
    return prospects 