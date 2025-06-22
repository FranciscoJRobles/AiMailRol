from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from api.core.database import SessionLocal
from api.schemas.character import CharacterCreate, CharacterOut
from api.managers.character_manager import CharacterManager
from pydantic import BaseModel
from typing import Any, Dict

router = APIRouter(prefix="/characters", tags=["characters"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=CharacterOut)
def create_character(character: CharacterCreate, db: Session = Depends(get_db)):
    return CharacterManager.create(db, character)

@router.get("/{character_id}", response_model=CharacterOut)
def get_character(character_id: int, db: Session = Depends(get_db)):
    return CharacterManager.get(db, character_id)

@router.get("/", response_model=list[CharacterOut])
def list_characters(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return CharacterManager.list(db, skip, limit)

@router.delete("/{character_id}", response_model=CharacterOut)
def delete_character(character_id: int, db: Session = Depends(get_db)):
    return CharacterManager.delete(db, character_id)

@router.put("/{character_id}", response_model=CharacterOut)
def update_character(character_id: int, character: CharacterCreate, db: Session = Depends(get_db)):
    return CharacterManager.update(db, character_id, character.model_dump())

# Endpoints PATCH para modificar solo los campos hoja_json y estado_actual

@router.patch("/{character_id}/hoja_json", response_model=CharacterOut)
def update_hoja_json(character_id: int, data: dict = Body(...), db: Session = Depends(get_db)):
    character = db.query(CharacterManager.get_model()).filter_by(id=character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found for character_id")
    character.hoja_json = data
    db.commit()
    db.refresh(character)
    return character

@router.patch("/{character_id}/estado_actual", response_model=CharacterOut)
def update_estado_actual(character_id: int, data: dict = Body(...), db: Session = Depends(get_db)):
    character = db.query(CharacterManager.get_model()).filter_by(id=character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found for character_id")
    character.estado_actual = data
    db.commit()
    db.refresh(character)
    return character
