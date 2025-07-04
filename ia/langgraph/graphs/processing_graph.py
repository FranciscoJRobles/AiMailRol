"""
Grafo principal para procesamiento de emails usando LangGraph.
Orquesta el flujo completo desde análisis hasta respuesta.
"""
from IPython.display import Image, display
from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from ..states.story_state import EmailState
from ..nodes.narrative_email_analysis_node import narrative_email_analysis_node
from ..nodes.combat_email_analysis_node import combat_email_analysis_node
from ..nodes.context_gathering_node import gather_context_node
from ..nodes.rules_validation_node import validate_rules_node
from ..nodes.narrative_response_generation_node import narrative_generate_response_node
from ..nodes.combat_response_generation_node import combat_generate_response_node
from ..nodes.state_transition_node import transition_state_node
from api.models.scene import PhaseType
from api.models.email import Email
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ProcessingGraph:
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
        workflow.add_node("narrative_email_analysis", narrative_email_analysis_node)
        workflow.add_node("combat_email_analysis", combat_email_analysis_node)
        workflow.add_node("narrative_generate_response", narrative_generate_response_node)
        workflow.add_node("combat_generate_response", combat_generate_response_node)
        workflow.add_node("transition_state", transition_state_node)
        
        # Definir el flujo
        workflow.set_entry_point("gather_context")
        
        workflow.add_conditional_edges(
            "gather_context",
                lambda state: self.route_analysis_node(state),  # Usar route_analysis_node para decidir el nodo
            {
                "narrative_email_analysis": "narrative_email_analysis",
                "combat_email_analysis": "combat_email_analysis"
            }
        )
        workflow.add_edge("narrative_email_analysis", "narrative_generate_response")
        workflow.add_edge("combat_email_analysis", "combat_generate_response")
        workflow.add_edge("narrative_generate_response", END)
        workflow.add_edge("combat_generate_response", END)
        

        
        # Compilar el grafo
        return workflow.compile(checkpointer=self.checkpointer)
    
    def process_email(
        self, 
        email: Email, 
        db_session: Any,
        current_state: str = PhaseType.narracion
    ) -> Dict[str, Any]:
        """
        Procesa un email completo usando el grafo.
        
        Args:
            email: Instancia del email a procesar
            db_session: Sesión de base de datos
            current_state: Estado actual del juego
            
        Returns:
            Resultado del procesamiento
        """
        try:
            logger.info(f"Iniciando procesamiento de email {email.id}")
            
            # Estado inicial
            initial_state: EmailState = {
                'email_id': email.id,
                'email_data': {
                    'sender': email.sender,
                    'recipients': email.recipients,
                    'subject': email.subject,
                    'body': email.body
                },
                'clasificacion_intenciones': None,
                'transicion_detectada': None,
                'metajuego_detectado': False,
                'campaign_id': email.campaign_id,
                'scene_id': email.scene_id,
                'story_id': None,
                'player_id': email.player_id,
                'character_id': None,
                'json_ambientacion': None,
                'json_reglas': None,
                'json_hojas_personajes': None,
                'json_estado_actual_personajes': None,
                'contexto_historial': None,
                'contexto_ultimos_emails': None,
                'personajes_pj': None,
                'nombre_personajes_pj': None,
                'personajes_pnj': None,
                'contexto_sistema': None,
                'contexto_usuario': None,
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
            config = {"configurable": {"thread_id": f"email_{email.id}"}}
            result = self.graph.invoke(initial_state, config)
            
            # Resultado del procesamiento
            processing_result = {
                'success': result.get('processed', False),
                'email_id': email.id,
                'respuesta_generada': result.get('respuesta_ia'),
                'email_respuesta': result.get('email_respuesta'),
                'intenciones_detectadas': result.get('intenciones', []),
                'transicion_detectada': result.get('transicion_detectada'),
                'estado_final': result.get('estado_actual'),
                'errors': result.get('errors', [])
            }
            
            if processing_result['success']:
                logger.info(f"Email {email.id} procesado exitosamente")
            else:
                logger.error(f"Error procesando email {email.id}: {processing_result['errors']}")
            
            return processing_result
            
        except Exception as e:
            logger.error(f"Error crítico procesando email {email.id}: {e}")
            return {
                'success': False,
                'email_id': email.id,
                'errors': [f"Error crítico: {str(e)}"]
            }
    
    def get_graph_visualization(self) -> str:
        """Genera una visualización automática del grafo compilado en formato PNG usando Mermaid."""
        try:
            # Obtener el grafo compilado
            compiled_graph = self._build_graph()
            display(Image(compiled_graph.get_graph().draw_mermaid_png()))
            
            return "Visualización generada"
        except Exception as e:
            return f"Error generando la visualización: {str(e)}"
    
    def route_analysis_node(self,state: EmailState):
        """
        Determina qué nodo de análisis usar basado en el estado actual.
    
        """
        if state.get("estado_actual") == PhaseType.narracion:
            return "narrative_email_analysis"
        elif state.get("estado_actual") == PhaseType.combate:
            return "combat_email_analysis"
        return END

# Instancia global del grafo
processing_graph = ProcessingGraph()
