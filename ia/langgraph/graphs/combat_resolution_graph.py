"""
Grafo especializado para resolución de situaciones de combate.
Maneja turnos, iniciativas y resolución de acciones de combate.
"""

from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from ..states.email_state import EmailState
from ..nodes.email_analysis_node import analyze_email_node
from ..nodes.context_gathering_node import gather_context_node
from ..nodes.rules_validation_node import validate_rules_node
from api.managers.turn_manager import TurnManager
from api.managers.character_manager import CharacterManager
from ia.ia_client import IAClient
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)

def combat_initiative_node(state: EmailState) -> EmailState:
    """Nodo para gestionar iniciativa en combate."""
    try:
        logger.info("Procesando iniciativa de combate")
        
        # Si ya estamos en modo de turno, verificar orden de iniciativa
        if state.get('estado_actual') == 'accion_en_turno' and state.get('scene_id'):
            # Obtener turno activo
            active_turn = TurnManager.get_active_turn_by_scene(
                state['db_session'], 
                state['scene_id']
            )
            
            if active_turn and state.get('personajes_pj'):
                # Determinar orden de iniciativa si no existe
                if not hasattr(active_turn, 'orden_iniciativa') or not active_turn.orden_iniciativa:
                    orden = calculate_initiative_order(state['personajes_pj'])
                    # Actualizar turno con orden de iniciativa
                    TurnManager.update_turn_initiative(
                        state['db_session'], 
                        active_turn.id, 
                        orden
                    )
                    state['initiative_order'] = orden
                else:
                    state['initiative_order'] = active_turn.orden_iniciativa
                
                # Verificar si es el turno del personaje correcto
                current_character_turn = get_current_character_turn(
                    state['initiative_order'], 
                    active_turn
                )
                
                if current_character_turn != state.get('character_id'):
                    state['out_of_turn'] = True
                    state['expected_character'] = current_character_turn
        
        logger.info("Iniciativa procesada")
        
    except Exception as e:
        logger.error(f"Error procesando iniciativa: {e}")
        if not state.get('errors'):
            state['errors'] = []
        state['errors'].append(f"Error en iniciativa: {str(e)}")
    
    return state

def combat_resolution_node(state: EmailState) -> EmailState:
    """Nodo para resolver acciones de combate."""
    try:
        logger.info("Resolviendo acciones de combate")
        
        if not state.get('intenciones'):
            return state
        
        ia_client = IAClient(perfil="precisa")
        resoluciones = []
        
        # Procesar cada intención de combate
        for intencion in state['intenciones']:
            if intencion.get('tipo') == 'combate':
                resolucion = resolve_combat_action(
                    intencion, 
                    state.get('personajes_pj', []),
                    state.get('character_id'),
                    state.get('ruleset', {}),
                    ia_client
                )
                resoluciones.append(resolucion)
        
        state['combat_resolutions'] = resoluciones
        
        # Verificar si el combate continúa o termina
        if all(r.get('combat_ended', False) for r in resoluciones):
            state['estado_nuevo'] = 'narracion'
            state['combat_ended'] = True
        
        logger.info(f"Resueltas {len(resoluciones)} acciones de combate")
        
    except Exception as e:
        logger.error(f"Error resolviendo combate: {e}")
        if not state.get('errors'):
            state['errors'] = []
        state['errors'].append(f"Error en resolución: {str(e)}")
    
    return state

def combat_response_node(state: EmailState) -> EmailState:
    """Nodo para generar respuestas específicas de combate."""
    try:
        logger.info("Generando respuesta de combate")
        
        ia_client = IAClient(perfil="creativa")
        
        # Construir prompt específico para combate
        prompt_parts = []
        
        # Contexto base
        if state.get('contexto_sistema'):
            prompt_parts.append(state['contexto_sistema'])
        
        prompt_parts.append("""
        MODO COMBATE ACTIVO:
        Estás narrando una secuencia de combate. Mantén la tensión y el ritmo apropiados.
        Describe las acciones de manera dinámica y visual.
        """)
        
        # Información de iniciativa
        if state.get('initiative_order'):
            prompt_parts.append(f"Orden de iniciativa: {state['initiative_order']}")
        
        if state.get('out_of_turn'):
            prompt_parts.append(f"""
            ⚠️ ACCIÓN FUERA DE TURNO:
            Este personaje está actuando fuera de su turno. 
            Corresponde actuar al personaje ID: {state.get('expected_character')}
            """)
        
        # Resoluciones de combate
        if state.get('combat_resolutions'):
            prompt_parts.append("RESOLUCIONES DE COMBATE:")
            for i, res in enumerate(state['combat_resolutions'], 1):
                prompt_parts.append(f"{i}. {json.dumps(res, indent=2, ensure_ascii=False)}")
        
        # Email original
        if state.get('email_data'):
            prompt_parts.append(f"\nACCIÓN DEL JUGADOR:")
            prompt_parts.append(state['email_data'].get('body', ''))
        
        # Estado de fin de combate
        if state.get('combat_ended'):
            prompt_parts.append("""
            \n🏁 FIN DEL COMBATE:
            El combate ha terminado. Narra la conclusión y transición a narración libre.
            """)
        
        prompt_parts.append("""
        \nGenera una respuesta narrativa de combate que:
        1. Mantenga la tensión y el ritmo
        2. Describa las acciones de manera visual
        3. Aplique las resoluciones calculadas
        4. Mantenga el orden de turnos
        5. Haga avanzar la escena de combate
        """)
        
        prompt_completo = "\n".join(prompt_parts)
        
        # Generar respuesta
        contexto = {
            "sistema": prompt_completo,
            "historial": state.get('contexto_historial', [])
        }
        
        respuesta = ia_client.procesar_mensaje(
            "Genera respuesta de combate",
            contexto,
            "creativa"
        )
        
        state['respuesta_ia'] = respuesta
        
        # Formatear email de respuesta
        email_data = state.get('email_data', {})
        state['email_respuesta'] = {
            'subject': f"Re: {email_data.get('subject', 'Combate')}",
            'body': respuesta,
            'thread_id': email_data.get('thread_id', ''),
            'recipients': [email_data.get('sender', '')],
            'campaign_id': state.get('campaign_id'),
            'scene_id': state.get('scene_id'),
            'type': 'IAResponse'
        }
        
        logger.info("Respuesta de combate generada")
        
    except Exception as e:
        logger.error(f"Error generando respuesta de combate: {e}")
        if not state.get('errors'):
            state['errors'] = []
        state['errors'].append(f"Error en respuesta de combate: {str(e)}")
    
    return state

def calculate_initiative_order(personajes: list) -> list:
    """Calcula el orden de iniciativa para los personajes."""
    try:
        # Por ahora orden simple basado en ID (luego se puede mejorar con stats)
        orden = sorted([p.get('id') for p in personajes if p.get('id')])
        logger.info(f"Orden de iniciativa calculado: {orden}")
        return orden
    except Exception as e:
        logger.error(f"Error calculando iniciativa: {e}")
        return []

def get_current_character_turn(orden_iniciativa: list, turno_activo) -> int:
    """Determina qué personaje debe actuar en el turno actual."""
    try:
        if not orden_iniciativa:
            return None
        
        # Lógica simple: rotar por el orden
        # (En implementación real usarías el número de turno)
        turno_numero = getattr(turno_activo, 'numero_turno', 1)
        indice = (turno_numero - 1) % len(orden_iniciativa)
        return orden_iniciativa[indice]
        
    except Exception as e:
        logger.error(f"Error obteniendo turno actual: {e}")
        return None

def resolve_combat_action(
    intencion: Dict[str, Any], 
    personajes: list, 
    character_id: int,
    ruleset: Dict[str, Any],
    ia_client: IAClient
) -> Dict[str, Any]:
    """Resuelve una acción específica de combate."""
    try:
        # Obtener información del personaje
        personaje = next((p for p in personajes if p.get('id') == character_id), {})
        
        prompt = f"""
        Resuelve esta acción de combate según las reglas del juego:
        
        PERSONAJE:
        {json.dumps(personaje, indent=2, ensure_ascii=False)}
        
        ACCIÓN:
        {json.dumps(intencion, indent=2, ensure_ascii=False)}
        
        REGLAS:
        {ruleset.get('reglas', 'Reglas estándar de rol narrativo')}
        
        Calcula:
        1. Probabilidad de éxito
        2. Daño/efecto potencial
        3. Consecuencias de la acción
        4. Si la acción termina el combate
        
        Responde en JSON:
        {{
            "exito": true/false,
            "resultado": "descripción del resultado",
            "dano": numero_o_null,
            "efectos": ["lista de efectos"],
            "combat_ended": true/false,
            "descripcion_narrativa": "texto para narrar"
        }}
        """
        
        contexto = {"sistema": prompt, "historial": []}
        respuesta = ia_client.procesar_mensaje(
            "Resuelve acción de combate",
            contexto,
            "precisa"
        )
        
        return json.loads(respuesta)
        
    except Exception as e:
        logger.error(f"Error resolviendo acción de combate: {e}")
        return {
            "exito": False,
            "resultado": f"Error en resolución: {str(e)}",
            "combat_ended": False,
            "descripcion_narrativa": "La acción no pudo ser resuelta correctamente."
        }

class CombatResolutionGraph:
    """Grafo especializado para resolución de combate."""
    
    def __init__(self):
        self.checkpointer = MemorySaver()
        self.graph = self._build_graph()

    
    def _build_graph(self) -> StateGraph:
        """Construye el grafo de resolución de combate."""
        workflow = StateGraph(EmailState)
        
        # Nodos específicos de combate
        workflow.add_node("analyze_email", analyze_email_node)
        workflow.add_node("gather_context", gather_context_node)
        workflow.add_node("combat_initiative", combat_initiative_node)
        workflow.add_node("combat_resolution", combat_resolution_node)
        workflow.add_node("combat_response", combat_response_node)
        
        # Flujo de combate
        workflow.set_entry_point("analyze_email")
        workflow.add_edge("analyze_email", "gather_context")
        workflow.add_edge("gather_context", "combat_initiative")
        workflow.add_edge("combat_initiative", "combat_resolution")
        workflow.add_edge("combat_resolution", "combat_response")
        workflow.add_edge("combat_response", END)
        
        return workflow.compile(checkpointer=self.checkpointer)
    
    def process_combat_email(
        self, 
        email_id: int, 
        db_session: Any,
        current_state: str = "accion_en_turno"
    ) -> Dict[str, Any]:
        """
        Procesa un email de combate usando el grafo especializado.
        
        Args:
            email_id: ID del email a procesar
            db_session: Sesión de base de datos
            current_state: Estado actual del juego
            
        Returns:
            Resultado del procesamiento de combate
        """
        try:
            logger.info(f"Procesando email de combate {email_id}")
            
            # Estado inicial para combate
            initial_state: EmailState = {
                'email_id': email_id,
                'email_data': {},
                'intenciones': None,
                'transicion_detectada': None,
                'campaign_id': None,
                'scene_id': None,
                'story_state_id': None,
                'player_id': None,
                'character_id': None,
                'contexto_sistema': None,
                'contexto_historial': None,
                'personajes_pj': None,
                'ruleset': None,
                'validaciones': None,
                'estado_actual': current_state,
                'estado_nuevo': None,
                'respuesta_ia': None,
                'email_respuesta': None,
                'timestamp': datetime.now(),
                'processed': False,
                'errors': None,
                'db_session': db_session,
                # Específicos de combate
                'initiative_order': None,
                'out_of_turn': False,
                'expected_character': None,
                'combat_resolutions': None,
                'combat_ended': False
            }
            
            # Ejecutar grafo de combate
            config = {"configurable": {"thread_id": f"combat_{email_id}"}}
            result = self.graph.invoke(initial_state, config)
            
            return {
                'success': result.get('processed', False),
                'email_id': email_id,
                'respuesta_generada': result.get('respuesta_ia'),
                'combat_ended': result.get('combat_ended', False),
                'initiative_order': result.get('initiative_order'),
                'out_of_turn': result.get('out_of_turn', False),
                'combat_resolutions': result.get('combat_resolutions', []),
                'errors': result.get('errors', [])
            }
            
        except Exception as e:
            logger.error(f"Error procesando combate: {e}")
            return {
                'success': False,
                'email_id': email_id,
                'errors': [f"Error crítico en combate: {str(e)}"]
            }

# Instancia global del grafo de combate
combat_resolution_graph = CombatResolutionGraph()
