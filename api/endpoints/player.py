from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.core.database import get_db
from api.schemas.player import PlayerCreate, PlayerOut
from api.managers.player_manager import PlayerManager

router = APIRouter(prefix="/players", tags=["players"])

@router.post("/", response_model=PlayerOut)
def create_player(player: PlayerCreate, db: Session = Depends(get_db)):
    return PlayerManager.create(db, player)

@router.get("/{player_id}", response_model=PlayerOut)
def get_player(player_id: int, db: Session = Depends(get_db)):
    return PlayerManager.get(db, player_id)

@router.get("/", response_model=list[PlayerOut])
def list_players(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return PlayerManager.list(db, skip, limit)

@router.put("/{player_id}", response_model=PlayerOut)
def update_player(player_id: int, player: PlayerCreate, db: Session = Depends(get_db)):
    return PlayerManager.update(db, player_id, player.model_dump())

@router.delete("/{player_id}", response_model=PlayerOut)
def delete_player(player_id: int, db: Session = Depends(get_db)):
    return PlayerManager.delete(db, player_id)

