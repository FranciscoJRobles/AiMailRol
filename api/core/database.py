import os
from utils.env_loader import get_env_variable
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Carga la URL de la base de datos desde el .env
DATABASE_URL = get_env_variable("DATABASE_URL", "postgresql+psycopg2://usuario:contraseña@localhost:5432/aimailrol")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
