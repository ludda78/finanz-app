-- Migration: Add updated_at timestamps for last-modified tracking
-- Run once on the Raspberry Pi database

ALTER TABLE monatswerte
    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT NOW();

ALTER TABLE kontostand_monatsende_ist
    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT NOW();
