"""
Nodo para generación de respuestas narrativas.
Combina análisis, contexto y validaciones para generar la respuesta final.
"""

from typing import Dict, Any
from ..states.email_state import EmailState
from ia.ia_client import IAClient
import logging
import json

logger = logging.getLogger(__name__)

class ResponseGenerationNode:
    """Nodo encargado de generar la respuesta narrativa final."""
    
    def __init__(self):
        self.ia_client = IAClient(perfil="creativa")
    
    def __call__(self, state: EmailState) -> EmailState:
        """
        Genera la respuesta narrativa basada en todo el contexto disponible.
        
        Args:
            state: Estado completo con análisis, contexto y validaciones
            
        Returns:
            Estado actualizado con respuesta generada
        """
        try:
            logger.info("Generando respuesta narrativa")
            
            # Construir el prompt completo para la respuesta
            prompt_sistema = self._build_system_prompt(state)
            prompt_accion = self._build_action_prompt(state)
            
            # Generar respuesta usando la IA
            contexto = {
                "sistema": prompt_sistema,
                "historial": state.get('contexto_historial', [])
            }
            
            respuesta = self.ia_client.procesar_mensaje(
                prompt_accion,
                contexto,
                "creativa"
            )
            
            state['respuesta_ia'] = respuesta
            
            # Preparar email de respuesta
            email_respuesta = self._format_email_response(state, respuesta)
            state['email_respuesta'] = email_respuesta
            
            logger.info("Respuesta generada exitosamente")
            
        except Exception as e:
            logger.error(f"Error generando respuesta: {e}")
            if not state.get('errors'):
                state['errors'] = []
            state['errors'].append(f"Error en generación: {str(e)}")
            
            # Generar respuesta de error básica
            state['respuesta_ia'] = "Lo siento, ha ocurrido un error procesando tu mensaje. Por favor, intenta de nuevo."
            state['email_respuesta'] = self._format_error_response(state)
        
        return state
    
    def _build_system_prompt(self, state: EmailState) -> str:
        """Construye el prompt de sistema con todo el contexto."""
        prompt_parts = []
        
        # Instrucciones básicas
        prompt_parts.append("""
        Eres un narrador de rol narrativo experto. Tu trabajo es responder a las acciones de los jugadores
        de manera inmersiva, manteniendo la coherencia narrativa y aplicando las reglas del juego.
        """)
        
        # Contexto del sistema (ambientación, resúmenes)
        if state.get('contexto_sistema'):
            prompt_parts.append("CONTEXTO DEL JUEGO:")
            prompt_parts.append(state['contexto_sistema'])
        
        # Información de personajes
        if state.get('personajes_pj'):
            prompt_parts.append("\nPERSONAJES JUGADORES:")
            for pj in state['personajes_pj']:
                prompt_parts.append(f"- {pj.get('nombre', 'Sin nombre')} (ID: {pj.get('id')})")
        
        # Reglas relevantes
        if state.get('ruleset'):
            prompt_parts.append(f"\nREGLAS IMPORTANTES:")
            prompt_parts.append(state['ruleset'].get('reglas', ''))
        
        # Estado actual del juego
        estado = state.get('estado_actual', 'narracion')
        if estado == 'accion_en_turno':
            prompt_parts.append("""
            \nESTADO: Actualmente en modo de TURNOS. Los personajes deben declarar acciones ordenadamente.
            Espera a que todos los jugadores declaren antes de resolver las acciones.
            """)
        else:
            prompt_parts.append("""
            \nESTADO: Actualmente en modo de NARRACIÓN LIBRE. Los personajes pueden actuar libremente.
            """)
        
        return "\n".join(prompt_parts)
    
    def _build_action_prompt(self, state: EmailState) -> str:
        """Construye el prompt con las acciones específicas del jugador."""
        prompt_parts = []
        
        # Email original
        if state.get('email_data'):
            prompt_parts.append(f"EMAIL DEL JUGADOR:")
            prompt_parts.append(f"Asunto: {state['email_data'].get('subject', '')}")
            prompt_parts.append(f"Contenido: {state['email_data'].get('body', '')}")
        
        # Intenciones analizadas
        if state.get('intenciones'):
            prompt_parts.append(f"\nACCIONES DETECTADAS:")
            for i, intencion in enumerate(state['intenciones'], 1):
                prompt_parts.append(f"{i}. {intencion.get('tipo')}: {intencion.get('bloque')}")
        
        # Validaciones aplicadas
        if state.get('validaciones'):
            prompt_parts.append(f"\nVALIDACIONES:")
            for validacion in state['validaciones']:
                if not validacion.get('valida'):
                    prompt_parts.append(f"❌ Acción inválida: {validacion.get('razon')}")
                elif validacion.get('requiere_tirada'):
                    prompt_parts.append(f"🎲 Requiere tirada: {validacion.get('dificultad')}")
                else:
                    prompt_parts.append(f"✅ Acción válida: {validacion.get('razon')}")
        
        # Transición de estado si la hay
        if state.get('transicion_detectada', {}).get('cambio_detectado'):
            nuevo_estado = state.get('estado_nuevo')
            prompt_parts.append(f"\n⚠️ CAMBIO DE ESTADO DETECTADO: Cambiar a {nuevo_estado}")
        
        prompt_parts.append("""
        \nGENERA UNA RESPUESTA NARRATIVA que:
        1. Responda a todas las acciones del jugador
        2. Mantenga la inmersión y coherencia narrativa
        3. Aplique las validaciones y reglas
        4. Avance la historia de manera interesante
        5. Si hay cambio de estado, narralo de manera natural
        
        Responde como el narrador del juego, dirigiéndote al jugador en segunda persona.
        """)
        
        return "\n".join(prompt_parts)
    
    def _format_email_response(self, state: EmailState, respuesta: str) -> Dict[str, Any]:
        """Formatea la respuesta como un email."""
        email_data = state.get('email_data', {})
        
        # Determinar asunto
        subject_original = email_data.get('subject', '')
        if not subject_original.startswith('Re:'):
            subject = f"Re: {subject_original}"
        else:
            subject = subject_original
        
        return {
            'subject': subject,
            'body': respuesta,
            'thread_id': email_data.get('thread_id', ''),
            'recipients': [email_data.get('sender', '')],
            'campaign_id': state.get('campaign_id'),
            'scene_id': state.get('scene_id'),
            'type': 'IAResponse'
        }
    
    def _format_error_response(self, state: EmailState) -> Dict[str, Any]:
        """Formatea una respuesta de error."""
        email_data = state.get('email_data', {})
        
        return {
            'subject': f"Re: {email_data.get('subject', 'Error')}",
            'body': "Lo siento, ha ocurrido un error procesando tu mensaje. Por favor, intenta de nuevo o contacta al administrador.",
            'thread_id': email_data.get('thread_id', ''),
            'recipients': [email_data.get('sender', '')],
            'campaign_id': state.get('campaign_id'),
            'scene_id': state.get('scene_id'),
            'type': 'IAResponse'
        }

# Función helper para usar en el grafo
def generate_response_node(state: EmailState) -> EmailState:
    """Función de conveniencia para usar en el grafo LangGraph."""
    node = ResponseGenerationNode()
    return node(state)
