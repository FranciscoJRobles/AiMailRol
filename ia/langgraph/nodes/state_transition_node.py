"""
Nodo para gestión de transiciones de estado del juego.
Actualiza el estado de la partida y persiste cambios en BD.
"""

from typing import Dict, Any
from ..states.email_state import EmailState
from api.managers.email_manager import EmailManager
from api.managers.scene_manager import SceneManager
from api.managers.turn_manager import TurnManager
from api.models.email import Email, EmailType
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class StateTransitionNode:
    """Nodo encargado de gestionar transiciones de estado y persistir cambios."""
    
    def __call__(self, state: EmailState) -> EmailState:
        """
        Gestiona transiciones de estado y persiste cambios en la base de datos.
        
        Args:
            state: Estado completo con respuesta generada
            
        Returns:
            Estado actualizado con cambios persistidos
        """
        try:
            logger.info("Iniciando transición de estado")
            
            # Aplicar transición de estado si la hay
            if state.get('transicion_detectada', {}).get('cambio_detectado'):
                self._apply_state_transition(state)
            
            # Guardar email de respuesta
            if state.get('email_respuesta'):
                self._save_response_email(state)
            
            # Marcar email original como procesado
            self._mark_email_processed(state)
            
            # Actualizar estado de escena si es necesario
            self._update_scene_state(state)
            
            state['processed'] = True
            logger.info("Transición de estado completada")
            
        except Exception as e:
            logger.error(f"Error en transición de estado: {e}")
            if not state.get('errors'):
                state['errors'] = []
            state['errors'].append(f"Error en transición: {str(e)}")
        
        return state
    
    def _apply_state_transition(self, state: EmailState):
        """Aplica la transición de estado detectada."""
        nuevo_estado = state.get('estado_nuevo')
        if not nuevo_estado:
            return
        
        logger.info(f"Aplicando transición a estado: {nuevo_estado}")
        
        # Si cambiamos a modo de turnos, crear turno inicial
        if nuevo_estado == 'accion_en_turno':
            self._initialize_turn_mode(state)
        
        # Si salimos de modo de turnos, limpiar turnos pendientes
        elif nuevo_estado == 'narracion' and state.get('estado_actual') == 'accion_en_turno':
            self._finalize_turn_mode(state)
        
        # Actualizar estado actual
        state['estado_actual'] = nuevo_estado
    
    def _initialize_turn_mode(self, state: EmailState):
        """Inicializa el modo de turnos."""
        try:
            if not state.get('scene_id'):
                return
            
            # Crear un nuevo turno si no existe uno activo
            scene = SceneManager.get_scene_by_id(state['db_session'], state['scene_id'])
            if scene:
                # Verificar si ya hay un turno activo
                active_turn = TurnManager.get_active_turn_by_scene(
                    state['db_session'], 
                    state['scene_id']
                )
                
                if not active_turn:
                    # Crear nuevo turno
                    turn_data = {
                        'scene_id': state['scene_id'],
                        'numero_turno': 1,
                        'activo': True,
                        'descripcion': 'Turno iniciado por acción de combate/estructurada'
                    }
                    TurnManager.create_turn(state['db_session'], turn_data)
                    logger.info("Nuevo turno creado")
                
        except Exception as e:
            logger.error(f"Error inicializando modo de turnos: {e}")
    
    def _finalize_turn_mode(self, state: EmailState):
        """Finaliza el modo de turnos."""
        try:
            if not state.get('scene_id'):
                return
            
            # Marcar turno activo como completado
            active_turn = TurnManager.get_active_turn_by_scene(
                state['db_session'], 
                state['scene_id']
            )
            
            if active_turn:
                TurnManager.complete_turn(state['db_session'], active_turn.id)
                logger.info("Turno finalizado")
                
        except Exception as e:
            logger.error(f"Error finalizando modo de turnos: {e}")
    
    def _save_response_email(self, state: EmailState):
        """Guarda el email de respuesta en la base de datos."""
        try:
            email_response = state['email_respuesta']
            
            # Crear nuevo email de respuesta
            email_data = {
                'type': EmailType.RESPUESTA,
                'subject': email_response['subject'],
                'body': email_response['body'],
                'sender': 'ia_narrator@aimailrol.com',  # Email del narrador IA
                'recipients': email_response['recipients'],
                'thread_id': email_response['thread_id'],
                'message_id': f"ia_{datetime.now().timestamp()}",  # ID único
                'campaign_id': email_response.get('campaign_id'),
                'scene_id': email_response.get('scene_id'),
                'processed': True,  # Ya está procesado por definición
                'date': datetime.now()
            }
            
            EmailManager.create_email(state['db_session'], email_data)
            logger.info("Email de respuesta guardado")
            
        except Exception as e:
            logger.error(f"Error guardando email de respuesta: {e}")
    
    def _mark_email_processed(self, state: EmailState):
        """Marca el email original como procesado."""
        try:
            if state.get('email_id'):
                EmailManager.mark_as_processed(
                    state['db_session'], 
                    state['email_id']
                )
                logger.info(f"Email {state['email_id']} marcado como procesado")
                
        except Exception as e:
            logger.error(f"Error marcando email como procesado: {e}")
    
    def _update_scene_state(self, state: EmailState):
        """Actualiza el estado de la escena si es necesario."""
        try:
            if not state.get('scene_id'):
                return
            
            # Si hay información relevante para actualizar en la escena
            # (por ejemplo, resumen de lo que acaba de pasar)
            
            # Por ahora, solo logeamos
            logger.info(f"Estado de escena {state['scene_id']} podría necesitar actualización")
            
        except Exception as e:
            logger.error(f"Error actualizando estado de escena: {e}")

# Función helper para usar en el grafo
def transition_state_node(state: EmailState) -> EmailState:
    """Función de conveniencia para usar en el grafo LangGraph."""
    node = StateTransitionNode()
    return node(state)
