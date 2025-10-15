from models import Monatswert
from fastapi import FastAPI, HTTPException, Depends, Body
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
from fastapi.responses import JSONResponse

from fastapi.middleware.cors import CORSMiddleware
from crud import create_ungeplante_transaktion, get_ungeplante_transaktionen
from enum import Enum
from crud import berechne_soll_kontostaende_fuer_jahr, verify_jahresuebersicht_calculation



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
    enddatum: Optional[str] = None  # Optional mit Default None
    
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
            "INSERT INTO feste_ausgaben (beschreibung, betrag, kategorie, zahlungsintervall, zahlungsmonate, startdatum, enddatum) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING *;",
            (ausgabe.beschreibung, ausgabe.betrag, ausgabe.kategorie, ausgabe.zahlungsintervall, ausgabe.zahlungsmonate, ausgabe.startdatum, ausgabe.enddatum),
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
                zahlungsintervall = %s, zahlungsmonate = %s, startdatum = %s, enddatum = %s
            WHERE id = %s
            RETURNING *;
            """,
            (ausgabe.beschreibung, ausgabe.betrag, ausgabe.kategorie, ausgabe.zahlungsintervall, 
             ausgabe.zahlungsmonate, ausgabe.startdatum, ausgabe.enddatum, ausgabe_id),
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
        VALUES (%s, %s, %s, %s) RETURNING id
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

    # Datum für den angegebenen Monat und Jahr erstellen
    erster_des_monats = f"{jahr}-{monat:02d}-01"
    
    # Abfrage der festen Ausgaben für den Monat mit Berücksichtigung von Start- und Enddatum
    cur.execute("""
        SELECT * FROM feste_ausgaben
        WHERE %s = ANY(zahlungsmonate)
        AND (startdatum IS NULL OR startdatum <= %s)
        AND (enddatum IS NULL OR enddatum >= %s)
        """, (monat, erster_des_monats, erster_des_monats))

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

    # Konvertiere alle feste_ausgaben zu Dictionaries, um Modifikationen zu erlauben
    feste_ausgaben = [dict(row) for row in feste_ausgaben]
    
    # Umwandeln von datetime und date Objekten in String (ISO 8601 Format)
    for ausgabe in feste_ausgaben:
        if ausgabe['startdatum']:
            ausgabe['startdatum'] = ausgabe['startdatum'].isoformat()
        if ausgabe['enddatum']:
            ausgabe['enddatum'] = ausgabe['enddatum'].isoformat()
            
    # Konvertiere ungeplante_ausgaben zu Dictionaries für Modifikationen
    ungeplante_ausgaben = [dict(row) for row in ungeplante_ausgaben]
    for ausgabe in ungeplante_ausgaben:
        if ausgabe['datum']:
            ausgabe['datum'] = ausgabe['datum'].isoformat()
        if ausgabe['erstellt_am']:
            ausgabe['erstellt_am'] = ausgabe['erstellt_am'].isoformat()

    # Konvertiere ungeplante_einnahmen zu Dictionaries für Modifikationen
    ungeplante_einnahmen = [dict(row) for row in ungeplante_einnahmen]
    for einnahme in ungeplante_einnahmen:
        if einnahme['datum']:
            einnahme['datum'] = einnahme['datum'].isoformat()
        if einnahme['erstellt_am']:
            einnahme['erstellt_am'] = einnahme['erstellt_am'].isoformat()

    conn.close()

    # Monatsübersicht zurückgeben
    return {
        "monat": monat,
        "jahr": jahr,
        "feste_ausgaben": feste_ausgaben,
        "feste_einnahmen": feste_einnahmen,
        "ungeplante_ausgaben": ungeplante_ausgaben,
        "ungeplante_einnahmen": ungeplante_einnahmen,
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
def get_jahresuebersicht(jahr: int, db=Depends(get_db)):
    """
    Liefert eine vollständige Jahresübersicht für das angegebene Jahr:
    - Einnahmen & Ausgaben (mit Änderungen)
    - Kategorie 'Andrea' wird ignoriert
    - Monatliches Mittel ohne Andrea
    - Delta zum Mittel, kumulativ Soll-Kontostand, virtueller Kontostand
    - Enthält zusätzlich monats_daten mit allen Posten
    """
    try:
       # 1️⃣ Jahresdurchschnitt (ohne Andrea) einmalig holen
        mittelwert = float(crud.get_monatliches_mittel_feste_ausgaben_ohne_andrea(db, jahr) or 0)
        print(f"📊 Mittelwert feste Ausgaben (ohne Andrea) für {jahr}: {mittelwert:.2f} €")

        # --- 2️⃣ Monatsweise Berechnung aller Kennzahlen ---
        ergebnisse = []
        virtueller_kontostand = 0.0
        kumulatives_delta = 0.0

        for monat in range(1, 13):
            ausgaben = float(crud.get_feste_ausgaben_monat_jahresuebersicht(db, jahr, monat) or 0)
            einnahmen = float(crud.get_feste_einnahmen_monat_jahresuebersicht(db, jahr, monat) or 0)
            #  mittel_ausgaben = float(mittel_ausgaben or 0)

            saldo = einnahmen - ausgaben
            virtueller_kontostand += saldo

            # Delta zum Mittel: Wie stark weichen die Ausgaben vom Durchschnitt ab?
            delta_mittel = ausgaben - mittelwert

            # Soll-Kontostand: kumulierte Abweichung über das Jahr
            kumulatives_delta += delta_mittel
# --- 🧾 Debug-Log ---
            print(
                f"[{jahr}-{monat:02d}] "
                f"Ausgaben={ausgaben:.2f} €, Mittel={mittelwert:.2f} €, "
                f"Δ={delta_mittel:.2f} €, Kumuliert={kumulatives_delta:.2f}, "
                f"Einnahmen={einnahmen:.2f} €, Saldo={saldo:.2f}, "
                f"Virtuell={virtueller_kontostand:.2f}"
            )

            ergebnisse.append({
                "monat": monat,
                "ausgaben": round(ausgaben, 2),
                "einnahmen": round(einnahmen, 2),
                "saldo": round(saldo, 2),
                "virtueller_kontostand": round(virtueller_kontostand, 2),
                "delta_mittel": round(delta_mittel, 2),
                "soll_kontostand": round(kumulatives_delta, 2)
            })

        # --- 3️⃣ Detaildaten (monats_daten) aufbauen ---
        monats_daten = []
        for monat in range(1, 13):
            # Feste Ausgaben inkl. Änderungen
            ausgaben_query = db.execute(text("""
                SELECT 
                    fa.id, fa.beschreibung, 
                    COALESCE(
                        (SELECT betrag 
                         FROM ausgaben_aenderungen aa
                         WHERE aa.ausgabe_id = fa.id
                           AND aa.gueltig_ab <= :datum
                         ORDER BY aa.gueltig_ab DESC
                         LIMIT 1),
                        fa.betrag
                    ) AS betrag,
                    fa.kategorie
                FROM feste_ausgaben fa
                WHERE (fa.kategorie IS NULL OR LOWER(fa.kategorie) NOT LIKE '%andrea%')
                  AND (fa.startdatum IS NULL OR fa.startdatum <= :datum)
                  AND (fa.enddatum IS NULL OR fa.enddatum >= :datum)
                  AND :monat = ANY(fa.zahlungsmonate)
                ORDER BY fa.kategorie, fa.beschreibung
            """), {"datum": date(jahr, monat, 1), "monat": monat})

            ausgaben = [
                {
                    "id": row.id,
                    "beschreibung": row.beschreibung,
                    "betrag": float(row.betrag),
                    "kategorie": row.kategorie
                }
                for row in ausgaben_query
            ]

            # Feste Einnahmen inkl. Änderungen (ohne Andrea)
            einnahmen_query = db.execute(text("""
                SELECT 
                    fe.id,
                    fe.name AS beschreibung,  -- alias, damit Frontend-Feld gleich bleibt
                    COALESCE(
                        (SELECT betrag 
                         FROM einnahmen_aenderungen ea
                         WHERE ea.einnahme_id = fe.id
                           AND ea.gueltig_ab <= :datum
                         ORDER BY ea.gueltig_ab DESC
                        LIMIT 1),
                       fe.betrag
                    ) AS betrag,
                    fe.kategorie
                FROM feste_einnahmen fe
                WHERE :monat = ANY(fe.zahlungsmonate)
                  AND (fe.kategorie IS NULL OR LOWER(fe.kategorie) NOT LIKE '%andrea%')
                  AND (fe.startdatum IS NULL OR fe.startdatum <= :datum)
                  AND (fe.enddatum IS NULL OR fe.enddatum >= :datum)
                ORDER BY fe.kategorie, fe.name
            """), {"datum": date(jahr, monat, 1), "monat": monat})


            einnahmen = [
                {
                    "id": row.id,
                    "beschreibung": row.beschreibung,
                    "betrag": float(row.betrag),
                    "kategorie": row.kategorie
                }
                for row in einnahmen_query
            ]

            monats_daten.append({
                "monat": monat,
                "ausgaben": ausgaben,
                "einnahmen": einnahmen
            })

        # --- 4️⃣ Rückgabe ---
        return {
            "jahr": jahr,
            "monatliches_mittel_ausgaben_ohne_andrea": round(mittelwert, 2),
            "monate": ergebnisse,
            "monats_daten": monats_daten
        }

    except Exception as e:
        print("❌ Fehler in /jahresuebersicht:", e)
        return JSONResponse(
            status_code=500,
            content={
                "error": "Fehler bei der Berechnung der Jahresübersicht",
                "details": str(e)
            }
        )
    
@app.get("/soll-kontostaende/{jahr}")
def get_soll_kontostaende_jahr(jahr: int):
    """
    Hole alle Soll-Kontostände für ein Jahr
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, jahr, monat, kontostand_soll, created_at, updated_at 
        FROM kontostand_monatsende_soll 
        WHERE jahr = %s 
        ORDER BY monat
    """, (jahr,))
    kontostaende = cur.fetchall()
    conn.close()
    return kontostaende

@app.get("/soll-kontostaende/{jahr}/{monat}")
def get_soll_kontostand_monat(jahr: int, monat: int):
    """
    Hole Soll-Kontostand für einen spezifischen Monat
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, jahr, monat, kontostand_soll, created_at, updated_at 
        FROM kontostand_monatsende_soll 
        WHERE jahr = %s AND monat = %s
    """, (jahr, monat))
    kontostand = cur.fetchone()
    conn.close()
    
    if not kontostand:
        raise HTTPException(status_code=404, detail="Soll-Kontostand nicht gefunden")
    
    return kontostand

@app.post("/soll-kontostaende/berechnen/{jahr}")
def berechne_und_speichere_soll_kontostaende(jahr: int):
    """
    Berechnet und speichert alle Soll-Kontostände für ein Jahr neu
    """
    try:
        conn = get_db_connection()
        
        # Berechne die Soll-Kontostände
        soll_kontostaende = berechne_soll_kontostaende_fuer_jahr(conn, jahr)
        
        # 🔎 Debug-Ausgabe zum Vergleich mit Vue
        print("\n=== DEBUG: Soll-Kontostände Backend-Berechnung ===")
        verify_jahresuebersicht_calculation(conn, jahr)
        print("=== ENDE DEBUG ===\n")

        cur = conn.cursor()
        
        for monat, kontostand in enumerate(soll_kontostaende, 1):
            # Prüfe ob Eintrag bereits existiert
            cur.execute("""
                SELECT id FROM kontostand_monatsende_soll 
                WHERE jahr = %s AND monat = %s
            """, (jahr, monat))
            existing = cur.fetchone()
            
            if existing:
                # Update existierenden Eintrag
                cur.execute("""
                    UPDATE kontostand_monatsende_soll 
                    SET kontostand_soll = %s, updated_at = CURRENT_TIMESTAMP 
                    WHERE jahr = %s AND monat = %s
                """, (float(kontostand), jahr, monat))
            else:
                # Erstelle neuen Eintrag
                cur.execute("""
                    INSERT INTO kontostand_monatsende_soll (jahr, monat, kontostand_soll) 
                    VALUES (%s, %s, %s)
                """, (jahr, monat, float(kontostand)))
        
        conn.commit()
        conn.close()
        
        return {"message": f"Soll-Kontostände für {jahr} erfolgreich berechnet und gespeichert"}
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        raise HTTPException(status_code=500, detail=f"Fehler beim Berechnen: {str(e)}")

@app.put("/soll-kontostaende/{jahr}/{monat}")
def update_soll_kontostand(jahr: int, monat: int, kontostand_data: dict):
    """
    Manuelles Update eines Soll-Kontostands
    """
    kontostand_soll = kontostand_data.get("kontostand_soll")
    if kontostand_soll is None:
        raise HTTPException(status_code=400, detail="kontostand_soll ist erforderlich")
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Prüfe ob Eintrag existiert
    cur.execute("""
        SELECT id FROM kontostand_monatsende_soll 
        WHERE jahr = %s AND monat = %s
    """, (jahr, monat))
    existing = cur.fetchone()
    
    if existing:
        # Update existierenden Eintrag
        cur.execute("""
            UPDATE kontostand_monatsende_soll 
            SET kontostand_soll = %s, updated_at = CURRENT_TIMESTAMP 
            WHERE jahr = %s AND monat = %s
        """, (float(kontostand_soll), jahr, monat))
    else:
        # Erstelle neuen Eintrag
        cur.execute("""
            INSERT INTO kontostand_monatsende_soll (jahr, monat, kontostand_soll) 
            VALUES (%s, %s, %s)
        """, (jahr, monat, float(kontostand_soll)))
    
    conn.commit()
    
    # Hole den aktualisierten/erstellten Eintrag
    cur.execute("""
        SELECT id, jahr, monat, kontostand_soll, created_at, updated_at 
        FROM kontostand_monatsende_soll 
        WHERE jahr = %s AND monat = %s
    """, (jahr, monat))
    result = cur.fetchone()
    
    conn.close()
    return result
    
@app.post("/kontostand-ist")
def save_ist_kontostand(payload: dict = Body(...), db: Session = Depends(get_db)):
        return crud.save_ist_kontostand(db, payload)

@app.get("/kontostand-ist/{jahr}/{monat}")
def get_ist_kontostand(jahr: int, monat: int, db: Session = Depends(get_db)):
        return crud.get_ist_kontostand(db, jahr, monat)
        
# Ausgaben-Änderungen
@app.post("/feste-ausgaben/{ausgabe_id}/aenderungen", response_model=schemas.AusgabeAenderung)
def add_ausgabe_aenderung(ausgabe_id: int, aenderung: schemas.AusgabeAenderungCreate, db=Depends(get_db)):
    return crud.create_ausgabe_aenderung(db, ausgabe_id, aenderung)

@app.get("/feste-ausgaben/{ausgabe_id}/aenderungen", response_model=list[schemas.AusgabeAenderung])
def list_ausgabe_aenderungen(ausgabe_id: int, db=Depends(get_db)):
    return crud.get_ausgabe_aenderungen(db, ausgabe_id)

# Einnahmen-Änderungen
@app.post("/feste-einnahmen/{einnahme_id}/aenderungen", response_model=schemas.EinnahmeAenderung)
def add_einnahme_aenderung(einnahme_id: int, aenderung: schemas.EinnahmeAenderungCreate, db=Depends(get_db)):
    return crud.create_einnahme_aenderung(db, einnahme_id, aenderung)

@app.get("/feste-einnahmen/{einnahme_id}/aenderungen", response_model=list[schemas.EinnahmeAenderung])
def list_einnahme_aenderungen(einnahme_id: int, db=Depends(get_db)):
    return crud.get_einnahme_aenderungen(db, einnahme_id)
    