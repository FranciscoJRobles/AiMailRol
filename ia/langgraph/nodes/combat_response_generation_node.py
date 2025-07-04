"""
Nodo para generación de respuestas de combate.
Combina análisis, contexto y validaciones para generar la respuesta final.
"""

from typing import Dict, Any
from ..states.story_state import EmailState
from ia.ia_client import IAClient
import logging
import json

logger = logging.getLogger(__name__)

class CombatResponseGenerationNode:
    """Nodo encargado de generar la respuesta de combate final."""
    
    def __init__(self):
        self.ia_client = IAClient(perfil="creativa")
    
    
# Función helper para usar en el grafo
def combat_generate_response_node(state: EmailState) -> EmailState:
    """Función de conveniencia para usar en el grafo LangGraph."""
    node = CombatResponseGenerationNode()
    return node(state)
