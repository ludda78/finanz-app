from sqlalchemy.orm import Session
import models
import schemas
from datetime import datetime
from sqlalchemy import and_
from typing import List, Optional
from decimal import Decimal
from sqlalchemy import text

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
    if DEBUG:
        debug_alle_kategorien(conn)

    monatliches_mittel_ausgaben = get_monatliches_mittel_feste_ausgaben_ohne_andrea(conn, jahr)
    if DEBUG:
        print(f"\n=== DEBUG: Berechne Soll-Kontostände für {jahr} ===")
        print(f"Monatliches Mittel feste Ausgaben (ohne Andrea): {monatliches_mittel_ausgaben:.2f} €")
        print(f"\n{'Monat':<6} {'Monatsausgaben':<15} {'Delta':<12} {'Kumulativ':<12}")
        print("-" * 50)

    soll_kontostaende = []
    kumulatives_delta = 0
    
    for monat in range(1, 13):
        feste_ausgaben_monat = get_feste_ausgaben_monat_jahresuebersicht(conn, jahr, monat)
        delta = monatliches_mittel_ausgaben - feste_ausgaben_monat
        kumulatives_delta += delta
        soll_kontostaende.append(kumulatives_delta)
        if DEBUG:
            print(f"{monat:<6} {feste_ausgaben_monat:<15.2f} {delta:<12.2f} {kumulatives_delta:<12.2f}")
    
    if DEBUG:
        print("=== ENDE DEBUG Soll-Kontostände ===\n")
    
    return soll_kontostaende

def get_monatliches_mittel_feste_ausgaben_ohne_andrea(conn, jahr):
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM feste_ausgaben 
        WHERE kategorie IS NULL OR LOWER(kategorie) NOT LIKE %s
    """, ('%andrea%',))
    alle_ausgaben = [dict(row) for row in cur.fetchall()]
    
    if DEBUG:
        print("\n=== DEBUG: Berechnung Monatsmittel feste Ausgaben (ohne *Andrea*) ===")
    jahres_summe_ausgaben = 0
    
    for monat in range(1, 13):
        monat_summe = 0
        monatsdatum = f"{jahr}-{monat:02d}-01"
        from datetime import datetime
        monatsdatum_obj = datetime.strptime(monatsdatum, "%Y-%m-%d").date()
        
        for ausgabe in alle_ausgaben:
            if monat in ausgabe['zahlungsmonate']:
                start_aktiv = ausgabe['startdatum'] is None or ausgabe['startdatum'] <= monatsdatum_obj
                end_aktiv = ausgabe['enddatum'] is None or ausgabe['enddatum'] >= monatsdatum_obj
                if start_aktiv and end_aktiv:
                    monat_summe += float(ausgabe['betrag'])
        
        if DEBUG:
            print(f"Monat {monat:2d}: {monat_summe:.2f} €")
        jahres_summe_ausgaben += monat_summe
    
    monatliches_mittel = jahres_summe_ausgaben / 12
    if DEBUG:
        print(f"Jahressumme Ausgaben: {jahres_summe_ausgaben:.2f} €")
        print(f"Monatliches Mittel: {monatliches_mittel:.2f} €")
        print("=== ENDE DEBUG Monatsmittel ===\n")
    
    return monatliches_mittel




def get_feste_ausgaben_monat_jahresuebersicht(conn, jahr, monat):
    """
    Hole die festen Ausgaben für einen Monat (ohne alle Kategorien, die 'Andrea' enthalten)
    """
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM feste_ausgaben 
        WHERE kategorie IS NULL OR LOWER(kategorie) NOT LIKE %s
    """, ('%andrea%',))
    alle_ausgaben = [dict(row) for row in cur.fetchall()]
    
    monat_summe = 0
    monatsdatum = f"{jahr}-{monat:02d}-01"
    from datetime import datetime
    monatsdatum_obj = datetime.strptime(monatsdatum, "%Y-%m-%d").date()
    
    if DEBUG:
        print(f"\n--- DEBUG: Monat {monat:02d}/{jahr} ---")
    
    for ausgabe in alle_ausgaben:
        if monat in ausgabe['zahlungsmonate']:
            start_aktiv = ausgabe['startdatum'] is None or ausgabe['startdatum'] <= monatsdatum_obj
            end_aktiv = ausgabe['enddatum'] is None or ausgabe['enddatum'] >= monatsdatum_obj
            
            if start_aktiv and end_aktiv:
                betrag = float(ausgabe['betrag'])
                monat_summe += betrag
                if DEBUG:
                    print(f"✔ ID {ausgabe['id']}: {ausgabe['beschreibung']} "
                          f"({ausgabe['kategorie']}) {betrag:.2f} €")
            else:
                if DEBUG:
                    print(f"✘ IGNORIERT: {ausgabe['beschreibung']} – "
                          f"außerhalb Zeitraum (Start: {ausgabe['startdatum']}, End: {ausgabe['enddatum']})")
        else:
            if DEBUG:
                print(f"✘ IGNORIERT: {ausgabe['beschreibung']} – nicht im Monat {monat}")
    
    if DEBUG:
        print(f"Summe Monat {monat:02d}: {monat_summe:.2f} €")
        print(f"--- ENDE DEBUG Monat {monat:02d} ---\n")
    
    return monat_summe



def verify_jahresuebersicht_calculation(conn, jahr):
    """
    Überprüfe die Berechnung - sollte mit deiner Jahresübersicht übereinstimmen
    """
    monatliches_mittel = get_monatliches_mittel_feste_ausgaben_ohne_andrea(conn, jahr)
    print(f"Monatliches Mittel feste Ausgaben (ohne Andrea): {monatliches_mittel:.2f} €")
    
    print(f"\n{'Monat':<6} {'Ausgaben':<10} {'Delta':<10} {'Kumulativ':<10}")
    print("-" * 40)
    
    kumulativ = 0
    for monat in range(1, 13):
        feste_ausgaben = get_feste_ausgaben_monat_jahresuebersicht(conn, jahr, monat)
        delta = monatliches_mittel - feste_ausgaben
        kumulativ += delta
        print(f"{monat:<6} {feste_ausgaben:<10.2f} {delta:<10.2f} {kumulativ:<10.2f}")
    
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

