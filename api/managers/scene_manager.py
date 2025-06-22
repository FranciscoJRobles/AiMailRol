from sqlalchemy.orm import Session
from api.schemas.scene import SceneCreate, SceneUpdate
from api.crud import scene as crud_scene
from typing import List, Optional
from api.models.scene import Scene as SceneModel

class SceneManager:
    @staticmethod
    def get_scene(db: Session, scene_id: int) -> Optional[SceneModel]:
        return crud_scene.get_scene(db, scene_id)

    @staticmethod
    def get_scenes(db: Session, skip: int = 0, limit: int = 100) -> List[SceneModel]:
        return crud_scene.get_scenes(db, skip, limit)

    @staticmethod
    def create_scene(db: Session, scene: SceneCreate) -> SceneModel:
        return crud_scene.create_scene(db, scene)

    @staticmethod
    def update_scene(db: Session, scene_id: int, scene_update: SceneUpdate) -> Optional[SceneModel]:
        return crud_scene.update_scene(db, scene_id, scene_update)

    @staticmethod
    def delete_scene(db: Session, scene_id: int) -> bool:
        return crud_scene.delete_scene(db, scene_id)
