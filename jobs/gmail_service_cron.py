# Tarea programada para consultar emails cada 15 segundos
import time
from services.gmail_service import GmailService

def start_email_cron():
    while True:
        print("Buscando emails no leídos del correo...")
        gmailService = GmailService()
        gmailService.fetch_all_unread_emails()        
        time.sleep(15)
