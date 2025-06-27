# orquestador_ia.py
"""
Orquestador principal para la IA del sistema de rol.
"""

from ia.agentes.agente_datos_iniciales import AgenteDatosIniciales
from ia.agentes.agente_email import AgenteAnalizadorEmail
from ia.agentes.agente_contexto_historia import AgenteContextoHistoria
from ia.agentes.agente_reglas import AgenteReglas
from ia.agentes.agente_subtrama_manager import AgenteSubtramaManager
from ia.agentes.agente_generador_respuesta import AgenteGeneradorRespuesta

class OrquestadorIA:
    def __init__(self):
        # Inicializar los agentes necesarios
        self.contexto_inicial = AgenteDatosIniciales()
        self.contexto_historia = AgenteContextoHistoria()
        self.procesador_email = AgenteAnalizadorEmail()
        self.reglas = AgenteReglas()
        self.subtrama_manager = AgenteSubtramaManager()
        self.generador_respuesta = AgenteGeneradorRespuesta()

    def emails_cron():
        """
        Método para iniciar el cron de emails.
        Aquí se puede implementar la lógica para consultar la tabla Emails periódicamente.
        """
        # Implementar lógica de cron aquí, si es necesario
        
        pass
    

    def procesar_email(self, email, lista_personajes_pj=None):
        datos_email = self.procesador_email.analizar(email, lista_personajes_pj)
        contexto = self.contexto_historia.obtener_contexto(datos_email)
        reglas = self.reglas.consultar(contexto)
        subtramas = self.subtrama_manager.gestionar(contexto)
        respuesta = self.generador_respuesta.generar(
            datos_email, contexto, reglas, subtramas
        )
        return respuesta
