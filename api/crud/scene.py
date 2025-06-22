from sqlalchemy.orm import Session
from api.models.scene import Scene, SceneStatus
from api.schemas.scene import SceneCreate, SceneUpdate
from typing import List, Optional
from datetime import datetime, timezone

def get_scene(db: Session, scene_id: int) -> Optional[Scene]:
    return db.query(Scene).filter(Scene.id == scene_id).first()

def get_scenes(db: Session, skip: int = 0, limit: int = 100) -> List[Scene]:
    return db.query(Scene).offset(skip).limit(limit).all()

def create_scene(db: Session, scene: SceneCreate) -> Scene:
    db_scene = Scene(**scene.model_dump())
    db.add(db_scene)
    db.commit()
    db.refresh(db_scene)
    return db_scene

def update_scene(db: Session, scene_id: int, scene_update: SceneUpdate) -> Optional[Scene]:
    db_scene = get_scene(db, scene_id)
    if not db_scene:
        return None
    for field, value in scene_update.model_dump(exclude_unset=True).items():
        setattr(db_scene, field, value)
    if scene_update.estado == SceneStatus.finalizada and not db_scene.fecha_cierre:
        db_scene.fecha_cierre = datetime.now(tz=timezone.utc)
    db.commit()
    db.refresh(db_scene)
    return db_scene

def delete_scene(db: Session, scene_id: int) -> bool:
    db_scene = get_scene(db, scene_id)
    if not db_scene:
        return False
    db.delete(db_scene)
    db.commit()
    return True
