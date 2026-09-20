CREATE TABLE IF NOT EXISTS kredite (
    id          SERIAL PRIMARY KEY,
    bezeichnung VARCHAR(255) NOT NULL,
    kategorie   VARCHAR(100) NOT NULL DEFAULT 'Sonstige',
    darlehensbetrag NUMERIC(12, 2) NOT NULL,
    zinssatz    NUMERIC(6, 4) NOT NULL,  -- Jahreszinssatz in Prozent, z.B. 3.25
    monatliche_rate NUMERIC(10, 2) NOT NULL,
    startdatum  DATE NOT NULL,
    notiz       TEXT,
    erstellt_am TIMESTAMP DEFAULT NOW()
);
