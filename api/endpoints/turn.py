from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from api.schemas.turn import TurnCreate, TurnUpdate, TurnOut
from api.managers.turn_manager import TurnManager
from api.core.database import get_db

router = APIRouter(prefix="/turns", tags=["turns"])

@router.post("/", response_model=TurnOut)
def create_turn(turn: TurnCreate, db: Session = Depends(get_db)):
    return TurnManager.create_turn(db, turn)

@router.get("/", response_model=List[TurnOut])
def read_turns(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return TurnManager.get_turns(db, skip=skip, limit=limit)

@router.get("/{turn_id}", response_model=TurnOut)
def read_turn(turn_id: int, db: Session = Depends(get_db)):
    turn = TurnManager.get_turn(db, turn_id)
    if not turn:
        raise HTTPException(status_code=404, detail="Turn not found")
    return turn

@router.put("/{turn_id}", response_model=TurnOut)
def update_turn(turn_id: int, turn_update: TurnUpdate, db: Session = Depends(get_db)):
    turn = TurnManager.update_turn(db, turn_id, turn_update)
    if not turn:
        raise HTTPException(status_code=404, detail="Turn not found")
    return turn

@router.delete("/{turn_id}", response_model=dict)
def delete_turn(turn_id: int, db: Session = Depends(get_db)):
    success = TurnManager.delete_turn(db, turn_id)
    if not success:
        raise HTTPException(status_code=404, detail="Turn not found")
    return {"ok": True}
