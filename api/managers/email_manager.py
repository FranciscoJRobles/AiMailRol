from typing import List
from sqlalchemy.orm import Session
from api.models.email import Email
from api.schemas.email import EmailCreate, EmailOut
from fastapi import HTTPException

class EmailManager:
    @staticmethod
    def create(db: Session, email: EmailCreate):
        """Crea un nuevo email"""
        db_email = Email(**email.model_dump())
        db.add(db_email)
        db.commit()
        db.refresh(db_email)
        return db_email

    @staticmethod
    def get(db: Session, email_id: int):
        """Obtiene un email por ID"""
        email = db.query(Email).filter(Email.id == email_id).first()
        if not email:
            raise HTTPException(status_code=404, detail="Email not found")
        return email

    @staticmethod
    def list(db: Session, skip: int = 0, limit: int = 100):
        """Lista todos los emails con paginación"""
        return db.query(Email).offset(skip).limit(limit).all()

    @staticmethod
    def delete(db: Session, email_id: int):
        """Elimina un email"""
        db_email = db.query(Email).filter(Email.id == email_id).first()
        if not db_email:
            raise HTTPException(status_code=404, detail="Email not found")
        db.delete(db_email)
        db.commit()
        return db_email

    @staticmethod
    def update(db: Session, email_id: int, email_data: dict):
        """Actualiza un email"""
        db_email = db.query(Email).filter(Email.id == email_id).first()
        if not db_email:
            raise HTTPException(status_code=404, detail="Email not found")
        for key, value in email_data.items():
            setattr(db_email, key, value)
        db.commit()
        db.refresh(db_email)
        return db_email

    @staticmethod
    def get_next_email(db: Session) -> Email:
        """Devuelve el email no procesado más antiguo"""
        return db.query(Email).filter(Email.processed == False).order_by(Email.date.asc()).first()

    @staticmethod
    def get_emails_processed_not_sumarized_by_scene_id(db: Session, scene_id: int):
        """Obtiene todos los emails asociados a una escena específica"""
        return db.query(Email).filter(Email.scene_id == scene_id, Email.processed == True, Email.resumido == False).order_by(Email.date.asc()).all()

    @staticmethod
    def mark_emails_as_sumarized(db: Session, emails: List[Email]):
        """Marca una lista de emails como resumidos"""
        for email in emails:
            email.resumido = True
        db.commit()
        