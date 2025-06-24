from sqlalchemy.orm import Session
from api.models.character import Character
from api.schemas.character import CharacterCreate, CharacterUpdate
from fastapi import HTTPException, status
from api.models.associations import campaign_characters

def create(db: Session, character: CharacterCreate):
    db_character = Character(**character.model_dump())
    db.add(db_character)
    db.commit()
    db.refresh(db_character)
    return db_character

def get(db: Session, character_id: int):
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    return character

def list(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Character).offset(skip).limit(limit).all()

def delete(db: Session, character_id: int):
    character = get(db, character_id)
    db.delete(character)
    db.commit()
    return character

def update(db: Session, character_id: int, character_data: CharacterUpdate):
    character = get(db, character_id)
    for key, value in character_data.model_dump(exclude_unset=True).items():
        setattr(character, key, value)
    db.commit()
    db.refresh(character)
    return character

def get_character_id_by_player_and_campaign(db, player_id: int, campaign_id: int):
    """
    Devuelve el character_id del personaje de un jugador en una campaña concreta.
    """
    character = db.query(Character).join(
        campaign_characters,
        (Character.id == campaign_characters.c.character_id)
    ).filter(
        campaign_characters.c.campaign_id == campaign_id,
        Character.player_id == player_id
    ).first()
    return character.id if character else None
