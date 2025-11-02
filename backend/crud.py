from datetime import date, datetime
from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
import models
import schemas


DEBUG = False  # zentraler Schalter


def debug_alle_kategorien(db: Session):
    if not DEBUG:
        return
    try:
        res = db.execute(text("SELECT DISTINCT kategorie FROM feste_ausgaben ORDER BY kategorie"))
        print("\n=== DEBUG: Alle Kategorien in feste_ausgaben ===")
        for row in res.fetchall():
            value = row._mapping["kategorie"]
            if value is None:
                print("NULL / None")
            else:
                print(f"'{value}' (clean: '{str(value).strip().lower()}')")
        print("=== ENDE DEBUG ===\n")
    except Exception as e:
        print(f"Fehler beim Debuggen der Kategorien: {e}")



    
def create_ungeplante_transaktion(db: Session, transaktion: schemas.UngeplantTransaktionCreate):
    db_transaktion = models.UngeplantTransaktion(
        typ=transaktion.typ,
        beschreibung=transaktion.beschreibung,
        betrag=transaktion.betrag,
        kommentar=transaktion.kommentar,
        monat=transaktion.monat,
        jahr=transaktion.jahr,
        datum=transaktion.datum or datetime.now(),
        status=transaktion.status or "kein_ausgleich",
    )
    db.add(db_transaktion)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(db_transaktion)
    return db_transaktion


def get_ungeplante_transaktionen(db: Session, monat: int, jahr: int):
    return (
        db.query(models.UngeplantTransaktion)
        .filter(models.UngeplantTransaktion.monat == monat, models.UngeplantTransaktion.jahr == jahr)
        .all()
    )

def berechne_soll_kontostaende_fuer_jahr(db: Session, jahr: int):
    """
    Berechnet mehrere Kennzahlen:
    - Summe Ausgaben / Einnahmen
    - Monatssaldo (Ein - Aus)
    - Virtueller Kontostand (kumulativ)
    - Delta zum Ausgaben-Mittel
    - Kontostand Monatsende Soll
    """
    monatliches_mittel_ausgaben = get_monatliches_mittel_feste_ausgaben_ohne_andrea(db, jahr)

    if DEBUG:
        print(f"\n=== DEBUG: Berechne Soll-Kontostände für {jahr} ===")
        print(f"Monatliches Mittel (ohne Andrea): {monatliches_mittel_ausgaben:.2f} €")
        print(f"\n{'Monat':<6} {'Einnahmen':<12} {'Ausgaben':<12} "
              f"{'Saldo':<12} {'Virtuell':<12} {'DeltaMittel':<12} {'SollKto':<12}")
        print("-" * 80)

    ergebnisse = []
    virtueller_kontostand = 0
    kumulatives_delta = 0  # für Soll-Kontostand

    for monat in range(1, 13):
        ausgaben = get_feste_ausgaben_monat_jahresuebersicht(db, jahr, monat)
        einnahmen = get_feste_einnahmen_monat_jahresuebersicht(db, jahr, monat)

        saldo = einnahmen - ausgaben
        virtueller_kontostand += saldo

        # Abweichung vom Mittel
        delta_mittel = monatliches_mittel_ausgaben - ausgaben
        kumulatives_delta += delta_mittel

        ergebnisse.append({
            "monat": monat,
            "ausgaben": ausgaben,
            "einnahmen": einnahmen,
            "saldo": saldo,
            "virtueller_kontostand": virtueller_kontostand,
            "delta_mittel": delta_mittel,
            "soll_kontostand": kumulatives_delta
        })

        if DEBUG:
            print(f"{monat:<6} {einnahmen:<12.2f} {ausgaben:<12.2f} "
                  f"{saldo:<12.2f} {virtueller_kontostand:<12.2f} "
                  f"{delta_mittel:<12.2f} {kumulatives_delta:<12.2f}")

    if DEBUG:
        print("=== ENDE DEBUG Soll-Kontostände ===\n")

    return ergebnisse


def get_monatliches_mittel_feste_ausgaben_ohne_andrea(db, jahr: int) -> float:
    """
    Berechne den durchschnittlichen Monatswert der festen Ausgaben (ohne Andrea)
    über das gesamte Jahr.
    """
    try:
        gesamt = 0.0
        monate_mit_daten = 0

        for monat in range(1, 13):
            # Gesamt-Ausgaben dieses Monats berechnen (gleiche Logik wie in der Jahresübersicht)
            result = db.execute(text("""
                SELECT COALESCE(SUM(
                    COALESCE(
                        (SELECT betrag 
                         FROM ausgaben_aenderungen aa
                         WHERE aa.ausgabe_id = fa.id
                           AND aa.gueltig_ab <= :datum
                         ORDER BY aa.gueltig_ab DESC
                         LIMIT 1),
                        fa.betrag
                    )
                ), 0)
                FROM feste_ausgaben fa
                WHERE (fa.kategorie IS NULL OR LOWER(fa.kategorie) NOT LIKE '%andrea%')
                  AND (fa.startdatum IS NULL OR fa.startdatum <= :datum)
                  AND (fa.enddatum IS NULL OR fa.enddatum >= :datum)
                  AND :monat = ANY(fa.zahlungsmonate)
            """), {"datum": date(jahr, monat, 1), "monat": monat}).scalar()

            gesamt += float(result or 0)
            monate_mit_daten += 1

        if monate_mit_daten == 0:
            return 0.0

        mittelwert = gesamt / monate_mit_daten
        # print(f"🔹 Berechneter Monatsdurchschnitt (ohne Andrea) für {jahr}: {mittelwert:.2f} €")
        return mittelwert

    except Exception as e:
        print("❌ Fehler in get_monatliches_mittel_feste_ausgaben_ohne_andrea:", e)
        return 0.0


def update_feste_ausgabe(db: Session, ausgabe_id: int, daten: dict):
    stmt = text("""
        UPDATE feste_ausgaben
           SET beschreibung = :beschreibung,
               betrag = :betrag,
               kategorie = :kategorie,
               zahlungsintervall = :zahlungsintervall,
               zahlungsmonate = :zahlungsmonate,
               startdatum = :startdatum,
               enddatum = :enddatum
         WHERE id = :id
     RETURNING id, beschreibung, betrag, kategorie, zahlungsintervall, zahlungsmonate, startdatum, enddatum;
    """)
    params = {
        "beschreibung": daten["beschreibung"],
        "betrag": daten["betrag"],
        "kategorie": daten["kategorie"],
        "zahlungsintervall": daten.get("zahlungsintervall"),
        "zahlungsmonate": daten.get("zahlungsmonate"),
        "startdatum": daten["startdatum"],
        "enddatum": daten.get("enddatum"),
        "id": ausgabe_id,
    }
    try:
        row = db.execute(stmt, params).fetchone()
        db.commit()
    except Exception:
        db.rollback()
        raise
    return dict(row._mapping) if row else None


def insert_feste_ausgabe(db: Session, daten: dict):
    stmt = text("""
        INSERT INTO feste_ausgaben (
            beschreibung, betrag, kategorie, zahlungsintervall, zahlungsmonate, startdatum, enddatum, erstellt_am
        ) VALUES (
            :beschreibung, :betrag, :kategorie, :zahlungsintervall, :zahlungsmonate, :startdatum, :enddatum, :erstellt_am
        )
     RETURNING id, beschreibung, betrag, kategorie, zahlungsintervall, zahlungsmonate, startdatum, enddatum, erstellt_am;
    """)
    params = {
        "beschreibung": daten["beschreibung"],
        "betrag": daten["betrag"],
        "kategorie": daten["kategorie"],
        "zahlungsintervall": daten.get("zahlungsintervall"),
        "zahlungsmonate": daten.get("zahlungsmonate"),
        "startdatum": daten["startdatum"],
        "enddatum": daten.get("enddatum"),
        "erstellt_am": date.today(),
    }
    try:
        row = db.execute(stmt, params).fetchone()
        db.commit()
    except Exception:
        db.rollback()
        raise
    return dict(row._mapping) if row else None


def get_feste_ausgaben_monat_jahresuebersicht(db: Session, jahr: int, monat: int) -> float:
    monatsdatum = date(jahr, monat, 1)
    query = text("""
        SELECT SUM(
          COALESCE(
            (SELECT betrag
               FROM ausgaben_aenderungen aa
              WHERE aa.ausgabe_id = fa.id
                AND aa.gueltig_ab <= :datum
           ORDER BY aa.gueltig_ab DESC
              LIMIT 1),
            fa.betrag
          )
        ) AS summe
          FROM feste_ausgaben fa
         WHERE (fa.startdatum IS NULL OR fa.startdatum <= :datum)
           AND (fa.enddatum   IS NULL OR fa.enddatum   >= :datum)
           AND :monat = ANY(fa.zahlungsmonate)
           AND (fa.kategorie IS NULL OR LOWER(fa.kategorie) NOT LIKE '%andrea%')
    """)
    result = db.execute(query, {"datum": monatsdatum, "monat": monat}).scalar()
    return float(result or 0.0)




def verify_jahresuebersicht_calculation(conn, jahr):
    """
    Überprüfe die Berechnung - sollte mit deiner Jahresübersicht übereinstimmen
    """
    monatliches_mittel = get_monatliches_mittel_feste_ausgaben_ohne_andrea(conn, jahr)
   # print(f"Monatliches Mittel feste Ausgaben (ohne Andrea): {monatliches_mittel:.2f} €")
    
   # print(f"\n{'Monat':<6} {'Ausgaben':<10} {'Delta':<10} {'Kumulativ':<10}")
  #  print("-" * 40)
    
    kumulativ = 0
    for monat in range(1, 13):
        feste_ausgaben = get_feste_ausgaben_monat_jahresuebersicht(conn, jahr, monat)
        delta = monatliches_mittel - feste_ausgaben
        kumulativ += delta
      #  print(f"{monat:<6} {feste_ausgaben:<10.2f} {delta:<10.2f} {kumulativ:<10.2f}")
    
    return kumulativ

def get_jahresuebersicht_daten_zur_verifikation(conn, jahr):
    """
    Hole die gleichen Daten wie die Jahresübersicht zur Verifikation
    """
    # Alle festen Ausgaben abrufen (ohne Andrea)
    cur = conn.cursor()
    cur.execute("SELECT * FROM feste_ausgaben WHERE kategorie != %s", ('Andrea',))
    alle_ausgaben = cur.fetchall()
    alle_ausgaben = [dict(row) for row in alle_ausgaben]
    
    print("=== JAHRESÜBERSICHT DATEN (ohne Andrea) ===")
    
    monats_daten = []
    jahres_summe = 0
    
    for monat in range(1, 13):
        monat_summe = get_feste_ausgaben_monat_jahresuebersicht(conn, jahr, monat)
        jahres_summe += monat_summe
        monats_daten.append({
            'monat': monat,
            'ausgaben_summe': monat_summe
        })
        print(f"Monat {monat:2d}: {monat_summe:.2f} €")
    
    monatliches_mittel = jahres_summe / 12
    print(f"\nJahressumme: {jahres_summe:.2f} €")
    print(f"Monatsmittel: {monatliches_mittel:.2f} €")
    
    return monats_daten, jahres_summe, monatliches_mittel

def analyze_feste_ausgaben_struktur(conn):
    """
    Analysiere die Struktur der feste_ausgaben Tabelle
    """
    cur = conn.cursor()
    
    print("=== FESTE AUSGABEN STRUKTUR ===")
    cur.execute("SELECT kategorie, COUNT(*) as anzahl, SUM(betrag) as summe FROM feste_ausgaben GROUP BY kategorie ORDER BY kategorie")
    
    for row in cur.fetchall():
        kategorie, anzahl, summe = row
        print(f"{kategorie}: {anzahl} Einträge, Summe: {summe:.2f} €")
    
    print("\n=== ALLE FESTE AUSGABEN (Detail) ===")
    cur.execute("SELECT id, beschreibung, betrag, kategorie, zahlungsmonate FROM feste_ausgaben ORDER BY kategorie, beschreibung")
    
    for row in cur.fetchall():
        id_val, beschreibung, betrag, kategorie, zahlungsmonate = row
        print(f"ID {id_val}: {beschreibung} ({kategorie}) - {betrag:.2f} € - Monate: {zahlungsmonate}")

# Unveränderte Hilfsfunktionen
def get_soll_kontostand_by_monat(conn, jahr, monat):
    """Hole einen spezifischen Soll-Kontostand"""
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM kontostand_monatsende_soll 
        WHERE jahr = %s AND monat = %s
    """, (jahr, monat))
    return cur.fetchone()

def delete_soll_kontostand(conn, jahr, monat):
    """Lösche einen Soll-Kontostand"""
    cur = conn.cursor()
    cur.execute("""
        DELETE FROM kontostand_monatsende_soll 
        WHERE jahr = %s AND monat = %s
    """, (jahr, monat))
    conn.commit()
    return cur.rowcount > 0

def save_soll_kontostaende(conn, jahr, soll_kontostaende):
    """
    Speichere die berechneten Soll-Kontostände in die Datenbank
    """
    cur = conn.cursor()
    
    for monat, soll_kontostand in enumerate(soll_kontostaende, 1):
        # Lösche existierenden Eintrag
        cur.execute("""
            DELETE FROM kontostand_monatsende_soll 
            WHERE jahr = %s AND monat = %s
        """, (jahr, monat))
        
        # Füge neuen Eintrag hinzu
        cur.execute("""
            INSERT INTO kontostand_monatsende_soll (jahr, monat, soll_kontostand)
            VALUES (%s, %s, %s)
        """, (jahr, monat, soll_kontostand))
    
    conn.commit()
    print(f"Soll-Kontostände für {jahr} erfolgreich gespeichert!")

# Hauptfunktion zum Ausführen
def berechne_und_speichere_soll_kontostaende(conn, jahr):
    """
    Hauptfunktion: Berechne und speichere Soll-Kontostände
    """
    print(f"Berechne Soll-Kontostände für {jahr}...")
    
    # Berechne die Soll-Kontostände
    soll_kontostaende = berechne_soll_kontostaende_fuer_jahr(conn, jahr)
    
    # Zeige Verifikation
    verify_jahresuebersicht_calculation(conn, jahr)
    
    # Speichere in Datenbank
    save_soll_kontostaende(conn, jahr, soll_kontostaende)
    
    return soll_kontostaende

def save_ist_kontostand(db, payload: dict):
    stmt = text("""
        INSERT INTO kontostand_monatsende_ist (jahr, monat, ist_kontostand, soll_kontostand, abweichung)
        VALUES (:jahr, :monat, :ist, :soll, :abw)
        ON CONFLICT (jahr, monat)
        DO UPDATE SET ist_kontostand = EXCLUDED.ist_kontostand,
                      soll_kontostand = EXCLUDED.soll_kontostand,
                      abweichung = EXCLUDED.abweichung
        RETURNING *;
    """)
    result = db.execute(stmt, {
        "jahr": payload["jahr"],
        "monat": payload["monat"],
        "ist": payload["ist_kontostand"],
        "soll": payload.get("soll_kontostand"),
        "abw": payload.get("abweichung"),
    })
    row = result.fetchone()
    db.commit()
    return dict(row._mapping) if row else None

def get_ist_kontostand(db: Session, jahr: int, monat: int):
    stmt = text("""
        SELECT *
          FROM kontostand_monatsende_ist
         WHERE jahr = :jahr AND monat = :monat
    """)
    row = db.execute(stmt, {"jahr": jahr, "monat": monat}).fetchone()
    return dict(row._mapping) if row else {"ist_kontostand": None}

# Ausgaben-Änderungen
def create_ausgabe_aenderung(db: Session, ausgabe_id: int, aenderung: schemas.AusgabeAenderungCreate):
    stmt = text("""
        INSERT INTO ausgaben_aenderungen (ausgabe_id, gueltig_ab, betrag)
        VALUES (:ausgabe_id, :gueltig_ab, :betrag)
     RETURNING id, ausgabe_id, gueltig_ab, betrag, erstellt_am
    """)
    params = {
        "ausgabe_id": ausgabe_id,
        "gueltig_ab": aenderung.gueltig_ab,
        "betrag": aenderung.betrag,
    }
    try:
        row = db.execute(stmt, params).fetchone()
        db.commit()
    except Exception:
        db.rollback()
        raise
    return dict(row._mapping) if row else None


def get_ausgabe_aenderungen(db: Session, ausgabe_id: int):
    stmt = text("""
        SELECT id, ausgabe_id, gueltig_ab, betrag, erstellt_am
          FROM ausgaben_aenderungen
         WHERE ausgabe_id = :ausgabe_id
      ORDER BY gueltig_ab ASC
    """)
    rows = db.execute(stmt, {"ausgabe_id": ausgabe_id}).fetchall()
    return [dict(r._mapping) for r in rows]

# Einnahmen-Änderungen
def create_einnahme_aenderung(db: Session, einnahme_id: int, aenderung: schemas.EinnahmeAenderungCreate):
    stmt = text("""
        INSERT INTO einnahmen_aenderungen (einnahme_id, gueltig_ab, betrag)
        VALUES (:einnahme_id, :gueltig_ab, :betrag)
     RETURNING id, einnahme_id, gueltig_ab, betrag, erstellt_am
    """)
    params = {
        "einnahme_id": einnahme_id,
        "gueltig_ab": aenderung.gueltig_ab,
        "betrag": aenderung.betrag,
    }
    try:
        row = db.execute(stmt, params).fetchone()
        db.commit()
    except Exception:
        db.rollback()
        raise
    return dict(row._mapping) if row else None


def get_einnahme_aenderungen(db: Session, einnahme_id: int):
    stmt = text("""
        SELECT id, einnahme_id, gueltig_ab, betrag, erstellt_am
          FROM einnahmen_aenderungen
         WHERE einnahme_id = :id
      ORDER BY gueltig_ab ASC
    """)
    rows = db.execute(stmt, {"id": einnahme_id}).fetchall()
    return [dict(r._mapping) for r in rows]

def get_feste_einnahmen_monat_jahresuebersicht(db: Session, jahr: int, monat: int) -> float:
    monatsdatum = date(jahr, monat, 1)
    query = text("""
        SELECT SUM(
          COALESCE(
            (SELECT betrag
               FROM einnahmen_aenderungen ea
              WHERE ea.einnahme_id = fe.id
                AND ea.gueltig_ab <= :datum
           ORDER BY ea.gueltig_ab DESC
              LIMIT 1),
            fe.betrag
          )
        ) AS summe
          FROM feste_einnahmen fe
         WHERE :monat = ANY(fe.zahlungsmonate)
           AND (fe.kategorie IS NULL OR LOWER(fe.kategorie) NOT LIKE '%andrea%')
           AND (fe.startdatum IS NULL OR fe.startdatum <= :datum)
           AND (fe.enddatum   IS NULL OR fe.enddatum   >= :datum)
    """)
    result = db.execute(query, {"datum": monatsdatum, "monat": monat}).scalar()
    return float(result or 0.0)

def effektiv_ausgabe_im_monat(db: Session, ausgabe_id: int, jahr: int, monat: int) -> float:
    ms = date(jahr, monat, 1)
    stmt = text("""
        SELECT betrag
          FROM ausgaben_aenderungen
         WHERE ausgabe_id = :ausgabe_id
           AND gueltig_ab < (:ms::date + INTERVAL '1 month')
      ORDER BY gueltig_ab DESC
         LIMIT 1
    """)
    row = db.execute(stmt, {"ausgabe_id": ausgabe_id, "ms": ms}).fetchone()
    return float(row[0]) if row else 0.0


def effektiv_einnahme_im_monat(db: Session, einnahme_id: int, jahr: int, monat: int) -> float:
    ms = date(jahr, monat, 1)
    stmt = text("""
        SELECT betrag
          FROM einnahmen_aenderungen
         WHERE einnahme_id = :einnahme_id
           AND gueltig_ab < (:ms::date + INTERVAL '1 month')
      ORDER BY gueltig_ab DESC
         LIMIT 1
    """)
    row = db.execute(stmt, {"einnahme_id": einnahme_id, "ms": ms}).fetchone()
    return float(row[0]) if row else 0.0


def ausgaben_monatssummen(db: Session, year: int):
    stmt = text("""
        WITH mon AS (
          SELECT make_date(:year, m, 1)::date AS monat
            FROM generate_series(1,12) AS m
        ),
        ids AS (
          SELECT id AS ausgabe_id FROM feste_ausgaben
        ),
        eff AS (
          SELECT i.ausgabe_id, m.monat,
                 COALESCE(a.betrag, 0)::numeric(10,2) AS betrag
            FROM ids i
            CROSS JOIN mon m
            LEFT JOIN LATERAL (
              SELECT betrag
                FROM ausgaben_aenderungen
               WHERE ausgabe_id = i.ausgabe_id
                 AND gueltig_ab < (m.monat + INTERVAL '1 month')
            ORDER BY gueltig_ab DESC
               LIMIT 1
            ) a ON TRUE
        )
        SELECT to_char(monat, 'YYYY-MM') AS ym,
               SUM(betrag)::numeric(12,2) AS sum_betrag
          FROM eff
      GROUP BY ym
      ORDER BY ym;
    """)
    rows = db.execute(stmt, {"year": year}).fetchall()
    return [dict(r._mapping) for r in rows]
    
def einnahmen_monatssummen(db: Session, year: int):
    stmt = text("""
        WITH mon AS (
          SELECT make_date(:year, m, 1)::date AS monat
            FROM generate_series(1,12) AS m
        ),
        ids AS (
          SELECT id AS einnahme_id FROM feste_einnahmen
        ),
        eff AS (
          SELECT i.einnahme_id, m.monat,
                 COALESCE(a.betrag, 0)::numeric(10,2) AS betrag
            FROM ids i
            CROSS JOIN mon m
            LEFT JOIN LATERAL (
              SELECT betrag
                FROM einnahmen_aenderungen
               WHERE einnahme_id = i.einnahme_id
                 AND gueltig_ab < (m.monat + INTERVAL '1 month')
            ORDER BY gueltig_ab DESC
               LIMIT 1
            ) a ON TRUE
        )
        SELECT to_char(monat, 'YYYY-MM') AS ym,
               SUM(betrag)::numeric(12,2) AS sum_betrag
          FROM eff
      GROUP BY ym
      ORDER BY ym;
    """)
    rows = db.execute(stmt, {"year": year}).fetchall()
    return [dict(r._mapping) for r in rows]

def update_ausgabe_aenderung(db: Session, aenderung_id: int, payload: schemas.AusgabeAenderungUpdate):
    sets, params = [], {"id": aenderung_id}
    if payload.gueltig_ab is not None:
        sets.append("gueltig_ab = :gueltig_ab")
        params["gueltig_ab"] = payload.gueltig_ab
    if payload.betrag is not None:
        sets.append("betrag = :betrag")
        params["betrag"] = payload.betrag
    if not sets:
        raise HTTPException(400, detail="Nichts zu aktualisieren.")

    stmt = text(f"""
        UPDATE ausgaben_aenderungen
           SET {", ".join(sets)}
         WHERE id = :id
     RETURNING id, ausgabe_id, gueltig_ab, betrag, erstellt_am
    """)
    try:
        row = db.execute(stmt, params).fetchone()
        if not row:
            db.rollback()
            raise HTTPException(404, detail="Änderung nicht gefunden.")
        db.commit()
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise
    return dict(row._mapping)


def delete_ausgabe_aenderung(db: Session, aenderung_id: int):
    stmt = text("DELETE FROM ausgaben_aenderungen WHERE id = :id RETURNING id")
    try:
        row = db.execute(stmt, {"id": aenderung_id}).fetchone()
        if not row:
            db.rollback()
            raise HTTPException(404, detail="Änderung nicht gefunden.")
        db.commit()
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise
    return {"deleted_id": aenderung_id}
    
def update_einnahme_aenderung(db: Session, aenderung_id: int, payload: schemas.EinnahmeAenderungUpdate):
    sets, params = [], {"id": aenderung_id}
    if payload.gueltig_ab is not None:
        sets.append("gueltig_ab = :gueltig_ab")
        params["gueltig_ab"] = payload.gueltig_ab
    if payload.betrag is not None:
        sets.append("betrag = :betrag")
        params["betrag"] = payload.betrag
    if not sets:
        raise HTTPException(400, detail="Nichts zu aktualisieren.")

    stmt = text(f"""
        UPDATE einnahmen_aenderungen
           SET {", ".join(sets)}
         WHERE id = :id
     RETURNING id, einnahme_id, gueltig_ab, betrag, erstellt_am
    """)
    try:
        row = db.execute(stmt, params).fetchone()
        if not row:
            db.rollback()
            raise HTTPException(404, detail="Änderung nicht gefunden.")
        db.commit()
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise
    return dict(row._mapping)


def delete_einnahme_aenderung(db: Session, aenderung_id: int):
    stmt = text("DELETE FROM einnahmen_aenderungen WHERE id = :id RETURNING id")
    try:
        row = db.execute(stmt, {"id": aenderung_id}).fetchone()
        if not row:
            db.rollback()
            raise HTTPException(404, detail="Änderung nicht gefunden.")
        db.commit()
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise
    return {"deleted_id": aenderung_id}

def timeline_ausgabe(db: Session, ausgabe_id: int, year: int):
    stmt = text("""
        WITH mon AS (
          SELECT make_date(:year, m, 1)::date AS monat
            FROM generate_series(1,12) AS m
        )
        SELECT to_char(monat,'YYYY-MM') AS ym,
               COALESCE((
                 SELECT betrag
                   FROM ausgaben_aenderungen a
                  WHERE a.ausgabe_id = :ausgabe_id
                    AND a.gueltig_ab < (mon.monat + INTERVAL '1 month')
               ORDER BY a.gueltig_ab DESC
                  LIMIT 1
               ), 0)::numeric(12,2) AS betrag
          FROM mon
      ORDER BY ym
    """)
    rows = db.execute(stmt, {"year": year, "ausgabe_id": ausgabe_id}).fetchall()
    return [dict(r._mapping) for r in rows]


def timeline_einnahme(db: Session, einnahme_id: int, year: int):
    stmt = text("""
        WITH mon AS (
          SELECT make_date(:year, m, 1)::date AS monat
            FROM generate_series(1,12) AS m
        )
        SELECT to_char(mon.monat,'YYYY-MM') AS ym,
               COALESCE((
                 SELECT ea.betrag
                   FROM einnahmen_aenderungen ea
                  WHERE ea.einnahme_id = :id
                    AND ea.gueltig_ab < (mon.monat + INTERVAL '1 month')
               ORDER BY ea.gueltig_ab DESC
                  LIMIT 1
               ), fe.betrag, 0)::numeric(12,2) AS betrag
          FROM mon
          JOIN feste_einnahmen fe ON fe.id = :id
      ORDER BY ym
    """)
    rows = db.execute(stmt, {"year": year, "id": einnahme_id}).fetchall()
    return [dict(r._mapping) for r in rows]

    
