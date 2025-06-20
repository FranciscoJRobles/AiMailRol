# Utilidad para cargar variables de entorno
from dotenv import load_dotenv
import os

load_dotenv()

def get_env_variable(key: str, default=None):
    return os.getenv(key, default)
