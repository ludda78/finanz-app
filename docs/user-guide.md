# Finanzapp – User Guide

Diese Anleitung richtet sich an Anwender der Finanzapp und beschreibt die grundlegenden Konzepte sowie die tägliche Nutzung der Anwendung.

---

## Was ist die Finanzapp?

Die Finanzapp unterstützt dich beim Überblick über Einnahmen, Ausgaben und Kontostände. Du erfasst feste und ungeplante Posten, vergleichst **Soll-** mit **Ist-Kontostand** und erkennst Abweichungen sowie Trends über Monate hinweg.

---

## Grundbegriffe

* **Soll-Kontostand**
  Vom System berechneter Endstand je Monat (geplant).

* **Ist-Kontostand**
  Dein tatsächlicher Kontostand, manuell eingetragen.

* **Abweichung**
  Differenz zwischen Ist- und Soll-Kontostand.

* **Feste Posten**
  Wiederkehrende Einnahmen oder Ausgaben (monatlich, vierteljährlich oder jährlich).

* **Ungeplante Transaktionen**
  Spontane Einnahmen oder Ausgaben, die nicht Teil der festen Planung sind und idealerweise ausgeglichen werden.

---

## Nutzung der App

### 1. Feste Posten definieren

Auf der Seite **„Feste Posten“** legst du wiederkehrende Einnahmen und Ausgaben an.

* Auswahl der Häufigkeit (monatlich / vierteljährlich / jährlich)
* Zuordnung zu einer vordefinierten Kategorie
* Freie Auswahl der Monate, in denen der Posten fällig ist

**Bekannte Einschränkung:**
Das nachträgliche Bearbeiten fester Posten kann aktuell beim Abspeichern fehlschlagen.

---

### 2. Jahresübersicht prüfen

Die Jahresübersicht bietet einen aggregierten Blick auf das gesamte Jahr.

**Kopfbereich:**

* Durchschnittliche Ausgaben
* Durchschnittliche Einnahmen
* Jahres- und Monatssaldo

**Tabellarischer Bereich:**

* Monatsweise Auflistung von Einnahmen, Ausgaben und Salden

**Kennzahlen unter der Tabelle:**

* **Summe Ausgaben:** Durchschnittliche feste Ausgaben pro Monat
* **Summe Einnahmen:** Durchschnittliche feste Einnahmen pro Monat
* **Monatssaldo:** Einnahmen minus Ausgaben
* **Virtueller Kontostand:** Kumulierte Monatssalden
* **Delta zum Ausgaben-Mittel:** Einordnung der Monatskosten im Vergleich zum Durchschnitt
* **Kontostand Monatsende Soll:** Erwarteter Kontostand am Monatsende

**Hinweis „Andrea“:**
Dieser Anteil ist ausschließlich für die Einnahmenstatistik relevant. Für die eigentlichen Finanzberechnungen wird er herausgerechnet, erscheint aber aus Transparenzgründen in der Anzeige.

---

### 3. Monatsübersicht nutzen

In der Monatsübersicht arbeitest du mit den tatsächlichen Bewegungen des Monats.

* Feste Posten abhaken, sobald sie bezahlt oder eingegangen sind
* **Ungeplante Transaktionen** im unteren Bereich erfassen

  * Ungeplante **Ausgaben** werden rot dargestellt
  * Die Aktion **„Ausgleich“** erzeugt automatisch eine passende ungeplante Einnahme

**Geplante Erweiterung:**
Eine Summenanzeige für ungeplante Einnahmen und Ausgaben zur besseren Übersicht.

---

### 4. Ist-Kontostand eintragen

Trage deinen aktuellen Kontostand im Feld **„Ist-Kontostand“** ein, um die Abweichung zum berechneten Soll-Kontostand sichtbar zu machen.

---

## Tipps

* Bei unstimmigen Werten die Funktion **„Soll-Kontostand neu berechnen“** nutzen
* Die **Swagger UI** unter `/docs` verwenden, um API-Endpunkte zu testen
* Zuerst feste Posten pflegen, anschließend Monats- und Jahresansichten nutzen

---

## Bekannte Einschränkungen und geplante Verbesserungen

### Aktuelle Einschränkungen

* Bearbeiten fester Posten ist nicht zuverlässig möglich

### Geplante Erweiterungen

* Kategorie-Auswertungen ("Wie viel gebe ich je Kategorie aus?")
* Vergleich von Vorjahren und Planung zukünftiger Jahre
* Übersicht zu Sparzielen und Rücklagen
* Trendanalyse Soll vs. Ist über mehrere Monate
