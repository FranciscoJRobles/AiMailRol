from sqlalchemy.orm import Session
from api.models.player import Player, PlayerStatus
from api.schemas.player import PlayerCreate
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

def create(db: Session, player: PlayerCreate):
    db_player = Player(email=player.email, nickname=player.nickname, estado=player.estado)
    db.add(db_player)
    try:
        db.commit()
        db.refresh(db_player)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email o nickname ya registrado.")
    return db_player

def get(db: Session, player_id: int):
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player

def list(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Player).offset(skip).limit(limit).all()

def delete(db: Session, player_id: int):
    player = get(db, player_id)
    db.delete(player)
    db.commit()
    return player

def update(db: Session, player_id: int, player_data: dict):
    player = get(db, player_id)
    for key, value in player_data.items():
        setattr(player, key, value)
    db.commit()
    db.refresh(player)
    return player
