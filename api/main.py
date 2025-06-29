from fastapi import FastAPI
import logging
from contextlib import asynccontextmanager
from sqlalchemy.exc import ProgrammingError
from api.core.database import Base, engine
import api.models.email, api.models.player, api.models.character, api.models.scene, api.models.story_state, api.models.turn, api.models.ruleset, api.models.campaign  # importa aquí todos los modelos que quieras crear
import threading
from jobs.gmail_service_cron import start_email_cron  # Importa desde la raíz del proyecto
from jobs.email_db_cron import start_email_db_processor  # Importa desde la raíz del proyecto
from api.endpoints import email, player, character, scene, story_state, turn, ruleset, campaign
import os

def configure_logging():
    """Configura el sistema de logging con diferentes niveles y archivos."""
    # Crear la carpeta 'logs' si no existe
    os.makedirs('logs', exist_ok=True)

    # Crear un logger
    logger = logging.getLogger("multi_level_logger")
    logger.setLevel(logging.DEBUG)  # Nivel mínimo para el logger

    # Formato común para los logs
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Manejador para mensajes DEBUG
    debug_handler = logging.FileHandler('logs/debug.log')
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.setFormatter(formatter)

    # Manejador para mensajes INFO y superiores
    info_handler = logging.FileHandler('logs/info.log')
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(formatter)

    # Manejador para mensajes ERROR y superiores
    error_handler = logging.FileHandler('logs/error.log')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    # Agregar los manejadores al logger
    logger.addHandler(debug_handler)
    logger.addHandler(info_handler)
    logger.addHandler(error_handler)

# Llamar a la configuración de logging
configure_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        Base.metadata.create_all(bind=engine)
        print("Tablas comprobadas/creadas correctamente.")
    except ProgrammingError as e:
        print(f"Error al crear tablas: {e}")
    # Hilo1: Lanzar el proceso de lectura de emails en un thread, bloqueado temporalmente
    email_thread = threading.Thread(target=start_email_cron, daemon=True)
    email_thread.start()
    print("Proceso de lectura de emails del correo iniciado en segundo plano.")
    # Hilo2: Lanzar el proceso de lectura de emails desde la base de datos
    email_db_thread = threading.Thread(target=start_email_db_processor, daemon=True)
    email_db_thread.start()
    print("Proceso de lectura de emails desde la base de datos iniciado en segundo plano.")
    yield  # Aquí puede ir el código de shutdown si lo necesitas

app = FastAPI(lifespan=lifespan)

app.include_router(email.router) 
app.include_router(player.router) 
app.include_router(character.router)
app.include_router(scene.router)
app.include_router(story_state.router)
app.include_router(turn.router)
app.include_router(ruleset.router)
app.include_router(campaign.router)