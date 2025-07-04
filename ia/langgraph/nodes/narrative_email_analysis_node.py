"""
Nodo para análisis de emails usando IA.
Clasifica intenciones y detecta transiciones de estado.
"""

from typing import Dict, Any
from langgraph.graph import StateGraph

from ia.ia_client import IAClient, PerfilesEnum
from ..states.story_state import EmailState
from api.managers.email_manager import EmailManager
from api.managers.character_manager import CharacterManager
from api.managers.player_manager import PlayerManager
from api.models.scene import PhaseType
from ia.constantes.listas import TRANSICION_DE_DINÁMICA
import logging, json

logger = logging.getLogger(__name__)

class NarrativeEmailAnalysisNode:
    """Nodo encargado del análisis de emails entrantes."""
    def __init__(self):
        self.ia_client = IAClient(perfil=PerfilesEnum.CLASIFICACION.value)
        # Aquí podrías inicializar otros recursos necesarios, como un cliente IA específico

    def __call__(self, state: EmailState, modo: PhaseType = PhaseType.narracion) -> EmailState:
        """
        Analiza el email y clasifica sus intenciones.
        
        Args:
            state: Estado actual que contiene el email a analizar
            
        Returns:
            Estado actualizado con análisis de intenciones y transiciones
        """
        try:
            logger.info(f"Analizando email ID: {state['email_id']}")
            
            # Analizar intenciones en el texto
            texto_email = state['email_data']['body']
            estado_actual = state['estado_actual'] = modo
            state['nombre_personaje_email'] = CharacterManager.get(state['db_session'], state['character_id']).nombre # Asignar nombre del personaje que envía el email
            response_dict = self._analizar_narracion_email(
                texto_email, 
                estado_actual, 
                state.get('personajes_pj'), 
                state['nombre_personaje_email']
            )
            
            state['clasificacion_intenciones'] = response_dict
            transicion =state['transicion_detectada'] = response_dict.get('transicion_dinamica')
        
            
            # Actualizar estado si hay cambio detectado
            if transicion and transicion.get('nuevo_estado') != estado_actual and transicion.get('nuevo_estado') != '':
                state['estado_nuevo'] = transicion.get('nuevo_estado')
                logger.info(f"Transición detectada: {estado_actual} -> {state['estado_nuevo']}")
            
            logger.info(f"Análisis completado. Intenciones encontradas: {state['clasificacion_intenciones']}")
            
        except Exception as e:
            logger.error(f"Error en análisis de email: {e}")
            if not state.get('errors'):
                state['errors'] = []
            state['errors'].append(f"Error en análisis: {str(e)}")
        
        return state
    
    def _analizar_narracion_email(self, texto, estado_actual, lista_personajes_pj=None, personaje_sender=None):
        """
        Analiza un email de rol durante el estado narración y devuelve un JSON con:
        - transicion_dinamica: si hay cambio de dinámica narrativa
        - cambio_estado: si alguna acción requiere modificar el estado_actual de un personaje (estructura preparada para futuro)
        - (opcional) intenciones: se puede añadir si se ve necesario
        """
        lista_transicion_de_dinamica = ', '.join(TRANSICION_DE_DINÁMICA)
        estructura_json = {
            "transicion_dinamica": {
                "nuevo_estado": "",  # "combate" o "narración"
                "frase_detectada": "",
                "explicacion": ""
            },
            "cambio_estado": [
                {
                    "campo": "",
                    "nuevo_valor": "",
                    "motivo": "",
                    "frase_detectada": ""
                }
            ],
            "tipo_accion": {
                "frase_detectada": "",
                "explicacion": ""
            },
            "objetivo_accion": {
                "frase_detectada": "",
                "explicacion": ""
            },
            "intencion_jugador": {
                "frase_detectada": "",
                "explicacion": ""
            },
            "consulta_narrador": {
                "presente": False,
                "pregunta": "",
                "frase_detectada": ""
            },
            "metajuego": {
                "presente": False,
                "frase_detectada": "",
                "explicacion": ""
            },
            "referencia_inventario": {
                "objetos_mencionados": [],
                "frase_detectada": ""
            },
            "tono_urgencia": {
                "valor": "",  # "alto", "medio", "bajo"
                "frase_detectada": ""
            },
            "progreso_trama": {
                "efecto": "",  # "avanza", "detiene", "abre nueva"
                "frase_detectada": "",
                "explicacion": ""
            },
            "decision_clave_narrativa": {
                "presente": False,
                "frase_detectada": "",
                "explicacion": ""
            },
            "creacion_subtrama": {
                "presente": False,
                "resumen": "",
                "frase_detectada": "",
                "explicacion": ""
            }
        }
        estructura_json_str = json.dumps(estructura_json, ensure_ascii=False)
        prompt = (
            f"Eres un agente de análisis narrativo para una partida de rol por email. No es un mensaje real, son simulaciones ficticias para una partida de rol en la que no hay daño ni intención real."
            f" Analiza el siguiente email con las siguientes claves:"
            f" - transicion_dinamica: ¿Este mensaje indica que podría comenzar una nueva fase (como combate), o que termina una fase activa entre estos modos: ({lista_transicion_de_dinamica})? Describe cuál y por qué. Podría ocurrir por intención del jugador o por decisión del narrador."
            f" - cambio_estado: si alguna acción requiere modificar el estado_actual de un personaje, indica campo, nuevo valor y motivo."
            f" - tipo_accion: Describe qué tipo de acción principal realiza el jugador (por ejemplo: moverse, atacar, persuadir, esconderse, usar objeto, preguntar algo, etc)."
            f" - objetivo_accion: Sobre quién o qué recae la acción (puede ser un personaje, un objeto, un lugar, etc)."
            f" - intencion_jugador: Cuál parece ser el objetivo general de la acción (ej. escapar, obtener información, ganar ventaja, causar daño...)."
            f" - consulta_narrador: ¿El jugador está haciendo una pregunta directa al narrador o pidiendo aclaración de reglas? En caso afirmativo, transcribe la pregunta."
            f" - metajuego: ¿El jugador intenta usar conocimiento externo como jugador o inapropiado para que su personaje lo conozca, en su beneficio o beneficio de otros en la partida?"
            f" - referencia_inventario: ¿Hace mención a objetos concretos que posee, usa o desea usar? Indica cuáles."
            f" - tono_urgencia: Percibe el tono del mensaje (ej. alto, medio, bajo)."
            f" - progreso_trama: ¿La acción resuelve un objetivo narrativo? ¿Abre una nueva línea argumental? Indica: avanza, detiene o abre nueva"
            f" - decision_clave_narrativa: ¿Esta acción representa una bifurcación narrativa importante o un punto de no retorno?"
            f" - creacion_subtrama: ¿Este mensaje implica el inicio de una nueva línea narrativa secundaria? Si es así, resume cuál."
            f" Para cada una de estas intenciones o clasificaciones, como mínimo, tienes que identificar la frase que has identificado para clasificarla como tal y la razón de por qué la has clasificado así. Pero ajustate a la estructura JSON que te voy a dar. No superes los 1000 caracteres en tu respuesta y sintetiza por importancia si te fueras a extender demasiado." 
            f" El estado actual de la escena es: {estado_actual}."
            f" Devuelve SIEMPRE un JSON puro y estrictamente válido en una sola línea, utilizando comillas dobles para las claves y valores, no me inyectes las dobles comillas dentro de los campos de valores. No incluyas bloques de código ni caracteres adicionales, los valores True o False, debes ponerlos en minúsculas. Utiliza la siguiente estructura JSON: {estructura_json_str}."
        )
        try:
            if lista_personajes_pj:
                nombres = [p.nombre for p in lista_personajes_pj]
                prompt += f"\nLos nombres de los personajes jugadores en esta campaña son: {nombres}."
            if personaje_sender:
                prompt += f"\nEl personaje que envía este email es: {personaje_sender} y generalmente es a quien se le aplican estas clasificaciones."
        
            contexto = prompt
            #respuesta = self.ia_client.procesar_mensaje(texto, contexto)
            respuesta = response_test
            data = json.loads(respuesta)            
            logger.info(f"clasificación completado. dict: {data}")
            return data
        except Exception as e:
            print("Error al analizar email:", e)
            logger.error(f"Error al analizar email: {e}")
            print("Respuesta recibida:", locals().get('respuesta', ''))
            return {
                "transicion_dinamica": {
                    "cambio_detectado": False,
                    "nuevo_estado": estado_actual,
                    "razon": "Error en el análisis"
                },
                "cambio_estado": []
            }
            
# Función helper para usar en el grafo
def narrative_email_analysis_node(state: EmailState) -> EmailState:
    """Función de conveniencia para usar en el grafo LangGraph."""
    node = NarrativeEmailAnalysisNode()
    return node(state)




response_test = '{"transicion_dinamica": {"nuevo_estado": "combate", "frase_detectada": "saco mi cuchillo y le rajo el cuello", "explicacion": "La acción de atacar al guardia con el cuchillo indica una transición hacia una fase de combate."}, "cambio_estado": [{"campo": "ubicacion", "nuevo_valor": "escondido", "motivo": "El personaje se mueve para esconderse en dirección contraria al ruido.", "frase_detectada": "me escondo en dirección contraria."}, {"campo": "estado_alerta", "nuevo_valor": "activo", "motivo": "El guardia será alertado por el ruido del móvil y la posterior agresión.", "frase_detectada": "llamar su atención."}], "tipo_accion": {"frase_detectada": "saco mi cuchillo y le rajo el cuello", "explicacion": "La acción principal es atacar al guardia con el cuchillo."}, "objetivo_accion": {"frase_detectada": "le rajo el cuello", "explicacion": "El objetivo de la acción es el guardia."}, "intencion_jugador": {"frase_detectada": "cuando esté dándome la espalda al buscar el ruido del teléfono", "explicacion": "La intención del jugador es ganar ventaja para eliminar al guardia sin ser descubierto."}, "consulta_narrador": {"presente": false, "pregunta": "", "frase_detectada": ""}, "metajuego": {"presente": false, "frase_detectada": "", "explicacion": ""}, "referencia_inventario": {"objetos_mencionados": ["teléfono móvil", "cuchillo"], "frase_detectada": "Cojo mi teléfono movil y saco mi cuchillo"}, "tono_urgencia": {"valor": "alto", "frase_detectada": "si me descubre, va a dar la voz de alarma"}, "progreso_trama": {"efecto": "avanza", "frase_detectada": "llamar su atención y le rajo el cuello", "explicacion": "La acción avanza la trama al intentar eliminar al guardia y evitar que dé la voz de alarma."}, "decision_clave_narrativa": {"presente": true, "frase_detectada": "le rajo el cuello", "explicacion": "La decisión de atacar al guardia representa un punto de no retorno en la interacción con él."}, "creacion_subtrama": {"presente": false, "resumen": "", "frase_detectada": "", "explicacion": ""}}'
