# Tarea programada para consultar emails cada 15 segundos
import time
from services.gmail_service import fetch_unread_emails
from models.email import Email
from services.gmail_service import send_reply_email
from services.combate_manager import CombateManager
from services.gmail_service import mark_as_read

combate_manager = CombateManager()

def start_email_cron():
    while True:
        print("Buscando emails no leídos...")
        emails = fetch_unread_emails()
        for email in emails:
            subject = email['subject']
            sender = email['sender']
            thread_id = email['thread_id']
            msg_id = email.get('id')
            if '[COMBATE]' in subject and '[TEST]' in subject:
                # Guardar remitente y mensaje en la ronda actual
                combate_manager.add_participante(thread_id, sender)
                combate_manager.add_mensaje(thread_id, sender, email['body'])
                # Si todos han respondido en la ronda actual, enviar respuesta y avanzar de ronda
                if combate_manager.todos_han_respondido(thread_id):
                    ronda_actual = combate_manager.combates[thread_id]["ronda_actual"]
                    respuestas = combate_manager.get_mensajes_ronda(thread_id, ronda_actual)
                    reply_body = "Respuestas de la ronda {}:\n".format(ronda_actual+1)
                    for jugador, respuesta in respuestas.items():
                        reply_body += f"\n{jugador}:\n{respuesta}\n"
                    reply_body += "\n¡Todos han respondido! Puedes contestar para la siguiente ronda."
                    reply_email = Email(
                        subject=subject,
                        body=reply_body,
                        sender=sender,
                        recipients=combate_manager.combates[thread_id]["participantes"],
                        thread_id=thread_id,
                        message_id=email.get('message_id', '')
                    )
                    send_reply_email(reply_email)
                    combate_manager.avanzar_ronda(thread_id)
                if msg_id:
                    mark_as_read(msg_id)
                continue  # No responder automáticamente
            # Responder normalmente si no es [COMBATE]
            send_reply_email(
                Email(
                    subject=email['subject'],
                    body=email['body'],
                    sender=email.get('sender', ''),
                    recipients=email.get('recipients', []),
                    thread_id=email.get('thread_id', '')
                )
            )
            if msg_id:
                mark_as_read(msg_id)
        time.sleep(15)

def reply_to_email(email: Email):
    """
    Responde a un email a todos los destinatarios del hilo.
    """
    send_reply_email(email)
