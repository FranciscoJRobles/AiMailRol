from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from api.schemas.scene import SceneCreate, SceneUpdate
from api.models.scene import Scene

class SceneManager:
    @staticmethod
    def get_scene(db: Session, scene_id: int) -> Optional[Scene]:
        """Obtiene una escena por ID"""
        return db.query(Scene).filter(Scene.id == scene_id).first()

    @staticmethod
    def get_scene_by_id(db: Session, scene_id: int):
        """Devuelve la escena correspondiente al id"""
        return db.query(Scene).filter(Scene.id == scene_id).first()

    @staticmethod
    def get_scenes(db: Session, skip: int = 0, limit: int = 100) -> List[Scene]:
        """Lista todas las escenas con paginación"""
        return db.query(Scene).offset(skip).limit(limit).all()

    @staticmethod
    def create_scene(db: Session, scene: SceneCreate) -> Scene:
        """Crea una nueva escena"""
        db_scene = Scene(**scene.model_dump())
        db.add(db_scene)
        db.commit()
        db.refresh(db_scene)
        return db_scene

    @staticmethod
    def update_scene(db: Session, scene_id: int, scene_update: SceneUpdate) -> Optional[Scene]:
        """Actualiza una escena"""
        db_scene = SceneManager.get_scene(db, scene_id)
        if not db_scene:
            return None
        for field, value in scene_update.model_dump(exclude_unset=True).items():
            setattr(db_scene, field, value)
        if scene_update.activa == False and not db_scene.fecha_cierre:
            db_scene.fecha_cierre = datetime.now(tz=timezone.utc)
        db.commit()
        db.refresh(db_scene)
        return db_scene

    @staticmethod
    def delete_scene(db: Session, scene_id: int) -> bool:
        """Elimina una escena"""
        db_scene = SceneManager.get_scene(db, scene_id)
        if not db_scene:
            return False
        db.delete(db_scene)
        db.commit()
        return True

    @staticmethod
    def get_active_scene_by_story(db: Session, story_id: int) -> Optional[Scene]:
        """Obtiene la escena activa por story_state_id"""
        return db.query(Scene).filter(Scene.story_id == story_id, Scene.activa == True).first()

    @staticmethod
    def get_actual_phase_by_scene_id(db: Session, scene_id: int) -> Optional[str]:
        """Obtiene la fase actual de una escena por ID"""
        return db.query(Scene.fase_actual).filter(Scene.id == scene_id).scalar()

    @staticmethod
    def get_scene_summary_by_id(db: Session, scene_id: int) -> Optional[str]:
        """Obtiene el resumen de una escena por ID"""
        return db.query(Scene.resumen).filter(Scene.id == scene_id).scalar()
    
    @staticmethod
    def update_scene_summary_by_id(db: Session, scene_id: int, new_summary: str):
        """Actualiza el resumen de una escena por ID"""
        db_scene = SceneManager.get_scene(db, scene_id)
        db_scene.resumen = new_summary
        db.commit()
        
    @staticmethod
    def get_not_summarized_scenes_by_story_id(db: Session, story_id: int) -> List[Scene]:
        """Obtiene todas las escenas no activas y no resumidas asociadas a una historia por su ID"""
        return db.query(Scene).filter(Scene.story_id == story_id, Scene.resumido == False, Scene.activa == False).order_by(Scene.fecha_inicio.asc()).all()
    
    @staticmethod
    def get_story_id_by_scene_id(db: Session, scene_id: int) -> Optional[int]:
        """Obtiene el ID de la historia asociada a una escena por su ID"""
        scene = db.query(Scene).filter(Scene.id == scene_id).first()
        return scene.story_id if scene else None
    
    @staticmethod
    def mark_scene_as_summarized(db: Session, scene_id: int):
        """Marca una escena como resumida"""
        db_scene = SceneManager.get_scene(db, scene_id)
        if not db_scene:
            return False
        db_scene.resumido = True
        db.commit()
        return True