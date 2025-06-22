from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqlalchemy.exc import ProgrammingError
from api.core.database import Base, engine
import api.models.email, api.models.player, api.models.character  # importa aquí todos los modelos que quieras crear
import threading
from jobs.email_cron import start_email_cron  # Importa desde la raíz del proyecto
from api.endpoints import email, player, character

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        Base.metadata.create_all(bind=engine)
        print("Tablas comprobadas/creadas correctamente.")
    except ProgrammingError as e:
        print(f"Error al crear tablas: {e}")
    # Lanzar el proceso de lectura de emails en un thread, bloqueado temporalmente
    #email_thread = threading.Thread(target=start_email_cron, daemon=True)
    #email_thread.start()
    #print("Proceso de lectura de emails iniciado en segundo plano.")
    yield  # Aquí puede ir el código de shutdown si lo necesitas

app = FastAPI(lifespan=lifespan)

app.include_router(email.router) 
app.include_router(player.router) 
app.include_router(character.router)