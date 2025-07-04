from typing import Dict, Any
from langgraph.graph import StateGraph

from ia.ia_client import IAClient, PerfilesEnum
from ..states.story_state import EmailState
from api.managers.email_manager import EmailManager
from api.managers.character_manager import CharacterManager
from api.managers.player_manager import PlayerManager
from api.models.scene import PhaseType
from ia.constantes.listas import TRANSICION_DE_DINÁMICA
import logging, json

logger = logging.getLogger(__name__)

class CombatEmailAnalysisNode:
    """Nodo encargado del análisis de emails entrantes en modo combate."""
    def __init__(self):
        self.ia_client = IAClient(perfil=PerfilesEnum.CLASIFICACION.value)
        # Aquí podrías inicializar otros recursos necesarios, como un cliente IA específico

    def __call__(self, state: EmailState) -> EmailState:
         
        return state

# Función helper para usar en el grafo
def combat_email_analysis_node(state: EmailState) -> EmailState:
    """Función de conveniencia para usar en el grafo LangGraph."""
    node = CombatEmailAnalysisNode()
    return node(state)


