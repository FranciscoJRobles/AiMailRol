# Tarea programada para consultar emails cada 15 segundos
import time
from services.gmail_service import fetch_all_unread_emails

def start_email_cron(initialGame: bool = False):
    # if initialGame:
    #     # Si es el inicio de un juego, enviar mensaje inicial a todos los jugadores
    #     subject = '[COMBATE][TEST] Combate de prueba'
    #     body = 'Turno 1: \n ¡Comienza el combate! Responde a este email con tu acción.'
    #     email = Email(
    #         subject=subject,
    #         body=body,
    #         recipients=jugadores
    #     )
    #     send_reply_email(email)
    while True:
        print("Buscando emails no leídos del correo...")
        fetch_all_unread_emails()        
        time.sleep(15)
