"""
Estado persistente del juego que se mantiene entre procesamiento de emails.
"""

from typing import TypedDict, Optional, Dict, Any, List
from datetime import datetime

class GameState(TypedDict):
    """Estado global del juego que persiste entre emails."""
    
    # Identificadores principales
    campaign_id: int
    current_scene_id: Optional[int]
    current_story_state_id: Optional[int]
    
    # Estado actual del juego
    estado_actual: str  # "narración" o "combate"
    
    # Personajes activos
    personajes_activos: List[Dict[str, Any]]  # PJs en la escena actual
    pnjs_relevantes: List[Dict[str, Any]]  # PNJs importantes para la escena
    
    # Contexto narrativo actual
    resumen_escena_actual: Optional[str]
    resumen_estado_historia: Optional[str]
    resumen_campaña: Optional[str]
    
    # Información de combate (si aplica)
    en_combate: bool
    turno_actual: Optional[int]
    iniciativa_orden: Optional[List[int]]  # IDs de personajes en orden de iniciativa
    
    # Subtramas activas
    subtramas_activas: List[Dict[str, Any]]
    
    # Últimos emails procesados (para contexto)
    ultimos_emails: List[Dict[str, Any]]  # Historial reciente
    
    # Metadatos
    last_updated: datetime
    thread_id: Optional[str]  # Thread de email actual
