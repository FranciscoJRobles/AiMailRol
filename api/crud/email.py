from sqlalchemy.orm import Session
from api.models.email import Email
from api.schemas.email import EmailCreate

def create_email(db: Session, email: EmailCreate) -> Email:
    db_email = Email(**email.model_dump())
    db.add(db_email)
    db.commit()
    db.refresh(db_email)
    return db_email

def get_email(db: Session, email_id: int) -> Email:
    return db.query(Email).filter(Email.id == email_id).first()

def get_emails(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Email).offset(skip).limit(limit).all()

def delete_email(db: Session, email_id: int):
    db_email = db.query(Email).filter(Email.id == email_id).first()
    if db_email:
        db.delete(db_email)
        db.commit()
    return db_email

def update_email(db: Session, email_id: int, email_data: dict):
    db_email = db.query(Email).filter(Email.id == email_id).first()
    if db_email:
        for key, value in email_data.items():
            setattr(db_email, key, value)
        db.commit()
        db.refresh(db_email)
    return db_email
