from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from api.schemas.story import StoryCreate, StoryUpdate, StoryOut
from api.managers.story_manager import StoryManager
from api.core.database import get_db

router = APIRouter(prefix="/stories", tags=["stories"])

@router.post("/", response_model=StoryOut)
def create_story(story: StoryCreate, db: Session = Depends(get_db)):
    return StoryManager.create_story(db, story)

@router.get("/", response_model=List[StoryOut])
def read_stories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return StoryManager.get_stories(db, skip=skip, limit=limit)

@router.get("/{story_id}", response_model=StoryOut)
def read_story(story_id: int, db: Session = Depends(get_db)):
    story = StoryManager.get_story(db, story_id)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    return story

@router.put("/{story_id}", response_model=StoryOut)
def update_story(story_id: int, story_update: StoryUpdate, db: Session = Depends(get_db)):
    story = StoryManager.update_story(db, story_id, story_update)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    return story

@router.patch("/{story_id}", response_model=StoryOut)
def partial_update_story(story_id: int, story_update: StoryUpdate, db: Session = Depends(get_db)):
    try:
        story = StoryManager.update_story(db, story_id, story_update)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    return story

@router.delete("/{story_id}", response_model=dict)
def delete_story(story_id: int, db: Session = Depends(get_db)):
    success = StoryManager.delete_story(db, story_id)
    if not success:
        raise HTTPException(status_code=404, detail="Story not found")
    return {"ok": True}
