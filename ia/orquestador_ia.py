# orquestador_ia.py
"""
Orquestador principal para la IA del sistema de rol.
"""

from ia.agentes.agente_procesador_email import AgenteProcesadorEmail
from ia.agentes.agente_contexto_historia import AgenteContextoHistoria
from ia.agentes.agente_reglas import AgenteReglas
from ia.agentes.agente_pnj_manager import AgentePNJManager
from ia.agentes.agente_subtrama_manager import AgenteSubtramaManager
from ia.agentes.agente_generador_respuesta import AgenteGeneradorRespuesta

class OrquestadorIA:
    def __init__(self):
        self.procesador_email = AgenteProcesadorEmail()
        self.contexto_historia = AgenteContextoHistoria()
        self.reglas = AgenteReglas()
        self.pnj_manager = AgentePNJManager()
        self.subtrama_manager = AgenteSubtramaManager()
        self.generador_respuesta = AgenteGeneradorRespuesta()

    def procesar_email(self, email):
        datos_email = self.procesador_email.analizar(email)
        contexto = self.contexto_historia.obtener_contexto(datos_email)
        reglas = self.reglas.consultar(contexto)
        pnj_acciones = self.pnj_manager.gestionar(contexto)
        subtramas = self.subtrama_manager.gestionar(contexto)
        respuesta = self.generador_respuesta.generar(
            datos_email, contexto, reglas, pnj_acciones, subtramas
        )
        return respuesta
