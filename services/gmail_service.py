# Servicio para interactuar con Gmail
from typing import List, Dict
from utils.env_loader import get_env_variable
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
import os
from datetime import datetime
from email.mime.text import MIMEText
from email.utils import COMMASPACE
import base64
import re
from api.core.database import SessionLocal
from api.schemas.email import EmailCreate
from api.models.email import EmailType
from api.models.player import Player
from api.models.character import Character
from api.models.associations import campaign_characters
from api.managers.campaign_manager import CampaignManager
from api.managers.story_manager import StoryManager
from api.managers.scene_manager import SceneManager
from api.managers.character_manager import CharacterManager
from api.managers.player_manager import PlayerManager
from api.managers.email_manager import EmailManager
from api.models.campaign import Campaign
from api.models.story import Story
from api.managers.story_manager import StoryManager

# Variables globales para configuración y autenticación
CONFIG_DIR = os.path.join(os.path.dirname(__file__), '..', 'config')
CREDENTIALS_PATH = os.path.join(CONFIG_DIR, 'credentials.json')
TOKEN_PATH = os.path.join(CONFIG_DIR, 'token.json')
SCOPES = get_env_variable("GMAIL_SCOPES").split(",")

class GmailService:
    def __init__(self):
        """
        Inicializa el servicio de Gmail y valida el token.
        """
        self.config_dir = CONFIG_DIR
        self.credentials_path = CREDENTIALS_PATH
        self.token_path = TOKEN_PATH
        self.scopes = SCOPES
        self.service = None
        self._initialize_service()

    def _initialize_service(self):
        """
        Inicializa el servicio de Gmail y valida el token.
        Si el token no es válido, intenta refrescarlo o generar uno nuevo.
        """
        if not os.path.exists(self.token_path):
            print(f"El archivo {self.token_path} no existe. Es necesario realizar el flujo OAuth2.")
            self._create_valid_token()

        try:
            creds = Credentials.from_authorized_user_file(self.token_path, self.scopes)
            # Realizar una solicitud de prueba para validar las credenciales
            try:
                service = build('gmail', 'v1', credentials=creds)
                service.users().getProfile(userId='me').execute()
                self.service = service
                print("Credenciales válidas y servicio inicializado correctamente.")
            except Exception as e:
                print(f"Error al validar las credenciales: {e}. Intentando refrescar o regenerar el token...")
                if creds.refresh_token:
                    creds.refresh(Request())
                    with open(self.token_path, 'w') as token:
                        token.write(creds.to_json())
                    print("Token refrescado exitosamente.")
                    self.service = build('gmail', 'v1', credentials=creds)
                else:
                    self._create_valid_token()
        except Exception as e:
            print(f"Error crítico al inicializar el servicio de Gmail: {e}")
            self._create_valid_token()

    def _create_service(self):
        """
        Comprueba si el servicio de Gmail está inicializado.
        Si no lo está, lanza una excepción.
        """
        if not os.path.exists(self.token_path):
            print(f"El archivo {self.token_path} no existe. Es necesario realizar el flujo OAuth2.")
            self._create_valid_token()           
        try:
            creds = Credentials.from_authorized_user_file(self.token_path, self.scopes)
            service = build('gmail', 'v1', credentials=creds)
            service.users().getProfile(userId='me').execute()
            return creds  # Si la solicitud tiene éxito, las credenciales son válidas
        except RefreshError as e:
            print(f"Error al validar las credenciales del servicio gmail, creando un token.json nuevo: {e}")    
            return False

    def _create_valid_token(self):
        """
        Crea un token válido para la API de Gmail.
        """
        if not os.path.exists(self.credentials_path):
            raise Exception(f"No se encontró {self.credentials_path}. Asegúrate de tener las credenciales de la API de Gmail.")

        creds = None
        try:
            if os.path.exists(self.token_path):
                creds = Credentials.from_authorized_user_file(self.token_path, self.scopes)
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    raise RefreshError  # Forzar flujo OAuth2 si el refresh falla
        except RefreshError:
            print("El token ha sido revocado o expirado. Generando uno nuevo...")
            flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, self.scopes)
            creds = flow.run_local_server(port=0)
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())

        print(f"Token creado y guardado en {self.token_path}")

    def get_service(self):
        """
        Devuelve la instancia del servicio de Gmail.
        """
        if self.service is None:
            raise Exception("El servicio de Gmail no ha sido inicializado. Llama a initialize_gmail_service() primero.")
        return self.service

    def move_to_label(self, message_id, label_name):
        service = self.get_service()
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

    def send_reply_email(self, email):
        """
        Envía una respuesta al email recibido, a todos los destinatarios del hilo.
        El cuerpo incluirá '[Respuesta generada por IA]' y la conversación anterior con formato de cita Gmail.
        """
        service = self.get_service()
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
            'raw': self.create_message_raw(
                email.recipients,
                email.subject,
                reply_body,
                getattr(email, 'message_id', '')
            ),
            'threadId': email.thread_id
        }
        service.users().messages().send(userId='me', body=message).execute()
        print(f"Email enviado a: {email.recipients} con asunto: {email.subject}")

    def create_message_raw(self, to, subject, body, in_reply_to_message_id):
        mime_message = MIMEText(body)
        mime_message['to'] = COMMASPACE.join(to) if isinstance(to, list) else to
        mime_message['subject'] = subject
        if in_reply_to_message_id:
            mime_message['In-Reply-To'] = in_reply_to_message_id
            mime_message['References'] = in_reply_to_message_id
        raw = base64.urlsafe_b64encode(mime_message.as_bytes()).decode()
        return raw

    def mark_as_read(self, message_id):
        service = self.get_service()
        service.users().messages().modify(userId='me', id=message_id, body={'removeLabelIds': ['UNREAD']}).execute()

    def send_new_thread_email(self, email):
        """
        Envía un mensaje nuevo (no respuesta) a todos los jugadores para iniciar el combate.
        """
        service = self.get_service()
        mime_message = MIMEText(email.body)
        mime_message['to'] = COMMASPACE.join(email.recipients) if isinstance(email.recipients, list) else email.recipients
        mime_message['subject'] = email.subject
        raw = base64.urlsafe_b64encode(mime_message.as_bytes()).decode()
        message = {'raw': raw}
        service.users().messages().send(userId='me', body=message).execute()
        print(f"Mensaje inicial enviado a: {email.recipients} con asunto: {email.subject}")

    def fetch_all_unread_emails(self, label_ignore="IGNORADOS_POR_IA"):
        """
        Recupera todos los emails no leídos de la bandeja de entrada.
        Si el subject contiene una palabra clave de campaña activa, los guarda en la base de datos con toda la información relevante.
        Si no, los mueve a la etiqueta/carpeta 'IGNORADOS_POR_IA' (o la que se indique).
        """
        db = SessionLocal()
        # Recupera todas las palabras clave de campañas activas usando CampaignManager
        #storystates_keywords = StoryStateManager.get_active_storystate_keywords(db, campaign_id=None) 
        service = self.get_service()
        results = service.users().messages().list(userId='me', labelIds=['UNREAD']).execute()
        messages = results.get('messages', [])
        for msg in messages:
            msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()
            headers = msg_data['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')

            # Verificar si el asunto contiene una palabra clave de campaña activa
            campaign_keyword_match = re.search(r'\[(.*?)\]', subject)
            if not campaign_keyword_match:
                self.move_to_label(msg['id'], label_ignore)
                continue

            campaign_keyword = campaign_keyword_match.group(1)
            campaign = CampaignManager.get_campaign_by_keyword(db, campaign_keyword)
            if not campaign:
                self.move_to_label(msg['id'], label_ignore)
                continue

            sender = next((h['value'] for h in headers if h['name'] == 'From'), '')
            player_id = PlayerManager.get_player_id_by_email(db, sender)
            character_id = CharacterManager.get_character_id_by_player_and_campaign(db, player_id, campaign.id)

            story_keyword_match = re.search(r'\((.*?)\)', subject)
            story = None
            if story_keyword_match:
                story_keyword = story_keyword_match.group(1)
                story = StoryManager.get_active_story_by_keyword(db, story_keyword, campaign.id)

            if not story:
                # Handle missing story case
                self.move_to_label(msg['id'], label_ignore)
                continue

            scene_id = SceneManager.get_active_scene_by_story(db, story.id) if story else None
            body = msg_data['snippet']  # O msg_data['payload']['body'] si está disponible
            recipients = next((h['value'] for h in headers if h['name'] == 'To'), '').split(',')
            thread_id = msg_data.get('threadId', '')
            message_id = msg_data.get('id', '')
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
            self.mark_as_read(msg['id'])
        db.close()

