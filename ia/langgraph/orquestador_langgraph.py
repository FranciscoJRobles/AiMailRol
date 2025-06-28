"""
Nuevo orquestador IA basado en LangGraph.
Reemplaza el OrquestadorIA original con un sistema más robusto y escalable.
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from api.core.database import SessionLocal
from api.managers.email_manager import EmailManager
from .graphs.email_processing_graph import email_processing_graph
from .graphs.combat_resolution_graph import combat_resolution_graph
from .states.game_state import GameState
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class OrquestadorLangGraph:
    """Orquestador principal usando LangGraph para procesamiento de emails."""
    
    def __init__(self):
        self.email_graph = email_processing_graph
        self.combat_graph = combat_resolution_graph
        self.game_states = {}  # Cache de estados de juego por campaña
    
    def procesar_email(self, email_id: Optional[int] = None, db_session: Optional[Session] = None) -> Dict[str, Any]:
        """
        Procesa un email usando LangGraph.
        
        Args:
            email_id: ID específico del email a procesar (opcional)
            db_session: Sesión de BD (opcional, se crea una nueva si no se proporciona)
            
        Returns:
            Resultado del procesamiento
        """
        # Crear sesión de BD si no se proporciona
        if not db_session:
            db_session = SessionLocal()
            should_close_session = True
        else:
            should_close_session = False
        
        try:
            # Si no se especifica email_id, buscar el siguiente pendiente
            if email_id is None:
                email = EmailManager.get_next_email(db_session)
                if not email:
                    logger.info("No hay emails pendientes para procesar")
                    return {
                        'success': True,
                        'message': 'No hay emails pendientes',
                        'emails_processed': 0
                    }
                email_id = email.id
            
            logger.info(f"Iniciando procesamiento de email {email_id}")
            
            # Obtener información básica del email
            email = EmailManager.get(db_session, email_id)
            if not email:
                logger.error(f"Email {email_id} no encontrado")
                return {
                    'success': False,
                    'error': f'Email {email_id} no encontrado'
                }
            
            # Determinar estado actual del juego
            current_state = self._get_current_game_state(email, db_session)
            
            # Determinar qué grafo usar basado en el contexto
            graph_to_use = self._select_graph(email, current_state)
            
            # Procesar email con el grafo seleccionado
            if graph_to_use == 'combat':
                result = self.combat_graph.process_combat_email(
                    email_id, 
                    db_session, 
                    current_state.get('estado_actual', 'accion_en_turno')
                )
            else:
                result = self.email_graph.process_email(
                    email_id, 
                    db_session, 
                    current_state.get('estado_actual', 'narracion')
                )
            
            # Actualizar estado del juego si el procesamiento fue exitoso
            if result.get('success'):
                self._update_game_state(email, result, db_session)
            
            # Enviar email de respuesta si se generó
            if result.get('success') and result.get('email_respuesta'):
                self._send_response_email(result['email_respuesta'], db_session)
            
            logger.info(f"Procesamiento de email {email_id} completado: {result.get('success', False)}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error crítico procesando email {email_id}: {e}")
            return {
                'success': False,
                'email_id': email_id,
                'error': f'Error crítico: {str(e)}'
            }
        finally:
            if should_close_session:
                db_session.close()
    
    def procesar_emails_pendientes(self, max_emails: int = 10) -> Dict[str, Any]:
        """
        Procesa múltiples emails pendientes en lote.
        
        Args:
            max_emails: Máximo número de emails a procesar
            
        Returns:
            Resumen del procesamiento en lote
        """
        db_session = SessionLocal()
        
        try:
            emails_procesados = 0
            emails_exitosos = 0
            errores = []
            
            logger.info(f"Iniciando procesamiento en lote (máximo {max_emails} emails)")
            
            while emails_procesados < max_emails:
                # Buscar siguiente email pendiente
                email = EmailManager.get_next_email(db_session)
                if not email:
                    logger.info("No hay más emails pendientes")
                    break
                
                # Procesar email
                result = self.procesar_email(email.id, db_session)
                emails_procesados += 1
                
                if result.get('success'):
                    emails_exitosos += 1
                    logger.info(f"Email {email.id} procesado exitosamente")
                else:
                    errores.append({
                        'email_id': email.id,
                        'error': result.get('error', 'Error desconocido')
                    })
                    logger.error(f"Error procesando email {email.id}: {result.get('error')}")
            
            return {
                'success': True,
                'emails_procesados': emails_procesados,
                'emails_exitosos': emails_exitosos,
                'emails_con_error': len(errores),
                'errores': errores
            }
            
        except Exception as e:
            logger.error(f"Error en procesamiento en lote: {e}")
            return {
                'success': False,
                'error': f'Error en lote: {str(e)}',
                'emails_procesados': emails_procesados,
                'emails_exitosos': emails_exitosos
            }
        finally:
            db_session.close()
    
    def _get_current_game_state(self, email, db_session: Session) -> Dict[str, Any]:
        """Obtiene el estado actual del juego para el email."""
        try:
            campaign_id = email.campaign_id
            scene_id = email.scene_id
            
            # Si tenemos el estado en cache, usarlo
            if campaign_id in self.game_states:
                cached_state = self.game_states[campaign_id]
                # Verificar si el estado está actualizado
                if cached_state.get('last_updated', datetime.min) > datetime.now().replace(hour=0):
                    return cached_state
            
            # Obtener estado actual desde la BD
            # Por defecto, asumir narración libre
            current_state = {
                'estado_actual': 'narracion',
                'campaign_id': campaign_id,
                'scene_id': scene_id,
                'last_updated': datetime.now()
            }
            
            # Verificar si hay un turno activo (indicaría combate)
            if scene_id:
                from api.managers.turn_manager import TurnManager
                active_turn = TurnManager.get_active_turn_by_scene(db_session, scene_id)
                if active_turn:
                    current_state['estado_actual'] = 'accion_en_turno'
                    current_state['turno_activo'] = active_turn.id
            
            # Cachear estado
            if campaign_id:
                self.game_states[campaign_id] = current_state
            
            return current_state
            
        except Exception as e:
            logger.error(f"Error obteniendo estado del juego: {e}")
            return {
                'estado_actual': 'narracion',
                'campaign_id': getattr(email, 'campaign_id', None),
                'scene_id': getattr(email, 'scene_id', None),
                'last_updated': datetime.now()
            }
    
    def _select_graph(self, email, current_state: Dict[str, Any]) -> str:
        """Selecciona qué grafo usar basado en el email y estado actual."""
        try:
            # Si ya estamos en combate, usar grafo de combate
            if current_state.get('estado_actual') == 'accion_en_turno':
                return 'combat'
            
            # Análisis rápido del contenido para detectar palabras clave de combate
            body = getattr(email, 'body', '').lower()
            combat_keywords = [
                'atacar', 'golpear', 'combate', 'luchar', 'pelear',
                'disparo', 'espada', 'magia ofensiva', 'hechizo de ataque',
                'iniciativa', 'turno', 'defensa'
            ]
            
            if any(keyword in body for keyword in combat_keywords):
                logger.info("Detectadas palabras clave de combate, usando grafo de combate")
                return 'combat'
            
            # Por defecto, usar grafo normal
            return 'normal'
            
        except Exception as e:
            logger.error(f"Error seleccionando grafo: {e}")
            return 'normal'
    
    def _update_game_state(self, email, result: Dict[str, Any], db_session: Session):
        """Actualiza el estado del juego basado en el resultado del procesamiento."""
        try:
            campaign_id = getattr(email, 'campaign_id', None)
            if not campaign_id:
                return
            
            # Actualizar estado en cache
            if campaign_id in self.game_states:
                state = self.game_states[campaign_id]
                
                # Actualizar estado si hubo transición
                if result.get('transicion_detectada', {}).get('cambio_detectado'):
                    state['estado_actual'] = result.get('estado_final', state.get('estado_actual'))
                
                # Actualizar si el combate terminó
                if result.get('combat_ended'):
                    state['estado_actual'] = 'narracion'
                
                state['last_updated'] = datetime.now()
                
                logger.info(f"Estado del juego actualizado para campaña {campaign_id}")
            
        except Exception as e:
            logger.error(f"Error actualizando estado del juego: {e}")
    
    def _send_response_email(self, email_response: Dict[str, Any], db_session: Session):
        """Envía el email de respuesta (placeholder - implementar según tu sistema de envío)."""
        try:
            # TODO: Implementar envío real de emails según tu configuración
            # Por ahora solo logeamos que se generó una respuesta
            
            logger.info(f"Email de respuesta preparado:")
            logger.info(f"  Asunto: {email_response.get('subject', '')}")
            logger.info(f"  Destinatarios: {email_response.get('recipients', [])}")
            logger.info(f"  Thread ID: {email_response.get('thread_id', '')}")
            
            # Aquí iría la integración con tu servicio de envío de emails
            # Ejemplo: gmail_service.send_email(email_response)
            
        except Exception as e:
            logger.error(f"Error enviando email de respuesta: {e}")
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del procesamiento."""
        try:
            db_session = SessionLocal()
            
            # Contar emails pendientes
            pending_emails = EmailManager.count_pending_emails(db_session)
            
            # Contar emails procesados hoy
            from datetime import date
            today_processed = EmailManager.count_processed_today(db_session, date.today())
            
            db_session.close()
            
            return {
                'emails_pendientes': pending_emails,
                'emails_procesados_hoy': today_processed,
                'estados_juego_activos': len(self.game_states),
                'grafos_disponibles': ['normal', 'combat']
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {
                'error': str(e),
                'emails_pendientes': 0,
                'emails_procesados_hoy': 0
            }

# Instancia global del orquestador
orquestador_langgraph = OrquestadorLangGraph()
