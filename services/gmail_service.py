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
from api.core.database import SessionLocal
from api.schemas.email import EmailCreate
from api.models.email import EmailType
from api.models.player import Player
from api.models.character import Character
from api.models.associations import campaign_characters
from api.managers.campaign_manager import CampaignManager
from api.managers.story_state_manager import StoryStateManager
from api.managers.character_manager import CharacterManager
from api.managers.player_manager import PlayerManager
from api.managers.email_manager import EmailManager
from api.models.campaign import Campaign
from api.managers.player_manager import get_player_id_by_email
from api.models.story_state import StoryState  # Importar StoryState

# Variables globales para configuración y autenticación
SCOPES = get_env_variable("GMAIL_SCOPES").split(",")
TOKEN_PATH = os.path.join(os.path.dirname(__file__), '..', 'config', 'token.json')


def get_gmail_service():
    if not os.path.exists(TOKEN_PATH):
        raise Exception("No se encontró config/token.json. Realiza el flujo OAuth2 para obtenerlo.")
    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    return build('gmail', 'v1', credentials=creds)

def move_to_label(message_id, label_name):
    service = get_gmail_service()
    # Buscar o crear la etiqueta
    labels = service.users().labels().list(userId='me').execute().get('labels', [])
    label_id = next((l['id'] for l in labels if l['name'] == label_name), None)
    if not label_id:
        label = service.users().labels().create(userId='me', body={'name': label_name}).execute()
        label_id = label['id']
    # Añadir la etiqueta y quitar INBOX
    service.users().messages().modify(
        userId='me',
        id=message_id,
        body={'addLabelIds': [label_id], 'removeLabelIds': ['INBOX']}
    ).execute()

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

def fetch_all_unread_emails(label_ignore="IGNORADOS_POR_IA"):
    """
    Recupera todos los emails no leídos de la bandeja de entrada.
    Si el subject contiene una palabra clave de campaña activa, los guarda en la base de datos con toda la información relevante.
    Si no, los mueve a la etiqueta/carpeta 'IGNORADOS_POR_IA' (o la que se indique).
    """
    db = SessionLocal()
    # Recupera todas las palabras clave de campañas activas usando CampaignManager
    storystates_keywords = StoryStateManager.get_active_storystate_keywords(db, campaign_id=None) 
    service = get_gmail_service()
    results = service.users().messages().list(userId='me', labelIds=['UNREAD']).execute()
    messages = results.get('messages', [])
    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()
        headers = msg_data['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')

        # Verificar si el asunto contiene una palabra clave de campaña activa
        campaign_keyword_match = re.search(r'\[(.*?)\]', subject)
        if not campaign_keyword_match:
            move_to_label(msg['id'], label_ignore)
            continue

        campaign_keyword = campaign_keyword_match.group(1)
        campaign = CampaignManager.get_campaign_by_keyword(db, campaign_keyword)
        if not campaign:
            move_to_label(msg['id'], label_ignore)
            continue

        # Buscar palabra clave de StoryState en el formato (LABEL)
        story_state_keyword_match = re.search(r'\((.*?)\)', subject)
        story_state = None
        if story_state_keyword_match:
            story_state_keyword = story_state_keyword_match.group(1)
            story_state = StoryStateManager.get_active_story_state_by_keyword(db, story_state_keyword, campaign.id)
        else:
            move_to_label(msg['id'], label_ignore)
            continue

        if not story_state:
            # Si no se encuentra StoryState, marcar como solicitud de creación
            print(f"Solicitud de creación de StoryState detectada: {subject}")
            # TODO: Implementar lógica para manejar solicitudes de creación de StoryState
            continue

        # recuperar la Scene_id de la StoryState

        # Procesar email
        sender = next((h['value'] for h in headers if h['name'] == 'From'), '')
        recipients = [h['value'] for h in headers if h['name'] in ['To', 'Cc', 'Bcc']]
        thread_id = msg_data.get('threadId', '')
        message_id = next((h['value'] for h in headers if h['name'].lower() == 'message-id'), '')
        body = ''
        if 'data' in msg_data['payload']['body']:
            body = base64.urlsafe_b64decode(msg_data['payload']['body']['data']).decode('utf-8')
        else:
            for part in msg_data['payload'].get('parts', []):
                if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                    break

        player_id = PlayerManager.get_current_player_id_by_email(db, sender)
        character_id = CharacterManager.get_character_id_by_player_and_campaign(db, player_id, campaign.id)
        scene_id = StoryStateManager.get_scene_id_by_story_state(db, story_state.id) if story_state else None
        email_obj = EmailCreate(
            player_id=player_id,
            character_id=character_id,
            campaign_id=campaign.id,
            scene_id=scene_id,
            type=EmailType.ENTRADA,
            subject=subject,
            body=body,
            sender=sender,
            recipients=recipients,
            thread_id=thread_id,
            message_id=message_id,
            processed=False,
            resumido=False
        )
        EmailManager.create(db, email_obj)
        mark_as_read(msg['id'])
    db.close()
