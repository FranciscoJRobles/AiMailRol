from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from api.schemas.scene import SceneCreate, SceneUpdate, SceneResponse
from api.managers.scene_manager import SceneManager
from api.core.database import get_db

router = APIRouter(prefix="/scenes", tags=["scenes"])

@router.post("/", response_model=SceneResponse)
def create_scene(scene: SceneCreate, db: Session = Depends(get_db)):
    return SceneManager.create_scene(db, scene)

@router.get("/", response_model=List[SceneResponse])
def get_scenes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return SceneManager.get_scenes(db, skip=skip, limit=limit)

@router.get("/{scene_id}", response_model=SceneResponse)
def get_scene(scene_id: int, db: Session = Depends(get_db)):
    scene = SceneManager.get_scene(db, scene_id)
    if not scene:
        raise HTTPException(status_code=404, detail="Scene not found")
    return scene

@router.put("/{scene_id}", response_model=SceneResponse)
def update_scene(scene_id: int, scene_update: SceneUpdate, db: Session = Depends(get_db)):
    scene = SceneManager.update_scene(db, scene_id, scene_update)
    if not scene:
        raise HTTPException(status_code=404, detail="Scene not found")
    return scene

@router.patch("/{scene_id}", response_model=SceneResponse)
def partial_update_scene(scene_id: int, scene_update: SceneUpdate, db: Session = Depends(get_db)):
    scene = SceneManager.update_scene(db, scene_id, scene_update)
    if not scene:
        raise HTTPException(status_code=404, detail="Scene not found")
    return scene

@router.delete("/{scene_id}", response_model=dict)
def delete_scene(scene_id: int, db: Session = Depends(get_db)):
    success = SceneManager.delete_scene(db, scene_id)
    if not success:
        raise HTTPException(status_code=404, detail="Scene not found")
    return {"ok": True}
