import csv
import io
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models import models
from app.schemas import schemas

router = APIRouter()

# Company endpoints
@router.post("/companies/", response_model=schemas.Company)
def create_company(company: schemas.CompanyCreate, db: Session = Depends(get_db)):
    db_company = models.Company(**company.model_dump())
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company

@router.get("/companies/", response_model=List[schemas.Company])
def get_companies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    companies = db.query(models.Company).offset(skip).limit(limit).all()
    return companies

@router.get("/companies/{company_id}", response_model=schemas.Company)
def get_company(company_id: int, db: Session = Depends(get_db)):
    company = db.query(models.Company).filter(models.Company.id == company_id).first()
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return company

@router.put("/companies/{company_id}", response_model=schemas.Company)
def update_company(company_id: int, company_update: schemas.CompanyCreate, db: Session = Depends(get_db)):
    company = db.query(models.Company).filter(models.Company.id == company_id).first()
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
    
    contents = await file.read()
    try:
        reader = csv.DictReader(io.StringIO(contents.decode("utf-8-sig")))
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="CSV must be UTF-8")
    required = {"name", "email", "title", "company"}
    missing = required - set(reader.fieldnames or [])
    if missing:
        raise HTTPException(status_code=400, detail=f"CSV missing columns: {sorted(missing)}")

    companies_created = prospects_created = prospects_skipped = 0
    for row in reader:
        company = db.query(models.Company).filter(models.Company.name == row["company"]).first()
        if not company:
            company = models.Company(
                name=row["company"],
                industry=row.get("industry") or None,
                website=row.get("website") or None,
                description=row.get("company_description") or None,
            )
            db.add(company)
            db.flush()
            companies_created += 1
        if db.query(models.Prospect).filter(models.Prospect.email == row["email"]).first():
            prospects_skipped += 1
            continue
        db.add(models.Prospect(
            name=row["name"],
            email=row["email"],
            position=row.get("title") or None,
            company_id=company.id,
            linkedin_url=row.get("linkedin") or None,
        ))
        prospects_created += 1
    db.commit()
    return {
        "message": "CSV processed successfully",
        "companies_created": companies_created,
        "prospects_created": prospects_created,
        "prospects_skipped": prospects_skipped,
    }

# Prospect endpoints
@router.post("/prospects/", response_model=schemas.Prospect)
def create_prospect(prospect: schemas.ProspectCreate, db: Session = Depends(get_db)):
    db_prospect = models.Prospect(**prospect.model_dump())
    db.add(db_prospect)
    db.commit()
    db.refresh(db_prospect)
    return db_prospect

@router.get("/prospects/", response_model=List[schemas.Prospect])
def get_prospects(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Prospect)
    if status:
        query = query.filter(models.Prospect.status == status)
    prospects = query.offset(skip).limit(limit).all()
    return prospects

@router.get("/prospects/{prospect_id}", response_model=schemas.Prospect)
def get_prospect(prospect_id: int, db: Session = Depends(get_db)):
    prospect = db.query(models.Prospect).filter(models.Prospect.id == prospect_id).first()
    if prospect is None:
        raise HTTPException(status_code=404, detail="Prospect not found")
    return prospect

# Email Template endpoints
@router.post("/templates/", response_model=schemas.EmailTemplate)
def create_template(template: schemas.EmailTemplateCreate, db: Session = Depends(get_db)):
    db_template = models.EmailTemplate(**template.model_dump())
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template

@router.get("/templates/", response_model=List[schemas.EmailTemplate])
def get_templates(
    company_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.EmailTemplate)
    if company_id:
        query = query.filter(models.EmailTemplate.company_id == company_id)
    if is_active is not None:
        query = query.filter(models.EmailTemplate.is_active == is_active)
    return query.all()

# Email Engagement endpoints
@router.post("/engagements/", response_model=schemas.EmailEngagement)
def create_engagement(engagement: schemas.EmailEngagementCreate, db: Session = Depends(get_db)):
    db_engagement = models.EmailEngagement(**engagement.model_dump())
    db.add(db_engagement)
    
    # Update prospect's last_contacted and engagement_score
    prospect = db.query(models.Prospect).filter(models.Prospect.id == engagement.prospect_id).first()
    if prospect:
        prospect.last_contacted = datetime.now(timezone.utc)
        prospect.engagement_score = (prospect.engagement_score or 0) + engagement.engagement_score
    
    db.commit()
    db.refresh(db_engagement)
    return db_engagement

@router.get("/engagements/metrics/", response_model=schemas.EngagementMetrics)
def get_engagement_metrics(
    company_id: Optional[int] = None,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    start_date = datetime.now(timezone.utc) - timedelta(days=days)
    query = db.query(models.EmailEngagement).filter(models.EmailEngagement.sent_at >= start_date)
    
    if company_id:
        query = query.join(models.Prospect).filter(models.Prospect.company_id == company_id)
    
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
        best_template = db.query(models.EmailTemplate).filter(models.EmailTemplate.id == best_template_id).first()
        metrics["best_performing_template"] = best_template.name if best_template else None
    
    return metrics

@router.get("/prospects/{prospect_id}/engagement/", response_model=schemas.ProspectEngagement)
def get_prospect_engagement(prospect_id: int, db: Session = Depends(get_db)):
    prospect = db.query(models.Prospect).filter(models.Prospect.id == prospect_id).first()
    if not prospect:
        raise HTTPException(status_code=404, detail="Prospect not found")
    
    engagements = db.query(models.EmailEngagement).filter(
        models.EmailEngagement.prospect_id == prospect_id
    ).order_by(models.EmailEngagement.sent_at.desc()).all()
    
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

# AI email generation and sending
from app.services import email_service  # noqa: E402


def _get_prospect_or_404(db: Session, prospect_id: int) -> models.Prospect:
    prospect = db.query(models.Prospect).filter(models.Prospect.id == prospect_id).first()
    if prospect is None:
        raise HTTPException(status_code=404, detail="Prospect not found")
    return prospect


@router.post("/prospects/{prospect_id}/generate-email", response_model=schemas.GeneratedEmail)
def generate_email(
    prospect_id: int,
    request: Optional[schemas.GenerateEmailRequest] = None,
    db: Session = Depends(get_db),
):
    request = request or schemas.GenerateEmailRequest()
    prospect = _get_prospect_or_404(db, prospect_id)
    template = None
    if request.template_id is not None:
        template = db.query(models.EmailTemplate).filter(models.EmailTemplate.id == request.template_id).first()
        if template is None:
            raise HTTPException(status_code=404, detail="Template not found")
    try:
        result = email_service.generate_personalized_email(
            prospect, prospect.company, template, request.additional_context
        )
    except email_service.ConfigError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:  # OpenAI/network errors
        raise HTTPException(status_code=502, detail=f"Email generation failed: {e}")
    return {"prospect_id": prospect.id, **result}


@router.post("/prospects/{prospect_id}/send-email", response_model=schemas.SendEmailResult)
def send_email(prospect_id: int, request: schemas.SendEmailRequest, db: Session = Depends(get_db)):
    prospect = _get_prospect_or_404(db, prospect_id)
    try:
        email_service.send_email(prospect.email, request.subject, request.body)
    except email_service.ConfigError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Sending failed: {e}")
    prospect.last_contacted = datetime.now(timezone.utc)
    if prospect.status == "new":
        prospect.status = "contacted"
    engagement_id = None
    if request.template_id is not None:
        engagement = models.EmailEngagement(prospect_id=prospect.id, template_id=request.template_id)
        db.add(engagement)
        db.flush()
        engagement_id = engagement.id
    db.commit()
    return {"prospect_id": prospect.id, "to": prospect.email, "sent": True, "engagement_id": engagement_id}
