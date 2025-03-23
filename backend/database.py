from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

# Umgebungsvariablen aus .env Datei laden
load_dotenv()

# Datenbankverbindung herstellen
DATABASE_URL = os.getenv("DATABASE_URL")

# Engine erstellen
engine = create_engine(DATABASE_URL)

# Session erstellen
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base-Klasse für die Models
Base = declarative_base()

# Dependency für FastAPI Endpunkte
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
