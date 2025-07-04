"""
Estado que se pasa entre nodos durante el procesamiento de un email.
"""

from typing import TypedDict, Optional, List, Dict, Any
from datetime import datetime
from api.models.character import Character
from api.models.scene import PhaseType

class EmailState(TypedDict):
    """Estado que contiene toda la información necesaria para procesar un email."""
    
    # Email original
    email_id: int
    email_data: Dict[str, Any]  # Datos del email (subject, body, sender, etc.)
    
    # Análisis del email
    clasificacion_intenciones: Optional[List[Dict[str, Any]]]  # Lista de intenciones clasificadas
    transicion_detectada: Optional[Dict[str, Any]]  # Cambio de estado detectado
    metajuego_detectado: bool # Indica si se detectó metajuego
    
    # Contexto del juego
    campaign_id: Optional[int]
    scene_id: Optional[int]
    story_id: Optional[int]
    player_id: Optional[int]
    character_id: Optional[int]
    
    # Contexto narrativo
    json_ambientacion: Optional[Dict[str, Any]]  # Contexto de ambientación de la campaña
    json_reglas: Optional[Dict[str, Any]]  # JSON de reglas específicas
    json_hojas_personajes: Optional[List[Dict[str, Any]]]  # Lista de JSONs de hojas de personaje
    json_estado_actual_personajes: Optional[List[Dict[str, Any]]]  # Lista de JSONs de estado actual de personajes
    contexto_sistema: Optional[Dict[str, Any]]  # Prompt de sistema para la IA
    contexto_historial: Optional[Dict[str,Any]]  # Historial narrativo, engloba los resumenes de Campaign Story y Scene
    contexto_ultimos_emails: Optional[List[Dict[str, Any]]]  # Últimos emails que se añadirán al historial sin resumir
    personajes_pj: Optional[List[Character]]  # Lista de personajes jugadores
    personajes_pnj: Optional[List[Dict[str, Any]]]  # Lista de personajes no jugadores relevantes
    nombre_personajes_pj: Optional[List[str]]  # Nombres de personajes jugadores
    nombre_personajes_pnj: Optional[List[str]]  # Nombres de personajes no jugadores relevantes
    nombre_personaje_email: Optional[str]  # Nombre del personaje que envía el email
    
    contexto_sistema: Optional[Dict[str, Any]]  # Prompt de sistema para la IA
    contexto_usuario: Optional[Dict[str, Any]]  # Prompt de usuario para la IA
    
    # Reglas y validaciones
    ruleset: Optional[Dict[str, Any]]  # Reglas de la campaña
    validaciones: Optional[List[Dict[str, Any]]]  # Validaciones aplicadas
    
    # Estado del juego
    estado_actual: PhaseType  # "narracion" o "accion_en_turno"
    estado_nuevo: Optional[PhaseType]  # Nuevo estado si hay transición
    
    # Información de combate (si aplica)
    turno_actual: Optional[int]
    iniciativa_orden: Optional[List[int]]  # IDs de personajes en orden de iniciativa
    
    # Respuesta generada
    respuesta_ia: Optional[str]  # Respuesta generada por la IA
    email_respuesta: Optional[Dict[str, Any]]  # Email de respuesta formateado
    
    # Metadatos
    timestamp: datetime
    processed: bool
    errors: Optional[List[str]]  # Lista de errores durante el procesamiento
    
    # Datos de la sesión de BD
    db_session: Optional[Any]  # Sesión de base de datos
