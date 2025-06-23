# ia_client.py
"""
Módulo para gestionar la conexión y procesamiento de mensajes con la IA.
"""

from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from utils.env_loader import get_env_variable

class IAClient:
    # Perfiles de configuración para la IA
    PERFILES = {
        "creativa": {
            "temperature": 1.0,
            "top_p": 0.95,
            "max_tokens": 512
        },
        "precisa": {
            "temperature": 0.2,
            "top_p": 0.7,
            "max_tokens": 256
        },
        "neutral": {
            "temperature": 0.7,
            "top_p": 0.85,
            "max_tokens": 400
        },
        "resumen": {
            "temperature": 0.3,
            "top_p": 0.8,
            "max_tokens": 2048
        }
    }

    def __init__(self, config=None, perfil: str = "creativa"):
        """
        Inicializa el cliente de IA con Azure OpenAI y LangChain.
        Permite seleccionar un perfil de parámetros.
        """
        self.config = config or {}
        self.perfil = perfil
        # Carga de variables desde .env
        self.deployment_name = get_env_variable("AZURE_OPENAI_DEPLOYMENT_NAME", "")
        self.endpoint = get_env_variable("AZURE_OPENAI_ENDPOINT", "")
        self.api_version = get_env_variable("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        self.api_key = get_env_variable("AZURE_OPENAI_API_KEY", "")
        # Inicializa el modelo con los parámetros del perfil
        self._init_llm()
        self.contexto_inicial = None  # Guardará el SystemMessage de contexto


    def _init_llm(self):
        """
        Inicializa el modelo LLM con los parámetros del perfil actual.
        """
        params = self.PERFILES.get(self.perfil, self.PERFILES["creativa"])
        self.llm = AzureChatOpenAI(
            azure_deployment=self.deployment_name,
            azure_endpoint=self.endpoint,
            api_version=self.api_version,
            api_key=self.api_key,
            temperature=params["temperature"],
            top_p=params["top_p"],
            max_tokens=params["max_tokens"]
        )

    def set_perfil(self, perfil: str):
        """
        Cambia el perfil de parámetros de la IA y reinicializa el modelo.
        """
        if perfil in self.PERFILES:
            self.perfil = perfil
            self._init_llm()
        else:
            raise ValueError(f"Perfil '{perfil}' no definido.")

    def generar_contexto_inicial(self, texto_contexto: str):
        """
        Genera y almacena el contexto inicial del juego como SystemMessage.
        Este contexto se usará al inicio de la aventura para dotar de reglas, ambientación, etc.
        """
        self.contexto_inicial = SystemMessage(content=texto_contexto)


    def procesar_mensaje(self, mensaje: str, contexto: dict = None, perfil: str = None) -> str:
        """
        Procesa un mensaje usando la IA de Azure OpenAI y devuelve la respuesta generada.
        Permite especificar un perfil de parámetros para esta llamada.
        :param mensaje: Texto a enviar a la IA.
        :param contexto: Diccionario opcional con contexto adicional (por ejemplo, historial, sistema, etc.).
        :param perfil: (opcional) Nombre del perfil de parámetros a usar para esta llamada.
        :return: Respuesta generada por la IA.
        """
        if perfil and perfil != self.perfil:
            self.set_perfil(perfil)
        mensajes = []
        # Ejemplo de contexto: puedes pasar un historial de mensajes o instrucciones de sistema
        if contexto:
            if "sistema" in contexto:
                mensajes.append(HumanMessage(role="system", content=contexto["sistema"]))
            if "historial" in contexto:
                for msg in contexto["historial"]:
                    mensajes.append(HumanMessage(content=msg))
        mensajes.append(HumanMessage(content=mensaje))
        response = self.llm.invoke(mensajes)
        return response.content


