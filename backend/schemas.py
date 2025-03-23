from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date

class FesteAusgabeSchema(BaseModel):
    id: int
    beschreibung: str
    betrag: float
    kategorie: str
    zahlungsintervall: Optional[str] = None
    zahlungsmonate: Optional[List[int]] = None
    startdatum: date
    enddatum: Optional[date] = None
    erstellt_am: Optional[date] = None

    class Config:
        from_attributes = True

class UngeplanteAusgabeSchema(BaseModel):
    id: int
    beschreibung: str
    betrag: float
    kategorie: str
    datum: date
    erstellt_am: Optional[date] = None

    class Config:
        from_attributes = True

class UngeplanteEinnahmeSchema(BaseModel):
    id: int
    beschreibung: str
    betrag: float
    datum: date
    erstellt_am: Optional[date] = None

    class Config:
        from_attributes = True

class MonatsuebersichtResponse(BaseModel):
    monat: int
    jahr: int
    feste_ausgaben: List[FesteAusgabeSchema]
    ungeplante_ausgaben: List[UngeplanteAusgabeSchema]
    ungeplante_einnahmen: List[UngeplanteEinnahmeSchema]
    gesamt_ausgaben: float
    gesamt_einnahmen: float

class UngeplantTransaktionCreate(BaseModel):
    typ: str
    beschreibung: str
    betrag: float
    kommentar: Optional[str] = None
    monat: int
    jahr: int
    
    class Config:
        orm_mode = True
    