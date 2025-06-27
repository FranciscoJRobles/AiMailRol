import re
from ia.agentes.subagentes.subagente_analisis_email import SubagenteAnalisisEmailIA
from api.managers.email_manager import EmailManager
from api.models.email import Email
from sqlalchemy.orm import Session

class AgenteAnalizadorEmail:
    def __init__(self, db: Session = None):
        self.email = EmailManager().get_next_email(db) if db else None
        self.ia_subagenteAnalisisEmailIA = SubagenteAnalisisEmailIA()
        self.db = db

    def analizar(self, email, lista_personajes_pj=None, estado_actual="narracion"):
        texto = email.body if hasattr(email, 'body') else ''

        # IA: obtener todas las intenciones del texto completo
        ia_intenciones = self.ia_subagenteAnalisisEmailIA.clasificar(texto, lista_personajes_pj)
        ia_transicion = self.ia_subagenteAnalisisEmailIA.analizarTransicion(texto, estado_actual)
        
        return { "intenciones" :ia_intenciones,
                "transicion": ia_transicion}
