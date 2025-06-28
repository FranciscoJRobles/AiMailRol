"""
Nodo para análisis de emails usando IA.
Clasifica intenciones y detecta transiciones de estado.
"""

from typing import Dict, Any
from langgraph.graph import StateGraph
from ..states.email_state import EmailState
from api.managers.email_manager import EmailManager
from api.managers.character_manager import CharacterManager
from api.managers.player_manager import PlayerManager
from ia.agentes.subagentes.subagente_analisis_email import SubagenteAnalisisEmailIA
import logging

logger = logging.getLogger(__name__)

class EmailAnalysisNode:
    """Nodo encargado del análisis de emails entrantes."""
    
    def __init__(self):
        self.subagente_analisis = SubagenteAnalisisEmailIA()
    
    def __call__(self, state: EmailState) -> EmailState:
        """
        Analiza el email y clasifica sus intenciones.
        
        Args:
            state: Estado actual que contiene el email a analizar
            
        Returns:
            Estado actualizado con análisis de intenciones y transiciones
        """
        try:
            logger.info(f"Analizando email ID: {state['email_id']}")
            
            # Obtener datos del email si no están en el estado
            if not state.get('email_data'):
                email = EmailManager.get(state['db_session'], state['email_id'])
                state['email_data'] = {
                    'subject': email.subject,
                    'body': email.body,
                    'sender': email.sender,
                    'thread_id': email.thread_id,
                    'campaign_id': email.campaign_id,
                    'scene_id': email.scene_id,
                    'player_id': email.player_id,
                    'character_id': email.character_id
                }
            
            # Actualizar identificadores en el estado
            state['campaign_id'] = state['email_data'].get('campaign_id')
            state['scene_id'] = state['email_data'].get('scene_id')
            state['player_id'] = state['email_data'].get('player_id')
            state['character_id'] = state['email_data'].get('character_id')
            
            # Obtener lista de personajes jugadores si hay campaña
            if state['campaign_id']:
                personajes = CharacterManager.list(state['db_session'])
                # Filtrar por campaña
                state['personajes_pj'] = [
                    {
                        'id': p.id,
                        'nombre': p.nombre,
                        'player_id': p.player_id
                    }
                    for p in personajes 
                    if any(c.id == state['campaign_id'] for c in p.campaigns)
                ]
            
            # Analizar intenciones en el texto
            texto_email = state['email_data']['body']
            intenciones = self.subagente_analisis.clasificar(
                texto_email, 
                state.get('personajes_pj')
            )
            state['intenciones'] = intenciones
            
            # Analizar posible transición de estado
            estado_actual = state.get('estado_actual', 'narracion')
            transicion = self.subagente_analisis.analizarTransicion(
                texto_email, 
                estado_actual
            )
            state['transicion_detectada'] = transicion
            
            # Actualizar estado si hay cambio detectado
            if transicion and transicion.get('cambio_detectado'):
                state['estado_nuevo'] = transicion.get('nuevo_estado')
                logger.info(f"Transición detectada: {estado_actual} -> {state['estado_nuevo']}")
            
            logger.info(f"Análisis completado. Intenciones encontradas: {len(intenciones)}")
            
        except Exception as e:
            logger.error(f"Error en análisis de email: {e}")
            if not state.get('errors'):
                state['errors'] = []
            state['errors'].append(f"Error en análisis: {str(e)}")
        
        return state

# Función helper para usar en el grafo
def analyze_email_node(state: EmailState) -> EmailState:
    """Función de conveniencia para usar en el grafo LangGraph."""
    node = EmailAnalysisNode()
    return node(state)
