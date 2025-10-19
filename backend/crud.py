from sqlalchemy.orm import Session
import models
import schemas
from datetime import datetime
from sqlalchemy import and_, text
from typing import List, Optional
from decimal import Decimal
from sqlalchemy import text
from datetime import date

DEBUG = False  # zentraler Schalter


def debug_alle_kategorien(conn):
    if not DEBUG:
        return
    cur = conn.cursor()
    try:
        cur.execute("SELECT DISTINCT kategorie FROM feste_ausgaben ORDER BY kategorie")
        kategorien = cur.fetchall()
        print("\n=== DEBUG: Alle Kategorien in feste_ausgaben ===")
        for row in kategorien:
            value = row[0] if isinstance(row, tuple) else row.get("kategorie")
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

def berechne_soll_kontostaende_fuer_jahr(conn, jahr):
    """
    Berechnet mehrere Kennzahlen:
    - Summe Ausgaben / Einnahmen
    - Monatssaldo (Ein - Aus)
    - Virtueller Kontostand (kumulativ)
    - Delta zum Ausgaben-Mittel
    - Kontostand Monatsende Soll
    """
    monatliches_mittel_ausgaben = get_monatliches_mittel_feste_ausgaben_ohne_andrea(conn, jahr)

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
        ausgaben = get_feste_ausgaben_monat_jahresuebersicht(conn, jahr, monat)
        einnahmen = get_feste_einnahmen_monat_jahresuebersicht(conn, jahr, monat)

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


def update_feste_ausgabe(conn, ausgabe_id: int, daten: dict):
    """
    Aktualisiert eine feste Ausgabe (inkl. Enddatum)
    Erwartet ein dict mit den Schlüsseln:
    beschreibung, betrag, kategorie, zahlungsintervall, zahlungsmonate, startdatum, enddatum
    """
    cur = conn.cursor()
    cur.execute("""
        UPDATE feste_ausgaben
        SET beschreibung = %s,
            betrag = %s,
            kategorie = %s,
            zahlungsintervall = %s,
            zahlungsmonate = %s,
            startdatum = %s,
            enddatum = %s
        WHERE id = %s
        RETURNING id, beschreibung, betrag, kategorie, zahlungsintervall, zahlungsmonate, startdatum, enddatum;
    """, (
        daten["beschreibung"],
        daten["betrag"],
        daten["kategorie"],
        daten.get("zahlungsintervall"),
        daten.get("zahlungsmonate"),
        daten["startdatum"],
        daten.get("enddatum"),  # ✅ optional
        ausgabe_id
    ))
    result = cur.fetchone()
    conn.commit()
    return dict(result._mapping) if result else None


def insert_feste_ausgabe(conn, daten: dict):
    """
    Fügt eine neue feste Ausgabe hinzu (inkl. optionalem Enddatum)
    """
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO feste_ausgaben (
            beschreibung, betrag, kategorie, zahlungsintervall, zahlungsmonate, startdatum, enddatum, erstellt_am
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id, beschreibung, betrag, kategorie, zahlungsintervall, zahlungsmonate, startdatum, enddatum, erstellt_am;
    """, (
        daten["beschreibung"],
        daten["betrag"],
        daten["kategorie"],
        daten.get("zahlungsintervall"),
        daten.get("zahlungsmonate"),
        daten["startdatum"],
        daten.get("enddatum"),  # ✅ neu
        date.today()
    ))
    result = cur.fetchone()
    conn.commit()
    return dict(result._mapping)


def get_feste_ausgaben_monat_jahresuebersicht(db, jahr, monat):
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
          AND (fa.enddatum IS NULL OR fa.enddatum >= :datum)
          AND :monat = ANY(fa.zahlungsmonate)
          AND (fa.kategorie IS NULL OR LOWER(fa.kategorie) NOT LIKE '%andrea%')
    """)
    result = db.execute(query, {"datum": monatsdatum, "monat": monat}).scalar()
    return float(result or 0)




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

def get_ist_kontostand(db, jahr: int, monat: int):
    stmt = text("""
        SELECT * 
        FROM kontostand_monatsende_ist 
        WHERE jahr = :jahr AND monat = :monat
    """)
    result = db.execute(stmt, {"jahr": jahr, "monat": monat}).fetchone()
    return dict(result._mapping) if result else {"ist_kontostand": None}

# Ausgaben-Änderungen
def create_ausgabe_aenderung(db, ausgabe_id: int, aenderung: schemas.AusgabeAenderungCreate):
    cur = db.cursor()
    cur.execute("""
        INSERT INTO ausgaben_aenderungen (ausgabe_id, gueltig_ab, betrag)
        VALUES (%s, %s, %s)
        RETURNING id, ausgabe_id, gueltig_ab, betrag, erstellt_am
    """, (ausgabe_id, aenderung.gueltig_ab, aenderung.betrag))
    result = cur.fetchone()
    db.commit()
    return dict(result._mapping)

def get_ausgabe_aenderungen(db, ausgabe_id: int):
    cur = db.cursor()
    cur.execute("""
        SELECT * FROM ausgaben_aenderungen
        WHERE ausgabe_id = %s
        ORDER BY gueltig_ab ASC
    """, (ausgabe_id,))
    return [dict(row._mapping) for row in cur.fetchall()]

# Einnahmen-Änderungen
def create_einnahme_aenderung(db, einnahme_id: int, aenderung: schemas.EinnahmeAenderungCreate):
    cur = db.cursor()
    cur.execute("""
        INSERT INTO einnahmen_aenderungen (einnahme_id, gueltig_ab, betrag)
        VALUES (%s, %s, %s)
        RETURNING id, einnahme_id, gueltig_ab, betrag, erstellt_am
    """, (einnahme_id, aenderung.gueltig_ab, aenderung.betrag))
    result = cur.fetchone()
    db.commit()
    return dict(result._mapping)

def get_einnahme_aenderungen(db, einnahme_id: int):
    cur = db.cursor()
    cur.execute("""
        SELECT * FROM einnahmen_aenderungen
        WHERE einnahme_id = %s
        ORDER BY gueltig_ab ASC
    """, (einnahme_id,))
    return [dict(row._mapping) for row in cur.fetchall()]

def get_feste_einnahmen_monat_jahresuebersicht(db, jahr, monat):
    """
    Liefert die Summe aller festen Einnahmen für einen Monat.
    - Berücksichtigt Änderungen aus einnahmen_aenderungen
    - Ignoriert Kategorie 'Andrea'
    """
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
    return float(result or 0)

