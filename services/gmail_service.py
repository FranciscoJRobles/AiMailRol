# Servicio para interactuar con Gmail
from typing import List, Dict
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from utils.env_loader import get_env_variable
from datetime import datetime
from email.mime.text import MIMEText
from email.utils import COMMASPACE
import base64
import re
import os

# Variables globales para configuración y autenticación
SCOPES = get_env_variable("GMAIL_SCOPES").split(",")
TOKEN_PATH = os.path.join(os.path.dirname(__file__), '..', 'config', 'token.json')


def get_gmail_service():
    if not os.path.exists(TOKEN_PATH):
        raise Exception("No se encontró config/token.json. Realiza el flujo OAuth2 para obtenerlo.")
    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    return build('gmail', 'v1', credentials=creds)


def fetch_unread_emails() -> List[Dict[str, str]]:
    """
    Obtiene los emails no leídos de Gmail cuyo asunto contiene la palabra clave [TEST].
    Devuelve una lista de diccionarios con 'subject', 'body', 'sender', 'recipients', 'thread_id'.
    """
    service = get_gmail_service()
    results = service.users().messages().list(userId='me', labelIds=['UNREAD'], q='[TEST]').execute()
    messages = results.get('messages', [])
    emails = []
    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()
        headers = msg_data['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
        if '[TEST]' not in subject:
            continue
        sender = next((h['value'] for h in headers if h['name'] == 'From'), '')
        recipients = [h['value'] for h in headers if h['name'] in ['To', 'Cc', 'Bcc']]
        thread_id = msg_data.get('threadId', '')
        message_id = next((h['value'] for h in headers if h['name'].lower() == 'message-id'), '')
        body = ''
        if 'data' in msg_data['payload']['body']:
            body = base64.urlsafe_b64decode(msg_data['payload']['body']['data']).decode('utf-8')
        else:
            # Si el cuerpo está en las partes
            for part in msg_data['payload'].get('parts', []):
                if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                    break
        emails.append({'subject': subject, 'body': body, 'sender': sender, 'recipients': recipients, 'thread_id': thread_id, 'id': msg['id'], 'message_id': message_id})
    return emails


def send_reply_email(email):
    """
    Envía una respuesta al email recibido, a todos los destinatarios del hilo.
    El cuerpo incluirá '[Respuesta generada por IA]' y la conversación anterior con formato de cita Gmail.
    """
    service = get_gmail_service()
    # Formato Gmail: El [fecha], [remitente] escribió:\n> línea1\n> línea2...

    # Intenta extraer fecha y remitente del body original (si no, usa sender)
    fecha = datetime.now().strftime('%a, %d %b %Y %H:%M')
    remitente = email.sender
    # Formatea el body anterior como cita
    body_citado = '\n'.join(f'> {line}' for line in email.body.splitlines())
    reply_body = (
        "[Respuesta generada por IA]\n\nrespuesta de prueba\n\n"
        f"El {fecha}, {remitente} escribió:\n{body_citado}"
    )
    message = {
        'raw': create_message_raw(
            email.recipients,
            email.subject,
            reply_body,
            getattr(email, 'message_id', '')
        ),
        'threadId': email.thread_id
    }
    service.users().messages().send(userId='me', body=message).execute()
    print(f"Email enviado a: {email.recipients} con asunto: {email.subject}")

   
def create_message_raw(to, subject, body, in_reply_to_message_id):
    mime_message = MIMEText(body)
    mime_message['to'] = COMMASPACE.join(to) if isinstance(to, list) else to
    mime_message['subject'] = subject
    if in_reply_to_message_id:
        mime_message['In-Reply-To'] = in_reply_to_message_id
        mime_message['References'] = in_reply_to_message_id
    raw = base64.urlsafe_b64encode(mime_message.as_bytes()).decode()
    return raw

def mark_as_read(message_id):
    service = get_gmail_service()
    service.users().messages().modify(userId='me', id=message_id, body={'removeLabelIds': ['UNREAD']}).execute()

def send_new_thread_email(email):
    """
    Envía un mensaje nuevo (no respuesta) a todos los jugadores para iniciar el combate.
    """
    service = get_gmail_service()
    mime_message = MIMEText(email.body)
    mime_message['to'] = COMMASPACE.join(email.recipients) if isinstance(email.recipients, list) else email.recipients
    mime_message['subject'] = email.subject
    raw = base64.urlsafe_b64encode(mime_message.as_bytes()).decode()
    message = {'raw': raw}
    service.users().messages().send(userId='me', body=message).execute()
    print(f"Mensaje inicial enviado a: {email.recipients} con asunto: {email.subject}")
