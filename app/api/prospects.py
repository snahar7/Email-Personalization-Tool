from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database.database import get_db
from app.models.prospect import Prospect
from app.schemas.prospect import ProspectCreate, Prospect as ProspectSchema

router = APIRouter()

@router.post("/", response_model=ProspectSchema)
def create_prospect(prospect: ProspectCreate, db: Session = Depends(get_db)):
    db_prospect = Prospect(**prospect.model_dump())
    db.add(db_prospect)
    db.commit()
    db.refresh(db_prospect)
    return db_prospect

@router.get("/{prospect_id}", response_model=ProspectSchema)
def get_prospect(prospect_id: int, db: Session = Depends(get_db)):
    prospect = db.query(Prospect).filter(Prospect.id == prospect_id).first()
    if prospect is None:
        raise HTTPException(status_code=404, detail="Prospect not found")
    return prospect

@router.get("/", response_model=List[ProspectSchema])
def list_prospects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    prospects = db.query(Prospect).offset(skip).limit(limit).all()
    return prospects 