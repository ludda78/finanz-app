from sqlalchemy.orm import Session
import models
import schemas
from datetime import datetime

def create_ungeplante_transaktion(db: Session, transaktion: schemas.UngeplantTransaktionCreate):
    db_transaktion = models.UngeplantTransaktion(
        typ=transaktion.typ,
        beschreibung=transaktion.beschreibung,
        betrag=transaktion.betrag,
        kommentar=transaktion.kommentar,
        monat=transaktion.monat,
        jahr=transaktion.jahr,
        datum=transaktion.datum or datetime.now(),
        status=transaktion.status or "kein_ausgleich"  # Status-Feld hinzufügen
    )
    db.add(db_transaktion)
    db.commit()
    db.refresh(db_transaktion)
    return db_transaktion

def get_ungeplante_transaktionen(db: Session, monat: int, jahr: int):
    return db.query(models.UngeplantTransaktion).filter(
        models.UngeplantTransaktion.monat == monat, 
        models.UngeplantTransaktion.jahr == jahr
    ).all()

# Weitere CRUD-Funktionen können hier hinzugefügt werden