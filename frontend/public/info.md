
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

### Die Kontostand-Box in der Monatsübersicht lesen
Die Box beantwortet eine Frage: **Ist am Monatsende so viel Geld auf dem Konto wie geplant?** Grün = mehr als geplant, Rot = weniger. Über den Button **„? Wie lese ich das?"** in der Box siehst du denselben Rechenweg mit den Zahlen des gewählten Monats.

**Beispiel (Oktober):** Soll −272 €, Ist aktuell 876 €, Ist Monatsende −765 €, offene ungeplante Ausgaben 154 €.

| Zahl | Bedeutung | Beispiel |
|---|---|---|
| **Soll-Kontostand** | So viel muss am Monatsende auf dem Konto sein, damit sich teure und günstige Monate übers Jahr ausgleichen (Jahresende ±0). Negativ = das Konto darf laut Plan im Minus sein. | −272 € |
| **Virtueller Kontostand** | Geplante feste Einnahmen minus Ausgaben seit Januar – der Stand, wenn alles exakt nach Plan läuft. | −631 € |
| **Ist aktuell** | Dein heute eingetragener Kontostand. | 876 € |
| **Abweichung** | Ist aktuell − Soll. Mitten im Monat meist zu positiv, weil noch feste Posten abgehen. Erst am Monatsende aussagekräftig. | +1148 € |
| **Ist Monatsende** | Hochrechnung: Ist aktuell − noch offene feste Ausgaben + noch offene feste Einnahmen. | −765 € |
| **Abweichung Monatsende** | Ist Monatsende − Soll. **Die wichtigste Zahl.** | −765 − (−272) = −493 € |

**Gelber Kasten (offene ungeplante Ausgaben):** Diese Ausgaben sind schon vom Konto weg, aber noch nicht ausgeglichen. Buchst du sie zurück, steigt „Ist Monatsende" um den Betrag: −765 + 154 = −611 €, Abweichung zum Soll also −339 €. Die graue Klammer („−400 € ggü. September") ist der Trend: Ende September lagst du +61 € über dem Soll, jetzt −339 € darunter – der Abstand hat sich in diesem Monat um 400 € verschlechtert.

**Weißer Kasten:** wiederholt die Abweichung von heute und zeigt, wie du den Vormonat abgeschlossen hast (Ist − Soll am Monatsende).

**Faustregel:** Auf „Abweichung Monatsende" schauen – bei offenen ungeplanten Ausgaben auf den gelben Kasten. Die graue Klammer sagt dir, ob der Monat besser oder schlechter lief als der letzte.

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
