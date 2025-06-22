from api.crud.email import create_email, get_email, get_emails, delete_email, update_email
from api.schemas.email import EmailCreate, EmailOut
from fastapi import HTTPException
from sqlalchemy.orm import Session

class EmailManager:
    @staticmethod
    def create(db: Session, email: EmailCreate):
        return create_email(db, email)

    @staticmethod
    def get(db: Session, email_id: int):
        email = get_email(db, email_id)
        if not email:
            raise HTTPException(status_code=404, detail="Email not found")
        return email

    @staticmethod
    def list(db: Session, skip: int = 0, limit: int = 100):
        return get_emails(db, skip, limit)

    @staticmethod
    def delete(db: Session, email_id: int):
        email = delete_email(db, email_id)
        if not email:
            raise HTTPException(status_code=404, detail="Email not found")
        return email

    @staticmethod
    def update(db: Session, email_id: int, email_data: dict):
        email = update_email(db, email_id, email_data)
        if not email:
            raise HTTPException(status_code=404, detail="Email not found")
        return email
