from models import Monatswert
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from sqlalchemy.orm import Session
from database import get_db
from database import SessionLocal, engine
from sqlalchemy.sql import text
from datetime import datetime 
from pydantic import BaseModel
from typing import List, Optional
from datetime import date
import crud
import models
import schemas
from schemas import UngeplantTransaktionCreate
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv

from fastapi.middleware.cors import CORSMiddleware
from crud import create_ungeplante_transaktion, get_ungeplante_transaktionen
from enum import Enum

# Enum für den Status der ungeplanten Ausgaben
class TransaktionStatus(str, Enum):
    AUSGEGLICHEN = "ausgeglichen"
    NICHT_AUSGEGLICHEN = "nicht_ausgeglichen"
    KEIN_AUSGLEICH = "kein_ausgleich"

# Modell für ungeplante Ausgaben
class UngeplanteAusgabe(BaseModel):
    beschreibung: str
    betrag: float
    kategorie: Optional[str] = None  # Optional, da es keine festen Kategorien gibt
    datum: date  # Ein Datum für die Ausgabe
    erstellt_am: Optional[str] = None  # Automatisch generiert, wenn nicht angegeben
    status: Optional[TransaktionStatus] = TransaktionStatus.KEIN_AUSGLEICH

# Modell für ungeplante Einnahmen
class UngeplanteEinnahme(BaseModel):
    beschreibung: str
    betrag: float
    kategorie: Optional[str] = None  # Optional, je nach Bedarf
    datum: date  # Ein Datum für die Einnahme
    erstellt_am: Optional[str] = None  # Automatisch generiert, wenn nicht angegeben
    status: Optional[TransaktionStatus] = TransaktionStatus.KEIN_AUSGLEICH
    
# Modell für die Aktualisierung des Status
class StatusUpdate(BaseModel):
    status: TransaktionStatus

# Pydantic-Modell für Ausgaben
class FesteAusgabe(BaseModel):
    id: Optional[int] = None  # ID ist optional
    beschreibung: str
    betrag: float
    kategorie: str
    zahlungsintervall: str
    zahlungsmonate: list[int]
    startdatum: str
    
class FesteEinnahme(BaseModel):
    id: Optional[int] = None
    name: str
    betrag: float
    kategorie: Optional[str] = None  # New field
    zahlungsmonate: List[int]

# Modell für Monatsübersicht
class Monatsuebersicht(BaseModel):
    monat: int
    jahr: int
    feste_ausgaben: List[FesteAusgabe]  # Feste Ausgaben im Monat
    feste_einnahmen: List[FesteEinnahme] # Feste Einnahmen im Monat
    ungeplante_ausgaben: List[UngeplanteAusgabe]  # Ungeplante Ausgaben im Monat
    ungeplante_einnahmen: List[UngeplanteEinnahme]  # Ungeplante Einnahmen im Monat
 #   gesamt_ausgaben: float  # Summe der Ausgaben
 #   gesamt_einnahmen: float  # Summe der Einnahmen
 
 # Schemas-Erweiterung für den Status
class UngeplantTransaktionCreate(BaseModel):
    # Bestehende Felder beibehalten
    typ: str
    beschreibung: str
    betrag: float
    kommentar: Optional[str] = None
    monat: int
    jahr: int
    datum: Optional[datetime] = None
    status: Optional[TransaktionStatus] = TransaktionStatus.KEIN_AUSGLEICH


app = FastAPI()

# Erlaube CORS für alle Ursprünge (optional: kannst auch eine bestimmte URL angeben)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Erlaube alle Ursprünge (kann auch auf ["http://192.168.178.138:8080"] beschränkt werden)
    allow_credentials=True,
    allow_methods=["*"],  # Erlaube alle Methoden wie GET, POST, etc.
    allow_headers=["*"],  # Erlaube alle Header
)

# Umgebungsvariablen aus .env Datei laden
load_dotenv()

# Datenbankverbindung herstellen
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


def get_db_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        cursor_factory=RealDictCursor
    )

@app.get("/feste-ausgaben/")
def get_feste_ausgaben():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM feste_ausgaben;")
    ausgaben = cur.fetchall()
    conn.close()
    return ausgaben

@app.post("/feste-ausgaben/")
def create_feste_ausgabe(ausgabe: FesteAusgabe):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO feste_ausgaben (beschreibung, betrag, kategorie, zahlungsintervall, zahlungsmonate, startdatum) VALUES (%s, %s, %s, %s, %s, %s) RETURNING *;",
            (ausgabe.beschreibung, ausgabe.betrag, ausgabe.kategorie, ausgabe.zahlungsintervall, ausgabe.zahlungsmonate, ausgabe.startdatum),
        )
        neue_ausgabe = cur.fetchone()
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()
    return neue_ausgabe

@app.put("/feste-ausgaben/{ausgabe_id}")
def update_feste_ausgabe(ausgabe_id: int, ausgabe: FesteAusgabe):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            UPDATE feste_ausgaben
            SET beschreibung = %s, betrag = %s, kategorie = %s, 
                zahlungsintervall = %s, zahlungsmonate = %s, startdatum = %s
            WHERE id = %s
            RETURNING *;
            """,
            (ausgabe.beschreibung, ausgabe.betrag, ausgabe.kategorie, ausgabe.zahlungsintervall, 
             ausgabe.zahlungsmonate, ausgabe.startdatum, ausgabe_id),
        )
        updated_ausgabe = cur.fetchone()
        conn.commit()
        if not updated_ausgabe:
            raise HTTPException(status_code=404, detail="Ausgabe nicht gefunden")
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()
    return updated_ausgabe

@app.delete("/feste-ausgaben/{ausgabe_id}")
def delete_feste_ausgabe(ausgabe_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM feste_ausgaben WHERE id = %s RETURNING *;", (ausgabe_id,))
        deleted_ausgabe = cur.fetchone()
        conn.commit()
        if not deleted_ausgabe:
            raise HTTPException(status_code=404, detail="Ausgabe nicht gefunden")
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()
    return {"message": "Ausgabe erfolgreich gelöscht"}


@app.get("/feste_einnahmen")
def get_feste_einnahmen():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, betrag, kategorie, zahlungsmonate FROM feste_einnahmen")
    
    # Mit RealDictCursor sind die Ergebnisse bereits Dictionaries
    einnahmen = cur.fetchall()
    
    conn.close()
    
    if not einnahmen:
        raise HTTPException(status_code=404, detail="Keine festen Einnahmen gefunden")
    
    # Bei RealDictCursor könnte es sein, dass die Datentypen nicht JSON-serialisierbar sind
    # Wir konvertieren sie daher explizit
    for item in einnahmen:
        if "betrag" in item and item["betrag"] is not None:
            # Decimal zu float konvertieren für JSON-Serialisierung
            item["betrag"] = float(item["betrag"])
        if "zahlungsmonate" in item and item["zahlungsmonate"] is not None:
            # Stelle sicher, dass zahlungsmonate serialisierbar ist
            item["zahlungsmonate"] = list(item["zahlungsmonate"])
    
    return {"feste_einnahmen": einnahmen}

@app.post("/feste_einnahmen/")
def add_feste_einnahme(einnahme: FesteEinnahme):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO feste_einnahmen (name, betrag, kategorie, zahlungsmonate)
        VALUES (%s, %s, %s) RETURNING id
    """, (einnahme.name, einnahme.betrag, einnahme.kategorie, einnahme.zahlungsmonate))
    
    # Mit RealDictCursor über Spaltennamen zugreifen
    result = cur.fetchone()
    new_id = result['id']  # Hier den Spaltennamen 'id' verwenden
    
    conn.commit()
    conn.close()
    
    return {
        "message": "Einnahme hinzugefügt", 
        "einnahme": {
            "id": new_id,
            "name": einnahme.name,
            "betrag": einnahme.betrag,
            "kategorie": einnahme.kategorie,
            "zahlungsmonate": einnahme.zahlungsmonate
        }
    }
    
@app.put("/feste_einnahmen/{einnahme_id}")
def update_feste_einnahme(einnahme_id: int, einnahme: FesteEinnahme):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            UPDATE feste_einnahmen
            SET name = %s, betrag = %s, kategorie = %s, zahlungsmonate = %s
            WHERE id = %s
            RETURNING *;
            """,
            (einnahme.name, einnahme.betrag, einnahme.kategorie, einnahme.zahlungsmonate, einnahme_id),
        )
        updated_einnahme = cur.fetchone()
        conn.commit()
        if not updated_einnahme:
            raise HTTPException(status_code=404, detail="Einnahme nicht gefunden")
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()
    return updated_einnahme

@app.delete("/feste_einnahmen/{einnahme_id}")
def delete_feste_einnahme(einnahme_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM feste_einnahmen WHERE id = %s RETURNING *;", (einnahme_id,))
        deleted_einnahme = cur.fetchone()
        conn.commit()
        if not deleted_einnahme:
            raise HTTPException(status_code=404, detail="Einnahme nicht gefunden")
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()
    return {"message": "Einnahme erfolgreich gelöscht"}

@app.get("/monatsuebersicht/{monat}")
def get_monatsuebersicht(monat: int):
    if monat < 1 or monat > 12:
        raise HTTPException(status_code=400, detail="Ungültiger Monat. Bitte 1-12 eingeben.")
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT * FROM feste_ausgaben
        WHERE %s = ANY(zahlungsmonate);
        """, (monat,)
    )
    ausgaben = cur.fetchall()
    conn.close()
    return ausgaben

@app.post("/ungeplante-ausgaben")
def create_ungeplante_ausgabe(ausgabe: UngeplanteAusgabe):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO ungeplante_ausgaben (beschreibung, betrag, kategorie, datum, erstellt_am, status)
            VALUES (%s, %s, %s, %s, NOW(), %s)
            RETURNING *;
            """,
            (ausgabe.beschreibung, ausgabe.betrag, ausgabe.kategorie, ausgabe.datum, ausgabe.status)
        )
        new_ausgabe = cur.fetchone()
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()
    return new_ausgabe

@app.post("/ungeplante-einnahmen")
def create_ungeplante_einnahme(einnahme: UngeplanteEinnahme):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO ungeplante_einnahmen (beschreibung, betrag, kategorie, datum, erstellt_am, status)
            VALUES (%s, %s, %s, %s, NOW(), %s)
            RETURNING *;
            """,
            (einnahme.beschreibung, einnahme.betrag, einnahme.kategorie, einnahme.datum, einnahme.status)
        )
        new_einnahme = cur.fetchone()
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()
    return new_einnahme

@app.get("/ungeplante-ausgaben")
def get_ungeplante_ausgaben():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM ungeplante_ausgaben;")
    ausgaben = cur.fetchall()
    conn.close()
    return ausgaben

@app.get("/ungeplante-einnahmen")
def get_ungeplante_einnahmen():
    conn = get_db_connection()
    cur.execute("SELECT * FROM ungeplante_einnahmen;")
    einnahmen = cur.fetchall()
    conn.close()
    return einnahmen
    
# Neue Endpunkte für die Aktualisierung des Status
@app.put("/ungeplante-ausgaben/{ausgabe_id}/status")
def update_ausgabe_status(ausgabe_id: int, status_update: StatusUpdate):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            UPDATE ungeplante_ausgaben
            SET status = %s
            WHERE id = %s
            RETURNING *;
            """,
            (status_update.status, ausgabe_id)
        )
        updated_ausgabe = cur.fetchone()
        conn.commit()
        if not updated_ausgabe:
            raise HTTPException(status_code=404, detail="Ausgabe nicht gefunden")
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()
    return updated_ausgabe

@app.put("/ungeplante-einnahmen/{einnahme_id}/status")
def update_einnahme_status(einnahme_id: int, status_update: StatusUpdate):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            UPDATE ungeplante_einnahmen
            SET status = %s
            WHERE id = %s
            RETURNING *;
            """,
            (status_update.status, einnahme_id)
        )
        updated_einnahme = cur.fetchone()
        conn.commit()
        if not updated_einnahme:
            raise HTTPException(status_code=404, detail="Einnahme nicht gefunden")
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()
    return updated_einnahme

# Endpunkt für vollständige Aktualisierung einer ungeplanten Ausgabe
@app.put("/ungeplante-ausgaben/{ausgabe_id}")
def update_ungeplante_ausgabe(ausgabe_id: int, ausgabe: UngeplanteAusgabe):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            UPDATE ungeplante_ausgaben
            SET beschreibung = %s, betrag = %s, kategorie = %s, datum = %s, status = %s
            WHERE id = %s
            RETURNING *;
            """,
            (ausgabe.beschreibung, ausgabe.betrag, ausgabe.kategorie, ausgabe.datum, ausgabe.status, ausgabe_id)
        )
        updated_ausgabe = cur.fetchone()
        conn.commit()
        if not updated_ausgabe:
            raise HTTPException(status_code=404, detail="Ausgabe nicht gefunden")
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()
    return updated_ausgabe

# Endpunkt für vollständige Aktualisierung einer ungeplanten Einnahme
@app.put("/ungeplante-einnahmen/{einnahme_id}")
def update_ungeplante_einnahme(einnahme_id: int, einnahme: UngeplanteEinnahme):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            UPDATE ungeplante_einnahmen
            SET beschreibung = %s, betrag = %s, kategorie = %s, datum = %s, status = %s
            WHERE id = %s
            RETURNING *;
            """,
            (einnahme.beschreibung, einnahme.betrag, einnahme.kategorie, einnahme.datum, einnahme.status, einnahme_id)
        )
        updated_einnahme = cur.fetchone()
        conn.commit()
        if not updated_einnahme:
            raise HTTPException(status_code=404, detail="Einnahme nicht gefunden")
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()
    return updated_einnahme

@app.get("/monatsuebersicht/{monat}/{jahr}", response_model=Monatsuebersicht)
def get_monatsuebersicht(monat: int, jahr: int):
    conn = get_db_connection()
    cur = conn.cursor()

    # Abfrage der festen Ausgaben für den Monat
    cur.execute("""
        SELECT * FROM feste_ausgaben
        WHERE %s = ANY(zahlungsmonate)
        """, (monat,))

    feste_ausgaben = cur.fetchall()

    # Feste Einnahmen abrufen
    cur.execute("""
        SELECT * FROM feste_einnahmen
        WHERE %s = ANY(zahlungsmonate)
    """, (monat,))
    feste_einnahmen = cur.fetchall()
    # Umwandlung von RealDictRow in Dictionary + Decimal in float
    feste_einnahmen = [dict(row) for row in feste_einnahmen]
    for einnahme in feste_einnahmen:
        einnahme['betrag'] = float(einnahme['betrag'])

    # print("DEBUG - Konvertierte feste_einnahmen:", feste_einnahmen)  # Testausgabe

    # Abfrage der ungeplanten Ausgaben für den Monat
    cur.execute("""
        SELECT * FROM ungeplante_ausgaben
        WHERE EXTRACT(MONTH FROM datum) = %s
        AND EXTRACT(YEAR FROM datum) = %s;
    """, (monat, jahr))
    ungeplante_ausgaben = cur.fetchall()

    # Abfrage der ungeplanten Einnahmen für den Monat
    cur.execute("""
        SELECT * FROM ungeplante_einnahmen
        WHERE EXTRACT(MONTH FROM datum) = %s
        AND EXTRACT(YEAR FROM datum) = %s;
    """, (monat, jahr))
    ungeplante_einnahmen = cur.fetchall()

	# Umwandeln von datetime in String (ISO 8601 Format)
    for ausgabe in feste_ausgaben:
        if ausgabe['startdatum']:
            ausgabe['startdatum'] = ausgabe['startdatum'].isoformat()
    for ausgabe in ungeplante_ausgaben:
        if ausgabe['erstellt_am']:
            ausgabe['erstellt_am'] = ausgabe['erstellt_am'].isoformat()

    for einnahme in ungeplante_einnahmen:
        if einnahme['erstellt_am']:
            einnahme['erstellt_am'] = einnahme['erstellt_am'].isoformat()

    # Berechnung der Gesamtausgaben und Gesamteinnahmen
    # gesamt_ausgaben = sum([row[2] for row in feste_ausgaben]) + sum([row[2] for row in ungeplante_ausgaben])
    # gesamt_einnahmen = sum([row[2] for row in ungeplante_einnahmen])

    conn.close()

    # Monatsübersicht zurückgeben
    return {
        "monat": monat,
        "jahr": jahr,
        "feste_ausgaben": feste_ausgaben,
        "feste_einnahmen": feste_einnahmen,
        "ungeplante_ausgaben": ungeplante_ausgaben,
        "ungeplante_einnahmen": ungeplante_einnahmen,
#        "gesamt_ausgaben": gesamt_ausgaben,
#        "gesamt_einnahmen": gesamt_einnahmen,
    }


@app.get("/monatswerte/{monat}/{jahr}")
async def get_monatswerte(monat: int, jahr: int, db: Session = Depends(get_db)):
    # Manuelle SQL-Abfrage zum Testen
    sql = f"SELECT * FROM monatswerte WHERE monat = {monat} AND jahr = {jahr};"
    result = db.execute(text(sql)).fetchall()
    
    # print(f"🔎 Manuelle SQL-Abfrage: {result}")

    werte = db.query(Monatswert).filter(
        Monatswert.monat == monat,
        Monatswert.jahr == jahr
    ).all()
    # print(f"Gefundene Monatswerte für {monat}/{jahr}: {werte}")  # Debugging-Ausgabe
 
    response = {
        "monatswerte": [
            {"kategorie": w.kategorie, "eintrag_id": w.eintrag_id, "ist": w.ist} 
            for w in werte
        ]
    }
    
    # print(f"📡 API-Response: {response}")
    
    return response

    
@app.post("/monatswerte")
async def set_monatswert(ist_wert_data: dict, db: Session = Depends(get_db)):
    print("Daten: ", ist_wert_data) # Überprüfe die empfangenen Daten!
    
    eintrag_id = ist_wert_data["eintrag_id"]
    monat = ist_wert_data["monat"]
    jahr = ist_wert_data["jahr"]
    kategorie = ist_wert_data["kategorie"]
    ist_wert = ist_wert_data["ist"]
    #beschreibung = ist_wert_data["beschreibung"]
    #soll = ist_wert_data["soll"]

    # 🛠️ Default-Werte setzen, falls sie nicht übermittelt wurden
    beschreibung = ist_wert_data.get("beschreibung", "Unbekannt")
    soll = ist_wert_data.get("soll", 0)

    # Direkte Update-Methode
    count = db.query(Monatswert).filter_by(eintrag_id=eintrag_id, monat=monat, jahr=jahr, kategorie=kategorie).count()
   #  print(f"Gefundene Datensätze: {count}")

    if count > 0:
        # Direktes Update für alle passenden Einträge
        db.query(Monatswert).filter_by(
            eintrag_id=eintrag_id, 
            monat=monat, 
            jahr=jahr, 
            kategorie=kategorie
        ).update({"ist": ist_wert})
    
        db.commit()
        return {"status": "updated", "count": count}
    else:
        # Neuen Wert anlegen mit Default-Werten
        neuer_wert = Monatswert(
            eintrag_id=eintrag_id,
            monat=monat,
            jahr=jahr,
            kategorie=kategorie,
            beschreibung=beschreibung,  # 🔹 Default: "Unbekannt"
            soll=soll,  # 🔹 Default: 0
            ist=ist_wert
        )
        db.add(neuer_wert)
        db.commit()
        db.refresh(neuer_wert)  # 🔹 Holt die generierte ID aus der DB
        return {"status": "created"}

@app.post("/ungeplante-transaktionen")
async def create_ungeplante_transaktion_endpoint(
    transaktion: UngeplantTransaktionCreate, 
    db: Session = Depends(get_db)
):
    return create_ungeplante_transaktion(db, transaktion)

@app.get("/ungeplante-transaktionen/{monat}/{jahr}")
async def read_ungeplante_transaktionen(
    monat: int, 
    jahr: int, 
    db: Session = Depends(get_db)
):
    return get_ungeplante_transaktionen(db, monat, jahr)
    
@app.delete("/ungeplante-transaktionen/{id}")
async def delete_ungeplante_transaktion(id: int, db: Session = Depends(get_db)):
    transaktion = db.query(models.UngeplantTransaktion).filter(
        models.UngeplantTransaktion.id == id
    ).first()

    if not transaktion:
        raise HTTPException(status_code=404, detail="Transaktion nicht gefunden")

    db.delete(transaktion)
    db.commit()
    return {"message": f"Transaktion mit ID {id} erfolgreich gelöscht"}
 
    
# Update PUT-Endpunkt für /ungeplante-transaktionen/{id}
@app.put("/ungeplante-transaktionen/{id}")
async def update_ungeplante_transaktion(
    id: int,
    transaktion_data: dict,
    db: Session = Depends(get_db)
):
    """
    Aktualisiert eine ungeplante Transaktion, einschließlich des Status.
    """
    # Die Transaktion aus der Datenbank abrufen
    transaktion = db.query(models.UngeplantTransaktion).filter(
        models.UngeplantTransaktion.id == id
    ).first()
    
    if not transaktion:
        raise HTTPException(status_code=404, detail="Transaktion nicht gefunden")
    
    # Felder aktualisieren, die im Request enthalten sind
    update_data = {}
    
    # Alle Felder prüfen, die aktualisiert werden könnten
    possible_fields = ["typ", "beschreibung", "betrag", "kommentar", "monat", 
                      "jahr", "datum", "status"]
    
    for field in possible_fields:
        if field in transaktion_data:
            setattr(transaktion, field, transaktion_data[field])
    
    # Änderungen in der Datenbank speichern
    db.commit()
    db.refresh(transaktion)
    
    return transaktion
    
@app.get("/jahresuebersicht/{jahr}")
def get_jahresuebersicht(jahr: int):
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Alle festen Ausgaben abrufen
    cur.execute("SELECT * FROM feste_ausgaben;")
    alle_ausgaben = cur.fetchall()
    
    # Alle festen Einnahmen abrufen
    cur.execute("SELECT * FROM feste_einnahmen;")
    alle_einnahmen = cur.fetchall()
    
    # Vorbereitung der Monatsübersicht
    monats_daten = []
    
    # Summen für jeden Monat berechnen
    for monat in range(1, 13):
        monats_ausgaben = []
        monat_summe = 0
        
        # Ausgaben für diesen Monat filtern und summieren
        for ausgabe in alle_ausgaben:
            # Prüfen, ob der aktuelle Monat in den Zahlungsmonaten ist
            if monat in ausgabe['zahlungsmonate']:
                monats_ausgaben.append({
                    'id': ausgabe['id'],
                    'beschreibung': ausgabe['beschreibung'],
                    'betrag': float(ausgabe['betrag']),
                    'kategorie': ausgabe['kategorie']
                })
                monat_summe += float(ausgabe['betrag'])
        
        # Einnahmen für diesen Monat filtern und summieren nach Kategorien
        monat_einnahmen = 0
        monats_einnahmen = []
        
        # Kategorien zum Filtern
        einnahmen_andrea = 0
        einnahmen_andreas = 0
        einnahmen_andere = 0
        
        for einnahme in alle_einnahmen:
            if monat in einnahme['zahlungsmonate']:
                betrag = float(einnahme['betrag'])
                monat_einnahmen += betrag
                
                # Einnahmen nach Kategorien filtern
                kategorie = einnahme.get('kategorie', 'Andere')
                
                monats_einnahmen.append({
                    'id': einnahme['id'],
                    'name': einnahme['name'],
                    'betrag': betrag,
                    'kategorie': kategorie
                })
                
                # Nach Kategorien filtern
                if kategorie == 'Andrea':
                    einnahmen_andrea += betrag
                elif kategorie == 'Andreas':
                    einnahmen_andreas += betrag
                else:
                    einnahmen_andere += betrag
        
        # Daten für diesen Monat speichern
        monats_daten.append({
            'monat': monat,
            'ausgaben': monats_ausgaben,
            'ausgaben_summe': monat_summe,
            'einnahmen': monats_einnahmen,
            'einnahmen_summe': monat_einnahmen,
            'einnahmen_andrea': einnahmen_andrea,
            'einnahmen_andreas': einnahmen_andreas,
            'einnahmen_andere': einnahmen_andere,
            'saldo': monat_einnahmen - monat_summe
        })
    
    # Jahres-Mittelwert berechnen
    jahres_summe_ausgaben = sum(m['ausgaben_summe'] for m in monats_daten)
    monatliches_mittel_ausgaben = jahres_summe_ausgaben / 12
    
    # Jahres-Mittelwert der Einnahmen
    jahres_summe_einnahmen = sum(m['einnahmen_summe'] for m in monats_daten)
    monatliches_mittel_einnahmen = jahres_summe_einnahmen / 12
    
    # Virtuellen Soll-Kontostand berechnen
    kumulierter_saldo = 0
    for monat_daten in monats_daten:
        # Delta zum Monatsmittel berechnen
        monat_delta = (monatliches_mittel_ausgaben - monat_daten['ausgaben_summe']) + (monat_daten['einnahmen_summe'] - monatliches_mittel_einnahmen)
        
        # Kumulieren
        kumulierter_saldo += monat_delta
        
        # Zum Monatsdatensatz hinzufügen
        monat_daten['delta_zum_mittel'] = monat_delta
        monat_daten['virtueller_kontostand'] = kumulierter_saldo
    
    conn.close()
    
    return {
        'monats_daten': monats_daten,
        'jahres_summe_ausgaben': jahres_summe_ausgaben,
        'monatliches_mittel_ausgaben': monatliches_mittel_ausgaben,
        'jahres_summe_einnahmen': jahres_summe_einnahmen,
        'monatliches_mittel_einnahmen': monatliches_mittel_einnahmen
    }
