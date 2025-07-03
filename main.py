from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqlalchemy.exc import ProgrammingError
from api.core.database import Base, engine
import api.models.email, api.models.player, api.models.character, api.models.scene, api.models.story, api.models.turn, api.models.ruleset, api.models.campaign  # importa aquí todos los modelos que quieras crear
import threading
from jobs.gmail_service_cron import start_email_cron  # Importa desde la raíz del proyecto
from jobs.email_db_cron import start_email_db_processor  # Importa desde la raíz del proyecto
from api.endpoints import email, player, character, scene, story, turn, ruleset, campaign
from utils.logger_config import configure_logging

# Configurar el logger
logger = configure_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Tablas comprobadas/creadas correctamente.")
    except ProgrammingError as e:
        logger.error(f"Error al crear tablas: {e}")
    # Hilo1: Lanzar el proceso de lectura de emails en un thread, bloqueado temporalmente
    email_thread = threading.Thread(target=start_email_cron, daemon=True)
    email_thread.start()
    logger.info("Proceso de lectura de emails del correo iniciado en segundo plano.")
    # Hilo2: Lanzar el proceso de lectura de emails desde la base de datos
    email_db_thread = threading.Thread(target=start_email_db_processor, daemon=True)
    email_db_thread.start()
    logger.info("Proceso de lectura de emails desde la base de datos iniciado en segundo plano.")
    yield  # Aquí puede ir el código de shutdown si lo necesitas

app = FastAPI(lifespan=lifespan)

app.include_router(email.router) 
app.include_router(player.router) 
app.include_router(character.router)
app.include_router(scene.router)
app.include_router(story.router)
app.include_router(turn.router)
app.include_router(ruleset.router)