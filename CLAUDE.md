# finanzapp – Projektkontext für Claude

Persönliche Finanz-App (Haushalt Martin + Andrea). Läuft lokal im Heimnetz auf einem Raspberry Pi.

## Stack

- **Frontend:** Vue.js 3 (Vue CLI), Bootstrap, Axios
- **Backend:** Python / FastAPI (uvicorn), SQLAlchemy
- **Datenbank:** PostgreSQL (lokal auf dem Pi)
- **Server:** nginx (statisches Frontend + API-Proxy) + systemd (Backend-Services)

## Projektstruktur

```
finanzapp/
├── frontend/          # Vue.js App
│   ├── src/
│   │   ├── components/
│   │   │   ├── MonatsUebersicht.vue    # Monatsübersicht, Kontostand, offene Posten
│   │   │   ├── JahresUebersicht.vue    # Jahreskennzahlen, feste Posten-Tabellen
│   │   │   ├── FesteKonfiguration.vue  # Verwaltung fester Ein-/Ausgaben
│   │   │   ├── Auswertung.vue          # Jahresauswertung: Saldo-Chart, variable Kosten, Delta feste Posten
│   │   │   ├── Kredite.vue             # Kreditverwaltung: Kennzahlen, Restschuld-Chart, CRUD
│   │   │   └── InfoPage.vue
│   │   └── api.js                      # Axios-Client, baseURL: "/api"
│   └── vue.config.js                   # Dev-Proxy /api → localhost:8001
└── backend/
    ├── main.py         # FastAPI-Endpunkte
    ├── crud.py         # Datenbanklogik, Berechnungen
    ├── models.py
    └── config.py       # ENV, DEBUG, FRONTEND_ORIGINS aus Env-Vars
```

## Wichtige Berechnungslogik

- **Soll-Kontostand** = kumulierte Abweichung der monatlichen Ausgaben vom Jahresdurchschnitt (nur feste Ausgaben, ohne Kategorie "Andrea"). Berechnet in `crud.py::berechne_soll_kontostaende_fuer_jahr`.
- **Virtueller Kontostand** = kumulierter Monatssaldo (Einnahmen − Ausgaben).
- **Delta zum Mittel** = monatliche Einzelabweichung vom Durchschnitt — Kumulation davon ergibt den Soll-Kontostand.
- **Annuitätendarlehen (Kredite)** = Tilgungsplan wird vollständig im Frontend berechnet (`Kredite.vue::berechnePlan`): Monatszins = Restschuld × Zinssatz / 12 / 100, Tilgung = Rate − Zinsen, neue Restschuld = Restschuld − Tilgung.

## API-Endpunkte (Backend)

| Methode | Pfad | Beschreibung |
|---------|------|--------------|
| GET | `/jahresuebersicht/{jahr}` | Jahreskennzahlen, Soll-/virtueller Kontostand, Detailposten |
| GET | `/variable-jahresuebersicht/{jahr}` | Ungeplante Transaktionen gruppiert nach Monat/Typ |
| GET | `/feste-posten-delta/{jahr}` | Finanzielle Auswirkung aller Änderungen an festen Posten |
| GET/POST | `/kredite` | Alle Kredite abrufen / neuen Kredit anlegen |
| PUT/DELETE | `/kredite/{id}` | Kredit bearbeiten / löschen |
| GET | `/feste-ausgaben`, `/feste-einnahmen` | Feste Posten verwalten |
| POST | `/kontostand-ist` | Ist-Kontostand speichern |

## Tabellen (Datenbank)

- `feste_ausgaben`, `feste_einnahmen` — feste monatliche Posten
- `ausgaben_aenderungen`, `einnahmen_aenderungen` — Betragsänderungen mit `gueltig_ab`
- `ungeplante_transaktionen` — variable Ein-/Ausgaben (Spalten: `typ`, `monat`, `jahr`, `betrag`)
- `kredite` — Darlehen (Darlehensbetrag, Zinssatz, Rate, Startdatum)

## Deployment-Workflow

Änderungen werden **lokal auf Windows** gemacht und per git auf den Pi deployed. Nie direkt auf dem Pi editieren.

### Raspberry Pi

- SSH: `ssh Martin@192.168.178.138` (Key-Auth)
- **Prod:** Port 80, `/opt/finanzapp/prod/`, Backend-Service `finanzapp-backend.service`
- **Dev:** Port 8080, `/opt/finanzapp/dev/`, Backend-Service `finanzapp-dev.service`

## Datenbanken

| | Datenbank | Config |
|---|---|---|
| **Prod** | `finanzverwaltung` | `/etc/systemd/system/finanzapp-backend.service.d/override.conf` |
| **Dev** | `finanzapp_dev` | `/opt/finanzapp/dev/backend/.env` |

User: `martin`, Host: `localhost:5432`

**Dev-DB mit Prod-Daten synchronisieren** (bei Bedarf vor Tests):
```bash
ssh Martin@192.168.178.138 "PGPASSWORD='...' pg_dump -U martin --clean --if-exists finanzverwaltung | PGPASSWORD='...' psql -U martin finanzapp_dev"
```

---

### Dev deployen

```bash
# 1. Lokal committen + pushen
git add <datei> && git commit -m "..." && git push origin dev

# 2. Pi syncen + Frontend bauen
ssh Martin@192.168.178.138 "cd /opt/finanzapp/dev && git pull && cd frontend && npm run build"

# 4. Nur bei Backend-Änderungen:
ssh Martin@192.168.178.138 "sudo systemctl restart finanzapp-dev.service"
```

### Prod deployen (Release)

```bash
git checkout main && git merge dev
git tag -a vX.Y.Z -m "Release vX.Y.Z" && git push && git push --tags

ssh Martin@192.168.178.138 "cd /opt/finanzapp/prod && git fetch --tags && git checkout vX.Y.Z"
ssh Martin@192.168.178.138 "cd /opt/finanzapp/prod/frontend && npm run build"
ssh Martin@192.168.178.138 "sudo systemctl restart finanzapp-backend.service"
```

## Git

- Remote: https://github.com/ludda78/finanz-app.git
- `dev` → aktive Entwicklung
- `main` → nur stabile Release-Commits, immer mit Git-Tag
