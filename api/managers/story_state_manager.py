from sqlalchemy.orm import Session
from api.models.story_state import StoryState
from api.models.character import Character
from api.schemas.story_state import StoryStateCreate, StoryStateUpdate
from typing import List, Optional
from datetime import datetime, timezone

class StoryStateManager:
    @staticmethod
    def get_story_state(db: Session, story_state_id: int) -> Optional[StoryState]:
        """Obtiene un estado de historia por ID"""
        return db.query(StoryState).filter(StoryState.id == story_state_id).first()

    @staticmethod
    def get_story_state_by_id(db: Session, story_state_id: int):
        """Devuelve el story_state correspondiente al id"""
        return db.query(StoryState).filter(StoryState.id == story_state_id).first()

    @staticmethod
    def get_story_states(db: Session, skip: int = 0, limit: int = 100) -> List[StoryState]:
        """Lista todos los estados de historia con paginación"""
        return db.query(StoryState).offset(skip).limit(limit).all()

    @staticmethod
    def create_story_state(db: Session, story_state: StoryStateCreate) -> StoryState:
        """Crea un nuevo estado de historia"""
        db_story_state = StoryState(**story_state.model_dump())
        db.add(db_story_state)
        db.commit()
        db.refresh(db_story_state)
        return db_story_state

    @staticmethod
    def update_story_state(db: Session, story_state_id: int, story_state_update: StoryStateUpdate) -> Optional[StoryState]:
        """Actualiza un estado de historia"""
        db_story_state = StoryStateManager.get_story_state(db, story_state_id)
        if not db_story_state:
            return None
        for field, value in story_state_update.model_dump(exclude_unset=True).items():
            if field == "character_ids":
                characters = db.query(Character).filter(Character.id.in_(value)).all()
                if len(characters) != len(value):
                    raise ValueError("Uno o más character_ids no existen")
                db_story_state.characters = characters
            else:
                setattr(db_story_state, field, value)
        db_story_state.fecha_actualizacion = datetime.now(tz=timezone.utc)
        db.commit()
        db.refresh(db_story_state)
        return db_story_state

    @staticmethod
    def delete_story_state(db: Session, story_state_id: int) -> bool:
        """Elimina un estado de historia"""
        db_story_state = StoryStateManager.get_story_state(db, story_state_id)
        if not db_story_state:
            return False
        db.delete(db_story_state)
        db.commit()
        return True

    @staticmethod
    def get_active_story_state_by_keyword(db: Session, keyword: str, campaign_id: int) -> Optional[StoryState]:
        """Devuelve el StoryState activo asociado a una palabra clave y campaña específica"""
        return db.query(StoryState).filter(
            StoryState.nombre_clave == keyword,
            StoryState.campaign_id == campaign_id,
            StoryState.activa == True
        ).first()

    @staticmethod
    def get_scene_id_by_story_state(db: Session, story_state:StoryState) -> Optional[int]:
        """Devuelve el ID de la escena activa asociada a un StoryState"""
        if not story_state or not story_state.scenes:
            return None
        # Buscar la escena activa dentro de las escenas asociadas al StoryState
        active_scene = next((scene for scene in story_state.scenes if scene.activa), None)
        return active_scene.id if active_scene else None

    @staticmethod
    def get_characters_by_story_state_id(db: Session, story_state_id: int) -> List[Character]:
        """Devuelve una lista de instancias de Character asociadas a un StoryState"""
        story_state = db.query(StoryState).filter(StoryState.id == story_state_id).first()
        return story_state.characters if story_state else []

    @staticmethod
    def get_active_storystate_keywords(db: Session, campaign_id: Optional[int] = None) -> List[str]:
        """
        Obtiene todas las palabras clave de StoryStates activos.
        
        Args:
            db: Sesión de base de datos
            campaign_id: ID de campaña específica (opcional)
            
        Returns:
            Lista de palabras clave de StoryStates activos
        """
        query = db.query(StoryState).filter(StoryState.activa == True)
        
        # Si se especifica campaign_id, filtrar por campaña
        if campaign_id is not None:
            query = query.filter(StoryState.campaign_id == campaign_id)
        
        story_states = query.all()
        
        # Extraer las palabras clave (asumiendo que tienes un campo 'keyword' en StoryState)
        keywords = [story_state.nombre_clave for story_state in story_states if story_state.nombre_clave]
        
        return keywords