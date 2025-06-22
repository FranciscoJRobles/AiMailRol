# ia_client.py
"""
Módulo para gestionar la conexión y procesamiento de mensajes con la IA.
"""

from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from utils.env_loader import get_env_variable

class IAClient:
    def __init__(self, config=None):
        """
        Inicializa el cliente de IA con Azure OpenAI y LangChain.
        """
        self.config = config or {}
        # Carga de variables desde .env
        self.deployment_name = get_env_variable("AZURE_OPENAI_DEPLOYMENT_NAME", "")
        self.endpoint = get_env_variable("AZURE_OPENAI_ENDPOINT", "")
        self.api_version = get_env_variable("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        self.api_key = get_env_variable("AZURE_OPENAI_API_KEY", "")
        self.llm = AzureChatOpenAI(
            azure_deployment=self.deployment_name,
            azure_endpoint=self.endpoint,
            api_version=self.api_version,
            api_key=self.api_key
        )
        self.contexto_inicial = None  # Guardará el SystemMessage de contexto


    def generar_contexto_inicial(self, texto_contexto: str):
        """
        Genera y almacena el contexto inicial del juego como SystemMessage.
        Este contexto se usará al inicio de la aventura para dotar de reglas, ambientación, etc.
        """
        self.contexto_inicial = SystemMessage(content=texto_contexto)


    def procesar_mensaje(self, mensaje: str, contexto: dict = None) -> str:
        """
        Procesa un mensaje usando la IA de Azure OpenAI y devuelve la respuesta generada.
        :param mensaje: Texto a enviar a la IA.
        :param contexto: Diccionario opcional con contexto adicional (por ejemplo, historial, sistema, etc.).
        :return: Respuesta generada por la IA.
        """
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
    
    
