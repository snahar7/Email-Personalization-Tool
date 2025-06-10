from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import pandas as pd
import io
from datetime import datetime, timedelta

from app.database.database import get_db
from app.models.models import Company, Prospect, EmailTemplate, EmailEngagement
from app.schemas.schemas import (
    Company, CompanyCreate,
    Prospect, ProspectCreate,
    EmailTemplate, EmailTemplateCreate,
    EmailEngagement, EmailEngagementCreate,
    EngagementMetrics, ProspectEngagement
)

router = APIRouter()

# Company endpoints
@router.post("/companies/", response_model=Company)
def create_company(company: CompanyCreate, db: Session = Depends(get_db)):
    db_company = Company(**company.dict())
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company

@router.get("/companies/", response_model=List[Company])
def get_companies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    companies = db.query(Company).offset(skip).limit(limit).all()
    return companies

@router.get("/companies/{company_id}", response_model=Company)
def get_company(company_id: int, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == company_id).first()
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return company

@router.put("/companies/{company_id}", response_model=Company)
def update_company(company_id: int, company_update: CompanyCreate, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == company_id).first()
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    
    for key, value in company_update.dict(exclude_unset=True).items():
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
@router.post("/prospects/", response_model=Prospect)
def create_prospect(prospect: ProspectCreate, db: Session = Depends(get_db)):
    db_prospect = Prospect(**prospect.dict())
    db.add(db_prospect)
    db.commit()
    db.refresh(db_prospect)
    return db_prospect

@router.get("/prospects/", response_model=List[Prospect])
def get_prospects(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Prospect)
    if status:
        query = query.filter(Prospect.status == status)
    prospects = query.offset(skip).limit(limit).all()
    return prospects

@router.get("/prospects/{prospect_id}", response_model=Prospect)
def get_prospect(prospect_id: int, db: Session = Depends(get_db)):
    prospect = db.query(Prospect).filter(Prospect.id == prospect_id).first()
    if prospect is None:
        raise HTTPException(status_code=404, detail="Prospect not found")
    return prospect

# Email Template endpoints
@router.post("/templates/", response_model=EmailTemplate)
def create_template(template: EmailTemplateCreate, db: Session = Depends(get_db)):
    db_template = EmailTemplate(**template.dict())
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template

@router.get("/templates/", response_model=List[EmailTemplate])
def get_templates(
    company_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    query = db.query(EmailTemplate)
    if company_id:
        query = query.filter(EmailTemplate.company_id == company_id)
    if is_active is not None:
        query = query.filter(EmailTemplate.is_active == is_active)
    return query.all()

# Email Engagement endpoints
@router.post("/engagements/", response_model=EmailEngagement)
def create_engagement(engagement: EmailEngagementCreate, db: Session = Depends(get_db)):
    db_engagement = EmailEngagement(**engagement.dict())
    db.add(db_engagement)
    
    # Update prospect's last_contacted and engagement_score
    prospect = db.query(Prospect).filter(Prospect.id == engagement.prospect_id).first()
    if prospect:
        prospect.last_contacted = datetime.utcnow()
        prospect.engagement_score += engagement.engagement_score
    
    db.commit()
    db.refresh(db_engagement)
    return db_engagement

@router.get("/engagements/metrics/", response_model=EngagementMetrics)
def get_engagement_metrics(
    company_id: Optional[int] = None,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    start_date = datetime.utcnow() - timedelta(days=days)
    query = db.query(EmailEngagement).filter(EmailEngagement.sent_at >= start_date)
    
    if company_id:
        query = query.join(Prospect).filter(Prospect.company_id == company_id)
    
    engagements = query.all()
    
    metrics = {
        "total_sent": len(engagements),
        "total_opened": sum(1 for e in engagements if e.opened_at),
        "total_clicked": sum(1 for e in engagements if e.clicked_at),
        "total_replied": sum(1 for e in engagements if e.replied_at),
        "average_engagement_score": sum(e.engagement_score for e in engagements) / len(engagements) if engagements else 0
    }
    
    # Find best performing template
    template_performance = {}
    for e in engagements:
        if e.template_id not in template_performance:
            template_performance[e.template_id] = {"opens": 0, "clicks": 0, "replies": 0}
        if e.opened_at:
            template_performance[e.template_id]["opens"] += 1
        if e.clicked_at:
            template_performance[e.template_id]["clicks"] += 1
        if e.replied_at:
            template_performance[e.template_id]["replies"] += 1
    
    best_template_id = max(
        template_performance.items(),
        key=lambda x: x[1]["opens"] + x[1]["clicks"] + x[1]["replies"]
    )[0] if template_performance else None
    
    if best_template_id:
        best_template = db.query(EmailTemplate).filter(EmailTemplate.id == best_template_id).first()
        metrics["best_performing_template"] = best_template.name if best_template else None
    
    return metrics

@router.get("/prospects/{prospect_id}/engagement/", response_model=ProspectEngagement)
def get_prospect_engagement(prospect_id: int, db: Session = Depends(get_db)):
    prospect = db.query(Prospect).filter(Prospect.id == prospect_id).first()
    if not prospect:
        raise HTTPException(status_code=404, detail="Prospect not found")
    
    engagements = db.query(EmailEngagement).filter(
        EmailEngagement.prospect_id == prospect_id
    ).order_by(EmailEngagement.sent_at.desc()).all()
    
    engagement_trend = [
        {
            "sent": e.sent_at,
            "opened": e.opened_at,
            "clicked": e.clicked_at,
            "replied": e.replied_at
        }
        for e in engagements
    ]
    
    return {
        "prospect": prospect,
        "total_emails": len(engagements),
        "last_engagement": engagements[0].sent_at if engagements else None,
        "engagement_trend": engagement_trend
    } 