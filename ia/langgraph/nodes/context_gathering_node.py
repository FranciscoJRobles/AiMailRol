"""
Nodo para recopilación de contexto del juego.
Obtiene historial, resúmenes y contexto necesario para la IA.
"""

from typing import Dict, Any
from ..states.email_state import EmailState
from api.managers.scene_manager import SceneManager
from api.managers.story_state_manager import StoryStateManager
from api.managers.campaign_manager import CampaignManager
from api.managers.ruleset_manager import RulesetManager
from api.managers.character_manager import CharacterManager
from ia.agentes.subagentes.subagente_recopilador_contexto import SubagenteRecopiladorContexto
from ia.agentes.subagentes.subagente_resumidor_textos import SubagenteResumidorTextos
from ia.ia_client import IAClient
import logging

logger = logging.getLogger(__name__)

class ContextGatheringNode:
    """Nodo encargado de recopilar todo el contexto necesario para la IA."""
    
    def __init__(self):
        self.ia_client = IAClient(perfil="resumen")
        self.resumidor_textos = SubagenteResumidorTextos(self.ia_client)
    
    def __call__(self, state: EmailState) -> EmailState:
        """
        Recopila el contexto completo para el procesamiento de IA.
        
        Args:
            state: Estado actual con identificadores de campaña, escena, etc.
            
        Returns:
            Estado actualizado con contexto completo
        """
        try:
            logger.info(f"Recopilando contexto para escena: {state.get('scene_id')}")
            
            # Inicializar recopilador de contexto
            recopilador = SubagenteRecopiladorContexto(
                state['db_session'], 
                self.resumidor_textos
            )
            
            # Obtener contexto narrativo si hay escena
            if state.get('scene_id'):
                contexto = recopilador.recopilar_resumenes_contexto(
                    scene_id=state['scene_id'],
                    max_emails=10,
                    n_puros=3
                )
                
                # Obtener ambientación de campaña
                if state.get('campaign_id'):
                    ambientacion = recopilador.obtener_contexto_ambientacion(
                        state['campaign_id']
                    )
                else:
                    ambientacion = None
                
                # Construir contexto de sistema
                sistema_parts = []
                
                if ambientacion:
                    sistema_parts.append(ambientacion)
                
                if contexto.get('campaign'):
                    sistema_parts.append(
                        f"Resumen campaña: {contexto['campaign'].get('resumen', '')}"
                    )
                
                if contexto.get('story_state'):
                    sistema_parts.append(
                        f"Resumen estado historia: {contexto['story_state'].get('contenido_resumido', '')}"
                    )
                
                if contexto.get('scene'):
                    sistema_parts.append(
                        f"Resumen escena: {contexto['scene'].get('resumen_estado', '')}"
                    )
                
                state['contexto_sistema'] = "\n".join([s for s in sistema_parts if s])
                
                # Construir historial narrativo
                historial = []
                if contexto.get('emails_puros'):
                    historial.extend(contexto['emails_puros'])
                if contexto.get('resumen_final'):
                    historial.append(contexto['resumen_final'])
                
                state['contexto_historial'] = historial
            
            # Obtener ruleset de la campaña
            if state.get('campaign_id'):
                try:
                    campaign = CampaignManager().get_campaign_by_id(
                        state['db_session'], 
                        state['campaign_id']
                    )
                    if campaign:
                        ruleset = RulesetManager().get_ruleset_by_campaign_id(
                            state['db_session'], 
                            campaign.id
                        )
                        if ruleset:
                            state['ruleset'] = {
                                'id': ruleset.id,
                                'nombre': ruleset.nombre,
                                'descripcion': ruleset.descripcion,
                                'reglas': ruleset.reglas
                            }
                except Exception as e:
                    logger.warning(f"No se pudo obtener ruleset: {e}")
            
            # Obtener información de personajes si no está ya en el estado
            if not state.get('personajes_pj') and state.get('campaign_id'):
                personajes = CharacterManager.list(state['db_session'])
                state['personajes_pj'] = [
                    {
                        'id': p.id,
                        'nombre': p.nombre,
                        'player_id': p.player_id,
                        'stats': getattr(p, 'stats', {}),
                        'estado_actual': getattr(p, 'estado_actual', {})
                    }
                    for p in personajes 
                    if any(c.id == state['campaign_id'] for c in p.campaigns)
                ]
            
            logger.info("Contexto recopilado exitosamente")
            
        except Exception as e:
            logger.error(f"Error recopilando contexto: {e}")
            if not state.get('errors'):
                state['errors'] = []
            state['errors'].append(f"Error en contexto: {str(e)}")
        
        return state

# Función helper para usar en el grafo
def gather_context_node(state: EmailState) -> EmailState:
    """Función de conveniencia para usar en el grafo LangGraph."""
    node = ContextGatheringNode()
    return node(state)
