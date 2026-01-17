# Finanzapp

Die Finanzapp ist ein System zur Verwaltung von Haushaltsfinanzen: feste Posten (regelmäßig), ungeplante Transaktionen sowie Soll-/Ist-Kontostände.

- **Backend:** FastAPI (Python 3.11), PostgreSQL  
- **Frontend:** Vue 3 + Bootstrap 5  
- **Zielplattform:** Raspberry Pi (lokal)

---
## Contributing
Please see CONTRIBUTING.md for development and release workflow.

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for instructions on running Finanzapp in
development and production environments.

## Anwenderhilfe
<!-- INFO_START -->

### Was ist die Finanzapp?
Die Finanzapp unterstützt dich beim Überblick über Einnahmen, Ausgaben und Kontostände. Du erfasst feste und ungeplante Posten, vergleichst **Soll-** mit **Ist-Kontostand** und erkennst Abweichungen/Trends.

### Grundbegriffe
- **Soll-Kontostand:** vom System berechneter Endstand je Monat (geplant).
- **Ist-Kontostand:** dein tatsächlicher Kontostand (manuell eingetragen).
- **Abweichung:** Ist minus Soll.
- **Feste Posten:** wiederkehrende Einnahmen/Ausgaben (monatlich/vierteljährlich/jährlich).
- **Ungeplante Transaktionen:** spontane Ausgaben/Einnahmen, die ausgeglichen werden sollten.

### Wie benutze ich die App?
1. **Feste Posten definieren** (Seite „Feste Posten“):  
   - Lege monatliche, vierteljährliche oder jährliche Ausgaben/Einnahmen an und ordne sie einer vordefinierten Kategorie zu.  
   - Du kannst frei auswählen, in **welchen Monaten** ein Posten fällig ist.  
   - **Hinweis (bekannter Fehler):** Nachträgliches Bearbeiten kann aktuell beim Abspeichern fehlschlagen.
2. **Jahresübersicht prüfen**:  
   - Kopfbereich zeigt: **Ausgaben-Mittel**, **Einnahmen-Mittel**, **Jahres-/Monatssaldo**.  
   - Darunter eine tabellarische Übersicht aller Monate mit Einnahmen, Ausgaben und Salden.  
   - **Kennzahlen unter der Tabelle:**  
     - **Summe Ausgaben:** Summe der festen Ausgaben pro Monat im Jahr  
     - **Summe Einnahmen:** Summe der festen Einnahmen pro Monat im Jahr  
     - **Monatssaldo:** Einnahmen – Ausgaben  
     - **Virtueller Kontostand:** kumulierte Monatssalden → so viel **müsste** am Monatsende auf dem Konto sein  
     - **Delta zum Ausgaben-Mittel:** zeigt, ob die Monatskosten im Vergleich zum Schnitt eher hoch/niedrig sind  
     - **Kontostand Monatsende Soll:** sehr wichtig – wie viel Geld am Monatsende im Vergleich zum Ausgaben-Mittel übrig sein muss  
   - **Hinweis „Andrea“:** Dieser Anteil ist nur für die **Einnahmen-Statistik** relevant (Anteil meiner Frau). Für meine eigentlichen Finanzberechnungen ist er sekundär und wird dort herausgerechnet; er erscheint zur Vollständigkeit in der Anzeige.
3. **Monatsübersicht nutzen**:  
   - Feste Posten abhaken, sobald bezahlt/eingegangen.  
   - **Ungeplante Transaktionen** unten erfassen:  
     - Ungeplante **Ausgaben** sind rot, müssen manuell ausgeglichen werden.  
     - Aktion **„Ausgleich“** erzeugt automatisch eine passende ungeplante **Einnahme**, die du direkt speichern kannst.  
   - **Geplante Ergänzung:** Eine kleine **Summenanzeige** direkt unter „Ungeplante Transaktionen“, die aktuelle Gesamt-Ausgaben/Einnahmen des Monats zeigt und ein mögliches Delta hervorhebt.
4. **Ist-Kontostand eintragen**:  
   - Im Feld „Ist-Kontostand“ deinen aktuellen Kontostand eingeben, um die **Abweichung** zum Soll zu sehen.

### Tipps
- „**Soll-Kontostand neu berechnen**“ klicken, wenn Werte unstimmig wirken.  
- **Swagger UI** unter `/docs` nutzen, um API-Endpunkte schnell zu testen.  
- Erst „Feste Posten“ pflegen, dann Monats-/Jahresansichten nutzen.

### Bekannte Einschränkungen & Verbesserungen
- ✖️ **Bearbeiten fester Posten:** Speichern klappt aktuell nicht zuverlässig.  
- ➕ **Kategorie-Auswertung**: „Wie viel gebe ich je Kategorie aus?“ (geplant).  
- ➕ **Jahre vorplanen / Historie:** Vorjahre vergleichen, Folgejahre vorbereiten (geplant).  
- ➕ **Sparen/Rücklagen-Zusammenfassung** (geplant).  
- ➕ **Trend Soll vs. Ist** über Monate zur Problemfrüherkennung (geplant).  

<!-- INFO_END -->

---

## Technische Details

### Start
Backend:
```bash
cd backend
uvicorn main:app --reload
# Swagger: http://localhost:8000/docs

# finanzapp-frontend

Frontend (Vue CLI)
cd frontend
npm install


Development (Hot-Reload):

npm run serve


Production Build:

npm run build


Lint & Fix:

npm run lint


👉 Konfiguration siehe: Vue CLI Configuration Reference

Datenbank

Wichtige Tabellen:

feste_ausgaben

feste_einnahmen

ungeplante_transaktionen

kontostand_monatsende_soll

kontostand_monatsende_ist (enthält Ist-Kontostände, UNIQUE (jahr, monat))

Beispiel-Migration Ist-Kontostände:

CREATE TABLE IF NOT EXISTS kontostand_monatsende_ist (
    id SERIAL PRIMARY KEY,
    jahr INT NOT NULL,
    monat INT NOT NULL,
    ist_kontostand NUMERIC(10,2) NOT NULL,
    soll_kontostand NUMERIC(10,2),
    abweichung NUMERIC(10,2),
    erstellt_am TIMESTAMP DEFAULT NOW(),
    UNIQUE (jahr, monat)
);

API-Endpunkte (Auswahl)
Soll-Kontostände

POST /soll-kontostaende/berechnen/{jahr} → berechnet alle Soll-Werte für ein Jahr

GET /soll-kontostaende/{jahr} → liefert Soll-Kontostände des Jahres

GET /soll-kontostaende/{jahr}/{monat} → liefert Soll-Kontostand für einen Monat

Ist-Kontostände

POST /kontostand-ist → legt an oder aktualisiert (via ON CONFLICT DO UPDATE)

GET /kontostand-ist/{jahr}/{monat} → liest den Ist-Kontostand eines Monats

Monats-/Jahresdaten

GET /monatsuebersicht/{jahr}/{monat} → feste Einnahmen/Ausgaben für Monat

GET /monatswerte/{jahr}/{monat} → Ist-Werte (z. B. tatsächlich gezahlte Beträge)

GET /ungeplante-transaktionen/{jahr}/{monat} → ungeplante Einnahmen/Ausgaben

Dev-Hinweise

Axios-Responses immer über .data auslesen.

SQLAlchemy Row-Objekte → dict(row._mapping) konvertieren.

Frontend-State:

festeAusgaben, festeEinnahmen

ungeplannteAusgaben, ungeplannteEinnahmen

sollKontostand, istKontostand, sollKontostandVormonat