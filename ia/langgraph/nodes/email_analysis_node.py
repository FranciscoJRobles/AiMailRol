"""
Nodo para análisis de emails usando IA.
Clasifica intenciones y detecta transiciones de estado.
"""

from typing import Dict, Any
from langgraph.graph import StateGraph

from ia.ia_client import IAClient
from ..states.email_state import EmailState
from api.managers.email_manager import EmailManager
from api.managers.character_manager import CharacterManager
from api.managers.player_manager import PlayerManager
from api.models.scene import PhaseType
from ia.constantes.listas import TRANSICION_DE_DINÁMICA
import logging, json

logger = logging.getLogger(__name__)

class EmailAnalysisNode:
    """Nodo encargado del análisis de emails entrantes."""
    

    
    def __call__(self, state: EmailState, modo: PhaseType.narracion) -> EmailState:
        """
        Analiza el email y clasifica sus intenciones.
        
        Args:
            state: Estado actual que contiene el email a analizar
            
        Returns:
            Estado actualizado con análisis de intenciones y transiciones
        """
        try:
            logger.info(f"Analizando email ID: {state['email_id']}")
            
            # Obtener datos del email si no están en el estado
            if not state.get('email_data'):
                email = EmailManager.get(state['db_session'], state['email_id'])
                state['email_data'] = {
                    'subject': email.subject,
                    'body': email.body,
                    'sender': email.sender,
                    'thread_id': email.thread_id,
                    'campaign_id': email.campaign_id,
                    'scene_id': email.scene_id,
                    'player_id': email.player_id,
                    'character_id': email.character_id
                }
            
            # Actualizar identificadores en el estado
            state['campaign_id'] = state['email_data'].get('campaign_id')
            state['scene_id'] = state['email_data'].get('scene_id')
            state['player_id'] = state['email_data'].get('player_id')
            state['character_id'] = state['email_data'].get('character_id')
            
            # Obtener lista de personajes jugadores si hay campaña
            if state['campaign_id']:
                personajes = CharacterManager.list(state['db_session'])
                # Filtrar por campaña
                state['personajes_pj'] = [
                    {
                        'id': p.id,
                        'nombre': p.nombre,
                        'player_id': p.player_id
                    }
                    for p in personajes 
                    if any(c.id == state['campaign_id'] for c in p.campaigns)
                ]
            
            # Analizar intenciones en el texto
            texto_email = state['email_data']['body']
            estado_actual = state.get('estado_actual', 'narracion')
            response_dict = self._analizar_narracion_email(
                texto_email, 
                estado_actual, 
                state.get('personajes_pj'), 
                state['email_data'].get('sender') #TODO: por aqui, hay que conseguir el nombre del personaje que envía el email
            )
            
            state['clasificacion_intenciones'] = response_dict.get['clasificacion_intenciones']
            state['transicion_detectada'] = response_dict.get('transicion_detectada')
            
            # Analizar posible transición de estado
            estado_actual = state.get('estado_actual', 'narracion')
            transicion = self.subagente_analisis.analizarTransicion(
                texto_email, 
                estado_actual
            )
            state['transicion_detectada'] = transicion
            
            # Actualizar estado si hay cambio detectado
            if transicion and transicion.get('cambio_detectado'):
                state['estado_nuevo'] = transicion.get('nuevo_estado')
                logger.info(f"Transición detectada: {estado_actual} -> {state['estado_nuevo']}")
            
            logger.info(f"Análisis completado. Intenciones encontradas: {len(intenciones)}")
            
        except Exception as e:
            logger.error(f"Error en análisis de email: {e}")
            if not state.get('errors'):
                state['errors'] = []
            state['errors'].append(f"Error en análisis: {str(e)}")
        
        return state

# Función helper para usar en el grafo
def analyze_email_node(state: EmailState) -> EmailState:
    """Función de conveniencia para usar en el grafo LangGraph."""
    node = EmailAnalysisNode()
    return node(state)


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
            f"Eres un agente de análisis narrativo para una partida de rol por email."
            f" Analiza el siguiente email y devuelve un JSON con las siguientes claves:"
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
            f" Devuelve SIEMPRE un JSON puro y estrictamente válido en una sola línea, utilizando comillas dobles para las claves y valores, no me inyectes las dobles comillas dentro de los campos de valores. No incluyas bloques de código ni caracteres adicionales, los valores True o False, debes ponerlos en minúsculas. Utiliza la siguiente estructura JSON: {estructura_json}."
        )
        if lista_personajes_pj:
            nombres = [p['nombre'] for p in lista_personajes_pj]
            prompt += f"\nLos nombres de los personajes jugadores en esta campaña son: {nombres}."
        if personaje_sender:
            prompt += f"\nEl personaje que envía este email es: {personaje_sender} y generalmente es a quien se le aplican estas clasificaciones."
        try:
            contexto = dict(sistema=prompt, historial=[])
            respuesta = IAClient.procesar_mensaje(texto, contexto, IAClient.PerfilesEnum.CLASIFICACION)
            data = json.loads(respuesta)
            return data
        except Exception as e:
            print("Error al analizar email:", e)
            print("Respuesta recibida:", locals().get('respuesta', ''))
            return {
                "transicion_dinamica": {
                    "cambio_detectado": False,
                    "nuevo_estado": estado_actual,
                    "razon": "Error en el análisis"
                },
                "cambio_estado": []
            }