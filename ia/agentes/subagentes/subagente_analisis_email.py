from ia.constantes.listas import TRANSICION_DE_DINÁMICA, INTENCIONES_EMAIL
from utils.utils import clean_json_response
from ia.ia_client import IAClient
import json

class SubagenteAnalisisEmailIA:
    def __init__(self, perfil="clasificacion"):
        self.ia_client = IAClient(perfil=perfil)

    def analizarTransicion(self, texto, estado_actual):
        lista_transicion_de_dinamica  = ', '.join(TRANSICION_DE_DINÁMICA)
        CAMBIO_DINAMICA_SCHEMA = """
            {
            "type": "object",
            "properties": {
                "cambio_detectado": { "type": "boolean" },
                "nuevo_estado": { 
                "type": "string",
                "enum": ["accion_en_turno", "narracion"]
                },
                "razon": { "type": "string" }
            },
            "required": ["cambio_detectado", "nuevo_estado", "razon"]
            }
            """
        prompt = (
            "Eres un agente de análisis narrativo para una partida de rol narrativo por email. Tu objetivo es identificar si hay un cambio de dinámica narrativa entre los modos principales de la historia: {lista_transicion_de_dinamica} en un texto que se te va a presentar. "
            "accion_en_turno: representa escenas estructuradas por turnos, típicas de combate, conflicto, persecución o situaciones tensas donde se deben declarar acciones de forma ordenada y secuencial."
            "narracion: representa escenas de narración libre, conversación, exploración o escenas donde los personajes actúan sin restricción por turnos."
            "el estado actual es: {estado_actual}. Si hay cambio, indícalo junto con la nueva dinámica detectada. Si no hay cambio, confirma que se mantiene el estado anterior."
            "Devuelve siempre un JSON en este formato: {CAMBIO_DINAMICA_SCHEMA}. "
        )
        try:
            contexto = dict(sistema=prompt, historial=[])
            respuesta = self.ia_client.procesar_mensaje(texto, contexto, IAClient.PerfilesEnum.CLASIFICACION)
            data = json.loads(clean_json_response(respuesta))
            return data
        except Exception as e:
            return False
        
        
    def clasificar(self, texto, lista_personajes_pj=None):
        lista_intenciones = ', '.join(INTENCIONES_EMAIL)
        prompt = (
            "Eres un agente inteligente que analiza emails de jugadores en una partida de rol por email. "
            "Debes dividir el texto en bloques o frases independientes según las intenciones de los personajes o jugadores. Puedes ayudarte de caracteres como puntos, comas, conectores como el caracter 'y' para separar frases. "
            f"Las intenciones posibles son: {lista_intenciones}. Te doy descripciones de cómo interpretar algunas intenciones para que las tengas en cuenta: "
            "dialogo_pj: solo se produce cuando un personaje jugador le habla a otro personaje jugador. "
            "dialogo_pnj: es cualquier diálogo con un personaje no jugador. "
            "accion_sencilla: es cualquier acción que no requiera tiradas de dados, como moverse de forma simple, abrir una puerta, etc. "
            "accion_con_tirada: es cualquier acción que requiera una tirada de dados, como golpear algo, buscar, investigar, etc. "
            "combate: es cualquier acción relacionada con el combate entre personajes, pnjs, criaturas, etc. Generalmente la narración se detendrá para entrar en un sistema de turnos. "
            "meta: es cualquier mensaje que no forma parte de la narración del juego, como avisos de ausencia, comentarios fuera de juego, etc. "
            "metajuego: es cualquier mensaje o comentario, sea del personaje o del jugador, que rompe la coherencia de la narración por uso de conocimiento que no debería tener el personaje o información que pone de manifiesto un jugador a otros que no debería conocer. "
            "consulta_narrador: es cualquier mensaje que un jugador envía al narrador para pedir información, debería iniciarse con 'narrador: ' o  'master: ' "
            "Para cada bloque o frase, identifica la intención principal. Si no puedes clasificar el bloque en ninguna de las intenciones listadas, usa 'otro'. "
            "Nunca agrupes varias acciones o frases en una sola intención: cada frase o párrafo relevante debe analizarse y clasificarse por separado. "
            "Devuelve SIEMPRE únicamente el JSON, sin ningún texto adicional antes o después, en una sola línea, sin saltos de línea ni caracteres de escape, y asegúrate de que la clave 'entidades' sea siempre un objeto (aunque solo tenga una clave 'descripcion'). No devuelvas el JSON como string ni con comillas escapadas. "
            "Esquema JSON: {\"type\":\"object\",\"properties\":{\"intenciones\":{\"type\":\"array\",\"items\":{\"type\":\"object\",\"properties\":{\"tipo\":{\"type\":\"string\"},\"entidades\":{\"type\":\"object\"},\"bloque\":{\"type\":\"string\"}},\"required\":[\"tipo\",\"entidades\",\"bloque\"]}}},\"required\":[\"intenciones\"]}"
        )
        if lista_personajes_pj:
            nombres = [p['nombre'] for p in lista_personajes_pj]
            prompt += f"\nLos nombres de los personajes jugadores en esta campaña son: {nombres}."
        try:
            contexto = dict(sistema=prompt, historial=[])
            respuesta = self.ia_client.procesar_mensaje(texto, contexto)
            data = json.loads(clean_json_response(respuesta))
            if data.get("intenciones"):
                # Validar que entidades sea un dict
                for intencion in data["intenciones"]:
                    if not isinstance(intencion.get("entidades"), dict):
                        intencion["entidades"] = {"descripcion": intencion["entidades"]}
                return data["intenciones"]
        except Exception as e:
            print("Error al parsear la respuesta IA:", e)
            print("Respuesta recibida:", respuesta)
        return []

    def analizar_email(self, texto, estado_actual, lista_personajes_pj=None):
        """
        Analiza un email de rol y devuelve un JSON con:
        - transicion_dinamica: si hay cambio de dinámica narrativa (como en analizarTransicion)
        - cambio_estado: si alguna acción requiere modificar el estado_actual de un personaje (estructura preparada para futuro)
        - (opcional) intenciones: se puede añadir si se ve necesario
        """
        lista_transicion_de_dinamica = ', '.join(TRANSICION_DE_DINÁMICA)
        prompt = (
            "Eres un agente de análisis narrativo para una partida de rol por email."
            " Analiza el siguiente email y devuelve un JSON con las siguientes claves:"
            " - transicion_dinamica: indica si hay un cambio de dinámica narrativa entre los modos principales ({lista_transicion_de_dinamica})."
            "   Si hay cambio, indica el nuevo estado ('accion_en_turno' o 'narracion') y la razón."
            " - cambio_estado: si alguna acción requiere modificar el estado_actual de un personaje, indica personaje, campo, nuevo valor y motivo."
            "   Si no hay cambios de estado necesarios, deja este campo como lista vacía."
            " El estado actual de la escena es: {estado_actual}."
            " Devuelve SIEMPRE un JSON con la siguiente estructura:"
            '{'
            '  "transicion_dinamica": {'
            '    "cambio_detectado": boolean,'
            '    "nuevo_estado": "accion_en_turno" | "narracion",'
            '    "razon": string'
            '  },'
            '  "cambio_estado": ['
            '    {'
            '      "personaje": string,'
            '      "campo": string,'
            '      "nuevo_valor": any,'
            '      "motivo": string'
            '    }, ...'
            '  ]'
            '}'
        )
        if lista_personajes_pj:
            nombres = [p['nombre'] for p in lista_personajes_pj]
            prompt += f"\nLos nombres de los personajes jugadores en esta campaña son: {nombres}."
        try:
            contexto = dict(sistema=prompt, historial=[])
            respuesta = self.ia_client.procesar_mensaje(texto, contexto, IAClient.PerfilesEnum.CLASIFICACION)
            data = json.loads(clean_json_response(respuesta))
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

