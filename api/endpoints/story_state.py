from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from api.schemas.story_state import StoryStateCreate, StoryStateUpdate, StoryStateOut
from api.managers.story_state_manager import StoryStateManager
from api.core.database import get_db

router = APIRouter(prefix="/story_states", tags=["story_states"])

@router.post("/", response_model=StoryStateOut)
def create_story_state(story_state: StoryStateCreate, db: Session = Depends(get_db)):
    return StoryStateManager.create_story_state(db, story_state)

@router.get("/", response_model=List[StoryStateOut])
def read_story_states(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return StoryStateManager.get_story_states(db, skip=skip, limit=limit)

@router.get("/{story_state_id}", response_model=StoryStateOut)
def read_story_state(story_state_id: int, db: Session = Depends(get_db)):
    story_state = StoryStateManager.get_story_state(db, story_state_id)
    if not story_state:
        raise HTTPException(status_code=404, detail="StoryState not found")
    return story_state

@router.put("/{story_state_id}", response_model=StoryStateOut)
def update_story_state(story_state_id: int, story_state_update: StoryStateUpdate, db: Session = Depends(get_db)):
    story_state = StoryStateManager.update_story_state(db, story_state_id, story_state_update)
    if not story_state:
        raise HTTPException(status_code=404, detail="StoryState not found")
    return story_state

@router.patch("/{story_state_id}", response_model=StoryStateOut)
def partial_update_story_state(story_state_id: int, story_state_update: StoryStateUpdate, db: Session = Depends(get_db)):
    try:
        story_state = StoryStateManager.update_story_state(db, story_state_id, story_state_update)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not story_state:
        raise HTTPException(status_code=404, detail="StoryState not found")
    return story_state

@router.delete("/{story_state_id}", response_model=dict)
def delete_story_state(story_state_id: int, db: Session = Depends(get_db)):
    success = StoryStateManager.delete_story_state(db, story_state_id)
    if not success:
        raise HTTPException(status_code=404, detail="StoryState not found")
    return {"ok": True}
