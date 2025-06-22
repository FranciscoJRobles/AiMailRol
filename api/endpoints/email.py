from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.core.database import SessionLocal
from api.schemas.email import EmailCreate, EmailOut
from api.managers.email_manager import EmailManager

router = APIRouter(prefix="/emails", tags=["emails"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=EmailOut)
def create_email(email: EmailCreate, db: Session = Depends(get_db)):
    return EmailManager.create(db, email)

@router.get("/{email_id}", response_model=EmailOut)
def get_email(email_id: int, db: Session = Depends(get_db)):
    return EmailManager.get(db, email_id)

@router.get("/", response_model=list[EmailOut])
def list_emails(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return EmailManager.list(db, skip, limit)

@router.delete("/{email_id}", response_model=EmailOut)
def delete_email(email_id: int, db: Session = Depends(get_db)):
    return EmailManager.delete(db, email_id)

@router.put("/{email_id}", response_model=EmailOut)
def update_email(email_id: int, email: EmailCreate, db: Session = Depends(get_db)):
    return EmailManager.update(db, email_id, email.model_dump())
