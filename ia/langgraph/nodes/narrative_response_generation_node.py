"""
Nodo para generación de respuestas narrativas.
Combina análisis, contexto y validaciones para generar la respuesta final.
"""

from typing import Dict, Any
from ..states.story_state import EmailState
from ia.ia_client import IAClient
import logging
import json

logger = logging.getLogger(__name__)

class NarrativeResponseGenerationNode:
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
            
            respuesta = self._ia_response(state)
            
            
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

    def _ia_response(self, state:EmailState) -> str:
        """Genera una respuesta de prueba para simular la IA."""
        # Aquí se puede implementar una lógica de prueba o mock
        
        clasificacion_intenciones = state.get('clasificacion_intenciones', [])
        estado_actual = state.get('estado_actual', 'narracion')
        lista_personajes_pj = [p.nombre for p in state.get('personajes_pj')]
        personaje_sender = state.get('nombre_personaje_email', 'Desconocido')
        estructura_json = {
            "fecha_y_lugar": "",
            "cuerpo_mensaje":"",
            "cambio_estado":"",
            "estado_actual_personaje": [{}],
            "decision_clave_narrativa": {
                "presente": False,
                "explicacion": ""
            },
            "creacion_subtrama": {
                "presente": False,
                "resumen": "",
                "explicacion": ""
            }
            
        }
        
        estructura_json_estado ={
            "nombre": "",
            "cambios":[{
                "key": "",
                "valor_anterior":"",
                "valor_nuevo": ""    
            }]
        }
        
        estructura_json_estado_str = json.dumps(estructura_json_estado, ensure_ascii=False)
        
        prompt = (
            f"Tu ÚNICA salida debe ser un JSON plano, estrictamente válido, en una sola línea. No escribas explicaciones ni ningún texto fuera del JSON.\n"
            f"Eres el narrador de una partida de rol por email. Recibes un nuevo mensaje de un jugador que describe acciones, pensamientos o intenciones de su personaje.\n"
            f"Tu tarea es generar una respuesta narrativa coherente, inmersiva y acorde a las reglas del juego, el contexto previo y la ambientación establecida. La salida debe ser en formato JSON.\n"
            f"En tu respuesta JSON, quiero que identifiques los siguientes campos:\n"
            f" - fecha_y_lugar: la fecha, hora y ubicación donde se desarrolla la escena. Recuerda ser lógico y cambiar estas fechas y ubicaciones conforme progresa la aventura de forma adecuada.\n"
            f" - cuerpo_mensaje: El texto narrativo que responderá a las acciones del jugador. Es el texto que vas a generar como respuesta al o los jugadores que mandan el email, aquí no debe habe clasificaciones, solo la respuesta que esperan los jugadores\n"
            f" - cambio_estado: Si en tu respuesta identificas que hemos cambiado el estado de la narración entre los modos, combate o narracion, devuelves un true. El estado actual es {estado_actual}.\n"
            f" - estado_actual_personaje: Una lista de JSON con el estado actualizado de los personajes afectados por las acciones del jugador. Para ello en el contexto debes tener los json estado_actual por cada jugador en la partida. Debes fijarte en todos los campos de esos json, detectar si en tu respuesta hay algún parámetro que debe cambiar para cada personaje y devolver una lista de JSON con la siguiente estructura: {estructura_json_estado_str} \n"
            f" - decision_clave_narrativa: Un booleano que indica si la respuesta marca una decisión clave o un punto de no retorno en la historia. Si es así, explica brevemente por qué.\n"
            f" - creacion_subtrama: Un booleano que indica si la respuesta crea una nueva subtrama o línea narrativa. Si es así, proporciona un resumen breve y una explicación de cómo se relaciona con la trama principal.\n"
            f"La lista de personajes jugadores presentes es:{lista_personajes_pj} y el personaje que envía este email es: {personaje_sender}.\n"
            f"Recuerda que tu respuesta debe ser coherente con el contexto narrativo, las reglas del juego y las acciones del jugador. SIEMPRE en formato JSON válido y sin explicaciones adicionales.\n"
        )
        
        try:
            estructura_json_str = json.dumps(estructura_json, ensure_ascii=False)
            contexto_sistema = json.dumps(state.get('contexto_sistema', []), ensure_ascii=False, indent=2)
            contexto = prompt + "\n\n" + contexto_sistema + "\n\n" + f"Devuelve SIEMPRE un JSON plano y estrictamente válido en una sola línea, sin explicaciones adicionales, los valores true o false debes ponerlos en minúsculas. No excedas los 1000 caracteres. Usa la siguiente estructura json para tu respuesta: {estructura_json_str}"
            texto_intro =(
                "Tu tarea es generar una respuesta narrativa coherente al último email recibido, Vas a recibir un bloque JSON con toda la información de contexto que necesitas para generar tu respuesta. Ese bloque contiene los siguientes campos:\n"
                " - estado_actual_pjs: contiene una lista de json con las caracteristicas más volátiles de los personajes(estado_actual_personaje) como salud, inventario y efectos temporales.\n"
                " - contexto_historial: contiene una lista de resumenes de la historia y eventos previos relevantes para la narración en orden de más global y tardía a mas específica y cercana en el tiempo.\n"
                " - emails: contiene una lista de los últimos emails enviados por los jugadores, ordenados de más antiguo a más reciente. No contiene el último mail.\n"
                " - ultimo_email: contiene el último email enviado por el jugador, que es el que debes responder.\n"
                "Este JSON te será entregado justo a continuación. Analízalo cuidadosamente y responde al ultimo_email según las reglas del sistema."
            )
            texto_contextual = json.dumps(state.get('contexto_usuario', {}), ensure_ascii=False, indent=2)
            texto = texto_intro + "\n\n" + texto_contextual + "\n\n" + "No generes explicaciones fuera del JSON. Concéntrate en redactar la mejor respuesta narrativa posible, teniendo en cuenta el contexto y la intención del jugador.\n"
            respuesta = self.ia_client.procesar_mensaje(texto, contexto)
            data = json.loads(respuesta)            
            logger.info(f"clasificación completado. dict: {data}")
            return data
        
        except Exception as e:
            print("Error en la respuesta IA al email:", e)
            logger.error(f"Error en la respuesta IA al email: {e}")
            return {
                "cuerpo_mensaje": "",
            }
        
    def _analize_ia_response(self, state: EmailState) -> Dict[str, Any]:
        """Analiza la respuesta de la IA y extrae los efectos."""
        # Aquí se implementaría la lógica de análisis de la respuesta
        # Por ahora, devolvemos un mock de respuesta
        
        prompt = (
            f"Eres un analista narrativo que revisa una respuesta generada por el narrador IA en una partida de rol por email. "
            f"Esta respuesta es la resolución oficial a las acciones de un jugador. Tu tarea es clasificar y extraer los efectos reales producidos por esta narración, "
            f"para que el sistema pueda actualizar los datos de estado del mundo de juego correctamente.\n\n"
            f"Analiza el texto teniendo en cuenta los siguientes puntos clave:\n"
            f" - cambio_estado: Si hay cambios en el estado de algún personaje o entidad (salud, inventario, posición, condiciones, etc). "
            f"Indica el campo afectado, el nuevo valor, y el motivo.\n"
            f" - inicio_fase: ¿La narración indica el inicio o final de una fase como 'combate', 'narración', o 'transición'? Describe cuál y por qué.\n"
            f" - resolucion_accion: ¿La acción que declaró el jugador fue exitosa, fallida, o con consecuencias inesperadas?\n"
            f" - progreso_trama: ¿La narración avanza, detiene o abre una nueva línea narrativa?\n"
            f" - eventos_importantes: Enumera los eventos clave que deben registrarse para el histórico de campaña.\n"
            f" - decision_clave_narrativa: ¿La escena marca una bifurcación importante o un punto de no retorno en la historia?\n\n"
            f"Para cada punto, identifica brevemente qué parte del texto te lleva a esa conclusión. "
            f"Devuelve la información como un JSON estructurado, sin explicaciones adicionales. No excedas los 1000 caracteres."
        )
        return {
            "cambio_estado": {"personaje_id": 1, "campo": "salud", "nuevo_valor": 80, "motivo": "herida leve"},
            "inicio_fase": None,
            "resolucion_accion": "exitosa",
            "progreso_trama": "avanzada",
            "eventos_importantes": ["batalla contra el dragón"],
            "decision_clave_narrativa": False
        }
# Función helper para usar en el grafo
def narrative_generate_response_node(state: EmailState) -> EmailState:
    """Función de conveniencia para usar en el grafo LangGraph."""
    node = NarrativeResponseGenerationNode()
    return node(state)
