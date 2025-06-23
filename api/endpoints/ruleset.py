from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from api.schemas.ruleset import RulesetCreate, RulesetUpdate, RulesetOut
from api.managers.ruleset_manager import RulesetManager
from api.core.database import get_db

router = APIRouter(prefix="/rulesets", tags=["rulesets"])

@router.post("/", response_model=RulesetOut)
def create_ruleset(ruleset: RulesetCreate, db: Session = Depends(get_db)):
    return RulesetManager.create_ruleset(db, ruleset)

@router.get("/", response_model=List[RulesetOut])
def read_rulesets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return RulesetManager.get_rulesets(db, skip=skip, limit=limit)

@router.get("/{ruleset_id}", response_model=RulesetOut)
def read_ruleset(ruleset_id: int, db: Session = Depends(get_db)):
    ruleset = RulesetManager.get_ruleset(db, ruleset_id)
    if not ruleset:
        raise HTTPException(status_code=404, detail="Ruleset not found")
    return ruleset

@router.put("/{ruleset_id}", response_model=RulesetOut)
def update_ruleset(ruleset_id: int, ruleset_update: RulesetUpdate, db: Session = Depends(get_db)):
    ruleset = RulesetManager.update_ruleset(db, ruleset_id, ruleset_update)
    if not ruleset:
        raise HTTPException(status_code=404, detail="Ruleset not found")
    return ruleset

@router.patch("/{ruleset_id}", response_model=RulesetOut)
def partial_update_ruleset(ruleset_id: int, ruleset_update: RulesetUpdate, db: Session = Depends(get_db)):
    ruleset = RulesetManager.update_ruleset(db, ruleset_id, ruleset_update)
    if not ruleset:
        raise HTTPException(status_code=404, detail="Ruleset not found")
    return ruleset

@router.delete("/{ruleset_id}", response_model=dict)
def delete_ruleset(ruleset_id: int, db: Session = Depends(get_db)):
    success = RulesetManager.delete_ruleset(db, ruleset_id)
    if not success:
        raise HTTPException(status_code=404, detail="Ruleset not found")
    return {"ok": True}
