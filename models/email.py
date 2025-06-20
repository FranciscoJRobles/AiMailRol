# Modelo de datos para un email
from dataclasses import dataclass

@dataclass
class Email:
    subject: str
    body: str
    sender: str = ''
    recipients: list = None
    thread_id: str = ''
    message_id: str = ''
