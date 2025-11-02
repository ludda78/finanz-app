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
    startdatum: date
    enddatum: Optional[date] = None  # Optional mit Default None
    
class FesteEinnahme(BaseModel):
    id: Optional[int] = None
    name: str
    betrag: float
    kategorie: Optional[str] = None  # New field
    zahlungsmonate: List[int]
    startdatum: Optional[date] = None
    enddatum: Optional[date] = None

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
    
def get_db_psycopg():
    conn = get_db_connection()  # <- deine Funktion, die psycopg2.connect(...) zurückgibt
    try:
        yield conn
    finally:
        conn.close()
        
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
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("""
            UPDATE feste_ausgaben
            SET 
                beschreibung = %s,
                betrag = %s,
                kategorie = %s,
                zahlungsintervall = %s,
                zahlungsmonate = %s,
                startdatum = %s,
                enddatum = %s
            WHERE id = %s
            RETURNING id, beschreibung, betrag, kategorie, zahlungsintervall, zahlungsmonate, startdatum, enddatum, erstellt_am;
        """, (
            ausgabe.beschreibung,
            ausgabe.betrag,
            ausgabe.kategorie,
            ausgabe.zahlungsintervall,
            ausgabe.zahlungsmonate,
            ausgabe.startdatum,
            ausgabe.enddatum,  # ✅ optional möglich
            ausgabe_id
        ))
        updated_ausgabe = cur.fetchone()
        conn.commit()

        if not updated_ausgabe:
            raise HTTPException(status_code=404, detail="Ausgabe nicht gefunden")

        return dict(updated_ausgabe)

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Fehler beim Aktualisieren: {e}")

    finally:
        conn.close()

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
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT id, name, betrag, kategorie, zahlungsmonate, startdatum, enddatum
          FROM feste_einnahmen
        ORDER BY id;
    """)
    rows = [dict(r) for r in cur.fetchall()]
    for r in rows:
        r["betrag"] = float(r["betrag"])
        if r.get("startdatum"): r["startdatum"] = r["startdatum"].isoformat()
        if r.get("enddatum"):   r["enddatum"]   = r["enddatum"].isoformat()
    conn.close()
    return {"feste_einnahmen": rows}

@app.post("/feste_einnahmen/")
def add_feste_einnahme(einnahme: FesteEinnahme):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        betrag = float(einnahme.betrag)
        monate = [int(m) for m in (einnahme.zahlungsmonate or [])]
        start = einnahme.startdatum
        ende = einnahme.enddatum

        cur.execute("""
            INSERT INTO feste_einnahmen
                (name, betrag, kategorie, zahlungsmonate, startdatum, enddatum)
            VALUES (%s,   %s,     %s,        %s,             %s,        %s)
            RETURNING id;
        """, (einnahme.name, betrag, einnahme.kategorie, monate, start, ende))
        new_id = cur.fetchone()["id"]
        conn.commit()
        return {"message": "Einnahme hinzugefügt", "id": new_id}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Insert fehlgeschlagen: {e}")
    finally:
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
         # Typen sicherstellen
        betrag = float(einnahme.betrag)
        monate = [int(m) for m in (einnahme.zahlungsmonate or [])]
        start = einnahme.startdatum  # schon date durch Pydantic
        ende = einnahme.enddatum     # schon date durch Pydantic
        
        cur.execute(
            """
            UPDATE feste_einnahmen
               SET name = %s,
                   betrag = %s,
                   kategorie = %s,
                   zahlungsmonate = %s,
                   startdatum = %s,
                   enddatum = %s
             WHERE id = %s
         RETURNING *;
            """,
            (einnahme.name, betrag, einnahme.kategorie, monate, start, ende, einnahme_id),
        )
        updated = cur.fetchone()
        conn.commit()
        if not updated:
            raise HTTPException(status_code=404, detail="Einnahme nicht gefunden")
        return {"message": "OK"}
    except Exception as e:
        conn.rollback()
        # wichtig: nicht „roh“ zurückgeben, sondern klar
        raise HTTPException(status_code=400, detail=f"Update fehlgeschlagen: {e}")
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

@app.get("/monatsuebersicht/{monat}/{jahr}", response_model=schemas.MonatsuebersichtResponse)
def get_monatsuebersicht(monat: int, jahr: int, db: Session = Depends(get_db)):
    stichtag = date(jahr, monat, 1)

    # Feste AUSGABEN (ohne Andrea) mit effektivem Betrag
    ausgaben_sql = text("""
        SELECT
            fa.id,
            fa.beschreibung,
            COALESCE((
                SELECT aa.betrag
                  FROM ausgaben_aenderungen aa
                 WHERE aa.ausgabe_id = fa.id
                   AND aa.gueltig_ab <= :stichtag
              ORDER BY aa.gueltig_ab DESC
                 LIMIT 1
            ), fa.betrag) AS betrag,
            fa.kategorie,
            fa.zahlungsintervall,
            fa.zahlungsmonate,
            fa.startdatum,
            fa.enddatum,
            fa.erstellt_am::date AS erstellt_am
        FROM feste_ausgaben fa
        WHERE :monat = ANY(fa.zahlungsmonate)
          AND (fa.startdatum IS NULL OR fa.startdatum <= :stichtag)
          AND (fa.enddatum   IS NULL OR fa.enddatum   >= :stichtag)
        ORDER BY lower(fa.beschreibung)
    """)
    ausgaben_rows = db.execute(ausgaben_sql, {"stichtag": stichtag, "monat": monat}).fetchall()
    feste_ausgaben = [dict(r._mapping) for r in ausgaben_rows]

    # ---- Dynamisch feststellen, wie das "Beschreibung"-Feld bei feste_einnahmen heißt ----
    # ---- Spalten von feste_einnahmen ermitteln ----
    cols = db.execute(text("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'feste_einnahmen'
    """)).fetchall()
    colnames = {r[0] for r in cols}

    # Feld für "Beschreibung" finden (oder Fallback)
    candidates = ["beschreibung", "name", "titel", "bezeichnung", "quelle"]
    label_col = next((c for c in candidates if c in colnames), None)
    if label_col:
        label_select = f"fe.{label_col} AS beschreibung"
        order_by = f"ORDER BY lower(fe.{label_col})"
    else:
        label_select = "('Einnahme #' || fe.id)::text AS beschreibung"
        order_by = "ORDER BY fe.id"

    # Select-Liste nur mit existierenden Spalten zusammenstellen
    select_parts = [
        "fe.id",
        label_select,
        "COALESCE((SELECT ea.betrag FROM einnahmen_aenderungen ea "
        "          WHERE ea.einnahme_id = fe.id AND ea.gueltig_ab <= :stichtag "
        "          ORDER BY ea.gueltig_ab DESC LIMIT 1), fe.betrag) AS betrag"
    ]

    # optionale Spalten:
    for opt in ["kategorie", "zahlungsintervall", "zahlungsmonate", "startdatum", "enddatum"]:
        if opt in colnames:
            select_parts.append(f"fe.{opt}")

    # erstellt_am speziell: falls vorhanden -> ::date, sonst NULL::date alias
    if "erstellt_am" in colnames:
        select_parts.append("fe.erstellt_am::date AS erstellt_am")
    else:
        select_parts.append("NULL::date AS erstellt_am")

    # WHERE-Bedingungen ebenfalls nur hinzufügen, wenn Spalte existiert:
    where_parts = []
    if "zahlungsmonate" in colnames:
        where_parts.append(":monat = ANY(fe.zahlungsmonate)")
    if "startdatum" in colnames:
        where_parts.append("(fe.startdatum IS NULL OR fe.startdatum <= :stichtag)")
    if "enddatum" in colnames:
        where_parts.append("(fe.enddatum IS NULL OR fe.enddatum >= :stichtag)")

    # Falls es eine der Spalten nicht gibt, wenigstens nicht an ihr filtern
    where_sql = " AND ".join(where_parts) if where_parts else "TRUE"

    # Finale SQL
    einnahmen_sql = text(f"""
        SELECT {", ".join(select_parts)}
        FROM feste_einnahmen fe
        WHERE {where_sql}
        {order_by}
    """)

    einnahmen_rows = db.execute(einnahmen_sql, {"stichtag": stichtag, "monat": monat}).fetchall()
    feste_einnahmen = [dict(r._mapping) for r in einnahmen_rows]

    # Ungeplante AUSGABEN/EINNAHMEN
    ungepl_ausg_sql = text("""
        SELECT id, beschreibung, betrag, kategorie, datum, erstellt_am::date AS erstellt_am
FROM ungeplante_ausgaben
         WHERE EXTRACT(MONTH FROM datum) = :monat
           AND EXTRACT(YEAR  FROM datum) = :jahr
         ORDER BY datum, id
    """)
    ungepl_einn_sql = text("""
        SELECT id, beschreibung, betrag, datum, erstellt_am::date AS erstellt_am
        FROM ungeplante_einnahmen
         WHERE EXTRACT(MONTH FROM datum) = :monat
           AND EXTRACT(YEAR  FROM datum) = :jahr
         ORDER BY datum, id
    """)
    ungeplante_ausgaben = [dict(r._mapping) for r in db.execute(ungepl_ausg_sql, {"monat": monat, "jahr": jahr}).fetchall()]
    ungeplante_einnahmen = [dict(r._mapping) for r in db.execute(ungepl_einn_sql, {"monat": monat, "jahr": jahr}).fetchall()]

    # Summen
    gesamt_ausgaben = float(
        sum(float(x["betrag"] or 0) for x in feste_ausgaben) +
        sum(float(x["betrag"] or 0) for x in ungeplante_ausgaben)
    )
    gesamt_einnahmen = float(
        sum(float(x["betrag"] or 0) for x in feste_einnahmen) +
        sum(float(x["betrag"] or 0) for x in ungeplante_einnahmen)
    )

    return {
        "monat": monat,
        "jahr": jahr,
        "feste_ausgaben": feste_ausgaben,
        "ungeplante_ausgaben": ungeplante_ausgaben,
        "ungeplante_einnahmen": ungeplante_einnahmen,
        "feste_einnahmen": feste_einnahmen,
        "gesamt_ausgaben": gesamt_ausgaben,
        "gesamt_einnahmen": gesamt_einnahmen,
    }


@app.get("/monatswerte/{monat}/{jahr}")
def get_monatswerte(monat: int, jahr: int, db: Session = Depends(get_db)):
    # Sichere, parametrisierte Test-Query (optional)
    result = db.execute(
        text("SELECT * FROM monatswerte WHERE monat = :m AND jahr = :j"),
        {"m": monat, "j": jahr},
    ).fetchall()

    # ORM-Query
    werte = (
        db.query(Monatswert)
        .filter(Monatswert.monat == monat, Monatswert.jahr == jahr)
        .all()
    )

    response = {
        "monatswerte": [
            {"kategorie": w.kategorie, "eintrag_id": w.eintrag_id, "ist": w.ist}
            for w in werte
        ]
    }
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
        # print(f"📊 Mittelwert feste Ausgaben (ohne Andrea) für {jahr}: {mittelwert:.2f} €")

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
            delta_mittel = mittelwert - ausgaben

            # Soll-Kontostand: kumulierte Abweichung über das Jahr
            kumulatives_delta += delta_mittel
# --- 🧾 Debug-Log ---
            # print(
                # f"[{jahr}-{monat:02d}] "
                # f"Ausgaben={ausgaben:.2f} €, Mittel={mittelwert:.2f} €, "
                # f"Δ={delta_mittel:.2f} €, Kumuliert={kumulatives_delta:.2f}, "
                # f"Einnahmen={einnahmen:.2f} €, Saldo={saldo:.2f}, "
                # f"Virtuell={virtueller_kontostand:.2f}"
            # )

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
                WHERE (fa.startdatum IS NULL OR fa.startdatum <= :datum)
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
def get_soll_kontostaende_jahr(jahr: int, db: Session = Depends(get_db)):
    """
    Hole alle Soll-Kontostände für ein Jahr (sortiert nach Monat)
    """
    result = db.execute(
        text("""
            SELECT id, jahr, monat, kontostand_soll, created_at, updated_at
            FROM kontostand_monatsende_soll
            WHERE jahr = :jahr
            ORDER BY monat
        """),
        {"jahr": jahr}
    ).fetchall()

    # SQLAlchemy liefert Row-Objekte zurück → in Dicts umwandeln
    kontostaende = [
        {
            "id": row.id,
            "jahr": row.jahr,
            "monat": row.monat,
            "kontostand_soll": float(row.kontostand_soll),
            "created_at": row.created_at,
            "updated_at": row.updated_at,
        }
        for row in result
    ]

    return kontostaende


@app.get("/soll-kontostaende/{jahr}/{monat}")
def get_soll_kontostand_monat(jahr: int, monat: int, db: Session = Depends(get_db)):
    """
    Hole Soll-Kontostand für einen spezifischen Monat
    """
    row = db.execute(
        text("""
            SELECT id, jahr, monat, kontostand_soll, created_at, updated_at
            FROM kontostand_monatsende_soll
            WHERE jahr = :jahr AND monat = :monat
        """),
        {"jahr": jahr, "monat": monat}
    ).fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Soll-Kontostand nicht gefunden")

    return {
        "id": row.id,
        "jahr": row.jahr,
        "monat": row.monat,
        "kontostand_soll": float(row.kontostand_soll),
        "created_at": row.created_at,
        "updated_at": row.updated_at,
    }

@app.post("/soll-kontostaende/berechnen/{jahr}")
def berechne_und_speichere_soll_kontostaende(jahr: int, db: Session = Depends(get_db)):
    """
    Berechnet und speichert alle Soll-Kontostände für ein Jahr neu.
    Nutzt SQLAlchemy Session statt roher psycopg2-Connection.
    """
    try:
        # 1️⃣ Berechne Soll-Kontostände (Liste mit 12 Monatswerten)
        soll_kontostaende = berechne_soll_kontostaende_fuer_jahr(db, jahr)

        # 2️⃣ Iteriere über die Ergebnisse und schreibe sie in die DB
        for eintrag in soll_kontostaende:
            monat = eintrag["monat"]
            kontostand = float(eintrag["soll_kontostand"])

            # Prüfe, ob Eintrag existiert
            existing = db.execute(
                text("""
                    SELECT id FROM kontostand_monatsende_soll
                    WHERE jahr = :jahr AND monat = :monat
                """),
                {"jahr": jahr, "monat": monat}
            ).fetchone()

            if existing:
                db.execute(
                    text("""
                        UPDATE kontostand_monatsende_soll
                        SET kontostand_soll = :kontostand,
                            updated_at = :now
                        WHERE jahr = :jahr AND monat = :monat
                    """),
                    {"kontostand": kontostand, "jahr": jahr, "monat": monat, "now": datetime.utcnow()}
                )
            else:
                db.execute(
                    text("""
                        INSERT INTO kontostand_monatsende_soll (jahr, monat, kontostand_soll)
                        VALUES (:jahr, :monat, :kontostand)
                    """),
                    {"jahr": jahr, "monat": monat, "kontostand": kontostand}
                )

        # 3️⃣ Commit durchführen
        db.commit()

        return {"message": f"Soll-Kontostände für {jahr} erfolgreich berechnet und gespeichert"}

    except Exception as e:
        db.rollback()
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
def add_ausgabe_aenderung(ausgabe_id: int,
                          aenderung: schemas.AusgabeAenderungCreate,
                          db: Session = Depends(get_db)):
    return crud.create_ausgabe_aenderung(db, ausgabe_id, aenderung)

@app.get("/feste-ausgaben/{ausgabe_id}/aenderungen", response_model=list[schemas.AusgabeAenderung])
def list_ausgabe_aenderungen(ausgabe_id: int,
                             db: Session = Depends(get_db)):
    return crud.get_ausgabe_aenderungen(db, ausgabe_id)

# Einnahmen-Änderungen
@app.post("/feste-einnahmen/{einnahme_id}/aenderungen", response_model=schemas.EinnahmeAenderung)
def add_einnahme_aenderung(einnahme_id: int,
                           aenderung: schemas.EinnahmeAenderungCreate,
                           db: Session = Depends(get_db)):
    return crud.create_einnahme_aenderung(db, einnahme_id, aenderung)

@app.get("/feste-einnahmen/{einnahme_id}/aenderungen", response_model=list[schemas.EinnahmeAenderung])
def list_einnahme_aenderungen(einnahme_id: int,
                              db: Session = Depends(get_db)):
    return crud.get_einnahme_aenderungen(db, einnahme_id)

@app.get("/feste-ausgaben/{ausgabe_id}/effektiv-im-monat")
def ausgabe_effektiv_im_monat(ausgabe_id: int, jahr: int, monat: int,
                              db: Session = Depends(get_db)):
    # Falls du die Hilfsfunktionen in crud belassen hast:
    from crud import effektiv_ausgabe_im_monat
    return {
        "ausgabe_id": ausgabe_id, "jahr": jahr, "monat": monat,
        "betrag": effektiv_ausgabe_im_monat(db, ausgabe_id, jahr, monat)
    }

@app.get("/feste-einnahmen/{einnahme_id}/effektiv-im-monat")
def einnahme_effektiv_im_monat(einnahme_id: int, jahr: int, monat: int,
                               db: Session = Depends(get_db)):
    from crud import effektiv_einnahme_im_monat
    return {
        "einnahme_id": einnahme_id, "jahr": jahr, "monat": monat,
        "betrag": effektiv_einnahme_im_monat(db, einnahme_id, jahr, monat)
    }

@app.get("/feste-ausgaben/monats-summen")
def get_ausgaben_monatssummen(jahr: int, db: Session = Depends(get_db)):
    return crud.ausgaben_monatssummen(db, jahr)

@app.get("/feste-einnahmen/monats-summen")
def get_einnahmen_monatssummen(jahr: int, db: Session = Depends(get_db)):
    return crud.einnahmen_monatssummen(db, jahr)

@app.patch("/feste-ausgaben/aenderungen/{aenderung_id}", response_model=schemas.AusgabeAenderung)
def patch_ausgabe_aenderung(aenderung_id: int,
                            body: schemas.AusgabeAenderungUpdate,
                            db: Session = Depends(get_db)):
    return crud.update_ausgabe_aenderung(db, aenderung_id, body)

@app.delete("/feste-ausgaben/aenderungen/{aenderung_id}")
def del_ausgabe_aenderung(aenderung_id: int, db: Session = Depends(get_db)):
    return crud.delete_ausgabe_aenderung(db, aenderung_id)

@app.patch("/feste-einnahmen/aenderungen/{aenderung_id}", response_model=schemas.EinnahmeAenderung)
def patch_einnahme_aenderung(aenderung_id: int,
                             body: schemas.EinnahmeAenderungUpdate,
                             db: Session = Depends(get_db)):
    return crud.update_einnahme_aenderung(db, aenderung_id, body)

@app.delete("/feste-einnahmen/aenderungen/{aenderung_id}")
def del_einnahme_aenderung(aenderung_id: int, db: Session = Depends(get_db)):
    return crud.delete_einnahme_aenderung(db, aenderung_id)

@app.get("/feste-ausgaben/{ausgabe_id}/timeline")
def get_timeline_ausgabe(ausgabe_id: int, jahr: int, db: Session = Depends(get_db)):
    return crud.timeline_ausgabe(db, ausgabe_id, jahr)

@app.get("/feste-einnahmen/{einnahme_id}/timeline")
def get_timeline_einnahme(einnahme_id: int, jahr: int, db: Session = Depends(get_db)):
    return crud.timeline_einnahme(db, einnahme_id, jahr)