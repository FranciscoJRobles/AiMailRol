from api.models.email import Email
from sqlalchemy.orm import Session

class SubagenteGestorEmails:
    def __init__(self, db: Session):
        self.db = db

    def obtener_emails_no_procesados(self, scene_id):
        """
        Devuelve los emails de la escena con processed=False.
        """
        return self.db.query(Email).filter(Email.scene_id == scene_id, Email.processed == False).order_by(Email.date.asc()).all()

    def gestionar_emails_para_contexto(self, scene_id, max_emails=10, n_puros=3):
        """
        Si hay menos de max_emails emails no procesados, devuelve sus bodies.
        Si hay max_emails o más, resume los más antiguos y deja los n_puros últimos como contexto puro.
        Devuelve: (emails_a_resumir, emails_puros, emails_objetos_a_resumir, emails_objetos_puros, hay_que_resumir)
        """
        emails = self.obtener_emails_no_procesados(scene_id)
        if len(emails) >= max_emails:
            emails_a_resumir = emails[:-n_puros]
            emails_puros = emails[-n_puros:]
            bodies_a_resumir = [email.body for email in emails_a_resumir]
            bodies_puros = [email.body for email in emails_puros]
            return bodies_a_resumir, bodies_puros, emails_a_resumir, emails_puros, True
        else:
            bodies = [email.body for email in emails]
            return [], bodies, [], emails, False

    def marcar_emails_como_procesados(self, emails):
        for email in emails:
            email.processed = True
        self.db.commit()
