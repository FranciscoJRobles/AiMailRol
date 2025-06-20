# Punto de entrada del servicio
import sys
from services.jugadores_manager import get_jugadores
from models.email import Email
from services.gmail_service import send_new_thread_email
from jobs.email_cron import start_email_cron

def main():
    if len(sys.argv) > 1 and sys.argv[1] == 'sendmail':
        # Enviar mensaje inicial a todos los jugadores
        jugadores = get_jugadores()
        subject = '[COMBATE][TEST] Combate de prueba'
        body = 'Turno 1: \n ¡Comienza el combate! Responde a este email con tu acción.'
        email = Email(
            subject=subject,
            body=body,
            recipients=jugadores
        )
        send_new_thread_email(email)

    start_email_cron()

if __name__ == "__main__":
    main()
