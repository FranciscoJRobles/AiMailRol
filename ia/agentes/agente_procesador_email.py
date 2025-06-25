import re
from ia.agentes.subagentes.subagente_intencion_mensaje_email import SubagenteClasificacionIntencionEmailIA
from api.models.email import Email
from sqlalchemy.orm import Session

class AgenteProcesadorEmail:
    def __init__(self, db: Session = None):
        self.ia_subagenteclasificacionIntencion = SubagenteClasificacionIntencionEmailIA()
        self.db = db

    def analizar(self, email, lista_personajes_pj=None):
        texto = email.body if hasattr(email, 'body') else ''

        # IA: obtener todas las intenciones del texto completo
        ia_intenciones = self.ia_subagenteclasificacionIntencion.analizar(texto, lista_personajes_pj)
        
        return { "intenciones" :ia_intenciones}

    def obtener_emails_no_procesados(self, scene_id):
        """
        Devuelve los emails de la escena con processed=False.
        """
        return self.db.query(Email).filter(Email.scene_id == scene_id, Email.processed == False).order_by(Email.date.asc()).all()

    def gestionar_emails_para_contexto(self, scene_id, max_emails=10):
        """
        Si hay menos de max_emails emails no procesados, devuelve sus bodies.
        Si hay max_emails o más, devuelve la lista de bodies y una bandera para resumir.
        """
        emails = self.obtener_emails_no_procesados(scene_id)
        bodies = [email.body for email in emails]
        if len(bodies) >= max_emails:
            return bodies, True, emails  # True indica que hay que resumir
        return bodies, False, emails

    def marcar_emails_como_procesados(self, emails):
        for email in emails:
            email.processed = True
        self.db.commit()
