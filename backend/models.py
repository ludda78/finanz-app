from sqlalchemy import Column, Integer, String, Date, Numeric, ARRAY, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

from datetime import datetime

Base = declarative_base()

class FesteAusgabe(Base):
    __tablename__ = "feste_ausgaben"

    id = Column(Integer, primary_key=True, index=True)
    beschreibung = Column(String(255), nullable=False)
    betrag = Column(Numeric(10, 2), nullable=False)
    kategorie = Column(String(50), nullable=False)
    zahlungsintervall = Column(String(15), nullable=True)
    zahlungsmonate = Column(ARRAY(Integer), nullable=True)
    startdatum = Column(Date, nullable=False)
    enddatum = Column(Date, nullable=True)
    erstellt_am = Column(Date, nullable=True)

class UngeplanteAusgabe(Base):
    __tablename__ = "ungeplante_ausgaben"

    id = Column(Integer, primary_key=True, index=True)
    beschreibung = Column(String(255), nullable=False)
    betrag = Column(Numeric(10, 2), nullable=False)
    kategorie = Column(String(50), nullable=False)
    datum = Column(Date, nullable=False)
    erstellt_am = Column(Date, nullable=True)

class UngeplanteEinnahme(Base):
    __tablename__ = "ungeplante_einnahmen"

    id = Column(Integer, primary_key=True, index=True)
    beschreibung = Column(String(255), nullable=False)
    betrag = Column(Numeric(10, 2), nullable=False)
    datum = Column(Date, nullable=False)
    erstellt_am = Column(Date, nullable=True)

class Monatswert(Base):
    __tablename__ = "monatswerte"

    #id = Column(Integer, primary_key=True, index=True, autoincrement=True)  # ❗ Hier ist ID neu!
    eintrag_id = Column(Integer, nullable=False, primary_key=True)
    monat = Column(Integer, nullable=False, primary_key=True)
    jahr = Column(Integer, nullable=False, primary_key=True)
    kategorie = Column(String, nullable=False, primary_key=True)
    beschreibung = Column(String, nullable=False)
    soll = Column(Integer, nullable=False)
    ist = Column(Integer, nullable=True)
    
class UngeplantTransaktion(Base):
    __tablename__ = "ungeplante_transaktionen"
    
    id = Column(Integer, primary_key=True, index=True)
    typ = Column(String, nullable=False)  # 'einnahme' oder 'ausgabe'
    beschreibung = Column(String, nullable=False)
    betrag = Column(Float, nullable=False)
    kommentar = Column(String, nullable=True)
    monat = Column(Integer, nullable=False)
    jahr = Column(Integer, nullable=False)
    datum = Column(DateTime, default=datetime.now)
    status = Column(String, default="kein_ausgleich")  # Neues Status-Feld