"""
Grafo principal para procesamiento de emails usando LangGraph.
Orquesta el flujo completo desde análisis hasta respuesta.
"""

from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from ..states.email_state import EmailState
from ..nodes.email_analysis_node import analyze_email_node
from ..nodes.context_gathering_node import gather_context_node
from ..nodes.rules_validation_node import validate_rules_node
from ..nodes.response_generation_node import generate_response_node
from ..nodes.state_transition_node import transition_state_node
from api.models.scene import PhaseType
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class NarrativeProcessingGraph:
    """Grafo principal para procesamiento de emails de rol."""
    
    def __init__(self):
        self.checkpointer = MemorySaver()  # Para persistir estado entre ejecuciones
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Construye el grafo de procesamiento."""
        
        # Crear el grafo con el estado tipado
        workflow = StateGraph(EmailState)
        
        # Agregar nodos
        workflow.add_node("gather_context", gather_context_node)
        workflow.add_node("analyze_email", analyze_email_node)
        workflow.add_node("generate_response", generate_response_node)
        workflow.add_node("transition_state", transition_state_node)
        
        # Definir el flujo
        workflow.set_entry_point("gather_context")
        
        # Flujo principal: análisis -> contexto -> validación -> respuesta -> transición
        workflow.add_edge("gather_context", "analyze_email")
        workflow.add_edge("analyze_email", "generate_response")
        workflow.add_edge("generate_response", "transition_state")
        workflow.add_edge("transition_state", END)
        
        # Compilar el grafo
        return workflow.compile(checkpointer=self.checkpointer)
    
    def process_narrative_email(
        self, 
        email_id: int, 
        db_session: Any,
        current_state: str = PhaseType.narracion
    ) -> Dict[str, Any]:
        """
        Procesa un email completo usando el grafo.
        
        Args:
            email_id: ID del email a procesar
            db_session: Sesión de base de datos
            current_state: Estado actual del juego
            
        Returns:
            Resultado del procesamiento
        """
        try:
            logger.info(f"Iniciando procesamiento de email {email_id}")
            
            # Estado inicial
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
                'db_session': db_session
            }
            
            # Ejecutar el grafo
            config = {"configurable": {"thread_id": f"email_{email_id}"}}
            result = self.graph.invoke(initial_state, config)
            
            # Resultado del procesamiento
            processing_result = {
                'success': result.get('processed', False),
                'email_id': email_id,
                'respuesta_generada': result.get('respuesta_ia'),
                'email_respuesta': result.get('email_respuesta'),
                'intenciones_detectadas': result.get('intenciones', []),
                'transicion_detectada': result.get('transicion_detectada'),
                'estado_final': result.get('estado_actual'),
                'errors': result.get('errors', [])
            }
            
            if processing_result['success']:
                logger.info(f"Email {email_id} procesado exitosamente")
            else:
                logger.error(f"Error procesando email {email_id}: {processing_result['errors']}")
            
            return processing_result
            
        except Exception as e:
            logger.error(f"Error crítico procesando email {email_id}: {e}")
            return {
                'success': False,
                'email_id': email_id,
                'errors': [f"Error crítico: {str(e)}"]
            }
    
    def get_graph_visualization(self) -> str:
        """Retorna una representación visual del grafo."""
        try:
            # Intentar generar visualización si está disponible
            from langgraph.graph import draw_ascii
            return draw_ascii(self.graph)
        except ImportError:
            return """
            Flujo del grafo de procesamiento de emails:
            
            [INICIO] -> gather_context -> analyze_email 
                     -> generate_response -> transition_state -> [FIN]
            """
    
    def process_email_stream(
        self, 
        email_id: int, 
        db_session: Any,
        current_state: str = PhaseType.narracion
    ):
        """
        Procesa un email y retorna un stream de eventos para monitoreo.
        
        Args:
            email_id: ID del email a procesar
            db_session: Sesión de base de datos
            current_state: Estado actual del juego
            
        Yields:
            Eventos del procesamiento paso a paso
        """
        try:
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
                'db_session': db_session
            }
            
            config = {"configurable": {"thread_id": f"email_{email_id}"}}
            
            # Stream de eventos
            for event in self.graph.stream(initial_state, config):
                yield event
                
        except Exception as e:
            yield {"error": f"Error en stream: {str(e)}"}

# Instancia global del grafo
narrative_processing_graph = NarrativeProcessingGraph()
