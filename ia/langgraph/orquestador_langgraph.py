"""
Nuevo orquestador IA basado en LangGraph.
Reemplaza el OrquestadorIA original con un sistema más robusto y escalable.
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from api.core.database import SessionLocal
from api.managers.email_manager import EmailManager
from api.managers.turn_manager import TurnManager
from api.managers.scene_manager import SceneManager
from api.models.email import Email  
from api.models.scene import Scene, PhaseType
from .graphs.processing_graph import processing_graph
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class OrquestadorLangGraph:
    """Orquestador principal usando LangGraph para procesamiento de emails."""
    
    def __init__(self):
        self.narrative_graph = processing_graph
        self.game_states = {}  # Cache de estados de juego por campaña
    
    def procesar_email(self) -> Dict[str, Any]:
        """
        Procesa el siguiente email pendiente usando LangGraph.
        
        Returns:
            Resultado del procesamiento:
            - Si encuentra email: lo procesa completamente
            - Si no hay emails pendientes: retorna success=True con reason='no_pending_emails'
        """
        # Crear una sesión para todo el procesamiento
        db_session = SessionLocal()
        
        try:
            # Buscar el siguiente email pendiente
            email = EmailManager.get_next_email(db_session)
            if not email:
                logger.info("No hay emails pendientes para procesar")
                return {
                    'success': True,
                    'message': 'No hay emails pendientes para procesar',
                    'email_processed': False,
                    'reason': 'no_pending_emails'
                }
            
            email_id = email.id
            logger.info(f"Iniciando procesamiento de email {email_id} de {email.sender} [proceso interrumpido aquí temporalmente]")
            
            # Determinar estado actual del juego
            current_state = self._get_current_game_state(email, db_session)
            
            # Determinar qué grafo usar basado en el contexto
            graph_to_use = self._select_graph(email, current_state)
            
            # Procesar email con el grafo seleccionado

            result = self.narrative_graph.process_email(
                email, 
                db_session, 
                current_state.get('estado_actual', PhaseType.narracion)
            )
            
            # Actualizar estado del juego si el procesamiento fue exitoso
            if result.get('success'):
                self._update_game_state(email, result, db_session)
                
                # Commit de toda la transacción si fue exitoso
                db_session.commit()
                logger.info(f"Procesamiento de email {email_id} completado exitosamente")
                
                # Agregar información de éxito al resultado
                result['email_processed'] = True
                result['email_id'] = email_id
            else:
                # Rollback si hubo error en el procesamiento
                db_session.rollback()
                logger.error(f"Error en procesamiento de email {email_id}, rollback aplicado")
                result['email_processed'] = False
            
            # Enviar email de respuesta si se generó (fuera de la transacción principal)
            if result.get('success') and result.get('email_respuesta'):
                self._send_response_email(result['email_respuesta'])
            
            
            return result
            
        except Exception as e:
            # Error crítico → rollback completo
            db_session.rollback()
            logger.error(f"Error crítico procesando email: {e}")
            return {
                'success': False,
                'error': f'Error crítico: {str(e)}'
            }
        finally:
            # Siempre cerrar la sesión
            db_session.close()
    
    def procesar_emails_pendientes(self, max_emails: int = 10) -> Dict[str, Any]: # no usado por ahora
        """
        Procesa múltiples emails pendientes en lote.
        Cada email se procesa en su propia transacción independiente.
        
        Args:
            max_emails: Máximo número de emails a procesar
            
        Returns:
            Resumen del procesamiento en lote
        """
        emails_procesados = 0
        emails_exitosos = 0
        errores = []
        
        logger.info(f"Iniciando procesamiento en lote (máximo {max_emails} emails)")
        
        try:
            while emails_procesados < max_emails:
                # Procesar siguiente email (cada uno en su propia transacción)
                result = self.procesar_email()
                
                # Si no hay más emails, terminar
                if result.get('reason') == 'no_pending_emails':
                    logger.info("No hay más emails pendientes")
                    break
                
                emails_procesados += 1
                
                if result.get('success'):
                    emails_exitosos += 1
                    email_id = result.get('email_id', 'unknown')
                    logger.info(f"Email {email_id} procesado exitosamente")
                else:
                    email_id = result.get('email_id', 'unknown')
                    errores.append({
                        'email_id': email_id,
                        'error': result.get('error', 'Error desconocido')
                    })
                    logger.error(f"Error procesando email {email_id}: {result.get('error')}")
            
            # Resultado final
            resultado_final = {
                'success': True,
                'emails_procesados': emails_procesados,
                'emails_exitosos': emails_exitosos,
                'emails_con_error': len(errores),
                'errores': errores
            }
            
            # Si no se procesó ningún email, agregar información adicional
            if emails_procesados == 0:
                resultado_final['message'] = 'No había emails pendientes para procesar'
                resultado_final['reason'] = 'no_pending_emails'
            
            return resultado_final
            
        except Exception as e:
            logger.error(f"Error en procesamiento en lote: {e}")
            return {
                'success': False,
                'error': f'Error en lote: {str(e)}',
                'emails_procesados': emails_procesados,
                'emails_exitosos': emails_exitosos,
                'errores': errores
            }
    
    def _get_current_game_state(self, email, db_session: Session) -> Dict[str, Any]:
        """Obtiene el estado actual del juego para el email usando el campo fase_actual."""
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
                'estado_actual': PhaseType.narracion,
                'campaign_id': campaign_id,
                'scene_id': scene_id,
                'last_updated': datetime.now()
            }

            # Recuperar fase actual de la escena si existe
            if scene_id:
                current_state['estado_actual'] = SceneManager.get_actual_phase_by_scene_id(db_session, scene_id)

            # Cachear estado
            if campaign_id:
                self.game_states[campaign_id] = current_state

            return current_state

        except Exception as e:
            logger.error(f"Error obteniendo fase_actual del juego: {e}")
            return {
                'estado_actual': PhaseType.narracion,
                'campaign_id': getattr(email, 'campaign_id', None),
                'scene_id': getattr(email, 'scene_id', None),
                'last_updated': datetime.now()
            }
    
    def _select_graph(self, email, current_state: Dict[str, Any]) -> str:
        """Selecciona qué grafo usar basado en el email y estado actual."""
        try:
            # Si ya estamos en combate, usar grafo de combate
            if current_state.get('estado_actual') == PhaseType.combate:
                return PhaseType.combate        
            
            # Por defecto, usar grafo normal
            return PhaseType.narracion
            
        except Exception as e:
            logger.error(f"Error seleccionando grafo: {e}")
            return PhaseType.narracion
    
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
                    state['estado_actual'] = PhaseType.narracion
                
                state['last_updated'] = datetime.now()
                
                logger.info(f"Estado del juego actualizado para campaña {campaign_id}")
            
        except Exception as e:
            logger.error(f"Error actualizando estado del juego: {e}")
    
    def _send_response_email(self, email_response: Dict[str, Any]):
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
