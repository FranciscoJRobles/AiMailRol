"""
Nodo para recopilación de contexto del juego.
Obtiene historial, resúmenes y contexto necesario para la IA.
"""

from typing import Dict, Any, List
from ..states.story_state import EmailState
from api.managers.scene_manager import SceneManager
from api.managers.story_manager import StoryManager
from api.managers.campaign_manager import CampaignManager
from api.managers.ruleset_manager import RulesetManager
from api.managers.character_manager import CharacterManager
from api.models.character import Character
from ia.langgraph.agentes.agente_recopilador_contexto import AgenteRecopiladorContexto
from ia.langgraph.agentes.agente_resumidor_textos import AgenteResumidorTextos
from ia.ia_client import IAClient
import logging

logger = logging.getLogger(__name__)

class ContextGatheringNode:
    """Nodo encargado de recopilar todo el contexto necesario para la IA."""
    
    def __init__(self):
        self.ia_client = IAClient(perfil="resumen")
        self.resumidor_textos = AgenteResumidorTextos()
    
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
            story_id = SceneManager.get_story_id_by_scene_id(state['db_session'], state.get('scene_id'))
            # Inicializar gestor de emails donde recuperamos los emails recientes y resumimos si superan un límite sin resumir
            recopilador = AgenteRecopiladorContexto(
                state['db_session'], 
                self.resumidor_textos
            )
            email_bodies_a_resumir, email_bodies_puros = recopilador.gestionar_emails_para_contexto(
                scene_id=state.get('scene_id', None),
                max_emails=10,
                n_puros=3
            )
            if email_bodies_a_resumir:
                # Si hay emails a resumir, procesarlos
                resumen_previo_scene = SceneManager.get_scene_summary_by_id(
                    state['db_session'], 
                    state.get('scene_id')
                )
                nuevo_resumen_scene = self.resumidor_textos.resumir_emails(resumen_previo_scene, email_bodies_a_resumir)
                SceneManager.update_scene_summary_by_id(state['db_session'], state.get('scene_id'), nuevo_resumen_scene)
            
            # Inicializar recopilador de contexto
            ambientacion_json, reglas_json = recopilador.obtener_contexto_ambientacion_y_reglas(
                state.get('campaign_id')
            )
            
            # Obtener contexto narrativo si hay escena
            if state.get('scene_id'):
                campaign_resumen, story_resumen, scene_bodies_a_resumir, scene_bodies_puros = recopilador.recopilar_resumenes_contexto(
                    scene_id=state['scene_id'],
                    max_scenes=5,
                    scenes_puros=3
                )
                scene = SceneManager.get_scene_by_id(state['db_session'], state['scene_id'])
                if (scene_bodies_a_resumir):
                    story_resumen = self.resumidor_textos.resumir_resumenes(story_resumen, scene_bodies_a_resumir, "El resumen que devuelvas no debe ser superior a 300 palabras.")
                
                
                contexto_narrativo = {
                    "campaign_resumen": campaign_resumen,
                    "story_resumen": story_resumen,
                    "scenes_resumenes": [],
                    "scene_actual":scene.resumen
                }

                for related_scene in scene_bodies_puros:
                    contexto_narrativo["scenes_resumenes"].append(related_scene)
                    
                # Obtener ambientación y reglas de campaña
                if state.get('campaign_id'):
                    ambientacion_json, reglas_json = recopilador.obtener_contexto_ambientacion_y_reglas(
                        state['campaign_id']
                    )
                else:
                    logger.warning("No se pudo obtener ambientación y reglas, campaign_id no está definido.")
                
                # Obtener personajes
                character_id_email = CharacterManager.get_character_id_by_player_and_campaign(state['db_session'],
                                                                                             state.get('player_id'),state.get('campaign_id'))    
                lista_personajes_pj = CharacterManager.get_characters_by_story_id(
                    state['db_session'], 
                    story_id
                )
                
                # Actualizar EmailState con contexto
                state['story_id']= story_id
                state['character_id'] = character_id_email
                state['json_ambientacion'] = ambientacion_json
                state['json_reglas'] = reglas_json
                state['json_hojas_personajes'] = self.character_sheets_from_characters(lista_personajes_pj)
                state['json_estado_actual_personajes'] = self.character_actual_state_from_characters(lista_personajes_pj)
                state['personajes_pj'] = lista_personajes_pj
                state['nombre_personajes_pj'] = self.names_from_characters(lista_personajes_pj)
                state['contexto_historial'] = contexto_narrativo
                state['contexto_ultimos_emails'] = email_bodies_puros
                state['contexto_sistema'] = {
                    'ambientacion': ambientacion_json,
                    'reglas': reglas_json,
                    'hojas_personajes': state['json_hojas_personajes']
                }
                state['contexto_usuario'] = {
                    'estado_actual_pjs': state['json_estado_actual_personajes'],
                    'contexto_historial': contexto_narrativo,
                    'emails': email_bodies_puros,
                    'ultimo_email': state.get('email_data', {}).get('body', ''),                    
                }
                logger.info("Contexto recopilado exitosamente")
            
        except Exception as e:
            logger.error(f"Error recopilando contexto: {e}")
            if not state.get('errors'):
                state['errors'] = []
            state['errors'].append(f"Error en contexto: {str(e)}")
        
        return state
    
    def names_from_characters(self, characters: List[Character]) -> List[str]:
        """
        Extrae los nombres de una lista de personajes.
        
        Args:
            characters: Lista de diccionarios con información de personajes.
            
        Returns:
            Lista de nombres de personajes.
        """
        return [character.nombre for character in characters if hasattr(character, 'nombre')]
    
    def character_sheets_from_characters(self, characters: List[Character]) -> List[Dict[str, Any]]:
        """
        Extrae las hojas de personaje de una lista de personajes.
        
        Args:
            characters: Lista de diccionarios con información de personajes.
            
        Returns:
            Lista de hojas de personaje.
        """
        return [character.hoja_json for character in characters if hasattr(character, 'hoja_json')]    
    
    def character_actual_state_from_characters(self, characters: List[Character]) -> List[Dict[str, Any]]:
        """
        Extrae el estado actual de los personajes de una lista de personajes.
        
        Args:
            characters: Lista de diccionarios con información de personajes.
            
        Returns:
            Lista de estados actuales de los personajes.
        """
        return [character.estado_actual for character in characters if hasattr(character, 'estado_actual')]    


# Función helper para usar en el grafo
def gather_context_node(state: EmailState) -> EmailState:
    """Función de conveniencia para usar en el grafo LangGraph."""
    node = ContextGatheringNode()
    return node(state)

