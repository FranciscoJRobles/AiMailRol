"""
Estado que se pasa entre nodos durante el procesamiento de un email.
"""

from typing import TypedDict, Optional, List, Dict, Any
from datetime import datetime

class EmailState(TypedDict):
    """Estado que contiene toda la información necesaria para procesar un email."""
    
    # Email original
    email_id: int
    email_data: Dict[str, Any]  # Datos del email (subject, body, sender, etc.)
    
    # Análisis del email
    clasificacion_intenciones: Optional[List[Dict[str, Any]]]  # Lista de intenciones clasificadas
    transicion_detectada: Optional[Dict[str, Any]]  # Cambio de estado detectado
    
    # Contexto del juego
    campaign_id: Optional[int]
    scene_id: Optional[int]
    story_state_id: Optional[int]
    player_id: Optional[int]
    character_id: Optional[int]
    
    # Contexto narrativo
    contexto_sistema: Optional[str]  # Prompt de sistema para la IA
    contexto_historial: Optional[List[str]]  # Historial narrativo
    personajes_pj: Optional[List[Dict[str, Any]]]  # Lista de personajes jugadores
    
    # Reglas y validaciones
    ruleset: Optional[Dict[str, Any]]  # Reglas de la campaña
    validaciones: Optional[List[Dict[str, Any]]]  # Validaciones aplicadas
    
    # Estado del juego
    estado_actual: str  # "narracion" o "accion_en_turno"
    estado_nuevo: Optional[str]  # Nuevo estado si hay transición
    
    # Respuesta generada
    respuesta_ia: Optional[str]  # Respuesta generada por la IA
    email_respuesta: Optional[Dict[str, Any]]  # Email de respuesta formateado
    
    # Metadatos
    timestamp: datetime
    processed: bool
    errors: Optional[List[str]]  # Lista de errores durante el procesamiento
    
    # Datos de la sesión de BD
    db_session: Optional[Any]  # Sesión de base de datos
