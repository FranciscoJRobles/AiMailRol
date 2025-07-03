from sqlalchemy.orm import Session
from api.models.player import Player, PlayerStatus
from api.schemas.player import PlayerCreate, PlayerUpdate
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from typing import Optional
from email.utils import parseaddr

class PlayerManager:
    @staticmethod
    def create(db: Session, player: PlayerCreate):
        """Crea un nuevo jugador"""
        db_player = Player(email=player.email, nickname=player.nickname, estado=player.estado)
        db.add(db_player)
        try:
            db.commit()
            db.refresh(db_player)
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email o nickname ya registrado.")
        return db_player

    @staticmethod
    def get(db: Session, player_id: int):
        """Obtiene un jugador por ID"""
        player = db.query(Player).filter(Player.id == player_id).first()
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        return player

    @staticmethod
    def list(db: Session, skip: int = 0, limit: int = 100):
        """Lista todos los jugadores con paginación"""
        return db.query(Player).offset(skip).limit(limit).all()

    @staticmethod
    def delete(db: Session, player_id: int):
        """Elimina un jugador"""
        player = PlayerManager.get(db, player_id)
        db.delete(player)
        db.commit()
        return player

    @staticmethod
    def update(db: Session, player_id: int, player_data: dict):
        """Actualiza un jugador"""
        player = PlayerManager.get(db, player_id)
        for key, value in player_data.items():
            setattr(player, key, value)
        db.commit()
        db.refresh(player)
        return player

    @staticmethod
    def get_player_id_by_email(db: Session, email: str) -> Optional[int]:
        """Devuelve el ID del jugador actual asociado a un email"""
        # Extraer solo la dirección de correo electrónico
        email_address = parseaddr(email)[1]
        player = db.query(Player).filter(Player.email == email_address).first()
        return player.id if player else None
